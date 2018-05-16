#########################################################################################################
#                                                                                                       #
#           rmSubmission:   django class to create Data Removal Page                                    #
#                                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                       #
#               Last update: Nov 02, 2016                                                               #
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
#-- rmSubmission: This class start Data Submission Cancelation Page              --
#----------------------------------------------------------------------------------

class rmSubmission(View):
    """
    This class starts Target Parameter Update Status Form
    """
#
#--- tamplate names
#
    template_name  = 'rm_submission/rm_submission.html'
    not_found_page = 'rm_submission/not_found_page.html'
#
#--- session expiration time in seconds
#
    time_exp = 3600 * 12

#----------------------------------------------------------------------------------
#-- get: "get" submitted data and display an appropriate page                    --
#----------------------------------------------------------------------------------

    def get(self, request, *args,  **kwargs):
        """
        this  part display the data submission cancellation page page
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
            interval   = 1
            if request.method == 'POST':
                form = request.POST
            else:
                form = request.GET

            updates_list = self.extract_data_for_rm_page(submitter)
#
#--- removed specified sign off entries
#
            chk = self.removed_sign_off_from_database(updates_list, form)
#
#--- if there is a change, re-read the database
#
            if chk > 0:
                updates_list = self.extract_data_for_rm_page(submitter)
#
#--- write html page
#
            return render_to_response(self.template_name, {
                                'durl'              : durl,
                                'updates_list'      : updates_list, 
                                'submitter'         : submitter,
                        }, RequestContext(request))
#
#--- if something went wrong,  display the error page
#
        except:
            return render_to_response(self.not_found_page,  RequestContext(request))

#----------------------------------------------------------------------------------
#-- post: passing around updated data                                           ---
#----------------------------------------------------------------------------------

    def post(self, request, *args, **kwargs):
        """
        passing around updated data
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

#-----------------------------------------------------
#-----------------------------------------------------
#-----------------------------------------------------

        try:
#
#--- read parameters from form
#
            interval   = 1
            if request.method == 'POST':
                form = request.POST
            else:
                form = request.GET

            submitter = form['submitter']

            updates_list = self.extract_data_for_rm_page(submitter)
#
#--- removed specified sign off entries
#
            chk = self.removed_sign_off_from_database(updates_list, form)
#
#--- if there is a change, re-read the database
#
            if chk > 0:
                updates_list = self.extract_data_for_rm_page(submitter)
#
#--- write html page
#
            return render_to_response(self.template_name, {
                                'durl'              : durl,
                                'updates_list'      : updates_list,
                                'submitter'         : submitter,
                        }, RequestContext(request))
#
#--- if something went wrong,  display the error page
#
        except:
            return render_to_response(self.not_found_page,  RequestContext(request))


###########################################################################################
##                other functions listing starts here                                   ###
###########################################################################################

#----------------------------------------------------------------------------------
#-- extract_data_for_rm_page: extract data which arenot verified  yet            --
#----------------------------------------------------------------------------------

    def extract_data_for_rm_page(self, submitter, interval=1):
        """
        extract data which arenot verified and those which were verified in the past "interval" days
        input:  submitter   --- the id of the submitter
                interval    --- time span in day which you want to display toward the past: default=1
        output: alist   a list of lists of extracted data
    
                        [obsidrev, general, acis, si mode, verified, seq number, poc, date, 
                         name of gen_status, name of acis_status, name of si mode stateus, 
                         name of verified status, gen_removable?, acis_removable?, si_mode_removable?
                         verify_removable?]
        """
#
#--- find data which created today or yesterday
#
        odate  = ocf.find_date_of_interval_date_before(interval)
        tlist  = oda.get_data_newer_than_date(odate)
#
#--- find data which are not verified
#
        tlist2 = oda.select_non_signed_off('verified')
        tlist  = tlist + tlist2 
#
#--- remove the entries which are already in approved list
#
        alist  = []
        for ent in tlist:
            obsidrev = ent[0]
            atemp    = re.split('\.', obsidrev)

            if ocf.is_approved(atemp[0]):
                continue
            else:
                alist.append(ent)
#
#--- get unique entries
#
        alist  = ocf.find_unique_entries(alist)
#
#--- add several extra information which will be used to display the data
#
        alist  = self.add_extra_information(alist, submitter)
#
#--- if the list is empty, return <blank> insted
# 
        if len(alist) == 0:
            alist = ''
    
        return alist

