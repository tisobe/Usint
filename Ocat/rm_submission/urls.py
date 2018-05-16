from django.conf.urls       import  *

from rm_submission.views    import rmSubmission

from ocatsite               import settings

urlpatterns = patterns('',
    
    url(r'^$', rmSubmission.as_view(),name='rm_submission'),
)
