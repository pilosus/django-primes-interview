import re
from django import template
from django.conf import settings

# see more: https://docs.djangoproject.com/en/1.10/howto/custom-template-tags/#inclusion-tags
register = template.Library()


## Custom filters ##

@register.simple_tag
def settings_value(setting_name):
    """Return value for a given setting variable.

    {% settings_value "LANGUAGE_CODE" %}
    """
    return getattr(settings, setting_name, "")


@register.filter(name='replace_flower_port')
def replace_flower_port(value):
    """Replace Flower port number in the value with arg.

    Assume: flower port's setting is settings.FLOWER_PORT
    """
    appendix = ':{0}/'.format(settings.FLOWER_PORT)

    if re.search(r'\:\d+\/?$', value):
        return re.sub(r'\:(\d+)\/?', appendix, value)
    else:
        return re.sub(r'\/?$', appendix, value)

## Custom inclusion tags ##

@register.inclusion_tag('datasets/pagination.html')
def show_pagination(items):
    """
    {% show_pagination items %}
    :param items: QuerySet object
    :return:
    """
    return {'items': items}