#----------------------------------------------------------------------------------
#-- add_extra_information: add status form names to the list                     --
#----------------------------------------------------------------------------------

    def add_extra_information(self, alist, submitter):
        """
        add status form names to the list
        input:  alist   ---- a list of lists of entries
        output: ulist   ---- a list with status form names
                example:    16259_002_gen, 16259_002_acis, ...
        """

        ulist = []
        rlist = []
        for blist in alist:
            obsidrev = blist[0]
            obsidrev = obsidrev.replace('.', '_')
            verified = blist[4]
#
#--- create names of parameters. example: 16259_002_gen
#
            gen_status    = obsidrev + '_gen'
            acis_status   = obsidrev + '_acis'
            si_status     = obsidrev + '_si'
            verify_status = obsidrev + '_verify'

            blist.append(gen_status)
            blist.append(acis_status)
            blist.append(si_status)
            blist.append(verify_status)
#
#-- get indicators for whether the entries are removable
#
            vstatus  = self.check_removable(blist, submitter)

            blist = blist + vstatus

            if 'y' in vstatus:
                ulist.append(blist)
            else:
                rlist.append(blist)

        ulist = ulist + rlist

        return ulist

#----------------------------------------------------------------------------------
#-- check_removable: check whether any of the signed off entries can be removed  --
#----------------------------------------------------------------------------------

    def check_removable(self, alist, submitter):
        """
        check whether any of the signed off entries can be removed
        input:  alist       --- a list of status (see extract_data_for_rm_page for definition)
                submitter   --- id of submitter
        output: [gen, acis, si_mode, verify]    --- stauts whether it is removable 'y' or 'n'
        """

        today     = ocf.today_date()
        odate     = ocf.disp_date_to_odate(today)

        yesterday = ocf.find_days_before_in_odate(odate)
#
#--- if  it is already verified, all others cannot be removed from the list
#
        if alist[4] == 'NA':
            gen     = self.check_remove_status(alist[1], submitter, yesterday)
            acis    = self.check_remove_status(alist[2], submitter, yesterday)
            si_mode = self.check_remove_status(alist[3], submitter, yesterday)
        else:
            gen     = 'n'
            acis    = 'n'
            si_mode = 'n'

        verify  = self.check_remove_status(alist[4], submitter, yesterday)

        return  [gen, acis, si_mode, verify]


#----------------------------------------------------------------------------------
#-- check_remove_status: check entry is removable                               ---
#----------------------------------------------------------------------------------

    def check_remove_status(self, entry, submitter, day_limit):
        """
        check entry is removable
        input:  entry       ---- sign off status, such as 'mccolml 08/10/15'
                submitter   ---- submitter's ID
                day_limit   ---- how far we allow to cancel the sign off in day
        output: chk         ---- 'y' or 'n'
        """
#
#--- if entry is not signed off yet, no action
#
        if (entry == 'NA') or (entry == 'NULL'):
            chk = 'n'
        else:
            atemp = re.split('\s+', entry)
            person = atemp[0]
            date   = atemp[1]
            odate  = ocf.disp_date_to_odate(date)
#
#--- submitter and the person signed-off must be the same
#    
            chk = 'n'
            if person == submitter:
                chk = 'y'
#
#--- only signed-off made today or yesterday can be removed
#
                if odate < day_limit:
                    chk = 'n'

        return chk

#----------------------------------------------------------------------------------
#-- removed_sign_off_from_database: remove the specified sign-off signature from  sql databse 
#----------------------------------------------------------------------------------

    def removed_sign_off_from_database(self, alist, form):
        """
        remove the specified sign-off signature from  sql databse
        input:  alist   --- a list of original data
                form    --- a submitted form
        output: updated sql database
        """

        tail_list = ['gen', 'acis', 'si', 'verify']
        today     = ocf.today_date()

        changed = 0
        for ent in alist:

            obsidrev = ent[0]
            poc      = ent[6]
            obsidchk = obsidrev.replace('.', '_')
#
#--- parameter name is something like 16259_002_gen (see tail_list above)
#
            chk = 0
            for k in range(0, len(tail_list)):

                name = obsidchk + '_' + tail_list[k]

                try:
                    val  = form[name]
                except:
                    val  = ''

                if val == 'Remove':
#
#--- change the signed-off siganture to 'NA'
#
                    chk     = 1
                    k1      = k + 1
                    ent[k1] =  'NA'

            if chk > 0:
#
#--- update sql database
#
                changed += chk
                oda.add_to_updates_list(ent[0], ent[1], ent[2], ent[3], ent[4], ent[5], ent[6], ent[7], today)

        return changed

