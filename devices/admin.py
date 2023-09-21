from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html

from devices.models import MQTTStatus, Processor, Switch, WaterPump, WaterTankSensor, WaterValve
from owners.mqtt_handler import mqtt_handler

# Register your models here.


@admin.register(MQTTStatus)
class MQTTStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'connected', 'started_at', 'updated_at']
    list_filter = ('connected',)
    search_fields = ('id', 'connected',)

    def has_add_permission(self, request):
        return False  # Disable the ability to add more than one MQTTStatus

    def has_delete_permission(self, request, obj=None):
        return False  # Disable the ability to delete MQTTStatus objects


class ProcessorSwitchesInline(admin.TabularInline):
    model = Switch
    show_change_link = True
    readonly_fields = ('id',)
    extra = 1
    classes = ('collapse', )


@admin.register(Processor)
class ProcessorAdmin(admin.ModelAdmin):
    list_display = ['device_id', 'owner', 'name', 'mqtt_topic',
                    'switch_count', 'pump_count', 'tank_sensor_count', 'valve_count',]
    list_filter = ("owner__name",)
    list_per_page = 10

    @admin.display(description="switch count")
    def switch_count(self, obj):
        return obj.switch_set.count()

    @admin.display(description="pump count")
    def pump_count(self, obj):
        return sum([switch.waterpump_set.count() for switch in obj.switch_set.all()])

    @admin.display(description="Water Tanks count")
    def tank_sensor_count(self, obj):
        return obj.watertanksensor_set.count()

    @admin.display(description="valve count")
    def valve_count(self, obj):
        return sum([1 if hasattr(tank, 'watervalve') else 0 for tank in obj.watertanksensor_set.all()])

    inlines = [ProcessorSwitchesInline]


class SwitchWaterPumpInline(admin.TabularInline):
    model = WaterPump
    show_change_link = True
    readonly_fields = ('id',)
    extra = 1
    classes = ('collapse', )


@admin.register(Switch)
class SwitchAdmin(admin.ModelAdmin):
    list_display = ['name', 'mqtt_topic', 'total_phases', 'processor']
    list_filter = ("processor__owner__name",)
    list_per_page = 10

    inlines = [SwitchWaterPumpInline]


class PumpWaterTankSensorInline(admin.TabularInline):
    model = WaterTankSensor
    show_change_link = True
    readonly_fields = ('id',)
    extra = 1
    classes = ('collapse', )


@admin.register(WaterPump)
class WaterPumpAdmin(admin.ModelAdmin):
    list_display = ['name', 'pin_number', 'mqtt_topic', 'status', 'switch']
    list_filter = ("switch__processor__owner__name",)
    list_per_page = 10

    inlines = [PumpWaterTankSensorInline]


class TankValveInline(admin.TabularInline):
    model = WaterValve
    show_change_link = True
    readonly_fields = ('id',)
    extra = 2


@admin.register(WaterTankSensor)
class WaterTankSensorAdmin(admin.ModelAdmin):
    list_display = ['name', 'sensor_pin_number', 'mqtt_topic', 'current_level',
                    'max_capacity', 'min_threshold', 'water_pump', 'processor',  'view_valve']
    list_filter = ("processor__owner__name", "max_capacity")
    list_per_page = 10

    def view_valve(self, obj):
        if hasattr(obj, 'watervalve'):
            url = reverse("admin:%s_%s_change" % (
                obj._meta.app_label,  'watervalve'),  args=[obj.watervalve.id])
            return format_html('<a href="{}">View Valve</a>', url)
        return "N/A"
        # Custom method to provide a link to view associated NodeMCUs
        # processor_count = obj.processor_set.count()
        # if processor_count > 0:
        #     url = reverse('admin:devices_watervalve_changelist') + \
        #         f'?owner__id__exact={obj.id}'
        #     return format_html('<a href="{}">{}</a>', url, 'VIEW (' + str(processor_count) + ')')
        # return processor_count

    view_valve.short_description = 'Valve'
    view_valve.allow_tags = True

    inlines = [TankValveInline]


@admin.register(WaterValve)
class WaterValveAdmin(admin.ModelAdmin):
    list_display = ['water_tank', 'name', 'pin_number', 'mqtt_topic', 'status']
    list_filter = ("water_tank__processor__owner__name",)
    list_per_page = 10
