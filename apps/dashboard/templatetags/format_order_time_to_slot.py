
from django import template

from utils import util

register = template.Library()

@register.filter
def format_order_time_to_slot(time_str):
    return util.trans_time_to_slot(time_str)
