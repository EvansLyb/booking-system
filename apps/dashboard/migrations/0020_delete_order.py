# Generated by Django 3.2.16 on 2023-06-21 09:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0019_alter_price_full_day_price'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Order',
        ),
    ]