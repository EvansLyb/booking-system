# Generated by Django 3.2.16 on 2023-06-01 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_freeze_lockinfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='freeze',
            name='court_type',
            field=models.CharField(choices=[('FULL', 'Full'), ('HALF', 'Half'), ('QUARTER', 'Quarter')], default=None, max_length=255),
        ),
    ]
