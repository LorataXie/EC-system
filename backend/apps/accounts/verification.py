import random
from django.core.cache import cache
from django.core.mail import send_mail


def _generate_code():
    return str(random.randint(100000, 999999))


def _set_cache(key, code):
    cache.set(f'verify_code:{key}', code, timeout=300)  # 5 minutes


def _check_cache(key, code):
    stored = cache.get(f'verify_code:{key}')
    if stored and stored == code:
        cache.delete(f'verify_code:{key}')
        return True
    return False


# ======== Email ========

def generate_email_code(email):
    code = _generate_code()
    _set_cache(email, code)
    return code


def verify_email_code(email, code):
    return _check_cache(email, code)


def send_verification_email(email, code):
    send_mail(
        subject='EC商城 - 邮箱验证码',
        message=f'您的验证码是：{code}，5 分钟内有效。请勿将验证码泄露给他人。',
        from_email=None,
        recipient_list=[email],
        fail_silently=False,
    )


# ======== Phone ========

def generate_phone_code(phone):
    code = _generate_code()
    _set_cache(phone, code)
    return code


def verify_phone_code(phone, code):
    return _check_cache(phone, code)


def send_verification_sms(phone, code):
    from .sms import send_sms
    try:
        send_sms(phone, code)
        return True, ''
    except Exception as e:
        return False, str(e)
