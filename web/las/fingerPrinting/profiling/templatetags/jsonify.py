from django import template
import json

register = template.Library()

@register.filter
def jsonify(value):
    try:
        return json.dumps(value)
    except:
        return ""
