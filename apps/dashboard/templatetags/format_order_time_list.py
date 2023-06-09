from django import template

from utils import util

register = template.Library()

@register.filter
def format_order_time_list(time_list):
    return util.trans_list_str_to_list(time_list)
