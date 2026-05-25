"""
账户模块 - 序列化器

负责请求数据的验证（反序列化）和响应数据的格式化（序列化）。
每个序列化器对应一个特定的 API 操作，遵循单一职责原则。

为什么序列化器要单独定义而不是在视图中处理：
1. 数据验证逻辑复用（如注册时的密码强度校验同时在多个入口使用）
2. 清晰的输入/输约定，与 Django Form 的设计理念一致
3. 嵌套关系的处理（如用户关联的地址列表）在序列化器中声明更直观
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Address

# 获取当前项目中配置的用户模型（而非直接 import User）
# 这样做的好处：如果将来切换到其他用户模型，只需修改 AUTH_USER_MODEL 配置
User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    邮箱注册序列化器。

    注册流程：
    1. 用户提交 email, username, password, password2, code（邮箱验证码）
    2. validate() 校验两次密码一致 + 验证码正确
    3. create() 调用 User.objects.create_user() 创建用户（密码自动哈希）

    为什么 password2 不存入数据库：它只是前端确认密码的辅助字段，
    在 validate() 中验证一致后即被 pop 掉，不会传给 create()。
    """

    # write_only=True: 密码只接受输入，不在任何响应中返回（安全考虑）
    # validators=[validate_password]: 使用 Django 内置密码强度校验器（最小长度、不能纯数字等）
    password = serializers.CharField(write_only=True, validators=[validate_password])

    # 确认密码字段，仅用于前端二次确认，不与模型字段对应
    password2 = serializers.CharField(write_only=True)

    # 邮箱验证码，required=False 允许序列化器初始化时不传（实际 validate 中会检查）
    code = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        # 注意：phone 不在 fields 中，邮箱注册不要求填手机号
        fields = ['email', 'username', 'password', 'password2', 'code']

    def validate(self, attrs):
        """
        全局验证：同时校验密码一致性和验证码正确性。

        为什么要在这里校验而不是在单个字段校验：
        密码一致性需要对比两个字段，单个字段校验方法只能访问自己的值，
        无法访问另一个字段。DRF 的 validate() 可以访问所有字段。

        Raises:
            ValidationError: 密码不一致或验证码错误
        """
        # 校验两次密码是否一致，验证通过后 pop 掉 password2（不需要传给 create）
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password2': '两次密码不一致'})

        # 校验邮箱验证码
        code = attrs.pop('code', None)
        if not code:
            raise serializers.ValidationError({'code': '请输入邮箱验证码'})
        # 延迟导入，避免模块加载时的循环依赖
        from .verification import verify_email_code
        if not verify_email_code(attrs['email'], code):
            raise serializers.ValidationError({'code': '验证码错误或已过期'})

        return attrs

    def create(self, validated_data):
        """
        创建新用户。

        使用 create_user() 而非 create() 的原因：
        create_user() 会自动调用 set_password() 对密码进行哈希处理，
        如果直接使用 create()，密码将以明文存储，这是严重的安全漏洞。
        """
        return User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
        )


class SendCodeSerializer(serializers.Serializer):
    """
    发送邮箱验证码的请求序列化器。

    仅接受一个 email 字段，由 EmailField 自动校验格式合法性。
    """

    # EmailField 自动校验邮箱格式（如必须包含 @ 和域名）
    email = serializers.EmailField()


class SendSmsCodeSerializer(serializers.Serializer):
    """
    发送短信验证码的请求序列化器。

    min_length=11, max_length=11 确保是合法手机号长度。
    注意：这里只做长度校验，不校验号段（如 13x/15x/18x），
    如需更严格的校验可在 validate_phone() 中添加正则。
    """

    phone = serializers.CharField(min_length=11, max_length=11)


