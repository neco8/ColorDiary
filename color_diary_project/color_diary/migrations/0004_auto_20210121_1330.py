# Generated by Django 3.1.4 on 2021-01-21 04:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('color_diary', '0003_auto_20210118_2256'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='color',
            options={'ordering': ['hex_color', 'id']},
        ),
    ]