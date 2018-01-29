from django import template

register = template.Library()

@register.filter
def replace(text, replStr):
    try:
        a, b = replStr.split(",", 1)
        return text.replace(a, b)
    except:
        return text
