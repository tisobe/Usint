from django.contrib import admin
from schedule_submitter.models import Schedule


class ScheduleAdmin(admin.ModelAdmin):
    list_display  = ('contact', 'start', 'finish', 'start_month', 'start_day', 'start_year', \
                     'finish_month', 'finish_day', 'finish_year', 'assigned')
    search_fields = ('contact', 'start', 'finish','assigned')
    ordering      = ('-start',)

admin.site.register(Schedule, ScheduleAdmin)
