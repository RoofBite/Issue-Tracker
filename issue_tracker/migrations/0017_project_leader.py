# Generated by Django 3.2.4 on 2021-08-12 13:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('issue_tracker', '0016_alter_issue_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='leader',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='leader_project_set', to=settings.AUTH_USER_MODEL),
        ),
    ]
