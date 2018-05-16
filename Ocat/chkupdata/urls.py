from django.conf.urls       import  *

from chkupdata.views        import chkUpData

from ocatsite               import settings

urlpatterns = patterns('',
    
    url(r'^(\d+.\d+)/$', chkUpData.as_view(),name='chkupdata'),
    url(r'^\d+.\d+/',    chkUpData.as_view(),name='chkupdata'),

    #url(r'^chkupdata/(\d+.\d+)/$', chkUpData.as_view(),name='chkupdata'),
    #url(r'^chkupdata/\d+.\d+/',    chkUpData.as_view(),name='chkupdata'),
)
