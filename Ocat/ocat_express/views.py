#########################################################################################################
#                                                                                                       #
#           ocatExpress:  django class to create Express Sign-off Page                                  #
#                                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                       #
#               Last update: Nov 17, 2016                                                               #
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
import utils.create_log_and_email as cle        #--- create a change log and send out eamil
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
#-- ocatExpress: This class start Express Sign-Off page                         ---
#----------------------------------------------------------------------------------

class ocatExpress(View):
    """
    This class starts Target Parameter Update Status Form
    """
#
#--- tamplate names
#
    template_name  = 'ocat_express/ocat_express.html'
    not_found_page = 'ocat_express/not_found_page.html'
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
        self.submitter = request.user.username
        self.durl      = durl

#
#--- check whether the user is still using the default password; if so send back to main page
#
        path = join(BASE_DIR, 'ocatsite/static/compare')
        f    = open(path, 'r')
        test = f.read().strip()
        f.close()
        usert = User.objects.get(username=self.submitter)
        if usert.check_password(test):
            return HttpResponseRedirect('/ocatmain/')

#-----------------------------------------------------
#---- normal porcess starts here                  
#-----------------------------------------------------

        try:
#
#--- read parameters from form
#
            if request.method == 'POST':
                form = request.POST
            else:
                form = request.GET
    
            self.set_param_null()
            wdict = self.make_dict(1)
            return render_to_response(self.template_name, wdict,  RequestContext(request))
#
#--- if something went wrong,  display the error page
#
        except:
            return render_to_response(self.not_found_page,  RequestContext(request))

#----------------------------------------------------------------------------------
#-- post: "Post"  submission                                                     --
#----------------------------------------------------------------------------------

    def post(self, request, *args, **kwargs):

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
        self.submitter = request.user.username
        self.durl      = durl

#
#--- check whether the user is still using the default password; if so send back to main page
#
        path = join(BASE_DIR, 'ocatsite/static/compare')
        f    = open(path, 'r')
        test = f.read().strip()
        f.close()
        usert = User.objects.get(username=self.submitter)
        if usert.check_password(test):
            return HttpResponseRedirect('/ocatmain/')

#----------------------------------------------------------------------------------
#-- main part starts here                                                       ---
#----------------------------------------------------------------------------------

        try:
#
#--- read parameters from form
#
            if request.method == 'POST':
                form = request.POST
            else:
                form = request.GET
    
            self.submitter = form['submitter']
#
#--- check whether any obsid submitted
# 
            achk = 0
            if ('obsid_list' in form) and (form['obsid_list']):
                if form['obsid_list'] != '':
                    achk = 1

            if ('check' in form) and (form['check']):
#
#--- submitted the list of obsids and go to the check page
#
                if achk > 0:
                    input_list = form['obsid_list']
                    self.check_requested_list(input_list)
                    wdict = self.make_dict(2)
                    return render_to_response(self.template_name, wdict, RequestContext(request))
#
#--- when you removed an obsid from the approved list
#
                elif form['check'] == 'Remove':
                    self.remove_entry_from_approve_list(form)
                    wdict = self.make_dict(2)
                    return render_to_response(self.template_name, wdict,  RequestContext(request))
#
#--- approve all obsids listed
#
                elif form['check'] == 'Approve All':
                    self.approve_the_list(form)
                    wdict = self.make_dict(3)
                    return render_to_response(self.template_name, wdict,  RequestContext(request))
#
#--- change the user id
#
                elif (achk == 0) and (form['check'] == 'Change'):
                    return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)
    
                    s_user = request.user.username + '_session'
                    request.session[s_user] = 'yes'
                    request.session.set_expiry(self.time_exp)
#
#--- back to the front page
#
                elif form['check'] == 'Back To Front Page':
                    self.set_param_null()
                    wdict = self.make_dict(1)
                    return render_to_response(self.template_name, wdict,  RequestContext(request))
                else:
#
#--- some reason there is no clear command, go back to the front page
#
                    self.set_param_null()
                    wdict = self.make_dict(1)
                    return render_to_response(self.template_name, wdict,  RequestContext(request))
#
#--- back to the check page (after changing entries)
# 
            elif ('obsidentry' in form) and (form['obsidentry']):
    
                    self.remove_entry_from_approve_list(form)
                    wdict = self.make_dict(2)
                    return render_to_response(self.template_name, wdict,  RequestContext(request))
#
#--- first time coming into page
#
            else:
                self.set_param_null()
                wdict = self.make_dict(1)
                return render_to_response(self.template_name, wdict,  RequestContext(request))
#
#--- if something went wrong,  display the error page
#
        except:
            return render_to_response(self.not_found_page,  RequestContext(request))


###########################################################################################
##                other functions listing starts here                                   ###
###########################################################################################

