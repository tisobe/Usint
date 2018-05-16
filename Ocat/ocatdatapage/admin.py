from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from django.contrib.auth.models import User
from models import UserProfile

from ocatdatapage.models import Approved, Updates, Data_tables, Obs_plan


class ApprovedAdmin(admin.ModelAdmin):
    list_display  = ('obsid', 'seqno', 'poc', 'date') 
    search_fields = ('obsid', 'seqno', 'poc', 'date')
    ordering      = ('-odate',)

class UpdatesAdmin(admin.ModelAdmin):
    list_display  = ('obsidrev','general', 'acis', 'si_mode', 'verified', 'seqno', 'poc', 'date') 
    search_fields = ('obsidrev','obsid', 'seqno', 'date')
    ordering      = ('-odate',)


class Data_tablesAdmin(admin.ModelAdmin):
    #list_display  = ('obsidrev','seq_nbr', 'prop_num', 'title', 'poc', 'date')
    list_display  = ('obsidrev','seq_nbr','prop_num', 'title', 'poc', 'date')
    search_fields = ('obsidrev','obsid', 'seq_nbr', 'prop_num', 'poc', 'date')
    ordering      = ('-odate',)


class Obs_planAdmin(admin.ModelAdmin):
    list_display  = ('obsid', 'seqno', 'otype', 'status', 'poc', 'ao', 'date')
    search_fields = ('obsid', 'seqno', 'otype', 'status', 'poc', 'ao', 'date')
    ordering      = ('-odate',)


admin.site.register(Approved,     ApprovedAdmin)
admin.site.register(Updates,      UpdatesAdmin)
admin.site.register(Obs_plan,     Obs_planAdmin)
admin.site.register(Data_tables,  Data_tablesAdmin)

#
#--- adding new fields to admin user
#
class ProfileInline(admin.StackedInline):
    model = UserProfile
    fk_name = 'user'
    max_num = 1


class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline,]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

