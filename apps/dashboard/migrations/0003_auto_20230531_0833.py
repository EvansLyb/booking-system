# Generated by Django 3.2.16 on 2023-05-31 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_auto_20230530_1012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='price',
            name='full_day_price',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='price',
            name='high_time_price',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='price',
            name='low_time_price',
            field=models.FloatField(),
        ),
    ]
