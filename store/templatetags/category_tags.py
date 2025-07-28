from django import template
from store.models import Category

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return ''

@register.simple_tag
def get_categories():
    """Return all top-level categories"""
    return Category.objects.filter(parent__isnull=True).order_by('order', 'title')

@register.simple_tag
def get_subcategories(category):
    """Return all subcategories of a category"""
    return category.subcategories.all().order_by('order', 'title')

@register.simple_tag
def get_featured_categories():
    """Return all featured categories"""
    return Category.objects.filter(is_featured=True).order_by('order', 'title')

@register.inclusion_tag('partials/category_menu.html')
def category_menu():
    """Render the category menu"""
    categories = Category.objects.filter(parent__isnull=True).order_by('order', 'title')
    return {'categories': categories}