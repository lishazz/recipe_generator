# Generated by Django 5.1.7 on 2025-03-26 04:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0006_user_is_chef_approved'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_chef_approved',
        ),
    ]
