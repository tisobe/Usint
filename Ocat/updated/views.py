#########################################################################################################
#                                                                                                       #
#           upDated:    django class to create Updated Target List Page                                 #
#                                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                       #
#               Last update: Oct 26, 2016                                                               #
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

#from ocatdatapage.forms         import OrUpdateFomr

import utils.ocatCommonFunctions as ocf         #--- various functions are saved here
import utils.prepdatdict         as pdd         #--- create data dictionary for the page
import utils.passWordCheck       as pwchk       #--- check user/password
import utils.ocatdatabase_access as oda         #--- accessing tools to ocat data page database
import utils.convertTimeFormat   as tcnv        #--- collections of time related conversion fuction
#
#--- reading directory list
#
from os.path import join, dirname, realpath
BASE_DIR = dirname(dirname(realpath(__file__)))
path = join(BASE_DIR, 'ocatsite/static/dir_list_py')

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

#----------------------------------------------------------------------------------
#-- upDate: This class start Update Target List                                 ---
#----------------------------------------------------------------------------------

class upDated(View):
    """
    This class starts Update Target List
    """
#
#--- tamplate names
#
    template_name  = 'updated/updated.html'
    not_found_page = 'updated/not_found_page.html'
#
#--- session expiration time in seconds
#
    time_exp = 3600 * 12

#----------------------------------------------------------------------------------
#-- get: "get" submitted data and display an appropriate page                    --
#----------------------------------------------------------------------------------

    def get(self, request, *args,  **kwargs):
        """
        this  part display the data page
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
                        return HttpResponseRedirect('/accounts/login/?next=%s' % '/ocatmain/')
            except:
                if not request.user.is_authenticated():
                    return HttpResponseRedirect('/accounts/login/?next=%s' % '/ocatmain/')
#
#--- every time the page is accessed/upated, the expiration clock is reset to the full length
#
            request.session[s_user] = 'yes'
            request.session.set_expiry(self.time_exp)
        else:
            if not request.user.is_authenticated():
                return HttpResponseRedirect('/accounts/login/?next=%s' % '/ocatmain/')

            s_user = request.user.username + '_session'
            request.session[s_user] = 'yes'
            request.session.set_expiry(self.time_exp)
#
#--- record the user's name for the later use
#
        submitter = request.user.username
#
#--- check whether the user is still using the default password; if so send back to main page
#
        path = join(BASE_DIR, 'ocatsite/static/compare')
        f    = open(path, 'r')
        test = f.read().strip()
        f.close()
        usert = User.objects.get(username=submitter)
        if usert.check_password(test):
            return HttpResponseRedirect('/ocatmain/')

#-----------------------------------------------------
#---- normal porcess starts here                  
#-----------------------------------------------------

        try:
#
#--- read parameters from form
#
            form = request.GET  
#
#--- set today's date
#
            [this_year, this_mon, year_list] = set_now()
            uyear = this_year + 1
    
            if ('check' in form) and (form['check']):
#
#--- back to top page request
# 
                return render_to_response(self.template_name, {
                                    'durl':             durl,
                                    'year_list':        year_list, 
                                    'endyear':          str(this_year),
                                    'endmonth':         this_mon,
                                }, RequestContext(request))
            else:
#
#--- display each year/month entry page
#
                chk = 0
                for year in range(2010, uyear):
                    syear = str(year)
                    if (syear in form) and (form[syear]):
                        smon = form[syear]
                        mon  = tcnv.changeMonthFormat(smon)
                        month = int(float(mon))
                        alist = extract_data_from_updates_list(year, month)
                        chk = 1

                        return render_to_response(self.template_name, {
                                    'durl':             durl,
                                    'month_display':    'y',
                                    'updates_list':     alist,   
                                }, RequestContext(request))
                if chk == 0:
#
#--- the first time that the page is called
#
                    endyear  = str(this_year)
                    endmonth = this_mon
     
                    return render_to_response(self.template_name,{
                                    'durl':             durl,
                                    'year_list':        year_list, 
                                    'endyear':          str(this_year), 
                                    'endmonth':         this_mon,
                                }, RequestContext(request))
#
#--- if something went wrong,  display the error page
#
        except:
            return render_to_response(self.not_found_page,  RequestContext(request))

#----------------------------------------------------------------------------------
#-- set_now: find today's date and set year range (this year + 1)               ---
#----------------------------------------------------------------------------------

def set_now():
    """
    find today's date and set year range (this year + 1)
    input: none
    output: a list includes
            this_year   --- this year
            this_mon    --- this month
            year_list   --- a list start from 201 and finish this_year + 1
    """
    tlist = tcnv.currentTime(format = 'UTC')
    this_year = tlist[0]
    this_mon  = tlist[1]
    uyear     = this_year + 1
    year_list = []
    for i in range(2010, uyear):
        year_list.append(str(i))
    return [this_year, this_mon, year_list]

#----------------------------------------------------------------------------------
#-- extract_data_from_updates_list: extract required data from updates table list sql 
#----------------------------------------------------------------------------------

def extract_data_from_updates_list(this_year, this_mon):
    """
    extract required data from updates table list sql
    input:  this_year   --- this year
            this_mon    --- this month
    output: r_list      --- a list of lists of extracted data. the interanl list:
            [obsidrev, general, acis, si_mode, verified, seqno, poc, date]
    """

    syear = str(this_year)
    ypart = syear[2] + syear[3]

    smon  = str(this_mon)
    if this_mon < 10:
        smon = '0' + smon

    sday  = '01'
    eday  = '32'

    start = ypart + smon + sday
    stop  = ypart + smon + eday

    start = int(float(start))
    stop  = int(float(stop))
#
#--- cycle through the date of month (1 to 31 for all months)
#
    out_list = []
    for pdate in range(start, stop):
        out = oda.get_data_marked_with_date(pdate)
        out_list = out_list + out
#
#--- we need only verified cases
#        
    r_list = []
    for ent in out_list:
        if ent[4] != 'NA':
            r_list.append(ent)

    return r_list

