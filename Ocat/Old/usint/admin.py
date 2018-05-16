from django.contrib             import admin
from django.contrib.auth.admin  import UserAdmin
from django.contrib.auth.models import User

from usint.models               import Usint

#
#--- Define an inline admin descriptor for Employee model
#--- which acts a bit like a singleton
#

class UsintInline(admin.StackedInline):
    model               = Usint
    can_delete          = False
    verbose_name_plural = 'status'
#
#--- Define a new User admin
#
class UserAdmin(UserAdmin):
    inlines = (UsintInline, )
#
#--- Re-register UserAdmin
#
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

