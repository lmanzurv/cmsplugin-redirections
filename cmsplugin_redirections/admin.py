# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import Redirection, GlobalRedirection, InvalidEndpoint

class RedirectionAdmin(admin.ModelAdmin):
    list_display = ('source', 'target_page', 'target_link', 'site_name', 'enabled')
    list_filter = ('site__name', 'enabled')
    fields = ('site', 'source', 'target_page', 'target_link', 'query_params', 'response_type', 'enabled')
    ordering = ('source',)

    def site_name(self, obj):
        return obj.site.name

    def get_queryset(self, request):
        qs = super(RedirectionAdmin, self).get_queryset(request)
        return qs.filter(globalredirection__isnull=True)

class GlobalRedirectionAdmin(admin.ModelAdmin):
    list_display = ('source', 'target_page', 'target_link', 'site_name', 'redirection_type', 'enabled')
    list_filter = ('site__name', 'redirection_type', 'enabled')
    fields = ('site', 'source', 'target_page', 'target_link', 'query_params', 'response_type', 'redirection_type', 'enabled')
    ordering = ('source',)

    def site_name(self, obj):
        return obj.site.name

class InvalidEndpointAdmin(admin.ModelAdmin):
    list_display = ('ip', 'url', 'timestamp')
    list_filter = ('ip', 'url')
    readonly_fields = ('ip', 'url', 'request', 'timestamp')
    ordering = ('-timestamp',)

admin.site.register(Redirection, RedirectionAdmin)
admin.site.register(GlobalRedirection, GlobalRedirectionAdmin)
admin.site.register(InvalidEndpoint, InvalidEndpointAdmin)
