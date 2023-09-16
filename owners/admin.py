from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from devices.models import Processor

from owners.models import TankOwner

# Register your models here.


class TankOwnerProcessorInline(admin.TabularInline):
    model = Processor
    show_change_link = True
    readonly_fields = ('id',)
    extra = 1  # Set the number of empty forms to display to 0
    classes = ('collapse', )


@admin.register(TankOwner)
class TankOwnerAdmin(admin.ModelAdmin):
    list_display = ["name", "mqtt_topic", "email", "phone", "view_processors"]
    list_per_page = 10
    
    def view_processors(self, obj):
        # Custom method to provide a link to view associated NodeMCUs
        processor_count = obj.processor_set.count()
        if processor_count > 0:
            url = reverse('admin:devices_processor_changelist') + \
                f'?owner__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, 'VIEW (' + str(processor_count) + ')')
        return processor_count

    view_processors.short_description = 'Processors'
    view_processors.allow_tags = True  # Allow HTML in the column

    inlines = [TankOwnerProcessorInline]
