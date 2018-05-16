#########################################################################################################
#                                                                                                       #
#           OcatDataPage: django class to create Ocat Data Page                                         #
#                                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                       #
#               last update: Sep 21, 2016                                                               #
#                                                                                                       #
#########################################################################################################

import re
import sys
import unittest

from django.views.generic       import View
from django.http                import HttpRequest, HttpResponseRedirect
from django.template            import RequestContext

from django.shortcuts           import render_to_response, get_object_or_404
from django.contrib             import auth
from django.conf                import settings
from django.contrib.auth.models import User

from ocatdatapage.forms         import OcatParamForm

import utils.ocatCommonFunctions as ocf         #--- various functions are saved here
import utils.prepdatdict         as pdd         #--- create data dictionary for the page
import utils.violationCheck      as vchk        #--- functions check violation
import utils.related_obs_list    as rol         #--- find other observations under the same poc
import utils.passWordCheck       as pwchk       #--- check user/password
import utils.create_log_and_email as cle        #--- create a change log and send out eamil
import utils.ocatdatabase_access as oda         #--- accessing tools to ocat data page database

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
#--- session expiration time in seconds
#
time_exp = 3600 * 12

#----------------------------------------------------------------------------------
#-- OcatDataPage: This class starts Ocat Data Page using django                 ---
#----------------------------------------------------------------------------------

class OcatDataPage(View):
    """
    This class starts Ocat Data Page using django
    """
#
#--- parameter lists for the variable rank entries
#
    window_list   = ('window_constraint', 'tstart_month', 'tstart_date', 'tstart_year', 'tstart_time', \
                    'tstop_month', 'tstop_date', 'tstop_year', 'tstop_time')
    roll_list     = ('roll_constraint', 'roll_180', 'roll', 'roll_tolerance')
    spwindow_list = ('chip', 'start_row',  'start_column', 'height', 'width', 'lower_threshold', \
                     'pha_range', 'sample')
#
#--- there are many form of 'NONE'
#
    non_list      = (None, 'NONE', 'None', 'No', 'NO', 'N', 'NA', 'NULL', '\s+', '')
#
#--- a list of paramters which need special treatments
#
    exclude_list  = ['window_flag', 'roll_flag', 'spwindow_flag', 'tstart', 'tstop','dra', 'ddec',   \
                    'roll_constraint', 'roll', 'roll_tolerance', 'window_constraint', \
                    'chip', 'start_row', 'start_column', 'height', 'width', 'lower_threshold',  \
                    'pha_range', 'sample', 'remarks', 'comments',]
#
#--- tamplate names
#
    template_name  = 'ocatdatapage/ocatdatapage.html'
    not_found_page = 'ocatdatapage/obsid_not_found.html'

#---------------------------------------------------

    form_class     = OcatParamForm
#
#--- dictionary of parameter <---> discriptive name
#
    name_dict      = ocf.read_name_list()
#
#--- password check
#   
    pdb            = pwchk.CheckUser()
#
#--- setting up the empty dictionary
#
    dat_dict       = {}
    org_dict       = {}
#
#--- lists of non-modifiable and modifiable parameter lists; the first one will be filled 
#
    nc_param       = []
    param_list     = pdd.return_changerble_param_list()
#
#--- obsid holder
#
    obsid          = ''

