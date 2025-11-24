from django import template
from django.apps import apps
from django.utils.html import format_html

register = template.Library()

@register.simple_block_tag(takes_context=True, name="requireapp", end_name="endrequireapp")
def require_app(context, content, app):
    if apps.is_installed(app):
        return format_html(content, context=context)

@register.simple_tag(name="lazyurl")
def lazy_url(url):
    
    return None
