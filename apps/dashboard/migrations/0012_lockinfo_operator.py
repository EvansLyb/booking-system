# Generated by Django 3.2.16 on 2023-06-06 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_auto_20230605_0559'),
    ]

    operations = [
        migrations.AddField(
            model_name='lockinfo',
            name='operator',
            field=models.CharField(blank=True, max_length=255, verbose_name='operator'),
        ),
    ]