#----------------------------------------------------------------------------------
#-- make_dict: make parameter dictionary                                        ---
#----------------------------------------------------------------------------------

    def make_dict(self, panel):
        """
        make parameter dictionary
        input:  panel           --- panel # (1, 2, or 3)
                durl            --- main url
                submitter       --- submitter's id
                entry_list      --- a string of obsids (maybe delimited by ;, , etc)
                obsidentry      --- a list of obsids
                ostatus         --- a status of the observation
                approve_list    --- a list of obsids which can be approved the submitter
                rejected_list   --- a list of obsids which cannot be apporve by the submitter
        output: wdict           --- a parameter dictionary

        """
        ycnt = 0
        ychk = 0
        for ent in self.entry_list:
            ycnt += 1
            if ent[7] == 'y':
                ychk = 1

        if ycnt == 0:
            ychk = -1

        wdict = {
            'durl'          : durl,
            'submitter'     : self.submitter,  
            'panel'         : panel, 
            'entry_list'    : self.entry_list, 
            'obsidentry'    : self.obsidentry, 
            'ostatus'       : self.ostatus ,
            'approved_list' : self.approved_list, 
            'rejected_list' : self.rejected_list,
            'ychk'          : ychk
        }

        return wdict

#----------------------------------------------------------------------------------
#-- set_param_null: set several self parameters to null                         ---
#----------------------------------------------------------------------------------

    def set_param_null(self):
        """
        set several self parameters to null
        input:  none
        output  entry_list      --- a string of obsids (maybe delimited by ;, , etc)
                obsidentry      --- a list of obsids
                ostatus         --- a status of the observation
                approve_list    --- a list of obsids which can be approved the submitter
                rejected_list   --- a list of obsids which cannot be apporve by the submitter
        """

        self.entry_list    = ''
        self.obsidentry    = ''
        self.ostatus       = ''
        self.approved_list = ''
        self.rejected_list = ''

#----------------------------------------------------------------------------------
#-- check_requested_list: create obsid list from input and extract basic info for each obsid 
#----------------------------------------------------------------------------------

    def check_requested_list(self, input_list):
        """
        create obsid list from input and extract basic info for each obsid
        input:  input_list          --- stinrg form of obsid list
        output: self.entry_list     --- [obsid, seqno, propno, target, title, note, pname, sind], 
                self.obsidentry 
                seof.ostatus
        """

#
#--- create obsid_list from the input
#
        obsid_list = make_obsid_list(input_list)
#
#--- create approve table lists (returning self.entry_list, self.obsidentry, self.ostatus)
#
        self.create_approve_table_list(obsid_list)

        self.approved_list = ''
        self.rejected_list = ''

#----------------------------------------------------------------------------------
#-- remove_entry_from_approve_list: removed "Remove"d obsid from the list and recreate basic info lists
#----------------------------------------------------------------------------------

    def remove_entry_from_approve_list(self,  form):
        """
        removed "Remove"d obsid from the list and recreate basic info lists
        input:  form        --- form passed
        output: self.entry_list     --- [obsid, seqno, propno, target, title, note, pname, sind], 
                self.obsidentry 
                seof.ostatus
        """
#
#--- form['obsidentry'] is a string with format of e.g, 17234:17235;17236
#
        obsidentry  = re.split(':', form['obsidentry'])

        obsid_list  = []
        for obsid in obsidentry:
    
            try:
                if form[str(obsid)] == 'Remove':
                    continue
            except:
                pass

            if ocf.chkNumeric(obsid):
                obsid_list.append(obsid)
#
#--- create approve table lists (returning self.entry_list, self.obsidentry, self.ostatus)
#
        self.create_approve_table_list(obsid_list)

        self.approved_list = ''
        self.rejected_list = ''

#----------------------------------------------------------------------------------
#-- approve_the_list: select which observations are approvable and approve them  --
#----------------------------------------------------------------------------------

    def approve_the_list(self, form):
        """
        select which observations are approvable and approve them
        input:  form        --- from parameters
                submitter   --- poc/submitter
        outpu: [approved_list, rejected_list]
               this also callsadd_to_approved_database, and add the approved
                obsids to the sql database.
        """

        obsidentry = re.split(':',form['obsidentry'])
        ostatus    = re.split(':',form['ostatus'])

        approved_list = []
        rejected_list = []
        for i in range(0, len(obsidentry)):
            obsid = obsidentry[i]
            if ocf.chkNumeric(obsid) == False:
                continue

            if ostatus[i] == 'y':
                approved_list.append(obsid)
            else:
                rejected_list.append(obsid)

        if len(approved_list) == 0:
            approved_list = 'na'
        if len(rejected_list) == 0:
            rejected_list = 'na'
