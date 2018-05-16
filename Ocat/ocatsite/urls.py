from django.conf.urls                   import patterns, include, url
from django.contrib                     import admin
from ocatsite                           import settings
from django.contrib.auth.views          import login, logout, password_change, password_change_done

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/',        include(admin.site.urls)),
    url(r'^utils/',        include('utils.urls',        namespace='utils')),
    url(r'^ocatmain/',     include('ocatmain.urls',     namespace='ocatmain')),
    url(r'^ocatdatapage/', include('ocatdatapage.urls', namespace='ocatdatapage')),
    url(r'^chkupdata/',    include('chkupdata.urls',    namespace='chkupdata')),
    url(r'^orupdate/',     include('orupdate.urls',     namespace='orupdate')),
    url(r'^updated/',      include('updated.urls',      namespace='updated')),
    url(r'^ocat_express/', include('ocat_express.urls', namespace='ocat_express')),
    url(r'^rm_submission/',         include('rm_submission.urls',     namespace='rm_submission')),
    url(r'^schedule_submitter/',    include('schedule_submitter.urls',namespace='schedule_submitter')),
    url(r'^accounts/login/$',       login),
    url(r'^accounts/logout/$',      logout),
    url(r'^registration/login/$',   login),
)
