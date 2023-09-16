from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
# from django.conf import settings

from .models import TankOwner


@receiver(pre_save, sender=TankOwner)
def tank_owner_pre_save(sender, instance, **kwargs):
    instance.mqtt_topic = instance.mqtt_topic.upper()


# @receiver(post_save, sender=NewsArticle)
# def news_save_handler(sender, **kwargs):
#     if settings.DEBUG:
#         print(f"{kwargs['instance']} saved.")


# @receiver(post_delete, sender=NewsArticle)
# def news_delete_handler(sender, **kwargs):
#     if settings.DEBUG:
#         print(f"{kwargs['instance']} deleted.")
