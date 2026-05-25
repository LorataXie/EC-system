"""
账户模块 - 验证码服务

为邮箱和手机号提供验证码的生成、存储、校验和发送功能。

设计说明：
- 验证码使用 Django 缓存系统存储（默认 Redis），设置 5 分钟过期
- 验证码为 6 位随机数字，兼顾安全性和用户体验
- 验证成功后立即删除缓存中的验证码，防止重复使用
- 邮箱和手机号使用各自的缓存键前缀，互不干扰
"""
import random
from django.core.cache import cache
from django.core.mail import send_mail


def _generate_code():
    """
    生成 6 位随机数字验证码。

    为什么用 6 位数字而不是更短/更长：
    - 4 位太短容易被暴力破解
    - 6 位在安全性和用户记忆负担之间取得较好平衡
    - 业界常见做法（支付宝、微信等均使用 6 位验证码）

    Returns:
        str: 6 位数字字符串，如 "384729"
    """
    return str(random.randint(100000, 999999))


def _set_cache(key, code):
    """
    将验证码存入缓存，设置 5 分钟过期时间。

    使用统一的缓存键前缀 'verify_code:'，方便在 Redis 中进行管理和批量清理。
    timeout=300 秒（5 分钟），超出后验证码自动失效，无需手动清理过期数据。

    Args:
        key: 邮箱地址或手机号，作为缓存的唯一标识
        code: 6 位验证码
    """
    cache.set(f'verify_code:{key}', code, timeout=300)  # 5 minutes


def _check_cache(key, code):
    """
    校验缓存中的验证码是否匹配。

    校验成功后立即删除缓存中的验证码，确保一次性使用（防止重放攻击）。
    校验失败不删除，用户可以在有效期内重试。

    Args:
        key: 邮箱地址或手机号
        code: 用户输入的验证码

    Returns:
        bool: True 表示验证通过，False 表示验证码不存在或不匹配
    """
    stored = cache.get(f'verify_code:{key}')
    if stored and stored == code:
        # 验证成功，立即删除防止重复使用
        cache.delete(f'verify_code:{key}')
        return True
    return False


# ======== 邮箱验证码 ========

def generate_email_code(email):
    """
    为指定邮箱生成验证码并存入缓存。

    这是一个便捷函数，组合了 _generate_code 和 _set_cache 两个步骤。

    Args:
        email: 用户邮箱地址

    Returns:
        str: 生成的 6 位验证码，供后续发送邮件使用
    """
    code = _generate_code()
    _set_cache(email, code)
    return code


def verify_email_code(email, code):
    """
    校验邮箱验证码是否正确。

    Args:
        email: 用户邮箱地址
        code: 用户输入的验证码

    Returns:
        bool: 验证是否通过
    """
    return _check_cache(email, code)


def send_verification_email(email, code):
    """
    发送包含验证码的邮件。

    使用 Django 内置的 send_mail 发送，邮件配置在 settings.py 的 EMAIL_* 中设置。
    邮件标题和正文都包含"EC商城"品牌标识，正文附带安全提示。

    Args:
        email: 收件人邮箱地址
        code: 要发送的验证码
    """
    send_mail(
        subject='EC商城 - 邮箱验证码',
        message=f'您的验证码是：{code}，5 分钟内有效。请勿将验证码泄露给他人。',
        from_email=None,  # 使用 settings.DEFAULT_FROM_EMAIL
        recipient_list=[email],
        fail_silently=False,  # 发送失败时抛出异常，由调用方决定如何处理
    )


# ======== 手机验证码 ========

def generate_phone_code(phone):
    """
    为指定手机号生成验证码并存入缓存。

    与邮箱验证码使用相同的缓存机制（_set_cache），
    但缓存键是手机号，与邮箱验证码的缓存空间隔离。

    Args:
        phone: 用户手机号

    Returns:
        str: 生成的 6 位验证码
    """
    code = _generate_code()
    _set_cache(phone, code)
    return code


def verify_phone_code(phone, code):
    """
    校验手机验证码是否正确。

    Args:
        phone: 用户手机号
        code: 用户输入的验证码

    Returns:
        bool: 验证是否通过
    """
    return _check_cache(phone, code)


def send_verification_sms(phone, code):
    """
    发送包含验证码的短信。

    当前因短信服务商签名审核问题，实际发送已停用（见 sms.py），
    但函数接口保留，以便将来恢复短信功能时无需修改调用方代码。

    Args:
        phone: 收短信的手机号
        code: 要发送的验证码

    Returns:
        tuple: (success: bool, error_message: str)
               success=True 表示发送成功，False 表示发送失败
    """
    from .sms import send_sms
    try:
        send_sms(phone, code)
        return True, ''
    except Exception as e:
        return False, str(e)
