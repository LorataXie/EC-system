from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Address

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    code = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2', 'code']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password2': '两次密码不一致'})

        code = attrs.pop('code', None)
        if not code:
            raise serializers.ValidationError({'code': '请输入邮箱验证码'})
        from .verification import verify_code
        if not verify_code(attrs['email'], code):
            raise serializers.ValidationError({'code': '验证码错误或已过期'})

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
        )


class SendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()


class SendSmsCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(min_length=11, max_length=11)


class LoginSerializer(serializers.Serializer):
    account = serializers.CharField()  # email or phone
    password = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    total_spent = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'phone', 'age', 'gender', 'is_vip', 'is_staff', 'is_active', 'total_spent', 'date_joined']
        read_only_fields = ['id', 'email', 'date_joined', 'total_spent']

    def get_total_spent(self, obj):
        from django.db.models import Sum
        from apps.orders.models import Order
        total = Order.objects.filter(user=obj).aggregate(s=Sum('total_amount'))['s']
        return float(total) if total else 0.00


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'recipient_name', 'phone', 'address_line1', 'address_line2',
                  'city', 'state', 'postal_code', 'country', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        if validated_data.get('is_default'):
            Address.objects.filter(user=validated_data['user'], is_default=True).update(is_default=False)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('is_default'):
            Address.objects.filter(user=instance.user, is_default=True).update(is_default=False)
        return super().update(instance, validated_data)


# ======== Phone Register ========

class PhoneRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    code = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['phone', 'password', 'password2', 'code']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password2': '两次密码不一致'})

        phone = attrs['phone']
        code = attrs.pop('code')
        from .verification import verify_phone_code
        if not verify_phone_code(phone, code):
            raise serializers.ValidationError({'code': '验证码错误或已过期'})

        if User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError({'phone': '该手机号已注册'})

        return attrs

    def create(self, validated_data):
        phone = validated_data['phone']
        return User.objects.create_user(
            email=f'{phone}@phone.user',
            username=phone,
            phone=phone,
            password=validated_data['password'],
        )


# ======== Phone Login ========

class PhoneLoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    code = serializers.CharField()

    def validate(self, attrs):
        from .verification import verify_phone_code
        if not verify_phone_code(attrs['phone'], attrs['code']):
            raise serializers.ValidationError({'code': '验证码错误或已过期'})
        return attrs


# ======== Password Reset ========

class PasswordResetRequestSerializer(serializers.Serializer):
    target = serializers.CharField()  # email

    def validate_target(self, value):
        User = get_user_model()
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('该邮箱未注册')
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    target = serializers.CharField()
    code = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])

    def validate(self, attrs):
        from .verification import verify_email_code
        if not verify_email_code(attrs['target'], attrs['code']):
            raise serializers.ValidationError({'code': '验证码错误或已过期'})
        return attrs


# ======== Legacy ========

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('原密码不正确')
        return value
