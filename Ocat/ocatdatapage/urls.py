from django.conf.urls       import  *

from ocatdatapage.views     import OcatDataPage

from ocatsite               import settings



urlpatterns = patterns('',
    
    url(r'^(\d+)/$', OcatDataPage.as_view(), name='ocatdatapage'),
    url(r'^\d+/',    OcatDataPage.as_view(), name='ocatdatapage'),
    url(r'^finalized/\d+/',       OcatDataPage.as_view(), name='finalized'),

    #url(r'^ocatdatapage/(\d+)/$', OcatDataPage.as_view(), name='ocatdatapage'),
    #url(r'^ocatdatapage/\d+/',    OcatDataPage.as_view(), name='ocatdatapage'),
    #url(r'^finalized/\d+/',       OcatDataPage.as_view(), name='finalized'),

)
