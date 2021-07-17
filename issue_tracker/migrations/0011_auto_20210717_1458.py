# Generated by Django 3.2.4 on 2021-07-17 12:58

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('issue_tracker', '0010_alter_issue_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='members',
        ),
        migrations.AddField(
            model_name='project',
            name='member',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='issue',
            name='title',
            field=models.CharField(max_length=80),
        ),
    ]