#
#--- update all databases
#
        add_to_approved_database(approved_list, self.submitter)
#
#--- send out notification email
#
        cle.send_out_email_for_express_approval(approved_list, self.submitter)

        self.entry_list    = ''
        self.obsidentry    = ''
        self.ostatus       = ''
        self.approved_list = approved_list
        self.rejected_list = rejected_list
        
#----------------------------------------------------------------------------------
#-- create_approve_table_list: extract basic information for each of given obsids -
#----------------------------------------------------------------------------------

    def create_approve_table_list(self, obsid_list):
        """
        extract basic information for each of given obsids
        input:  oubid_list  --- a list of obsid
                rlist       --- a list of lists with:
                                [obsid, seqno, propno, pi, target, title, poc, note, pname, sind]
                                where pname is form paramter name to be passed
                                      sind  is an inidcator of whether the submitter can approved
                obsidentry  --- a string of list of obsids e.g., 17234:17235;17236
                ostatus     --- a string of list of indicator which tells whether obsid can be approved
        """
        obsidentry  = ''
        ostatus     = ''
        rlist = []
        for obsid in obsid_list:
#
#--- check whether the observation is already approved
#
            achk = oda.get_values_from_approved(obsid)
            if achk[1] == 'na':
                approved = 1
            else:
                approved = 0
#
#--- check whether it is previously requested to update parameter values
#
            out = find_from_updates_list(obsid, approved, self.submitter)
#
#--- if it is not in updates_list, read the parameter values from the main database
#
            if out == None:
                out = find_from_main_db(obsid, approved, self.submitter)

            rlist.append(out)

            if obsidentry == '':
                obsidentry  = str(obsid)
                ostatus     = str(out[-1])
            else:
                obsidentry  = obsidentry  + ':' + str(obsid)
                ostatus     = ostatus     + ':' + str(out[-1])

        self.entry_list = rlist
        self.obsidentry = obsidentry
        self.ostatus    = ostatus 

###################################################################################
##             None Class Functions                                             ###
###################################################################################

#----------------------------------------------------------------------------------
#-- make_obsid_list: convert a string list of obsid into a list                  --
#----------------------------------------------------------------------------------

def make_obsid_list(input_list):
    """
    convert a string list of obsid into a list
    input:  input_list  --- a string list of obsid
    output: obsid_list  --- a list of obsid
    """
#
#--- split the obsid list entries to a list
#
    chk = 0
    mc = re.search('-', input_list)
    if mc is not None:
        chk = 1

    test_list  = re.split('\,|\;|\/|\s+|\t+', input_list)

    obsid_list  = []
#
#--- drop none numeric entries (such as blank space)
#
    for ent in test_list:
        mc = re.search('-', ent)
        if mc is not None:
            atemp = re.split('-', ent)
            try:
                begin = int(float(atemp[0]))
                end   = int(float(atemp[-1])) + 1
                for i in range(begin, end):
                    obsid_list.append(str(i))
            except:
                pass

        if ocf.chkNumeric(ent):
            obsid_list.append(ent)

    return obsid_list


#----------------------------------------------------------------------------------
#-- find_from_updates_list: find basic information of obsid from updates_list  ----
#----------------------------------------------------------------------------------

def find_from_updates_list(obsid, approved, submitter):
    """
    find basic information of obsid from updates_list
    input:  obsid       --- obsid
            approve     --- approved status
            submitter   --- submitter's ID
    output: a list of information:
                    [obsid, seqno, propno, pi, target, title, poc, note, pname, sind]
                    where pname is form paramter name to be passed
                          sind  is an inidcator of whether the submitter can approved
    """

    sind = 'y'
    dat_list = oda.select_data_for_obsid(obsid)

    if len(dat_list) > 0:

        obsidrev = dat_list[0][0]
        dat_dict = oda.read_updates_entries_to_dictionary(obsidrev)
#
#--- check whether it really has information needed
#
        if dat_dict['seq_nbr'][0] != 'na':
            seqno  = dat_dict['seq_nbr'][0]
            propno = dat_dict['prop_num'][0]
            target = dat_dict['targname'][0]
            title  = dat_dict['title'][0]
            poc    = dat_dict['poc'][0]
            try:
                simode = dat_dict['si_mode'][0]
            except:
                simode = ''
            note   = ''
#
#--- sometime poc changes depending of defferent revisioin. so check all of them
#
            poc_list = []
            for ent in dat_list:
                obsidrev = ent[0]
                dat_dict = oda.read_updates_entries_to_dictionary(obsidrev)
                poc      = dat_dict['poc'][0]
                poc_list.append(poc)

            if approved == 0:
                note = 'this observation is already on approved list.'
                sind = 'n'
            else:
                if submitter not in poc_list:
                    note = 'you are not POC (' + poc + ') of this observation.'
                    sind = 'n'
