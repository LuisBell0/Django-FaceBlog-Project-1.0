import datetime
from django import template
from django.utils import timezone

register = template.Library()


@register.filter(name='add_class')
def add_class(value, css_class):
    return value.as_widget(attrs={'class': css_class})


@register.filter
def time_filter(value):
    now = timezone.now()
    diff = now - value

    if diff < datetime.timedelta(minutes=1):
        return "just now"
    elif diff < datetime.timedelta(hours=1):
        return f"{int(diff.total_seconds() / 60)}m"
    elif diff < datetime.timedelta(days=1):
        return f"{int(diff.total_seconds() / 3600)}h"
    elif diff < datetime.timedelta(days=7):
        return f"{diff.days}d"
    elif diff < datetime.timedelta(days=365):
        weeks = diff.days // 7
        return f"{weeks}w" if weeks > 1 else "1w"
    else:
        years = diff.days // 365
        return f"{years}y" if years > 1 else "1y"
