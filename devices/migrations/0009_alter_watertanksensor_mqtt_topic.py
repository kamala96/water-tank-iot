# Generated by Django 4.2.5 on 2023-09-16 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0008_remove_processor_manual_mode_waterpump_auto_mode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watertanksensor',
            name='mqtt_topic',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
