# Generated by Django 4.2.5 on 2023-09-10 09:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0003_alter_watervalve_water_tank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watervalve',
            name='water_tank',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='watervalve', to='devices.watertanksensor'),
        ),
    ]