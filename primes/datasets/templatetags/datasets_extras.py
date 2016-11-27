from django import template

# see more: https://docs.djangoproject.com/en/1.10/howto/custom-template-tags/#inclusion-tags
register = template.Library()


## Custom filters ##

## Custom inclusion tags ##

@register.inclusion_tag('datasets/pagination.html')
def show_pagination(items):
    """
    {% show_pagination items %}
    :param items: QuerySet object
    :return:
    """
    return {'items': items}
