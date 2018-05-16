from django.conf.urls         import  *

from schedule_submitter.views import scheduleSubmitter

from ocatsite                 import settings

urlpatterns = patterns('',
    
    url(r'^$', scheduleSubmitter.as_view(),name='schedule_submitter'),
    #url(r'^schedule_submitter/$', scheduleSubmitter.as_view(),name='schedule_submitter'),
)
