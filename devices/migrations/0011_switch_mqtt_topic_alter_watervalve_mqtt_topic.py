# Generated by Django 4.2.5 on 2023-09-17 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0010_alter_processor_mqtt_topic'),
    ]

    operations = [
        migrations.AddField(
            model_name='switch',
            name='mqtt_topic',
            field=models.CharField(default='NOOOOO', max_length=100, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='watervalve',
            name='mqtt_topic',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]