from django import template

from utils import util

register = template.Library()

@register.filter
def index(indexable, i):
    return indexable[i]


@register.filter
def get_order_time_by_index(time_list, index):
    return util.format_order_time_list(time_list)[index]
