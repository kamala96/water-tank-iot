from django.db import models

from owners.models import TankOwner

# Create your models here.


class Processor(models.Model):
    owner = models.ForeignKey(TankOwner, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    mqtt_topic = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f'{self.owner.mqtt_topic}/{self.mqtt_topic}'


class Switch(models.Model):
    processor = models.ForeignKey(Processor, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mqtt_topic = models.CharField(max_length=100, unique=True)
    total_phases = models.IntegerField()

    def __str__(self):
        return f'{self.processor}/{self.name}'

    class Meta:
        verbose_name_plural = "Switches"


class WaterPump(models.Model):
    switch = models.ForeignKey(Switch, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    pin_number = models.CharField(max_length=100)
    mqtt_topic = models.CharField(max_length=100, unique=True)
    status = models.BooleanField(default=False)  # Status of the motor

    def __str__(self):
        return f'{self.name}: {self.switch}/{self.mqtt_topic}'

    def set_status(self, new_status):
        """
        Method to set the status of the WaterPump.

        Args:
            new_status (bool): The new status value (True for on, False for off).
        """
        self.status = new_status
        self.save()

    class Meta:
        verbose_name = "Water Pump"


class WaterTankSensor(models.Model):
    processor = models.ForeignKey(Processor, on_delete=models.CASCADE)
    water_pump = models.ForeignKey(WaterPump, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    max_capacity = models.FloatField()
    min_threshold = models.FloatField()
    current_level = models.FloatField()
    sensor_pin_number = models.CharField(max_length=100)
    mqtt_topic = models.CharField(max_length=100, unique=True)

    def set_current_level(self, new_level):
        """
        Set the current water level of the sensor and save it to the database.

        Args:
            new_level (float): The new current water level to set.
        """
        # Check if the new level does not exceed max_capacity
        if new_level <= self.max_capacity:
            self.current_level = new_level
            self.save()

    def get_full_topic(self):
        return f'{self.processor.owner.mqtt_topic}/{self.processor.mqtt_topic}/{self.water_pump.switch.mqtt_topic}/{self.water_pump.mqtt_topic}/PumpStatus'

    def calculate_percentage(self):
        if self.max_capacity == 0:
            return 0  # To avoid division by zero
        percentage = (self.max_capacity - self.current_level) / \
            (self.max_capacity) * 100
        return round(percentage, 2)

    def get_pump_status(self):
        if self.water_pump.status:
            return 'On'
        else:
            return 'Off'

    def get_pump_mode(self):
        if self.water_pump.auto_mode:
            return 'Auto'
        else:
            return 'Manual'

    def get_pump_topic(self):
        return self.water_pump.mqtt_topic

    def __str__(self):
        return f'{self.name} [Max: {self.max_capacity}] [Onwer: {self.processor}]'

    class Meta:
        verbose_name = "Water Tanks Sensor"


class WaterValve(models.Model):
    water_tank = models.OneToOneField(
        WaterTankSensor, on_delete=models.CASCADE, related_name='watervalve')
    name = models.CharField(max_length=100)
    pin_number = models.CharField(max_length=100)
    mqtt_topic = models.CharField(max_length=100, unique=True)
    status = models.BooleanField(default=False)  # Status of the solenoid valve

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Water Tanks Solenoid Valve"


class MQTTStatus(models.Model):
    connected = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_connected(self, value):
        self.connected = value
        self.save()

    @classmethod
    def get_status(cls):
        # Ensure there is only one MQTTStatus object in the database
        obj, created = cls.objects.get_or_create(pk=1)
        return obj.connected

    class Meta:
        verbose_name = "_MQTTStatus"
        verbose_name_plural = "_MQTTStatus"