#----------------------------------------------------------------------------------
#-- get: "get" submitted data and display an appropriate page                    --
#----------------------------------------------------------------------------------

    def get(self, request, *args,  **kwargs):
        """
        this passes form data from one to the next
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

        self.submitter = request.user.username

#-----------------------------------------------------
#---- normal porcess starts here                  
#-----------------------------------------------------

        if request.method == 'POST':
            form = request.POST
        else:
            form = request.GET

        if ('check' in form) and (form['check']):

            [self.org_dict, self.nc_dict, self.dat_dict] = self.update_db(form)

#-----------------------------------------------------
#--- for the case the CHANGES are SUBMITTED
#-----------------------------------------------------
          
            if form['check'] == 'Submit':

                self.submit_param_update(form)  #--- create self.wdict

                return  render_to_response(self.template_name, self.wdict, RequestContext(request)) 

#-----------------------------------------------------
#--- for the case  the submission is FINALIZED
#-----------------------------------------------------

            elif form['check'] == 'FINALIZE':
                try:
                    obsid = form['obsid']
                except:
                    obsid = self.obsid
                line = str(form) + '\n'

                self.finalize_parm_update(form, obsid)  #--- create self.wdict

                return render_to_response(self.template_name, self.wdict, RequestContext(request)) 

#-----------------------------------------------------
#--- for the case UPDATE
#-----------------------------------------------------

            else:

                self.reconstruct_original_text(form)

                form = self.form_class(initial = self.dat_dict)

                self.page_update_param(form)    #--- create self.wdict

                return render_to_response(self.template_name, self.wdict, RequestContext(request))

#-----------------------------------------------------
#--- the case that this is FIRST TIME OPENING the page 
#-----------------------------------------------------

        else:
            try:
                test  = float(args[0])
                obsid = args[0]
            except:
                try:
                    obsid = form['obsid']
                except:
                    obsid = self.obsid

            self.obsid = obsid

##            try:
#
#--- fill up the data dictionary
#
            [self.org_dict, self.nc_dict] = self.initialize_dat_dicts(self.obsid, self.submitter)
            self.dat_dict = self.org_dict
#
#--- update form entries
#
            form = self.form_class(initial = self.org_dict)

            self.page_update_param(form)

            return render_to_response(self.template_name, self.wdict, RequestContext(request))
#
#--- if the submitted obsid is not in the database, display the error page
#
##            except:
##                self.page_update_param(form)
##
##                return render_to_response(self.not_found_page, self.wdict, RequestContext(request))


#----------------------------------------------------------------------------------
#-- currently "POST" method is not used in this script                          ---
#----------------------------------------------------------------------------------

#    def post(self, request, *args, **kwargs):
#
#        return render_to_response(self.final_page, {'dbval': self.dat_dict, }, RequestContext(request))




###########################################################################################
##                other functions listing starts here                                   ###
###########################################################################################


#----------------------------------------------------------------------------------
#-- initialize_dat_dict: set the initial org_dict/dat_dict                      ---
#----------------------------------------------------------------------------------

    def initialize_dat_dicts(self, obsid, submitter, asis='norm'):
        """
        set the initial org_dict/dat_dict
        input:  obsid       --- obsid
                submitter   --- submitter
                asis        --- asis status; default: norm
                org_dict    --- a dictionary for the original values
                nc_dict     --- a dictionary of non changiable values
        """
        tmp_dict                 = pdd.prep_data_dict(obsid)
        tmp_dict['obsid']        = obsid
        tmp_dict['submitter']    = submitter
        tmp_dict['asis']         = asis 
        tmp_dict['planned_roll'] = ocf.find_planned_roll(obsid)

        org_dict = {}
        for key in tmp_dict.keys():
            org_dict[key] = tmp_dict[key]
#
#--- fill up the list of non-modifiable parameters; each element has a form of [param name, value]
#
        self.nc_param = pdd.return_non_changerble_param_list(tmp_dict)

        nc_dict = {}
        for ent in self.nc_param:
            nc_dict[ent[0]]  = str(ent[1])
            org_dict[ent[0]] = str(ent[1])

        return [org_dict, nc_dict]

#----------------------------------------------------------------------------------
#-- update_db: update data dictionary based of submitted changes               ----
#----------------------------------------------------------------------------------

    def update_db(self, form):
        """
        update data dictionary based of submitted changes
        input:  form             --- submitted parameters from GET
                dat_dict    --- the current data dictionary
        output: dat_dict    --- updated data dictionary
        """
#
#--- get db values again
#
        [org_dict, nc_dict] = self.initialize_dat_dicts(form['obsid'], self.submitter)
        dat_dict = {}
        for key in org_dict.keys():
            dat_dict[key] = org_dict[key]

        for key in form.keys():
#
#---  check the value is numeric. if so change back to float or int
#---  before saving in dat_dict
#
            nval = form[key]

            if ocf.chkNumeric(nval):
                nval = float(nval)
#
#--- check the original value is float or int
#
                try:
                    mc = re.search('\.', org_dict[key])
                    if mc is not None:
                        oval = float(org_dict[key])
                        fchk = 1
                    else:
                        fchk = 0
                except:
                    fchk = 0

                if fchk == 0:
                    test = int(nval)         #--- checking whether the value is integer
                    if nval == test:
                        nval = test
                else:
                    if oval == nval:
                        nval = oval
#
#--- if the value is in non_list (e.g., None), make sure original and submitted values
#--- take the same format
#
            try:
                oval = org_dict[key]
                if oval in self.non_list:
                    if nval in self.non_list:
                        nval = oval
            except:
                pass
#
#--- save the updated value
#
            dat_dict[key] = nval
#
#---------- special cases start here   -----------
#

#
#--- update dra and ddec (ra/dec are in HMS/DMS)
#
        [dra, ddec] = ocf.convert_ra_dec_decimal(dat_dict['ra'], dat_dict['dec'])
        dat_dict['dra']  = dra        
        dat_dict['ddec'] = ddec       
#
#--- check order flags and then set ordr to 1 if the ordr was originally 0
# 
        f_list = ['window_flag', 'roll_flag', 'spwindow_flag']
        o_list = ['time_ordr',   'roll_ordr', 'ordr']
        for i in range(0, 3):
            try:
                if form[f_list[i]] == 'Y':
                    if dat_dict[o_list[i]] == 0:
                        dat_dict[o_list[i]] = 1
            except:
                pass
#
#--- if asked increase the order from the current one, increase ordr by 1
#
        if form['check']  == "Add Another Time Constraint":
            self.add_new_ordr_list('time_ordr', 'window_constraint', self.spwindow_list)

        if form['check']  == "Add Another Roll Constraint":
            self.add_new_ordr_list('roll_ordr', 'roll_constraint',   self.roll_list)

        if form['check']  == "Add Another ACIS Window Constraint":
            self.add_new_ordr_list('ordr',      'chip',              self.spwindow_list)
#
#--- remove null rows from the ordered cases
#
        if form['check']  == "Remove Null Time Constraint":
            self.remove_null_from_ordr_list('time_ordr','window_constraint', 'window_flag', self.window_list)

        if form['check']  == "Remove Null Roll Constraint":
            self.remove_null_from_ordr_list('roll_ordr','roll_constraint',   'roll_flag', self.roll_list)

        if form['check']  == "Remove Null ACIS Window Constraint":
            self.remove_null_from_ordr_list('ordr',     'chip',          'spwindow_flag', self.spwindow_list)
#
#--- set si_mode to 'New Value Requsted', if any of the following parameters are modified
#
        for param in ['est_cnt_rate', 'forder_cnt_rate', 'raster_scan', 'grating', 'instrument', 'dither_flag']:
            try:
                oval = org_dict[param]
            except:
                oval = None
            try:
                nval = dat_dict[param]
            except:
                nval = None

            if oval != nval:
                dat_dict['si_mode'] = 'New Value Requsted'
                break

        return [org_dict, nc_dict, dat_dict]

#----------------------------------------------------------------------------------
#-- page_update_param: return dictionary of updated parameters                 ----
#----------------------------------------------------------------------------------

    def page_update_param(self, form):
        """
        return dictionary of updated parameters
        input:  form    --- form
        output: wdict   --- a dictionary of parameters
                    durl        --- url of the page
                    gen_name    --- form
                    submitter   --- submitter
                    pname       --- a dictionary of name 
                    dbval       --- a dictionary of data
                    ogval       --- a dictionary of original data
                    nc_param    --- non changable parameter list
                    permission  --- an indicator of whether the submitter is POC
        """
#
#--- find whether the submitter is POC
#
        try:
            permission = oda.is_user_in_the_group(self.submitter)
        except:
            permission = False

        self.wdict = {
            'durl'          : durl,
            'gen_name'      : form, 
            'submitter'     : self.submitter,
            'pname'         : self.name_dict, 
            'dbval'         : self.dat_dict, 
            'ogval'         : self.org_dict, 
            'nc_param'      : self.nc_param,
            'permission'    : permission,
        }

#----------------------------------------------------------------------------------
#-- submit_param_update: check submitted data and create warning etc if needed ----
#----------------------------------------------------------------------------------

    def submit_param_update(self, form):
        """
        check submitted data and create warning etc if needed
        input:  form            --- submitted form
        output: wdict           --- a dictionary of the data:
                    durl            --- a url of the page
                    gen_name        --- a form
                    submitter       --- a sumbitter
                    dbval           --- a submitted data set
                    ogval           --- a original data set
                    text_set        --- a list of lists: [pname, discriptive name]
                    submitted_dat   --- a list of the lists
                    std_warning     --- a list of starndard warning
                    cdo_warning     --- a list of cdo warning
                    spl_warning     --- a list of special warning
                    ccd_warning     --- a list of ccd check warning
                    std_chk         --- a indicator of standard warning (1:yes, 0: no)
                    cdo_chk         --- a indicator of cdo warning (1:yes, 0: no)
                    spl_chk         --- a indicator of special warning (1:yest, 0: no)

        """
#
#--- create a list of lists: each element has a form of [param name, display name, original value, updated value]
#
        [text_set, submitted_dat] = self.submission_data_set()

        std_chk = cdo_chk = spl_chk = 0
#
#--- checking whether submitted parameters are in the range
#
        std_warning   = vchk.create_normal_warning_list(self.org_dict, self.dat_dict)
        if len(std_warning) > 0:
            std_chk = '1'
#
#--- checking whether there are any changes which need CDO permissions
#
        cdo_warning   = vchk.cdo_checks(self.org_dict, self.dat_dict)
        if len(cdo_warning) > 0:
            cdo_chk = '1'
#
#--- checking more complicated warning checks, including ACIS CCD choices
#
        spl_warning   = vchk.check_special_cases(self.org_dict, self.dat_dict)
        ccd_warning   = vchk.check_ccds(self.dat_dict)
        spl_warning   = spl_warning + ccd_warning

        if len(spl_warning) > 0:
            spl_chk = '1'

        self.wdict = {
            'durl'          : durl,
            'gen_name'      : form, 
            'submitter'     : self.submitter,
            'dbval'         : self.dat_dict,
            'ogval'         : self.org_dict,
#
            'submitted'     : submitted_dat, 
            'text_set'      : text_set, 
            'std_warning'   : std_warning, 
            'std_chk'       : std_chk, 
            'cdo_warning'   : cdo_warning, 
            'cdo_chk'       : cdo_chk, 
            'spl_warning'   : spl_warning, 
            'spl_chk'       : spl_chk, 
        }


#----------------------------------------------------------------------------------
#-- finalize_parm_update: update parameters when finalization is submitted       --
#----------------------------------------------------------------------------------

    def finalize_parm_update(self, form, obsid):
        """
        update parameters when finalization is submitted
        input:  form    --- form
                obsid   --- obsid
        output: wdict           --- a dictionary of the data:
                    dual            --- a url of the page
                    gen_name        --- a form
                    submitter       --- a sumbitter
                    dbval           --- a submitted data set
                    ogval           --- a original data set
                    too_data        --- a list of too data
                    ddt_data        --- a list of ddt data
                    g30_data        --- a list of observations scheduled in the next 30 days
                    toochk          --- an indicator of too_data (1:yes, 0: no)
                    ddtchk          --- an indicator of ddt_data (1:yes, 0: no)
                    d30chk          --- an indicator of d30_data (1:yes, 0: no)
                    open_item       --- a list of observations which need signed off
        """

#
#--- extract other observations for this submitter so that s/he can see the observations after
#--- submitting the current work
#
        [too_data, ddt_data, d30_data] = rol.collect_poc_obs_list(self.submitter)
        toochk = ddtchk = d30chk = opi = 0

        if len(too_data) > 0:
            toochk = 1
        if len(ddt_data) > 0:
            ddtchk = 1
        if len(d30_data) > 0:
            d30chk = 1

        open_item = rol.check_open_sign_off_item(self.submitter)
        if len(open_item) > 0:
            opi    = 1
#
#--- create log and send out a notification email
#
        self.reconstruct_original_text(form)
        cle.create_emails_and_save_log(self.org_dict, self.dat_dict)
#
#--- if lts date is too close, send warning email
#
        [chk, lspan]  =  ocf.check_lts_date_coming(self.nc_dict['lts_lt_plan'])
        if chk:
            submitter = self.dat_dict['submitter']
            rev       = oda.set_new_rev(obsid)
            cle.send_lts_warning_email(lspan, submitter, obsid, rev)

        self.wdict = {
            'durl'          : durl,
            'gen_name'      : form, 
            'dbval'         : self.dat_dict,
            'submitter'     : self.submitter,
            'ogval'         : self.org_dict,
#
            'too_data'      : too_data, 
            'toochk'        : toochk,
            'ddt_data'      : ddt_data, 
            'ddtchk'        : ddtchk, 
            'd30_data'      : d30_data, 
            'd30chk'        : d30chk,
            'open_item'     : open_item, 
        }

#----------------------------------------------------------------------------------
#-- add_new_ordr_list: add a new empty row to the given rank-able entries       ---
#----------------------------------------------------------------------------------

    def add_new_ordr_list(self, ordr_name, const_name,  param_list):
        """
        add a new empty row to the given rank-able entries
        input:  ordr_name       --- name of ordr
                const_name      --- name of paramter which will marked with "NULL"
                                    all others are given a blank entry
                param_list      --- a list of parameters of this rank-able entry
        output: dat_dict        --- updated data dictionary
        note:   only 6 rows can be added.
        """
        if self.dat_dict[ordr_name] >= 6:
#
#--- you can have only 6 rows of data
#
            pass
        else:
            self.dat_dict[ordr_name] += 1

            ordr =  self.dat_dict[ordr_name]
    
            for name in param_list:
                pname = name + str(ordr)
#
#--- indicator parameter will be "NULL". All others are supplied an empty field
#
                if name == const_name:
                    self.dat_dict[pname] = 'NULL'
                    self.org_dict[pname] = 'NULL'
                else:
                    self.dat_dict[pname] = None
                    self.org_dict[pname] = None
    
#----------------------------------------------------------------------------------
#-- remove_null_from_ordr_list: remove all "NULL' rows from the given rank-able entries  
#----------------------------------------------------------------------------------

    def remove_null_from_ordr_list(self, ordr_name, const_name, flag,  param_list):
        """
        remove all "NULL' rows from the given rank-able entries
        input:  ordr_name       --- name of ordr
                const_name      --- name of paramter which will marked with "NULL"
                                    all others are given a blank entry
                flag            --- name of flag for this set of entries
                param_list      --- a list of parameters of this rank-able entry
        output: dat_dict        --- updated data dictionary
        """
        ordr  = int(float(self.dat_dict[ordr_name]))
        ordr1 = ordr + 1
#
#--- find which rows are marked "NULL"
#
        clist = []
        for i in range(1, ordr1):
            name = const_name + str(i)
            if self.dat_dict[name] == 'NULL':
                clist.append(i)

        clist.sort()
#
#--- remve the null row and fill the row with the values from the next row
#
        n = 0
        for j in clist:
            m = j - n
            if m == ordr:
                ordr -= 1
                break

            for k in range(m, ordr):
                k1 = k + 1
                for name in param_list:
                    name1 = name + str(k)
                    name2 = name + str(k1)

                    self.dat_dict[name1] = self.dat_dict[name2]

            ordr -= 1
            n    += 1
                
        self.dat_dict[ordr_name] = ordr
#
#--- if all rows are remved, changed the flag to "N"
#
        if ordr < 1:
            self.dat_dict[flag] = 'N'


#----------------------------------------------------------------------------------
#-- submission_data_set: create a list of list for each parameter                --
#----------------------------------------------------------------------------------

    def submission_data_set(self):
        """
        create a list of list for each parameter in the form of 
            [parameter name, display name, original value, updated value]
        input:  none, but uses self.org_dict, and self.dat_dict
        output: text_set    --- a list of lists: [pname, discriptive name]
                dat_set     --- a list of the lists
        """
#
#--- check whether remarks and comments are same, and also add text entries
#--- with "#$" in the position of " " (blank space) so that we can pass
#
        b_list = self.check_blank_in_line()     #--- b_list contains e.g. remarks_b for the version with "#$"
        text_set = []
        for ent in b_list:
            temp = [ent, self.dat_dict[ent]]
            text_set.append(temp)
#
#--- check all other submitted parameter changes
#
        dat_set = []
#
#--- check only modifiable parameters
#
        param_list = [item for item in self.param_list if item[0]  not in self.exclude_list]

        for ent in param_list:
#
#--- oval is the original parameter value
#
            try:
                oval = self.org_dict[ent[0]]
            except:
                oval = ''
#
#--- nval is the submitted parameter value
#
            try:
#
#--- give special treatment for dither parameters
#
                if ent[0] in ('y_amp', 'y_freq', 'y_phase', 'z_amp', 'z_freq', 'z_phase',):
                    if self.dat_dict['dither_flag'] == 'N':
                        nval = None
                    else:
                        if ent[0] in ('y_phase', 'z_phase'):
                            nval = self.dat_dict[ent[0]]
                        else:
                            nval = self.modify_dither_val(self.dat_dict, ent[0])
                else:
#
#--- all other cases
#
                    nval = self.dat_dict[ent[0]]
            except:
                nval = ''
#
#--- if the value is in non_list (e.g., None), make sure original and submitted values
#--- take the same format
#
            if oval in self.non_list:
                if nval in self.non_list:
                    nval = oval
#
#--- if the value is numeric, make sure that both original and new take same format
#--- e.g. int or float
#
            nval = ocf.check_numeric_float_or_int(oval, nval)
                
            oval = str(oval).strip()
            nval = str(nval).strip()
#
#--- checking whether ra and/or dec was updated in degree format' if so, display dra/ddec
#
            if ent[0]  == 'ra':
                pset = self.ra_dec_pset(nval, 'ra')
            if ent[0]  == 'dec':
                pset = self.ra_dec_pset(nval, 'dec')
#
#--- save the result in [param name, display name, original value, submitted value]
#
            else:
                pset = [ent[0], ent[1], oval, nval]

            dat_set.append(pset)
#
#--- if the paramter is one of the ordr cases, do farther parameter value checks
#
            if ent[0] == 'time_ordr':
                dat_set = self.adjust_time_ordr(self.dat_dict, dat_set)

            elif ent[0] == 'roll_ordr':
                dat_set = self.adjust_roll_ordr(self.dat_dict, dat_set)

            elif ent[0] == 'ordr':
                dat_set = self.adjust_spwindow_ordr(self.dat_dict, dat_set)
#
#--- aim point chip coordinates  update
#
        [chipx, chipy] = ocf.find_aiming_point(self.dat_dict['instrument'], self.dat_dict['y_det_offset'], self.dat_dict['z_det_offset'])
        pset = ['chipx', 'Chipx', self.dat_dict['chipx'], chipx]
        dat_set.append(pset)
        pset = ['chipy', 'Chipy', self.dat_dict['chipy'], chipy]
        dat_set.append(pset)

        return [text_set, dat_set]

#----------------------------------------------------------------------------------
#-- modify_dither_val: change the dither values from arcsec to degree            --
#----------------------------------------------------------------------------------

    def modify_dither_val(self, form,  pname):
        """
        change the dither values from arcsec to degree
        input:  form    --- form "dictionary"
                pname   --- parameter name
        output: val     --- modified value (in degree)
        """
        dname = pname + '_asec'
        try:
            val   = float(form[dname]) / 3600.0
#
#--- try to match with floating point with the original one. usually 6 digits.
#
            try:
                oval  = str(self.org_dict[pname])
                try:
                    test = float(oval)
                    if test == 0.0:
                        fpos = 6
                    else:
                        atemp = re.split('\.', oval)
                        fpos  = len(atemp[1])
                except:
                    fpos = 6
            except:
                fpos  = 6

            val = round(val, fpos)
        except:
            val = ''

        return val


#----------------------------------------------------------------------------------
#-- ra_dec_pset: check the input format of ra/dec and create pset                --
#----------------------------------------------------------------------------------

    def ra_dec_pset(self, nval,  ind):
        """
        check the input format of ra/dec and create pset
        input:  nval --- input value
                ind  --- indicator of 'ra' or 'dec'
        output: pset --- [pname, dname, original val, current val]
        """
        mc   = re.search(':', nval)
        mc2  = re.search(' ', nval)

        if (mc is None) and (mc2 is None):
#
#--- for the case, ra/dec is submitted in degree
#
            nval = nval.replace(',', '.')
            try:
                nval = float(nval)
            except:
                pass
            if ind == 'ra':
                oval = self.org_dict['dra']
                pset = ['dra', 'RA', oval, nval]
            elif ind == 'dec':
                oval   = self.org_dict['ddec']
                pset = ['ddec', 'DEC', oval, nval]
        else:
#
#--- for the case, ra/dec is submitted in HMS/DMS
#
            oval = self.org_dict[ind]

            if ind == 'ra':
                pset = ['ra','RA', oval, nval]
            else:
                mc3 = re.search('\-', str(nval))
                mc4 = re.search('\+', str(nval))

                if (mc3 is None) and (mc4 is None):
                    nval = '\+' + nval

                pset = ['dec', 'DEC', oval, nval]

        return pset

#----------------------------------------------------------------------------------
#-- adjust_roll_ordr: update/adjust acis roll constraint parameters             ---
#----------------------------------------------------------------------------------

    def adjust_roll_ordr(self, form, dat_set):
        """
        update/adjust acis roll constraint parameters
        input:  form    --- passed form dictionary   
                dat_set --- a list of data set
        output: dat_set --- modified dat_set
        """
        plist = self.roll_list
#
#--- find the original order
#
        try:
            test = float(self.org_dict['roll_ordr'])
            oval = int(test)
        except:
            oval = 0
#
#--- find the current order
#
        try:
            test = float(form['roll_ordr'])
            ival = int(test)
        except:
            ival = 0

#
#--- counting all current order
#
        if ival > 0:
            start = 1
            end   = ival + 1
            dat_set = self.add_order_pset_to_dat_set(start, end, dat_set, form, plist)
#
#--- for the case the updated version contain less constraints than the original
#
        if oval > ival:
            start = ival + 1
            end   = oval + 1
            dat_set = self.add_order_pset_to_dat_set(start, end, dat_set, form, plist)

        return dat_set


#----------------------------------------------------------------------------------
#-- adjust_spwindow_ordr: update/adjust acis window constraint parameters       ---
#----------------------------------------------------------------------------------

    def adjust_spwindow_ordr(self, form, dat_set):
        """
        update/adjust acis window constraint parameters
        input:  form    --- passed form dictionary   
                dat_set --- a list of data set
        output: dat_set --- modified dat_set
        """

        plist = self.spwindow_list
#
#--- find the original order
#
        try:
            test = float(self.org_dict['ordr'])
            oval = int(test)
        except:
            oval = 0
#
#--- find the current order
#
        try:
            test = float(form['ordr'])
            ival = int(test)
        except:
            ival = 0

#
#--- counting all current order
#
        if ival > 0:
            start = 1
            end   = ival + 1
            dat_set = self.add_order_pset_to_dat_set(start, end, dat_set, form, plist)
#
#--- for the case the updated version contain less constraints than the original
#
        if oval > ival:
            start = ival + 1
            end   = oval + 1
            dat_set = self.add_order_pset_to_dat_set(start, end, dat_set, form, plist)

        return dat_set

#----------------------------------------------------------------------------------
#-- add_order_part_to_dat_set: make pset and add to dat_set for ordered cases    --
#----------------------------------------------------------------------------------

    def add_order_pset_to_dat_set(self, start, end, dat_set, dat_dict, plist):
        """
        make pset and add to dat_set for ordered cases
        input:  start   --- starting value of the ordered rank
                end     --- ending value of the ordered rank
                dat_set --- dataset to which pset is added
                dat_dict--- current data_dict (actually form)
                plist   --- parameter list
        outpu:  dat_set --- udated dat_set
                note pset is in the form of [param name, discriptive name, orig value, updated value]
                if either orig value or updated value is not defined, None will be given
        """
        
        for i in range(start, end):
            for name in plist:
#
#--- tstart and tstop need a special treatment
#
                if name in ['tstart', 'tstop']:
                    pset = self.make_time_pset(name, i, dat_dict)
                    dat_set.append(pset)
                else:
#
#--- all other ordered cases
#
                    dname = name.capitalize()       #--- dname is descriptive name 
                    mc = re.search('_', name)
                    if mc is not None:
                        atemp = re.split('_', name)
                        dname = ''
                        for ent in atemp:
                            try:
                                dname = dname + ent.capitalize() + ' '
                            except:
                                dname = dname + ent + ' '
                    dname = dname + str(i)
                    oname = name  + str(i) 
                    try:
                        oval = self.org_dict[oname]
                    except:
                        oval = None
    
                    try:
                        nval = dat_dict[oname]
                    except:
                        nval = None
#
#--- if the old value is int, make sure the new one is int, too. float case is the same.
#        
                    if oval != None and nval != None:
                        try:
                            nval = ocf.check_numeric_float_or_int(oval, nval)
                            nval = str(nval)
                            oval = str(oval)
                        except:
                            pass

                    pset = [oname, dname, oval, nval]
                    dat_set.append(pset)

        return dat_set


#----------------------------------------------------------------------------------
#-- adjust_time_ordr: update/adjust acis time constraint parameters             ---
#----------------------------------------------------------------------------------

    def adjust_time_ordr(self, form, dat_set):
        """
        update/adjust acis time constraint parameters
        input:  form    --- passed formdictionary   
                dat_set --- a list of data set
        output: dat_set --- modified dat_set
                tstart/tstop are save as a single entry not as year, month, date, time separately
                in the database
        """
        plist = ('window_constraint', 'tstart', 'tstop')
#
#--- find the original order
#
        try:
            test = float(self.org_dict['time_ordr'])
            oval = int(test)
        except:
            oval = 0
#
#--- find the current order
#
        try:
            test = float(form['time_ordr'])
            ival = int(test)
        except:
            ival = 0

#
#--- counting all current order
#
        if ival > 0:
            start = 1
            end   = ival + 1
            dat_set = self.add_order_pset_to_dat_set(start, end, dat_set, form, plist)
#
#--- for the case the updated version contain less constraints than the original
#
        if oval > ival:
            start = ival + 1
            end   = oval + 1
            dat_set = self.add_order_pset_to_dat_set(start, end, dat_set, form, plist)

        return dat_set

#----------------------------------------------------------------------------------
#-- make_time_pset: combine month, date, year, and time entries into one       ----
#----------------------------------------------------------------------------------

    def make_time_pset(self, name, i, form):
        """
        combine month, date, year, and time entries into one (either tstart or tstop)
        and create pset of [param name, display name, original value, updated value]
        input:  name    --- either start or tstop
                i       --- order of the entry
                form    --- form dictionary
        output: pset    --- a list of the results
        """

        out  = ocf.convert_back_time_form(name, i, self.org_dict, form)

        pset = [out[0], out[0].capitalize(), out[1], out[2]]
#
#--- saving in data dictionary
#
        self.dat_dict[out[0]] = out[2]
        temp = " ".join(out[2].split('#$'))
        name = out[0] + '_b'
        self.dat_dict[name] = out[2]

        return pset

#----------------------------------------------------------------------------------
#-- check_blank_in_line:check whether original and updated entries are same     ---
#----------------------------------------------------------------------------------

    def check_blank_in_line(self):
        """
        call check_text_comp  to check whethere there is any  " " in the line.
        and updated entries are same and also replace " " with "#$"
        so that foram can transfer them without losing a part of the sentences.
        """

        self.check_text_comp('remarks')
        self.check_text_comp('comments')
        b_list = ['remarks_b', 'comments_b']

        try:
            order = self.dat_dict['time_ordr']
            if order > 0:
                for i in range(0, order):
                    k = i + 1
                    for pname in ['tstart', 'tstop']:
                        pname_n = pname + str(k)
                        self.check_text_comp(pname_n)
                        b_list.append(pname_n)
        except:
            pass

        return b_list
                    
#----------------------------------------------------------------------------------
#-- check_text_comp: replace " " with "#$" and send "backup" one                 --
#----------------------------------------------------------------------------------

    def check_text_comp(self, pname):
        """
        since form cannot pass sentences well, replace " " with "#$" and
        send "backup" one.
        input:  pname   --- parameter name of the value
        output: pname2  --- parameter name of hte "backup" value: pname + "_b"
                dat_dict[pname2] --- the value (sentences) with "#$"
        """
        try:
            org_pname = self.org_dict[pname].strip()
        except:
            org_pname = ''
            self.org_dict[pname] = ''

        try:
            dat_pname = self.dat_dict[pname].strip()
        except:
            dat_pname = ''
            self.dat_dict[pname] = ''
#
#--- first make a version of all " " removed for a test
#
        if ocf.null_value(org_pname):
            org_test = ''
        else:
            org_test = "".join(org_pname.split())

        if ocf.null_value(dat_pname):
            dat_test = ''
        else:
            dat_test = "".join(dat_pname.split())
#
#--- make a backup with "#$"
#
        backup   = "#$".join(dat_pname.split())
#
#--- test whether the original and the updated sentences are same without " " 
#
        if org_test == dat_test:
            self.dat_dict[pname] = org_pname
            if ocf.null_value(org_pname):
                backup = org_pname
            else:
                backup = "#$".join(org_pname.split())
#
#--- save the backup data with a sufix of "_b"
#
        pname2 = pname + '_b'
        self.dat_dict[pname2] = backup

#----------------------------------------------------------------------------------
#-- reconstruct_original_text: replace "#$" to " " in the text                  ---
#----------------------------------------------------------------------------------

    def reconstruct_original_text(self, form):
        """
        replace "#$" to " " so that a text will have the original " ".
        original form
        input:  form            --- submitted form "dictionary"
        output: sef.dat_dict    --- updated dat_dictionary
        """
#
#--- the remarks/comments with the '#$' are kept in remarks_b/comments_b
#
        if ('remarks_b' in form) and (form['remarks_b']):
            self.dat_dict['remarks'] = ocf.put_back_blank_in_line(form['remarks_b'])

        if ('comments_b' in form) and (form['comments_b']):
            self.dat_dict['comments'] = ocf.put_back_blank_in_line(form['comments_b'])
#
#--- tstart and tstop also have "spaces"
#
        order = self.dat_dict['time_ordr']
        if order > 0:
            for i in range(0, order):
                k = i + 1
                for name in ['tstart', 'tstop']:
                    pname  = name + str(k)
                    pname2 = pname + '_b'
                    
                    try:
                        self.dat_dict[pname] = ocf.put_back_blank_in_line(self.dat_dict[pname2])
                    except:
                        pass


#----------------------------------------------------------------------------------
