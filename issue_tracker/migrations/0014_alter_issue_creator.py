# Generated by Django 3.2.4 on 2021-07-19 10:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("issue_tracker", "0013_auto_20210717_1619"),
    ]

    operations = [
        migrations.AlterField(
            model_name="issue",
            name="creator",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="creator_issue_set",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
