# Generated by Django 3.2.4 on 2021-08-14 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issue_tracker', '0021_alter_issue_update_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='update_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
