# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-02-24 12:38
from __future__ import unicode_literals

import cms.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='Redirection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(db_index=True, help_text='The source should be a relative path of the form e.g. /en/source-path/', max_length=255, verbose_name='Source URL')),
                ('target_link', models.CharField(blank=True, help_text='The target link should be a relative path of the form e.g. /en/target-path/', max_length=255, null=True, verbose_name='Target URL')),
                ('response_type', models.CharField(choices=[('301', 'Permanent'), ('302', 'Temporary')], default='301', max_length=3, verbose_name='Response Code')),
                ('enabled', models.BooleanField(default=True, verbose_name='Enabled')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='site_redirections', to='sites.Site')),
                ('target_page', cms.models.fields.PageField(blank=True, help_text='A link to a page has priority over a text link', null=True, on_delete=django.db.models.deletion.CASCADE, to='cms.Page', verbose_name='Target Page')),
            ],
            options={
                'ordering': ('source',),
                'verbose_name': 'URL Redirect',
                'verbose_name_plural': 'URL Redirects',
            },
        ),
        migrations.AlterUniqueTogether(
            name='redirection',
            unique_together=set([('site', 'source')]),
        ),
    ]