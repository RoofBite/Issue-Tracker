# Generated by Django 3.2.4 on 2021-08-22 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issue_tracker', '0029_auto_20210822_1326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='comment',
            field=models.ManyToManyField(blank=True, to='issue_tracker.Comment'),
        ),
    ]