class LoginSerializer(serializers.Serializer):
    """
    登录请求序列化器。

    设计说明——为什么使用单一 account 字段而非 email + phone 两个字段：
    用户体验更好：用户只需一个输入框，系统自动判断是邮箱还是手机号。
    判断逻辑在视图层：如果 account 包含 '@' 则按邮箱处理，否则按手机号处理。
    """

    # 登录账号：可以是邮箱或手机号
    account = serializers.CharField()  # email or phone

    # 登录密码
    password = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """
    用户信息序列化器，用于返回用户数据（GET 响应）和更新用户资料（PATCH 响应）。

    总消费金额（total_spent）是计算字段而非数据库字段：
    每次查询时从订单表实时聚合，避免数据不一致（订单状态变更后金额需同步更新）。
    """

    # SerializerMethodField: 值由 get_total_spent() 方法动态计算，不来自模型字段
    total_spent = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'phone', 'age', 'gender', 'is_vip', 'is_staff', 'is_active', 'total_spent', 'date_joined']
        # 只读字段：邮箱和注册时间一旦设定不应被用户随意修改
        read_only_fields = ['id', 'email', 'date_joined', 'total_spent']

    def get_total_spent(self, obj):
        """
        计算用户历史总消费金额。

        从订单表聚合所有订单的 total_amount 求和。
        为什么使用 Sum 聚合而非在 User 模型上维护一个字段：
        用户模型不应关心订单的计费逻辑，保持模型的内聚性。
        性能说明：如果用户订单量极大（>10万），建议加 Redis 缓存。

        Returns:
            float: 总消费金额，无订单时返回 0.00
        """
        from django.db.models import Sum
        from apps.orders.models import Order
        total = Order.objects.filter(user=obj).aggregate(s=Sum('total_amount'))['s']
        return float(total) if total else 0.00