#
#--- if si mode is not defined, you cannot approve
#
            if simode in (None, 'NONE', 'None', 'No', 'NO', 'N', 'NA', 'NULL', '\s+', ''):
                note =  note + 'no si mode is given.'

                sind = 'n'
#
#--- check whether the observation is already on OR list
#
            if ocf.is_in_orlist(obsid):
                note =  note + 'in Active OR List.'
                sind = 'n'
#
#--- pname is parameter name used on web pages
#
            pname = 'obsid_' + str(obsid)
            out = [obsid, seqno, propno, target, title, note, pname, sind]
        else:
            out = None
    else:
        out = None

    return out
                    
#----------------------------------------------------------------------------------
#-- find_from_main_db: find basic information of obsid from the main database  ----
#----------------------------------------------------------------------------------

def find_from_main_db(obsid, approved, submitter):
    """
    find basic information of obsid from the main database
    input:  obsid       --- obsid
            approve     --- approved status
            submitter   --- submitter's ID
    output: a list of information:
                    [obsid, seqno, propno, pi, target, title, poc, note, pname, sind]
                    where pname is form paramter name to be passed
                          sind  is an inidcator of whether the submitter can approved
    """

    sind = 'y'
    try:
        [dat_dict, db ] = pdd.get_data_from_db(obsid)
        seqno  = dat_dict['seq_nbr']
        propno = dat_dict['prop_num']
        target = dat_dict['targname']
        title  = dat_dict['title']
        poc    = submitter

        if approved == 0:
            note = 'this observation is already on approved list.'
            sind = 'n'
        else:
            note = ''
    except:
#
#--- if obsid is not in the main database, return with 'na' values
#
        seqno  = 'na'
        propno = 'na'
        target = 'na'
        title  = 'na'
        poc    = submitter
        note   = 'no data for obsid: ' + str(obsid) + '.'
        sind   = 'n'
#
#--- pname is parameter name used on web pages
#
    pname = 'obsid_' + str(obsid)
    return [obsid, seqno, propno, target, title, note, pname, sind]


#----------------------------------------------------------------------------------
#-- add_to_approved_database: add to approved observations to the sql database    -
#----------------------------------------------------------------------------------

def add_to_approved_database(approved_list, poc):
    """
    add to approved observations to the sql database
    input:  approved_list   --- a list of approved obsid
            poc             --- poc/submitter
    output: updated sql database
    """

    for obsid in approved_list:
#
#--- set a revision # and obsidrev
#
        rev      = oda.set_new_rev(obsid)
        obsidrev = str(obsid) + '.' + str(rev)
#
#--- create data dictionary from the database
#
        pdict = read_database_to_dictionary(obsid, rev, poc)

        seqno = pdict['seq_nbr'][0]
        poc   = poc
        date  = pdict['date'][0]
#
#--- add to approved list
#
        oda.add_to_approved_list(obsid, seqno, poc, date)
#
#--- update updates_table.list database
#
        general  = 'NULL'
        acis     = 'NULL'
        si_mode  = 'NULL'
        verified = poc + ' ' + str(date)
        cdate    = date
        mdate    = date

        oda.add_to_updates_list(obsidrev, general, acis, si_mode, verified, seqno, poc, cdate, mdate)
#
#--- add obsidrev data into Data_tables
#
        oda.add_to_update_entry(pdict, obsidrev)


#----------------------------------------------------------------------------------
#-- read_database_to_dictionary: read data from database and put in a dictionary form 
#----------------------------------------------------------------------------------

def read_database_to_dictionary(obsid, rev, submitter):
    """
    read data from database and put in a dictionary form
    input:  obsid   --- obsid
            rev         --- revision #
            submitter   --- poc/submitter's name
    output: pdict       --- a data dictionary, each data is a list [orig val, new val]
    """
#
#--- read data from the database and put in a dictionary
#
    tmp_dict = pdd.prep_data_dict(obsid)
#
#--- change the format to appropriate for the sql
#
    pdict = {}
    for key in tmp_dict.keys():
        val = tmp_dict[key]
        pdict[key] = [val, val]
#
#--- extra parameters
#

    obsidrev = str(obsid) + '.' + str(rev)

    pdict['obsidrev']  = [obsidrev, obsidrev]
    pdict['rev']       = [rev, rev]
    pdict['asis']      = ['asis', 'asis']
    pdict['poc']       = [submitter, submitter]
    pdict['submitter'] = [submitter, submitter]

    today              = ocf.today_date()
    odate              = ocf.disp_date_to_odate(today)

    pdict['date']      = [today, today]
    pdict['odate']     = [odate, odate]

    return pdict


