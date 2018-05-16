from django.conf.urls   import  *

from ocatmain.views     import ocatMain 

from ocatsite           import settings

urlpatterns = patterns('',

    url(r'^$', ocatMain.as_view(),  name='ocatmain'),


)
