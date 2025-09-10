from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Template filter to lookup dictionary values."""
    return dictionary.get(key, '')

@register.filter 
def title_case(value):
    """Convert value to title case."""
    return value.replace('_', ' ').title() if value else ''