# Generated by Django 4.2.5 on 2023-09-16 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0009_alter_watertanksensor_mqtt_topic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='processor',
            name='mqtt_topic',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]