# -*- coding: utf-8 -*-
from django import http
from django.conf import settings
from django.contrib.sites.models import Site
from cms.utils.i18n import get_current_language
from .models import Redirection, GlobalRedirection, InvalidEndpoint
import json

RESERVED_KEYWORDS = [' ', '.js', '.css', '.php', '.jpg', '.png']
NOT_REDIRECT = ('/track/', '/admin/',)


class RedirectMiddleware(object):
    def process_request(self, request):
        # Ignore paths from media or static files
        if not request.path.startswith((settings.MEDIA_URL, settings.STATIC_URL)):
            # If the path has any of the reserved keywords, mark it as an invalid endpoint
            if [keyword for keyword in RESERVED_KEYWORDS if keyword in request.path]:
                InvalidEndpoint.objects.create(
                    ip=(request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0] if request.META.get('HTTP_X_FORWARDED_FOR') else request.META.get('REMOTE_ADDR')),
                    url=request.path,
                    request=json.dumps({
                        'method': request.META.get('REQUEST_METHOD', ''),
                        'port': request.META.get('SERVER_PORT', ''),
                        'protocol': request.META.get('SERVER_PROTOCOL', ''),
                        'host': request.META.get('HTTP_HOST', ''),
                        'remote_address': request.META.get('REMOTE_ADDR', ''),
                        'path': request.META.get('PATH_INFO', ''),
                        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                        'referrer': request.META.get('HTTP_REFERER', '')
                    })
                )
                return http.HttpResponseForbidden()
            if not request.path.startswith(NOT_REDIRECT):
                path = request.path.replace(' ', '')

                source = path.split('?', 1)[0] if '?' in path else path
                source += '/' if not source.endswith('/') else ''

                query_params = request.META['QUERY_STRING'] if 'QUERY_STRING' in request.META else None

                site_id = Site.objects.get_current().pk
                enabled = True

                # Test against global redirections first, then normal redirections
                try:
                    parts = [p for p in source.split('/') if p]
                    paths = []
                    text = '/' + parts[0] + '/'
                    paths.append(text)
                    for part in parts[1:]:
                        text += part + '/'
                        paths.append(text)

                    from django.db.models.functions import Length
                    redir = GlobalRedirection.objects.only('target_page', 'target_link', 'source', 'response_type', 'redirection_type') \
                        .filter(site_id=site_id, source__in=paths, enabled=enabled).order_by(Length('source').desc()).first()
                except:
                    redir = None

                lang = source[1:3]
                if lang not in [code[0] for code in list(settings.LANGUAGES)]:
                    lang = get_current_language()

                if redir is None:
                    try:
                        redir = Redirection.objects.only('target_page', 'target_link', 'source', 'response_type').get(site_id=site_id, source=source, enabled=enabled)
                    except:
                        pass

                if redir is not None and isinstance(redir, Redirection):
                    if redir.target_page:
                        target_link = redir.target_page.get_public_url(language=lang)
                    else:
                        target_link = redir.target_link
                        if not redir.target_link.startswith('/') and 'http' not in redir.target_link:
                            target_link = 'http://' + redir.target_link

                    if target_link != redir.source and target_link:
                        if isinstance(redir, GlobalRedirection) and redir.redirection_type == 'MP':
                            suffix = source.replace(redir.source, '')
                            target_link += ('/' if not target_link.endswith('/') else '') + suffix

                        if redir.query_params or query_params:
                            target_link += '?'

                        if redir.query_params:
                            target_link += redir.query_params

                        if query_params:
                            if not target_link.endswith('?'):
                                target_link += '&'
                            target_link += query_params

                        if redir.response_type == '302':
                            return http.HttpResponseRedirect(target_link)
                        else:
                            return http.HttpResponsePermanentRedirect(target_link)
