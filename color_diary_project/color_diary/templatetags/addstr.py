from django import template


register = template.Library()


def addstr(value, arg):
    return str(value) + str(arg)


register.filter('addstr', addstr)
