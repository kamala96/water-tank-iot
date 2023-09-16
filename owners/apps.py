from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OwnersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'owners'
    verbose_name = _(f"Institutions")

    def ready(self):
        from . import signals
        from django.db.models import Exists, OuterRef
        from .models import TankOwner
        from devices.models import Processor
        from .mqtt_handler import mqtt_handler

        try:
            # TankOwner objects with an associated Processor entry
            tank_owners_and_processor_entry = TankOwner.objects.annotate(
                has_processor=Exists(
                    Processor.objects.filter(owner=OuterRef('pk'))
                )
            )

            # Owners who have at least one processor entry
            tank_owners_with_processor = tank_owners_and_processor_entry.filter(
                has_processor=True)

            # Subscribe to High level MQTT for each owner
            for tank_owner in tank_owners_with_processor:
                topic = f'{str(tank_owner.mqtt_topic)}/#'
                mqtt_handler.subscribe_topic(topic)

        except Exception as e:
            pass
