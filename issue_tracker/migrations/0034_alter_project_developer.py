# Generated by Django 3.2.4 on 2021-08-23 13:23

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('issue_tracker', '0033_auto_20210822_1358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='developer',
            field=models.ManyToManyField(blank=True, null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
