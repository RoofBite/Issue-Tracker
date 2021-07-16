# Generated by Django 3.2.4 on 2021-07-16 17:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('issue_tracker', '0007_auto_20210716_1942'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='issue',
            name='tags',
        ),
        migrations.AddField(
            model_name='issue',
            name='tags',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='issue_tracker.issuetag'),
        ),
    ]
