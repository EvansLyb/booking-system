# Generated by Django 3.2.16 on 2023-06-05 05:27

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_auto_20230605_0510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facility',
            name='description',
            field=ckeditor_uploader.fields.RichTextUploadingField(default='', verbose_name='description'),
        ),
    ]
