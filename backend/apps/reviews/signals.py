from django.db.models import Avg
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Review


@receiver([post_save, post_delete], sender=Review)
def update_product_rating(sender, instance, **kwargs):
    product = instance.product
    avg = Review.objects.filter(product=product).aggregate(a=Avg('rating'))['a']
    product.rating_avg = round(float(avg), 2) if avg else 0.00
    product.save(update_fields=['rating_avg'])
