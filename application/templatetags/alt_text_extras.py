import inflect
from django import template
from pydoc import locate

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

@register.filter(name='isinstance')
def is_instance_template_tag(value, arg):
    """
    :param value: obj to check type of
    :param arg: type to check against in string form.
    :return: Boolean True if value's type is arg, else False.
    """
    return isinstance(value, locate(arg))