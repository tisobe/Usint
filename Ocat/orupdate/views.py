#########################################################################################################
#                                                                                                       #
#           orUpdate:   django class to create Target Parameter Update Status Form page                 #
#                                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                       #
#               Last update: Nov 22, 2016                                                               #
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

#
#--- there are many form of 'NONE'
#
non_list      = (None, 'NONE', 'None', 'No', 'NO', 'N', 'NA', 'NULL', '\s+', '')
#
#--- session expiration time in seconds
#
time_exp = 3600 * 12
#
#--- is this test?
#
develop  = 'yes'

#----------------------------------------------------------------------------------
#-- orUpdate: This class start Target Parameter Update Status Form               --
#----------------------------------------------------------------------------------

class orUpdate(View):
    """
    This class starts Target Parameter Update Status Form
    """

#    form_class    = OrUpdateFomr

#
#--- tamplate names
#
    template_name  = 'orupdate/orupdate.html'
    not_found_page = 'orupdate/not_found_page.html'

#----------------------------------------------------------------------------------
#-- get: "get" submitted data and display an appropriate page                    --
#----------------------------------------------------------------------------------

    def get(self, request, *args,  **kwargs):
        """
        get the data; login page and the initial page
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
            request.session.set_expiry(time_exp)
        else:
            if not request.user.is_authenticated():
                return HttpResponseRedirect('/accounts/login/?next=%s' % '/ocatmain/')

            s_user = request.user.username + '_session'
            request.session[s_user] = 'yes'
            request.session.set_expiry(time_exp)

        self.submitter = request.user.username
#
#--- find which group the submitter blongs to
#--- if s/he is a usint, directly go to ocrupdate page
#
        if oda.is_user_in_the_group(self.submitter, group='USINT'):
            self.group = 'usint'
        else:
            self.group = 'poc'
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
    
            if ('check' in form) and (form['check']):
                self.read_form_param(form)

#------------------------------------------
#--- the first time that the page is called
#------------------------------------------
            else:
                self.param_initialize()
    
                updates_list = self.extract_data_for_display()
                updates_list = bubble_up_unsigned_off_entries(updates_list)
    
                if self.group == 'poc':
                    self.poc     = self.submitter
                    updates_list = self.reorder_by_poc(updates_list)
    
                wdict =  self.mk_data_dict(updates_list)
                return render_to_response(self.template_name, wdict,  RequestContext(request))
#
#--- if something went wrong,  display the error page
#
        except:
            return render_to_response(self.not_found_page,  RequestContext(request))

#----------------------------------------------------------------------------------
#--  posting data: sending around data                                           --
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
            request.session.set_expiry(time_exp)
        else:
            if not request.user.is_authenticated():
                return HttpResponseRedirect('/accounts/login/?next=%s' % '/ocatmain/')

            s_user = request.user.username + '_session'
            request.session[s_user] = 'yes'
            request.session.set_expiry(time_exp)

        self.submitter = request.user.username

#-----------------------------------------------------
#-- the main part starts here                       --
#-----------------------------------------------------

        try:
#
#--- read parameters from form
#
            if request.method == 'POST':
                form = request.POST
            else:
                form = request.GET
#
#--- check any value (obsid, seq # etc) is submitted
#    
            achk = 0
            if ('disp_obsid' in form) and (form['disp_obsid']):
                if form['disp_obsid'] != '':
                    achk = 1

            if ('seqno' in form) and (form['seqno']):
                if form['seqno'] != '':
                    achk = 2

            if ('prop_num' in form) and (form['prop_num']):
                if form['prop_num'] != '':
                    achk = 3

            if ('user_id' in form) and (form['user_id']):
                if form['user_id'] != '':
                    achk = 4
#
#--- start checking what was requested
#
            if ('check' in form) and (form['check']):
                self.read_form_param(form)
#
#--- change of the user requested
#
                if (achk == 0) and (form['check'] == 'Change'):
                    return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)
#
#--- the case to order the observations by obsid
#
                elif form['check'] == 'Regroup by Obsids':
                    if self.nstd == '2':
                        updates_list = oda.get_verified_cases()
                    else:
                        updates_list = self.extract_data_for_display()
                        self.nstd = 1
    
                    updates_list = self.reordered_by_obsid(updates_list)
#
#--- if poc is given, bubble up the poc to the top
#
                    self.poc = form['user_id']
                    if self.poc != '':
                        updates_list = self.reorder_by_poc(updates_list)
    
                elif form['check'] == 'Display 30 Days':
                    self.interval     = 30
                    updates_list = self.extract_data_for_display()
                    updates_list.reverse()
                    self.nstd = 1
    
                elif form['check'] == 'Display Verified':
                    updates_list = oda.get_verified_cases()
                    updates_list.reverse()
                    self.nstd = 2
#
#--- the case to display obsidrev under the same obsid
#
                elif achk == 1:
                    try:
                        self.disp_obsid = form['disp_obsid']
                        if self.disp_obsid == '':
                            self.disp_obsid = form['prev_obsid']
                    except:
                        self.disp_obsid = form['prev_obsid']
    
                    updates_list = self.extract_data_for_display()
#
#--- the case to display obsidrev under the sequence number
#
                elif achk == 2:
                    try:
                        self.seqno = form['seqno']
                        if self.seqno == "":
                            self.seqno = form['seqno']
                    except:
                        self.seqno = form['prev_seqno']
    
                    updates_list = self.extract_data_for_display()
                    self.nstd = 1
                    self.nstd = 1
#
#--- the case to display obsidrev under the same prop number
#
                elif achk == 3:
                    try:
                        self.prop_num = form['prop_num']
                        if self.prop_num == "":
                            self.prop_num = form['prev_prop']
                    except:
                        self.prop_num = form['prev_prop']

                    updates_list = self.extract_data_for_display()
                    self.nstd = 1
#
#--- the case to bring up the observations of poc to the top
#
                elif achk == 4:
    
                    if self.nstd == '2':
                        updates_list = oda.get_verified_cases()
                    else:
                        updates_list = self.extract_data_for_display()
                        self.nstd = 1
    
                    self.poc = form['user_id']
                    if self.poc != '':
                        updates_list = self.reorder_by_poc(updates_list)
                    self.poc = ''
#
#--- back to normal display
#
                elif form['check'] == 'Standard':
                    self.param_initialize()
    
                    updates_list = self.extract_data_for_display()
                    updates_list = bubble_up_unsigned_off_entries(updates_list)
    
                wdict =  self.mk_data_dict(updates_list  )
    
                return render_to_response(self.template_name, wdict,  RequestContext(request))
#
#--- the case that the new sign off is submitted
#
            else:
                self.read_form_param(form)
                updates_list = self.extract_data_for_display()
    
                chk = self.update_sql_entries(updates_list, form)
                if chk > 0:
                    updates_list = self.extract_data_for_display()
                    updates_list = bubble_up_unsigned_off_entries(updates_list)
                else:
                    pass
    
                wdict =  self.mk_data_dict(updates_list  )
    
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
#-- mk_data_dict: create parameter dictionay to pass the values                 ---
#----------------------------------------------------------------------------------

    def mk_data_dict(self, updates_list):
        """
        create parameter dictionay to pass the values
        input:  updates_list    --- a list of the data
                nstd            ---
                poc             --- poc to be used
                disp_obsid      --- display obsid
                prop_num        --- proposal numbers
                seq_num         --- seq number
                interval        ---
        output: wdict           --- a dictionary of the parmeters
                all of aboe plus
                    durl        --- url
                    submitter   --- sumbmitter's id
                    group       --- group id
        """

        wdict = {
            'durl'          : durl, 
            'updates_list'  : updates_list, 
            'submitter'     : self.submitter,
            'nstd'          : self.nstd, 
            'poc'           : self.poc, 
            'prev_obsid'    : self.disp_obsid, 
            'prev_prop'     : self.prop_num, 
            'prev_seqno'    : self.seqno, 
            'interval'      : self.interval,
            'group'         : self.group,
        }

        return wdict

#----------------------------------------------------------------------------------
#-- param_initialize: initialize several parameters                              --
#----------------------------------------------------------------------------------

    def param_initialize(self):
        """
        initialize several parameters
        """

        self.prop_num   = ''
        self.seqno      = ''
        self.disp_obsid = ''
        self.poc        = ''
        self.interval   = 1
        self.nstd       = 0

#----------------------------------------------------------------------------------
#-- read_form_param: read parameters from passed form                            --
#----------------------------------------------------------------------------------

    def read_form_param(self, form):
        """
        read parameters from passed form
        input:  form    --- passed form
        output: parameters: [prop_num, seqno, disp_obsid, poc, interval, nstd]
        """
        try:
            prop_num = form['prop_num']
            if prop_num == '':
                prop_num = form['prev_prop']
        except:
            prop_num = form['prev_prop']

        try:
            seqno = form['seqno']
            if seqno == '':
                seqno = form['prev_seqno']
        except:
            seqno = form['prev_seqno']

        try:
            disp_obsid = form['disp_obsid']
            if disp_obsid == '':
                disp_obsid = form['prev_obsid']
        except:
            disp_obsid = form['prev_obsid']

        try:
            poc        = form['poc']
        except:
            poc        = ''

        try:
            interval   = int(float(form['interval']))
        except:
            interval   = 1

        try:
            nstd       = form['nstd']
        except:
            nstd       = 0

        self.prop_num   = prop_num
        self.seqno      = seqno
        self.disp_obsid = disp_obsid
        self.poc        = poc
        self.interval   = interval
        self.nstd       = nstd
        self.submitter  = form['submitter']
        self.group      = form['group']

#----------------------------------------------------------------------------------
#-- extract_data_for_display: extract data which arenot verified  yet            --
#----------------------------------------------------------------------------------

    def extract_data_for_display(self):
        """
        extract data which arenot verified and those which were verified in the past "interval" days
        input: interval --- time span in day which you want to display toward the past: default=1
               obsid    --- obsid, defalut <blank> (ignored)
               prop_num --- proposal number: defalut: <blank> (ignored)
        output: alist   a list of lists of extracted data
    
                        [obsidrev, general, acis, si mode, verified, seq number, poc, date, 
                         name of gen_status, name of acis_status, name of si mode stateus, 
                         name of verified status, new comments?, large coord shift?, multi rev?, 
                         higher rev?, obsidrev (for prev), in approved list?]
        """
#
#--- selected by obsid
#
        if self.disp_obsid != '':
            alist = oda.select_data_for_obsid(self.disp_obsid)
#
#--- selected by seqno
#
        elif self.seqno != '':
            alist = oda.select_data_for_seqno(self.seqno)
#
#--- selected by prop_num
#
        elif self.prop_num != '':

            alist = self.select_data_for_prop_num(self.prop_num)
#
#--- normal cases or selected by date interval
#
        else:
            odate = ocf.find_date_of_interval_date_before(self.interval)
            alist = oda.get_data_newer_than_date(odate)
#
#--- find data which are not verified and add it if the data include only the day before
#
            if self.interval == 1:
                alist2 = oda.select_non_signed_off('verified')
                alist  = alist + alist2 
#
#--- get unique entries
#
            alist  = ocf.find_unique_entries(alist)
            alist  = self.add_extra_information(alist)

        return alist

#----------------------------------------------------------------------------------
#-- select_data_for_prop_num: return a list of lists of updates_table.list entries for a given prop_num
#----------------------------------------------------------------------------------

    def select_data_for_prop_num(self, prop_num):
        """
        return a list of lists of updates_table.list entries for a given prop_num
        input: prop_num     --- proposal number
        output:update_list  --- a list of lists of update_table entries
        """

        obsidrev_list = oda.extract_data_for_propnum(prop_num)

        update_list = []
        for obsidrev in obsidrev_list:
            alist = oda.select_data_for_obsidrev(obsidrev)
            update_list = update_list + alist


        return update_list


#----------------------------------------------------------------------------------
#-- add_extra_information: add status form names to the list                     --
#----------------------------------------------------------------------------------

    def add_extra_information(self, alist):
        """
        add status form names to the list
        input:  alist   ---- a list
        output: rlist   ---- a list with status form names
                example:    16259_002_gen, 16259_002_acis, ...
        """

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
#-- get indicators for note column
#
            notes = check_note_part(blist[0], verified)

            blist = blist + notes

            rlist.append(blist)

        return rlist


#----------------------------------------------------------------------------------
#-- reordered_by_obsid: reorder the list by obsid                                --
#----------------------------------------------------------------------------------

    def reordered_by_obsid(self, alist):
        """
        reorder the list by obsid 
        input:  alist   ---- a list
        output: rlist   ---- a list ordered by obsid and rev# in increasing order
        """

        if len(alist) == 0:
            return alist
        else:
            t_dict = {}
            olist  = []
            for ent in alist:
                obsidrev = (float(ent[0]))
                t_dict[obsidrev] = ent
                olist.append(obsidrev)
    
            olist.sort()
             

            rlist = []
            for ent in olist:
                rlist.append(t_dict[ent])
    
            return rlist
            

#----------------------------------------------------------------------------------
#-- reorder_by_poc: reorder the list by putting a specific poc's observation at the top
#----------------------------------------------------------------------------------

    def reorder_by_poc(self, alist):
        """
        reorder the list by putting a specific poc's observation at the top
        input:  alist   --- a list
                poc     --- person in charge
        output: m_list  --- modified list
        """

        m_list = []
        o_list = []
        for ent in alist:

            try:
                test = ent[6]
            except:
                test = ''

            if test == self.poc:
                m_list.append(ent)
            else:
                o_list.append(ent)
    
        m_list = m_list + o_list
         
        return m_list

#----------------------------------------------------------------------------------
#-- update_sql_entries: updated updates_table.list sql database with a newinput data 
#----------------------------------------------------------------------------------

    def update_sql_entries(self, alist, form):
        """
        updated updates_table.list sql database with a newinput data
        input:  alist   --- a list of original data
                form    --- a submitted form
        output: updated sql database
        """

        tail_list = ['gen', 'acis', 'si', 'verify']
        today     = ocf.today_date()

        vchk = 0
        for ent in alist:

            if ent[4] != 'NA':          #---- verified by indicator
                continue
            
            obsidrev = ent[0]
            poc      = ent[6]
            obsidchk = obsidrev.replace('.', '_')
#
#--- check whether higher obsidrev is already verified. if so, do quick sign off
#
            hchk = check_higher_obsidrev(obsidrev)
            name = obsidchk + '_verify'
            try:
                dval = form[name]
            except:
                dval = ''

            if (hchk > 0) and (dval == 'verify'):
                    if ent[1] == 'NA':                      #---- general
                        ent[1] = self.submitter + ' ' + today
    
                    if ent[2] == 'NA':                      #---- acis
                        ent[2] = self.submitter + ' ' + today
    
                    if ent[3] == 'NA':                      #---- si_mode
                        ent[3] = self.submitter + ' ' + today
    
                    ent[4] = self.submitter + ' ' + today   #---- verified

            else:
#
#--- if verified is requested, check whether all entries are signed off before verified it
#
                dchk = 0
                if (dval != '') and  (dval != 'NA'):
                    for m in range(1, 4):
                        if ent[m] == 'NA':
                            dchk = 1
                            break
                if dchk > 0:
                    break
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

                    if val in non_list:
                        continue 

                    else:
#
#--- if it has a value update the value
#
                        chk     = 1
                        k1      = k + 1
                        val     = self.submitter + ' ' + today
                        ent[k1] = val

                if chk > 0:
#
#--- check whether we need to send email, and if so, send out email
#
                    try:
#
#--- in some cases, an empty data table was created; so check that and
#--- if that is the case, just skip sending out email
#
                        data  = oda.extract_values_for_given_obsidrev(obsidrev)
                        otype = data.req_type
                        inst  = data.req_instrument
                        mc    = re.search('HRC', inst)
                        if mc is not None:
                            inst = 'HRC'
                        else:
                            inst = 'ACIS'
#
#--- checking whether this is a development/test case
#
                        if develop == 'yes':
                            person = self.submitter
                        else:
                            person = poc

                        cle.send_or_email(otype, k1, ent, person, obsidrev, inst=inst)
                        vchk  = 1
                    except:
                        vchk  = 0
#
#--- update sql database
#
            oda.add_to_updates_list(ent[0], ent[1], ent[2], ent[3], ent[4], ent[5], ent[6], ent[7], today)

        return vchk


###########################################################################################
###                      Non self functions                                             ###
###########################################################################################

        
#----------------------------------------------------------------------------------
#-- check_note_part: add indicators for which notes to add to the note column   ---
#----------------------------------------------------------------------------------

def check_note_part(obsidrev,verified):
    """
    add indicators for which notes to add to the note column
    input:  obsidrev    --- obsid + rev
            verified    --- whether this obsidrev is verified
    output: notes_list  --- a list of note indicator
                            [new commnets?, large coord shift?, multi entries?,
                             higher entry signed off?, obsidrev of prev, already in approved list?]
    """

    notes_list = []
#
#--- check comments and coordinate shifts
#
    notes_list = check_comments_and_shift(obsidrev, notes_list)
#
#--- check how many entries open for this obsid
#
    notes_list = check_multi_entries(obsidrev, verified,  notes_list)
#
#--- check whether this is in approved list
# 
    notes_list = check_obs_in_approved_list(obsidrev, notes_list)

    return notes_list

#----------------------------------------------------------------------------------
#-- check_comments_and_shift: generate indicators for comments changes and coordinate shift 
#----------------------------------------------------------------------------------

def check_comments_and_shift(obsidrev, notes_list):
    """
    generate indicators for comments changes and coordinate shift
    input:  obsidrev    --- obsid + revision #
            notes_list  --- a list of indicators
    output: notes_list  --- an updated list of indicators
    """
#
#--- read the data for the obsidrev from sql Updates
#
    pdict = oda.read_updates_entries_to_dictionary(obsidrev)
#
#--- check comments
#
    temp  = pdict['comments']
    org   = temp[0]
    req   = temp[1]
    org   = org.replace('\s+|\t+|\n+', '')
    req   = req.replace('\s+|\t+|\n+', '')

    if org == req:
        notes_list.append('n')
    else:
        notes_list.append('y')
#
#--- check coordinate shift (large shift: >= 8 arcmin)
# 
    diff = find_coord_diff(pdict['ra'], pdict['dec'])

    if diff >= 0.133333333:
        notes_list.append('y')
    else:
        notes_list.append('n')

    return notes_list

#----------------------------------------------------------------------------------
#-- find_coord_diff: find coordinate shift                                       --
#----------------------------------------------------------------------------------

def find_coord_diff(ras, decs):
    """
    find coordinate shift
    input:  ras     --- a list of [org ra, req ra] in degree
            decs    --- a list of [org dec, req dec] in degree
    output: diff    --- coordinate shift in degree
    """

    try:
        ora   = float(ras[0])
        nra   = float(ras[1])
    except:
        ora   = 0.0
        nra   = 0.0

    try:
        odec  = float(decs[0])
        ndec  = float(decs[1])
    except:
        odec  = 0.0
        ndec  = 0.0

    diff  = math.sqrt((ora - nra)**2 + (odec - ndec)**2)

    return diff
    
#----------------------------------------------------------------------------------
#-- check_multi_entries: generate indicators for multiple entries               ---
#----------------------------------------------------------------------------------

def check_multi_entries(obsidrev, verified, notes_list):
    """
    generate indicators for multiple entries
    input:  obsidrev    --- obsid + revision #
            verified    --- whether this obsidrev is verified
            notes_list  --- a list of indicators
    output: notes_list  --- an updated list of indicators
                            add, whether there is multiple obsidrev entries open
                                 whether a higher than this obsidrev is already signed off
                                 if so, which obsidrev (if not, give '0')
    """

    atemp      = re.split('\.', obsidrev)
    obsid      = atemp[0]
    iobsidrev  = float(obsidrev)
#
#--- extract the entries with the same obsid from sql Updates
#
    alist      = oda.select_data_for_obsid(obsid)
#
#--- check multiple entries are opened
#
    if len(alist) > 1:
        chk1 = 0
        chk2 = 0
        for ent in alist:
            comp = float(ent[0])
#
#--- check multiple entry case
#
            if ent[4] == 'NA':
                if verified == 'NA':
                    if comp != iobsidrev:
                        chk1 = 1
#
#--- check whether the higher entries are signed off
#
            else:
                if verified == 'NA':
                    if comp > iobsidrev:
                        hobsidrev = str(comp)
                        chk2 = 1
                        break

        if chk1 > 0:
           notes_list.append('y')
        else:
           notes_list.append('n')

        if chk2 > 0:
           notes_list.append('y')
           notes_list.append(hobsidrev)     #--- hobsidrev is the higher signed off obsidrev
        else:
           notes_list.append('n')
           notes_list.append('0')
    else:
        notes_list.append('n')
        notes_list.append('n')
        notes_list.append('0')

    return notes_list

#----------------------------------------------------------------------------------
#-- check_obs_in_approved_list: generate an indicator for whether the observation in approved list
#----------------------------------------------------------------------------------

def check_obs_in_approved_list(obsidrev, notes_list):
    """
    generate an indicator for whether the observation in approved list
    input:  obsidrev    --- obsid + revision #
            notes_list  --- a list of indicator
    output: notes_list  --- an updated list of indicators
    """
    atemp      = re.split('\.', obsidrev)
    obsid      = atemp[0]
#
#--- read approved list
#
    chk = oda.get_values_from_approved(obsid)

    if chk[1] != 'na':
        notes_list.append('y')
    else:
        notes_list.append('n')

    return notes_list
            

#----------------------------------------------------------------------------------
#-- check_higher_obsidrev: check whether higher revsion is already verified     ---
#----------------------------------------------------------------------------------

def check_higher_obsidrev(obsidrev):
    """
    check whether higher revsion is already verified
    input:  obsidrev    --- obsid + revision #
    output: chk         --- 1 if there is higher resiion verified. 0 otherwise
    """
    atemp      = re.split('\.', obsidrev)
    obsid      = atemp[0]
    iobsidrev  = float(obsidrev)
#
#--- extract the entries with the same obsid from sql Updates
#
    alist      = oda.select_data_for_obsid(obsid)
#
#--- higher obsidrev is already verified
#
    chk = 0
    if len(alist) > 1:
        for ent in alist:
            comp = float(ent[0])
            if comp <= iobsidrev:
                continue
            else:
                if ent[4] != 'NA':
                    chk = 1 
                    break

    return chk

#----------------------------------------------------------------------------------
#-- bubble_up_unsigned_off_entries: move non verified cases to the top of the list 
#----------------------------------------------------------------------------------

def bubble_up_unsigned_off_entries(alist):
    """
    move non verified cases to the top of the list
    input:  alist   --- a list of lists of entries
    output: alist   --- an updated list
    """

    top_list = []
    bot_list = []

    for ent in alist:
        if ent[4] == 'NA':
            top_list.append(ent)
        else:
            bot_list.append(ent)

    blist = top_list + bot_list

    return blist




