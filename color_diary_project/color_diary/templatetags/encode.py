from django import template

from ..utils import get_hashids


register = template.Library()


def encode(value):
    return get_hashids().encode(value)


register.filter('encode', encode)