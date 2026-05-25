"""
商品评价模块 - Django App 配置 (apps)

Django 应用配置文件，定义 reviews 应用的元信息和初始化逻辑。

ready() 方法的作用:
当 Django 启动时自动调用，用于注册信号接收器。
信号必须在应用就绪(ready)时导入，否则 Django 无法建立信号与接收器的连接。

如果不在此处导入 signals，信号接收器不会被注册，
评价变更时将不会自动更新商品的平均评分。
"""

from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    """
    评价应用配置类

    Django 约定每个 app 的 AppConfig 子类放在 apps.py 中，
    并在 INSTALLED_APPS 中注册 (此处为 'apps.reviews')。
    """

    # 默认主键字段类型: BigAutoField 是 64 位自增整数，比默认的 AutoField (32位) 容量更大
    default_auto_field = 'django.db.models.BigAutoField'

    # 应用的 Python 模块路径，必须与 INSTALLED_APPS 中的配置一致
    name = 'apps.reviews'

    # Django Admin 中显示的应用名称
    verbose_name = '商品评价'

    def ready(self):
        """
        Django 应用就绪回调

        在 Django 启动过程中，所有 app 加载完成后调用。
        此处导入 signals 模块，确保信号接收器 (@receiver) 被注册到 Django 的信号系统中。

        # noqa 注释: 告诉 lint 工具忽略 "imported but unused" 的警告，
        因为这个 import 的副作用 (注册信号) 才是真正目的，并非需要在代码中使用该模块。
        """
        import apps.reviews.signals  # noqa
