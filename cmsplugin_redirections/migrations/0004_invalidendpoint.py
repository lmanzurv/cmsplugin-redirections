# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-06-06 09:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_redirections', '0003_redirection_query_params'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvalidEndpoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(db_index=True, editable=False, max_length=255, verbose_name='IP Address')),
                ('url', models.TextField(db_index=True, editable=False, verbose_name='Requested URL')),
                ('request', models.TextField(editable=False, verbose_name='Request Info')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Invalid Endpoint',
                'verbose_name_plural': 'Invalid Endpoints',
            },
        ),
    ]