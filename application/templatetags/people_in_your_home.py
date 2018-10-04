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
def len_func(value):
    return len(value)

@register.filter(name='in')
def in_list(value, arg):
    arg = arg.split(',')
    return value in arg
