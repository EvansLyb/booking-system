# -*- encoding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Account(AbstractUser):
    is_super_admin = models.BooleanField(
      _('staff status'),
      default=False,
    )
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True)
