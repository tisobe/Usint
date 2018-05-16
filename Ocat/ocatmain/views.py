#########################################################################################################
#                                                                                                       #
#           ocatMain:   django class to create Ocat Main Page                                           #
#                                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                       #
#               Last update: Jan 18, 2017                                                               #
#                                                                                                       #
#########################################################################################################

import re
import sys
import os
import random
import unittest
import math

from django.views.generic       import View
from django.http                import HttpRequest, HttpResponseRedirect
from django.template            import RequestContext

from django.shortcuts           import render_to_response, get_object_or_404
from django.contrib             import auth
from django.conf                import settings
from django.contrib.auth.models import User
from django.db                  import connection, models
from django.core.urlresolvers   import resolve

import utils.ocatCommonFunctions as ocf         #--- various functions are saved here
import utils.prepdatdict         as pdd         #--- create data dictionary for the page
import utils.passWordCheck       as pwchk       #--- check user/password
import utils.ocatdatabase_access as oda         #--- accessing tools to ocat data page database
import utils.convertTimeFormat   as tcnv        #--- collections of time related conversion fuction
import utils.create_log_and_email as cle        #--- create a change log and send out eamil
import utils.related_obs_list    as rol         #--- find other observations under the same poc
#
#--- reading directory list
#
from os.path import join, dirname, realpath
BASE_DIR = dirname(dirname(realpath(__file__)))
path     = join(BASE_DIR, 'ocatsite/static/dir_list_py')

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split('::', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append path to a private folders
#
sys.path.append(base_dir)
sys.path.append(mta_dir)
#
#--- there are many form of 'NONE'
#
non_list = (None, 'NONE', 'None', 'No', 'NO', 'N', 'NA', 'NULL', '\s+', '')
#
#--- session expiration time in seconds
#
time_exp = 3600 * 12
#
#--- read other parm
#
path = join(BASE_DIR, 'ocatsite/static/compare')
f    = open(path, 'r')
test = f.read().strip()
f.close()

#----------------------------------------------------------------------------------
#-- ocatMain: This class starts Ocat Main Page using django                     ---
#----------------------------------------------------------------------------------

class ocatMain(View):
    """
    This class starts Target Parameter Update Status Form
    """
#
#--- tamplate names
#
    template_name  = 'ocatmain/ocatmain.html'
    template_name2 = 'ocatmain/ocatmain_usint.html'
    not_found_page = 'ocatmain/not_found_page.html'

#----------------------------------------------------------------------------------
#-- get: "get" submitted data and display the front page                        ---
#----------------------------------------------------------------------------------

    def get(self, request, *args,  **kwargs):
        """
        this  part display the data page
        """

        if request.method == 'POST':
            form = request.POST
        else:
            form = request.GET

#-----------------------------------------------------
#--- LOGIN PAGE 
#-----------------------------------------------------
#
#--- check whether it is still under the same session with the same user. if not display a login page
#
        if request.user:
            s_user = request.user.username + '_session'
            try:
                if request.session[s_user] != 'yes':
                    if not request.user.is_authenticated():
                        return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)
            except:
                if not request.user.is_authenticated():
                    return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)
#
#--- every time the page is accessed/upated, the expiration clock is reset to the full length
#
            request.session[s_user] = 'yes'
            request.session.set_expiry(time_exp)
        else:
            if not request.user.is_authenticated():
                return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)

            s_user = request.user.username + '_session'
            request.session[s_user] = 'yes'
            request.session.set_expiry(time_exp)
#
#--- record the user's name for the later use
#
        self.submitter = request.user.username
#
#--- set up several parameters needed
#
        self.setup_params()

        try:
#
#--- check whether the user is still using the defalut password, if so ask to change
#
            usert = User.objects.get(username=self.submitter)
            if usert.check_password(test):
            ###if usert.check_password('dfadfadfa'):
                wdict = self.mk_dict()
                wdict['passchange'] = 'yes'
                wdict['pcomment']   = 'Please update your password.'
                if self.group == 'usint':
                    return render_to_response(self.template_name2, wdict, RequestContext(request))
                else:
                    return render_to_response(self.template_name,  wdict, RequestContext(request))
            else:
