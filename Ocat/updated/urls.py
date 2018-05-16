from django.conf.urls       import  *

from updated.views          import upDated

from ocatsite               import settings

urlpatterns = patterns('',
    
    url(r'^$', upDated.as_view(),name='updated'),
    #url(r'^updated/$', upDated.as_view(),name='updated'),
)
