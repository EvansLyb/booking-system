# Generated by Django 3.2.16 on 2023-06-09 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('open_id', models.CharField(max_length=256, verbose_name='open_id')),
                ('phone_number', models.CharField(default='', max_length=32, verbose_name='phone_number')),
            ],
        ),
    ]