class AddressSerializer(serializers.ModelSerializer):
    """
    收货地址序列化器。

    创建和更新时自动关联当前登录用户，并处理默认地址的互斥逻辑：
    一个用户只能有一个默认地址，设置新默认地址时自动取消旧默认地址。
    """

    class Meta:
        model = Address
        fields = ['id', 'recipient_name', 'phone', 'address_line1', 'address_line2',
                  'city', 'state', 'postal_code', 'country', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_address_line1(self, value):
        """截断超过255字符的地址（Nominatim返回的display_name可能很长）"""
        return value[:255] if len(value) > 255 else value

    def create(self, validated_data):
        """
        创建新地址。

        处理两个关键逻辑：
        1. 自动注入当前登录用户作为地址所有者（不在请求中传递 user 字段更安全）
        2. 如果新地址设为默认，先将该用户的所有旧默认地址取消
        """
        # 从视图层的 context 中获取当前请求用户
        validated_data['user'] = self.context['request'].user
        # 如果新地址标记为默认，取消该用户已有的默认地址
        if validated_data.get('is_default'):
            Address.objects.filter(user=validated_data['user'], is_default=True).update(is_default=False)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        更新地址信息。

        同样处理默认地址互斥：如果用户将一个已有地址设为默认，
        需要先把该用户当前的默认地址取消，保证只有一个默认地址。
        """
        if validated_data.get('is_default'):
            Address.objects.filter(user=instance.user, is_default=True).update(is_default=False)
        return super().update(instance, validated_data)


# ======== 手机号注册 ========

class PhoneRegisterSerializer(serializers.ModelSerializer):
    """
    手机号注册序列化器。

    与邮箱注册的区别：
    1. 使用 phone 而非 email 作为唯一标识
    2. 自动生成虚拟邮箱（phone@phone.user），因为系统 USERNAME_FIELD 是 email，
       Django 要求 email 字段有值，这里用虚拟邮箱占位
    3. username 使用手机号，方便后台查看
    """

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    code = serializers.CharField(write_only=True)  # 短信验证码（必填）

    class Meta:
        model = User
        fields = ['phone', 'password', 'password2', 'code']

    def validate(self, attrs):
        """
        校验：密码一致性 + 短信验证码 + 手机号唯一性。
        """
        # 确认两次密码输入一致
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password2': '两次密码不一致'})

        phone = attrs['phone']
        code = attrs.pop('code')
        # 校验短信验证码
        from .verification import verify_phone_code
        if not verify_phone_code(phone, code):
            raise serializers.ValidationError({'code': '验证码错误或已过期'})

        # 检查手机号是否已被注册（unique=True 约束会在 save 时报错，这里提前给出友好提示）
        if User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError({'phone': '该手机号已注册'})

        return attrs

    def create(self, validated_data):
        """
        创建手机号注册用户。

        为什么生成虚拟邮箱 phone@phone.user：
        Django 的 AbstractUser 要求 email 字段必须存在（USERNAME_FIELD='email'），
        但手机号注册的用户可能没有邮箱。使用虚拟邮箱可以绕过这一限制，
        同时方便在后台识别这些用户是通过手机号注册的。
        """
        phone = validated_data['phone']
        return User.objects.create_user(
            email=f'{phone}@phone.user',  # 虚拟邮箱
            username=phone,                # 用手机号作为用户名
            phone=phone,
            password=validated_data['password'],
        )


# ======== 手机号登录 ========

class PhoneLoginSerializer(serializers.Serializer):
    """
    手机号验证码登录序列化器。

    与密码登录的区别：
    不需要密码，用户输入手机号和短信验证码即可登录。
    这是一种无密码登录方式，用户体验更好（无需记住密码），
    安全性依赖短信验证码的单次有效性。
    """

    phone = serializers.CharField()
    code = serializers.CharField()

    def validate(self, attrs):
        """
        仅校验短信验证码是否正确，不对手机号做存在性检查。
        如果用户不存在，视图层会处理（自动注册或返回错误）。
        """
        from .verification import verify_phone_code
        if not verify_phone_code(attrs['phone'], attrs['code']):
            raise serializers.ValidationError({'code': '验证码错误或已过期'})
        return attrs


# ======== 密码重置 ========

class PasswordResetRequestSerializer(serializers.Serializer):
    """
    密码重置请求——第一步：发送验证码。

    用户输入注册邮箱，系统验证该邮箱已注册后发送验证码。
    为什么要验证邮箱是否已注册：防止恶意用户向任意邮箱发送验证码骚扰他人。
    """

    # 目标邮箱
    target = serializers.CharField()  # email

    def validate_target(self, value):
        """
        校验目标邮箱是否已注册。

        使用字段级验证器 validate_<field_name> 而非全局 validate()，
        因为这里只关心单个字段的合法性，放在字段验证器中职责更清晰。
        """
        User = get_user_model()
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('该邮箱未注册')
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    密码重置请求——第二步：确认重置。

    用户输入邮箱、验证码和新密码，验证码通过后重置密码。
    """

    target = serializers.CharField()  # 邮箱
    code = serializers.CharField()    # 验证码
    new_password = serializers.CharField(validators=[validate_password])  # 新密码（带强度校验）

    def validate(self, attrs):
        """
        校验验证码是否正确。
        """
        from .verification import verify_email_code
        if not verify_email_code(attrs['target'], attrs['code']):
            raise serializers.ValidationError({'code': '验证码错误或已过期'})
        return attrs


# ======== 旧版密码修改 ========

class ChangePasswordSerializer(serializers.Serializer):
    """
    已登录用户的密码修改序列化器。

    与密码重置的区别：
    - 密码修改：用户已登录，知道旧密码，需要验证旧密码后设置新密码
    - 密码重置：用户忘记密码，通过邮箱验证码来设置新密码

    需要提供旧密码以验证操作者是账户本人，防止他人趁用户离开电脑时修改密码。
    """

    old_password = serializers.CharField()  # 旧密码（用于身份验证）
    new_password = serializers.CharField(validators=[validate_password])  # 新密码

    def validate_old_password(self, value):
        """
        验证旧密码是否正确。

        这是安全关键步骤：如果旧密码校验失败，说明操作者不知道原密码，
        可能是恶意操作，必须拒绝。
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('原密码不正确')
        return value
