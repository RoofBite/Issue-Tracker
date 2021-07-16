# Generated by Django 3.2.4 on 2021-07-16 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issue_tracker', '0008_auto_20210716_1944'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='issue',
            name='tags',
        ),
        migrations.AddField(
            model_name='issue',
            name='tags',
            field=models.ManyToManyField(blank=True, null=True, to='issue_tracker.IssueTag'),
        ),
    ]