#
#--- the first time that the page is called
#    
#
#--- access page are different depending on the user is POC or USINT
#
                wdict = self.mk_dict()
                if self.group == 'usint':
                    return render_to_response(self.template_name2, wdict, RequestContext(request))
                else:
                    return render_to_response(self.template_name,  wdict, RequestContext(request))
#
#--- if something went wrong,  display the error page
#
        except:
            return render_to_response(self.not_found_page,  RequestContext(request))


#-----------------------------------------------------
#-- post: post data                                 --
#-----------------------------------------------------

    def post(self, request, *args,  **kwargs):
        """
        posting data
        """
#-----------------------------------------------------
#--- LOGIN PAGE 
#-----------------------------------------------------
#
#--- check whether it is still under the same session with the same user. if not display a login page
#
        if request.user:
            s_user = request.user.username + '_session'
            try:
                if request.session[s_user] != 'yes':
                    if not request.user.is_authenticated():
                        return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)
            except:
                if not request.user.is_authenticated():
                    return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)
#
#--- every time the page is accessed/upated, the expiration clock is reset to the full length
#
            request.session[s_user] = 'yes'
            request.session.set_expiry(time_exp)
        else:
            if not request.user.is_authenticated():
                return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)

            s_user = request.user.username + '_session'
            request.session[s_user] = 'yes'
            request.session.set_expiry(time_exp)
#
#--- record the user's name for the later use
#
        self.submitter = request.user.username
#
#--- set up several parameters needed
#
        self.setup_params()

#-----------------------------------------------------
#-- main part starts here                           --
#-----------------------------------------------------

        try:
#
#--- get parameter values
#
            form = request.POST
#
#--- extract passed data
#
            [durl, section, obs_list, vlist] = self.recover_data(form)
            self.setup_params()
#
#--- usint and poc have different html pages
#
            if self.group == 'usint':
                wtemplate = self.template_name2
            else:
                wtemplate = self.template_name
#
#--- check whether the user is still using the default password
#
            usert = User.objects.get(username=self.submitter)
            if usert.check_password(test):
                change_p = 1                        #--- the user is still using the default password
            else:
                change_p = 0
#
#--- check whether obsid is submitted. then don't go to change user/password site
#
            achk = 0
            if ('ocat_obsid' in form) and (form['ocat_obsid']):
                if (form['ocat_obsid']) != '':
                    achk = 1                        #--- Ocat Data Page is requested

            if ('chk_obsid' in form) and (form['chk_obsid']):
                if (form['chk_obsid']) != '':
                    achk = 2                        #--- Chkupdata Page is requested
#
#--- changing the user or changin the password
#
            if ((achk == 0) and ('check0' in form) and (form['check0'])) or (change_p == 1):
#
#--- escape from change password page to change user page
#
                if('check3' in form) and ( form['check3'] == 'Change User'):
                        check3 = 1
                else:
                        check3 = 0
#
#--- changing the user
#
                if (form['check0'] == 'Change User') or ( check3 == 1):
                    return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)
     
                    s_user = request.user.username + '_session'
                    request.session[s_user] = 'yes'
                    request.session.set_expiry(self.time_exp)
#
#---- change password
#
                elif (form['check0'] == 'Change Password') or (change_p == 1):

                    wdict = self.mk_dict()

                    if (change_p == 0) and (('cancel' in form) and (form['cancel'] == 'Cancel')):

                        return render_to_response(wtemplate, wdict, RequestContext(request))
                    else:
                        user = User.objects.get(username=self.submitter)
                        if ('password' in form):
                            if user.check_password(form['password']):
                                try:
                                    npassword = form['npassword']
                                    cpassword = form['cpassword']
                                    pchk = 5
                                    if npassword == cpassword:
                                        user.set_password(npassword)
                                        user.save()
                                    else:
                                        pchk = 1
                                except:
                                    pchk = 1
                            else:
                                pchk = 2
                        else:
                            pchk = 0
