# Generated by Django 3.2.4 on 2021-07-17 14:19

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("issue_tracker", "0012_auto_20210717_1608"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="project",
            name="member",
        ),
        migrations.AddField(
            model_name="project",
            name="member",
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
