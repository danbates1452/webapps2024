# Generated by Django 5.0.2 on 2024-04-16 11:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payapp', '0002_rename_requests_request_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ('user', 'active')},
        ),
        migrations.AlterModelOptions(
            name='request',
            options={'ordering': ('by_person', 'status', 'amount')},
        ),
        migrations.AlterModelOptions(
            name='transaction',
            options={'ordering': ('submission_datetime', 'from_person', 'amount')},
        ),
        migrations.RemoveField(
            model_name='request',
            name='cancelled',
        ),
        migrations.RemoveField(
            model_name='request',
            name='completed',
        ),
        migrations.AddField(
            model_name='request',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')], default='PENDING', max_length=9),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='submission_datetime',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now),
        ),
    ]
