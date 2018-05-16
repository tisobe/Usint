from django.conf.urls       import  *

from ocat_express.views    import ocatExpress   

from ocatsite               import settings

urlpatterns = patterns('',
    
    #url(r'^ocat_express/$', ocatExpress.as_view(),name='ocat_express'),
    url(r'^$', ocatExpress.as_view(),name='ocat_express'),
)
