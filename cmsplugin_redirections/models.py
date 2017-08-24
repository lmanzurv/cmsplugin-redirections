# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from cms.cache import invalidate_cms_page_cache, _get_cache_version
from cms.models.fields import PageField
from cms.utils import get_cms_setting

class Redirection(models.Model):
    RESPONSE_CODES = (
        ('301', 'Permanent'),
        ('302', 'Temporary'),
    )

    site = models.ForeignKey(Site, on_delete=models.CASCADE, db_index=True, related_name='site_redirections')
    source = models.CharField(verbose_name=_('Source URL'), max_length=255, db_index=True, help_text=_('The source should be a relative path of the form e.g. /en/source-path/'))
    target_link = models.CharField(verbose_name=_('Target URL'), max_length=255, null=True, blank=True, help_text=_('The target link should be an external URL'))
    target_page = PageField(verbose_name=_('Target Page'), blank=True, null=True, help_text=_('A link to a page has priority over a text link'))
    query_params = models.CharField(verbose_name=_('Query Parameters'), max_length=255, null=True, blank=True, help_text=_('Please URL-encode the params as param1=value1&amp;param2=value2. Don\'t include the ?'))
    response_type = models.CharField(verbose_name=_('Response Code'), max_length=3, default='301', choices=RESPONSE_CODES)
    enabled = models.BooleanField(verbose_name=_('Enabled'), default=True)

    class Meta:
        verbose_name = _('URL Redirect')
        verbose_name_plural = _('URL Redirects')
        unique_together = ('site', 'source')
        ordering = ('source',)

    def clean(self, *args, **kwargs):
        if not self.source.startswith('/'):
            raise ValidationError('The source should start with /')
        if not self.source.endswith('/'):
            raise ValidationError('The source should end with /')
        if not self.target_link and not self.target_page:
            raise ValidationError('You must specify at least one of the target options: page or URL')
        if self.target_link and self.target_page:
            raise ValidationError('You can specify either target URL or page, not both')

        super(Redirection, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(Redirection, self).save(*args, **kwargs)
        invalidate_cms_page_cache()
        cache.set('redir:%s:%s:%s' % (self.site_id, self.source, self.enabled), self, get_cms_setting('CACHE_DURATIONS')['menus'], version=_get_cache_version())

    def delete(self, *args, **kwargs):
        super(Redirection, self).delete(*args, **kwargs)
        invalidate_cms_page_cache()

    def __unicode__(self):
        return '%s - %s' % (self.response_type, self.source)

class GlobalRedirection(Redirection):
    REDIRECTION_TYPES = (
        ('MP', 'Maintain path'),
        ('DP', 'Drop path'),
    )

    redirection_type = models.CharField(verbose_name=_('Redirection Type'), max_length=2, default='MP', choices=REDIRECTION_TYPES)

    class Meta:
        verbose_name = _('Global Redirect')
        verbose_name_plural = _('Global Redirects')

    def save(self, *args, **kwargs):
        super(GlobalRedirection, self).save(*args, **kwargs)
        invalidate_cms_page_cache()
        cache.set('redir:gl:%s:%s:%s' % (self.site_id, self.source, self.enabled), self, get_cms_setting('CACHE_DURATIONS')['menus'], version=_get_cache_version())

    def __unicode__(self):
        return '%s - %s - %s' % (self.response_type, self.redirection_type, self.source)

class InvalidEndpoint(models.Model):
    ip = models.CharField(verbose_name=_('IP Address'), max_length=255, db_index=True, editable=False)
    url = models.TextField(verbose_name=_('Requested URL'), db_index=True, editable=False)
    request = models.TextField(verbose_name=_('Request Info'), editable=False)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name = _('Invalid Endpoint')
        verbose_name_plural = _('Invalid Endpoints')

    def __unicode__(self):
        return '%s [%s]' % (self.url, self.ip)
