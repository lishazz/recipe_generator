# Generated by Django 5.1.7 on 2025-03-26 02:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0005_alter_rating_unique_together_rating_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_chef_approved',
            field=models.BooleanField(default=False),
        ),
    ]
