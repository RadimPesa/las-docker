from django import template
import json

register = template.Library()

@register.filter
def getattr(obj, key):
    try:
        if not isinstance(obj, dict):
            obj = json.loads(obj)
        return obj[key]
    except:
        return ""
