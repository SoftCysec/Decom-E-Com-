# Generated by Django 3.1.7 on 2021-08-22 08:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_item_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='s_active',
            new_name='is_active',
        ),
    ]
