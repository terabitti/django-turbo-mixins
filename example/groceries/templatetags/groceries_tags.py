from django import template
from ..models import Category

register = template.Library()


@register.simple_tag
def is_category_limit_exceeded():
    return Category.is_category_limit_exceeded()


@register.simple_tag
def max_categories():
    return Category.max_categories
