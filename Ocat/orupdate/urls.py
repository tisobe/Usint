from django.conf.urls       import  *

from orupdate.views         import orUpdate

from ocatsite               import settings

urlpatterns = patterns('',
    
    url(r'^$', orUpdate.as_view(),  name='orupdate'),
)