#
#--- add comment if the password change failed
# 
                        if pchk == 0:
                            wdict["passchange"] =  "yes"
                            wdict["pcomment"]   =  ""
                        elif pchk == 1:
                            wdict["passchange"] =  "yes"
                            wdict["pcomment"]   =  "New Passwords Did Not Match"
                        elif pchk == 2:
                            wdict["passchange"] =  "yes"
                            wdict["pcomment"]   =  "Original Password is Not Correct"
                        else:
                            wdict["passchange"] =  "no"
                            wdict["pcomment"]   =  "Password Updated!"

                        return render_to_response(wtemplate, wdict, RequestContext(request))
#
#--- change password cancelled
#
                else:
                    wdict = self.mk_dict()
                    return render_to_response(wtemplate, wdict, RequestContext(request))
#
#--- ocat data page
#
            elif achk == 1:
                obsid = form['ocat_obsid']
                return HttpResponseRedirect('/ocatdatapage/%s' % obsid)
#
#--- chkupdata page
#
            elif achk == 2:
                obsid = form['chk_obsid']
                ver   = form['chk_ver']
#
#--- open_chkupdata returns either parameters or a list of possible choices of the data
#
                vobs  = self.open_chkupdata(obsid, ver)
#
#--- if only obsid is given for chkupdata page choice, it will display
#--- a list of possible choices
#
                if isinstance(vobs, list):

                    wdict = self.mk_dict(vlist = vobs)
                    return render_to_response(wtemplate, wdict, RequestContext(request))
                else:
                    return HttpResponseRedirect('/chkupdata/%s' % vobs)
#
#--- display a page with all planned observations
#
            elif('check3' in form) and (form['check3']):
                if form['check3'] == 'Open All Planned Observation List':
    
                    obs_list = oda.extract_obs_plan('poc', self.submitter)
     
                    wdict = self.mk_dict(section='3', obs_list=obs_list)
                    return render_to_response(wtemplate, wdict, RequestContext(request))
                else:
                    wdict = self.mk_dict()

                return render_to_response(wtemplate, wdict, RequestContext(request))
#
#--- the first time that the page is called or empty submission is requesrted
#
            else:
                wdict = self.mk_dict()
            return render_to_response(wtemplate, wdict, RequestContext(request))

#
#--- if something went wrong,  display the error page
#
        except:
            return render_to_response(self.not_found_page,  RequestContext(request))

#--------------------------------------------------------------------------------------
#-- setup_params: setting up several parameters needed                               --
#--------------------------------------------------------------------------------------

    def setup_params(self):
        """
        setting up several parameters needed
        input:  submitter   --- submitter
        output: group       --- submitter's group id
                too_data    --- a list of too data
                ddt_data    --- a list of ddt data
                d30_data    --- a list of observations which are planned in the next 30 days
                toochk      --- indicator whether too data exist (1: yes, 0: no)
                ddtchk      --- indicator whether ddt data exist (1: yes, 0: no)
                d30chk      --- indicator whether d30 data exist (1: yes, 0: no)
                open_item   --- a list of data which need to be signed off
                opi         --- indicator whether open items exist (1: yes, 0: no)
        """
#
#--- find which group the submitter blongs to
#--- if s/he is a usint, directly go to ocrupdate page
#
        if oda.is_user_in_the_group(self.submitter, group='USINT'):
            self.group = 'usint'
        else:
            self.group = 'poc'
#
#--- read observations under the submitter
#
        [self.too_data, self.ddt_data, self.d30_data] = rol.collect_poc_obs_list(self.submitter)
        self.toochk = self.ddtchk = self.d30chk = self.opi = 0
        if len(self.too_data) > 0:
            self.toochk = 1
        if len(self.ddt_data) > 0:
            self.ddtchk = 1
        if len(self.d30_data) > 0:
            self.d30chk = 1
#
#--- check whether there are observations which need to be signed off
#
        self.open_item = rol.check_open_sign_off_item(self.submitter)
        if len(self.open_item) > 0:
            self.opi    = 1
#
#--- set submitter's next duty period
#
        self.period = oda.get_schedule_date_for_poc(self.submitter)


