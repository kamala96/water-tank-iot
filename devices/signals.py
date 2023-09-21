import re
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from owners.mqtt_handler import mqtt_handler
# from django.conf import settings

from .models import Processor, Switch, WaterPump, WaterTankSensor, WaterValve


@receiver(pre_save, sender=Processor)
def processor_pre_save(sender, instance, **kwargs):
    # Remove non-alphanumeric characters, spaces,
    cleaned_mqtt_topic = re.sub(r'[^a-zA-Z0-9]', '', instance.mqtt_topic)
    instance.mqtt_topic = cleaned_mqtt_topic


@receiver(pre_save, sender=Switch)
def switch_pre_save(sender, instance, **kwargs):
    instance.mqtt_topic = re.sub(r'[^a-zA-Z0-9]', '', instance.mqtt_topic)


@receiver(pre_save, sender=WaterPump)
def pump_pre_save(sender, instance, **kwargs):
    instance.mqtt_topic = re.sub(r'[^a-zA-Z0-9]', '', instance.mqtt_topic)

    # Check if the 'auto_mode' field has been updated
    if kwargs.get('update_fields') and 'auto_mode' in kwargs['update_fields']:
        pass


@receiver(pre_save, sender=WaterTankSensor)
def tank_pre_save(sender, instance, **kwargs):
    instance.mqtt_topic = re.sub(r'[^a-zA-Z0-9]', '', instance.mqtt_topic)


@receiver(pre_save, sender=WaterValve)
def valve_pre_save(sender, instance, **kwargs):
    instance.mqtt_topic = re.sub(r'[^a-zA-Z0-9]', '', instance.mqtt_topic)
