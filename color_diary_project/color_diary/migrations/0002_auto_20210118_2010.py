# Generated by Django 3.1.4 on 2021-01-18 11:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('color_diary', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='color',
            old_name='user',
            new_name='users',
        ),
    ]