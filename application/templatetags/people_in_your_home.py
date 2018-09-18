from django import template

register = template.Library()

@register.filter(name='subtract')
def subtract(value, arg):
    return value - int(arg)

@register.filter(name='list_index')
def list_index(value, arg):
    index = int(arg)
    return value[index]

@register.filter(name='len')
def list_index(value):
    return len(value)
