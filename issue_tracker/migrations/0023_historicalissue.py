# Generated by Django 3.2.4 on 2021-08-14 15:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('issue_tracker', '0022_alter_issue_update_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalIssue',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('title', models.CharField(max_length=80)),
                ('priority', models.CharField(choices=[('NONE', 'None'), ('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')], default='NONE', max_length=20)),
                ('status', models.CharField(choices=[('NEW', 'New'), ('OPEN', 'Open'), ('IN_PROGRESS', 'In progress'), ('RESOLVED', 'Resolved'), ('CLOSED', 'Closed'), ('MORE_INFO', 'More info needed')], default='NEW', max_length=20)),
                ('type', models.CharField(choices=[('BUG', 'Bug/Error'), ('FEATURE', 'Feature'), ('COMMENT', 'Comment')], default='BUG', max_length=20)),
                ('description', models.CharField(max_length=250, null=True)),
                ('create_date', models.DateTimeField(blank=True, editable=False)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('creator', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='issue_tracker.project')),
                ('user_assigned', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical issue',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