#--------------------------------------------------------------------------------------
#-- mk_dict: update a parameter dictioinary                                          --
#--------------------------------------------------------------------------------------

    def mk_dict(self, section='', obs_list ='', vlist=''):
        """
        update a parameter dictioinary 
        input:  self        --- use several self variables
                section     --- indicate which page to open
                obs_list    --- obsid list for section3
                vlist       --- a list of obsidrev for chkupdate page
        """
        dperiod = "\#\$".join(self.period.split(' '))
 
        wdict = {
            'submitter' : self.submitter,
            'period'    : self.period,
            'dperiod'   : dperiod,
            'title'     : 'Ocat Main Page',
            'opi'       : self.opi,
            'toochk'    : self.toochk,
            'ddtchk'    : self.ddtchk,
            'd30chk'    : self.d30chk,
            'open_item' : self.open_item,
            'too_data'  : self.too_data,
            'ddt_data'  : self.ddt_data,
            'd30_data'  : self.d30_data,
            'durl'      : durl,
            'section'   : section,
            'obs_list'  : obs_list,
            'vlist'     : vlist,
            'pcomment'  : '',
        }
        return wdict

#--------------------------------------------------------------------------------------
#-- recover_data: recover data from form dict passed                                ---
#--------------------------------------------------------------------------------------

    def recover_data(self, form):
        """
        recover data from form dict passed
        input:  form    --- form dictionary
        output: passed data 
        """
        self.submitter  = form['submitter']
        dperiod         = form['dperiod']
        self.period     = " ".join(dperiod.split('\#\$'))
        self.opi        = form['opi']
        self.toochk     = form['toochk']
        self.ddtchk     = form['ddtchk']
        self.d30chk     = form['d30chk']
        self.open_item  = form['open_item']
        self.too_data   = form['too_data']
        self.ddt_data   = form['ddt_data']
        self.d30_data   = form['d30_data']
        durl            = form['durl']
        section         = form['section']
        obs_list        = form['obs_list']
        vlist           = form['vlist']

        return [durl, section, obs_list, vlist]

#--------------------------------------------------------------------------------------
#-- open_chkupdata: return obsid.version or a list of possible obsid.version selections
#--------------------------------------------------------------------------------------

    def open_chkupdata(self, obsid, ver):
        """
        return obsid.version or a list of possible obsid.version selections
        input:  obsid   --- obsid
                ver     --- version. if it is a blank, it will return a list of possible choices
        output: vobs    --- if version is given, <obsid>.<version>
                vlist   --- if version is not given, a list of possible selction. 
        """
#
#--- version value is given, convert it to correct form
#
        if ver != '':
            ver = int(float(ver))

            if ver < 10:
                ver = '00' + str(ver)
            elif ver < 100:
                ver = '0' + str(ver)
            else:
                ver = str(ver)
            vobs = str(obsid) + '.' + str(ver)
            return vobs
#
#--- version value is not given, extract possible selctions and return a list
#
        else:

            olist = oda.select_data_for_obsid(str(obsid))
            vlist = []
            for ent in olist:
                vlist.append(ent[0])
            
            return vlist

#--------------------------------------------------------------------------------------
#-- login_page: log-in process                                                       --
#--------------------------------------------------------------------------------------

    def login_page(self, request):
        """
        log-in process 
        input:  request     --- session
        output: submitter   --- submitter's id
        """
#
#--- check whether it is still under the same session with the same user. if not display a login page
#
        if request.user:
            s_user = request.user.username + '_session'
            try:
                if request.session[s_user] != 'yes':
                    if not request.user.is_authenticated():
                        return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)
            except:
                if not request.user.is_authenticated():
                    return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)
#
#--- every time the page is accessed/upated, the expiration clock is reset to the full length
#
            request.session[s_user] = 'yes'
            request.session.set_expiry(self.time_exp)
            #request.session.set_expiry(time_exp)
        else:
            if not request.user.is_authenticated():
                return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)

            s_user = request.user.username + '_session'
            request.session[s_user] = 'yes'
            request.session.set_expiry(self.time_exp)
            #request.session.set_expiry(time_exp)
#
#--- record the user's name for the later use
#
        self.submitter = request.user.username
