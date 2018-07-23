import inflect
from django import template

register = template.Library()


@register.filter(name='inflect')
def number_to_spatial_ordinal(value):
    """
    Template tag to convert a number to it's equivalent spational ordinal
    For example: 2 -> Second
    :param value:
    :return:
    """
    engine = inflect.engine()

    abbreviated = engine.ordinal(value)
    ordinal = engine.number_to_words(abbreviated)

    return ordinal
