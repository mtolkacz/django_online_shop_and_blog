import math

from django import template
from django.conf import settings

register = template.Library()


@register.filter()
def page_numbers(count):
    return math.ceil(count/settings.REST_FRAMEWORK['PAGE_SIZE'])


@register.filter()
def temp_range(n):
    return range(n)


@register.simple_tag(takes_context=True)
def replace_get_parameter(context, field, value):
    dict_ = context['request'].GET.copy()
    dict_[field] = value
    return '?{}'.format(dict_.urlencode())


@register.simple_tag(takes_context=True)
def delete_get_parameter(context, field):
    dict_ = context['request'].GET.copy()
    if len(dict_) == 1:
        return str(context['request'].path)
    try:
        del dict_[field]
    except KeyError:
        pass

    return '?{}'.format(dict_.urlencode())


@register.simple_tag()
def active_request_get(request):
    dict = request.GET.copy()
    if 'ordering' in dict:
        del dict['ordering']
    if 'page' in dict:
        del dict['page']
    return len(dict) if len(dict) else False
