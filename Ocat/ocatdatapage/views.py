#########################################################################################################
#                                                                                                       #
#           OcatDataPage: django class to create Ocat Data Page                                         #
#                                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                       #
#               last update: Jan 06, 2017                                                               #
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
from django.contrib.auth.views  import password_change

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

#-----------------------------------------------------
#---- normal porcess starts here                  
#-----------------------------------------------------

        if request.method == 'POST':
            form = request.POST
        else:
            form = request.GET

        if ('check' in form) and (form['check']):
            pass
#-----------------------------------------------------
#--- the case that this is FIRST TIME OPENING the page 
#-----------------------------------------------------

        else:
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
#
#--- ocat page starts
#
            try:
                test  = float(args[0])
                obsid = args[0]
            except:
                try:
                    obsid = form['obsid']
                except:
                    obsid = self.obsid

            self.obsid = obsid

            try:
#
#--- fill up the data dictionary
#
                self.initialize_dat_dicts(self.obsid, self.submitter)
#
#--- update form entries
#
                form = self.form_class(initial = self.dat_dict)

                self.page_update_param(form)

                return render_to_response(self.template_name, self.wdict,  RequestContext(request))
#
#--- if the submitted obsid is not in the database, display the error page
#
            except:
                self.wdict = {
                    'durl'          : durl,
                    'gen_name'      : form, 
                    'submitter'     : self.submitter,
                }

                return render_to_response(self.not_found_page, self.wdict, RequestContext(request))


#----------------------------------------------------------------------------------
#-- posting data: sending around data                                           ---
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
#-----------------------------------------------------
#-----------------------------------------------------

        if request.method == 'POST':
            form = request.POST
        else:
            form = request.GET

#-----------------------------------------------------
#-----------------------------------------------------
#-----------------------------------------------------

        if ('changepass' in form) and (form['changepass']):
            
            return HttpResponseRedirect('/accounts/password_change_form')

        if ('cancel' in form) and (form['cancel']):
            pass
        elif ('passupdate' in form) and (form['passupdate']):
            try:
                npassword = form['npassword']
                cpassword = form['cpassword']
                if npassword == cpassword:
                    user = User.objects.get(username=self.submitter)
                    user.set_password(npassword)
                    user.save()
                else:
                    return HttpResponseRedirect('/accounts/password_change_form')
            except:

                return HttpResponseRedirect('/accounts/password_change_form')
            
#-----------------------------------------------------
#--- asking to open a new ocat data page with a different obsid
#-----------------------------------------------------

        if('tcheck' in form) and (form['tcheck']) and form['tcheck'] == 'Start':

                obsid = form['tobsid']
                html  = durl + '/ocatdatapage/' + str(obsid) + '/'
                return HttpResponseRedirect(html)

#-----------------------------------------------------
#---- normal porcess starts here                  
#-----------------------------------------------------

        elif ('check' in form) and (form['check']):

            self.update_db(form)

#-----------------------------------------------------
#--- for the case the CHANGES are SUBMITTED
#-----------------------------------------------------
          
            if form['check'] == 'Submit':

                self.reconstruct_original_text(form)
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
#
#--- pass the asis condition
#
                asis = form['asis']

                self.finalize_parm_update(form, obsid)  #--- create self.wdict

                return render_to_response(self.template_name, self.wdict, RequestContext(request)) 

#-----------------------------------------------------
#--- for the case UPDATE
#-----------------------------------------------------

            else:
                self.reconstruct_original_text(form, achk= 'all')
                form = self.form_class(initial = self.dat_dict)

                self.page_update_param(form)    #--- create self.wdict

                return render_to_response(self.template_name, self.wdict, RequestContext(request))


###########################################################################################
##                other functions listing starts here                                   ###
###########################################################################################


#----------------------------------------------------------------------------------
#-- initialize_dat_dict: set the initial dat_dict                               ---
#----------------------------------------------------------------------------------

    def initialize_dat_dicts(self, obsid, submitter, asis='norm'):
        """
        set the initial dat_dict
        input:  obsid       --- obsid
                submitter   --- submitter
                asis        --- asis status; default: norm
                dat_dict    --- a dictionary for the current values (self)
        """
        tmp_dict                 = pdd.prep_data_dict(obsid)
        tmp_dict['obsid']        = obsid
        tmp_dict['submitter']    = submitter
        tmp_dict['asis']         = asis 
        tmp_dict['planned_roll'] = ocf.find_planned_roll(obsid)

        for key in tmp_dict.keys():
            okey = 'org_' + key

            mc1 = re.search('start_date', key)
            mc2 = re.search('stop_date',  key)

            if (mc1 is not None) or (mc2 is not None):
                cnval = self.convert_day_format(key, tmp_dict)
                self.dat_dict[key]  = cnval
                self.dat_dict[okey] = cnval
            else:
                self.dat_dict[key]  = tmp_dict[key]
                self.dat_dict[okey] = tmp_dict[key]
#
#--- fill up the list of non-modifiable parameters; each element has a form of [param name, value]
#
        self.nc_param = pdd.return_non_changerble_param_list(tmp_dict)

        self.nc_dict = {}
        for ent in self.nc_param:
            self.nc_dict[ent[0]]  = str(ent[1])
            self.dat_dict[ent[0]] = str(ent[1])
#
#--- convert sentences with non-spaced versions
#
        self.check_blank_in_line()

#----------------------------------------------------------------------------------
#-- convert_day_format: convert single digit date format to tw digit one        ---
#----------------------------------------------------------------------------------

    def convert_day_format(self, key, tdict):
        """
        convert single digit date format to tw digit one 
        input:  key     --- dictionay key
                tdict   --- dictionary
        output: cnval   --- date format in "01"
        """

        try:
            nval = int(float(tdict[key]))
        except:
            nval = 1

        cnval = str(nval)
        if nval < 10:
            cnval = '0' + cnval

        return cnval

#----------------------------------------------------------------------------------
#-- update_db: update data dictionary based of submitted changes               ----
#----------------------------------------------------------------------------------

    def update_db(self, form):
        """
        update data dictionary based of submitted changes
        input:  form             --- submitted parameters from GET
                self.dat_dict    --- the current data dictionary
        output: self.dat_dict    --- updated data dictionary
        """

        self.dat_dict = {}
        self.dat_dict['obsid']         = form['obsid']
        self.dat_dict['submitter']     = form['submitter']
        self.dat_dict['asis']          = form['asis']
        self.dat_dict['planned_roll']  = form['planned_roll']
        self.dat_dict['hrc_si_select'] = form['hrc_si_select']

        self.nc_dict  = {}
        for key in form.keys():
            if key.startswith('org_'):
                self.dat_dict[key] = form[key]
                continue
            if key.startswith('nc_'):
                nkey = key.replace('nc_','')
                self.nc_dict[nkey]  = form[key]
                self.dat_dict[nkey] = form[key]
                continue
            if key in ['ra', 'dra', 'dec', 'ddec']:
                continue
#
#---  check the value is numeric. if so change back to float or int
#---  before saving in dat_dict
#
            nval = form[key]
            okey = 'org_' + key

            try:
                oval = form[okey]
            except:
                oval = ''

            if ocf.chkNumeric(nval):
                nval = float(nval)
#
#--- check the original value is float or int
#
                try:
                    mc = re.search('\.', oval)
                    if mc is not None:
                        oval = float(oval)
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
                if oval in self.non_list:
                    if nval in self.non_list:
                        nval = oval
            except:
                pass
#
#--- tstart and tstop date format modification (it takes "01" format)
#
            mc1 = re.search('start_date', key)
            mc2 = re.search('stop_date',  key)
            if (mc1 is not None) or (mc2 is not None):
                try:
                    nval = int(float(nval))
                except:
                    nval = 1
                try:
                    oval = int(float(oval))
                except:
                    oval = 1

                cnval = str(nval)
                coval = str(oval)
                if nval < 10:
                    cnval = '0' + cnval
                if oval < 10:
                    coval = '0' + coval

                nval = cnval
                oval = coval

#--- save the updated value
#
            self.dat_dict[key]  = nval
            self.dat_dict[okey] = oval
#
#---------- special cases start here   -----------
#
        [chipx, chipy] = ocf.find_aiming_point(self.dat_dict['instrument'], self.dat_dict['y_det_offset'], self.dat_dict['z_det_offset'])
        self.dat_dict['chipx']  = chipx      
        self.dat_dict['chipy']  = chipy      
#
#--- update dra and ddec (ra/dec are in HMS/DMS or in degree)
#
        rchk = 0
        dchk = 0

        try:
            self.dat_dict['ra'] = form['ra']
        except:
            rchk = 1
            self.dat_dict['ra'] = ocf.convert_ra_hms(form['dra'])

        try:
            self.dat_dict['dec'] = form['dec']
        except:
            dchk = 1
            self.dat_dict['dec'] = ocf.convert_dec_hms(form['ddec'])

        try:
            self.dat_dict['dra'] = form['dra']
        except:
            self.dat_dict['dra'] = ocf.convert_ra_to_decimal(self.dat_dict['ra'])

        try:
            self.dat_dict['ddec'] = form['ddec']
        except:
            self.dat_dict['ddec'] = ocf.convert_ra_to_decimal(self.dat_dict['dec'])


        if self.dat_dict['ra'] != self.dat_dict['org_ra']:
            if rchk == 0:
                mc = re.search(':',  form['ra'])
                if mc is not None:
                    self.dat_dict['dra'] = ocf.convert_ra_to_decimal(self.dat_dict['ra'])
                else:
                    self.dat_dict['dra'] =  self.dat_dict['ra']

        if self.dat_dict['dec'] != self.dat_dict['org_dec']:
            if dchk == 0:
                mc = re.search(':',  self.dat_dict['dec'])
                if mc is not None:
                    self.dat_dict['ddec'] = ocf.convert_dec_to_decimal(self.dat_dict['dec'])
                else:
                    self.dat_dict['ddec'] = self.dat_dict['dec']
#
#--- check order flags and then set ordr to 1 if the ordr was originally 0
# 
        f_list = ['window_flag', 'roll_flag', 'spwindow_flag']
        o_list = ['time_ordr',   'roll_ordr', 'ordr']
        for i in range(0, 3):
            try:
                if form[f_list[i]] == 'Y':
                    if self.dat_dict[o_list[i]] == 0:
                        self.dat_dict[o_list[i]] = 1
            except:
                pass
#
#--- monitor_list update
#
        try:
            mout = form['monitor_list_b']
            monitor_list = re.split('\#\$', mout)
            self.dat_dict['monitor_list'] = monitor_list
        except:
            self.dat_dict['monitor_list'] = ''
        
#
#--- if asked increase the order from the current one, increase ordr by 1
#
        if form['check']  == "Add Another Time Constraint":
            self.add_new_ordr_list('time_ordr', 'window_constraint', self.window_list)

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
                oparam = 'org_' + param
                oval = self.dat_dict[oparam]
            except:
                oval = None
            try:
                nval = self.dat_dict[param]
            except:
                nval = None

            if (oval in self.non_list) and (nval in self.non_list):
                nval = oval

            if oval != nval:
                self.dat_dict['si_mode'] = 'New Value Requsted'
                break

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
                    org_keys    --- a list of lists [<pname>, <value>] of parameters which
                                    are not explicitly passed
                    nccval      --- a dictionary of non modifiable data 
                    nc_param    --- non changable parameter list
                    permission  --- an indicator of whether the submitter is POC
        """
#
#--- find whether the submitter is POC
#
        try:
            submitter = self.dat_dict['submitter']
        except:
            submitter = self.submitter
        try:
            permission = oda.is_user_in_the_group(submitter)
        except:
            permission = False
#
#--- if the observation is done or canceled, you cannot submit data anymore
#
        if self.dat_dict['status'] in ['observed', 'archived', 'canceled', 'discarded']:
            permission = 'noedit'
#
#--- form cannot pass data with blank space; so create none spaced version and also recover
#--- the original form
#
        self.check_blank_in_line()

        org_keys = self.extra_pass_dict()

        self.wdict = {
            'durl'          : durl,
            'gen_name'      : form, 
            'submitter'     : submitter,
            'pname'         : self.name_dict, 
            'dbval'         : self.dat_dict, 
            'org_keys'      : org_keys,
            'ncval'         : self.nc_dict, 
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
                    org_keys        --- a list of lists [<pname>, <value>] of parameters which
                                        are not explicitly passed
                    nccval          --- a dictionary of non modifiable data 
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
        std_warning   = vchk.create_normal_warning_list(self.dat_dict)
        if len(std_warning) > 0:
            std_chk = '1'
#
#--- checking whether there are any changes which need CDO permissions
#
        cdo_warning   = vchk.cdo_checks(self.dat_dict)
        if len(cdo_warning) > 0:
            cdo_chk = '1'
#
#--- checking more complicated warning checks, including ACIS CCD choices
#
        spl_warning   = vchk.check_special_cases(self.dat_dict)
        ccd_warning   = vchk.check_ccds(self.dat_dict)
        spl_warning   = spl_warning + ccd_warning

        if len(spl_warning) > 0:
            spl_chk = '1'
#
#--- create a list of lists [<p name>,<val>] to pass the parameter values which are not
#--- explicitly passed
#
        org_keys = self.extra_pass_dict()

        self.check_blank_in_line()
    
        self.wdict = {
            'durl'          : durl,
            'gen_name'      : form, 
            'submitter'     : self.dat_dict['submitter'],
            'dbval'         : self.dat_dict,
            'ncval'         : self.nc_dict, 
            'org_keys'      : org_keys,
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
                    org_keys        --- a list of lists [<pname>, <value>] of parameters which
                                        are not explicitly passed
                    too_data        --- a list of too data
                    ddt_data        --- a list of ddt data
                    g30_data        --- a list of observations scheduled in the next 30 days
                    toochk          --- an indicator of too_data (1:yes, 0: no)
                    ddtchk          --- an indicator of ddt_data (1:yes, 0: no)
                    d30chk          --- an indicator of d30_data (1:yes, 0: no)
                    open_item       --- a list of observations which need signed off
        """

        submitter = form['submitter']

#
#--- extract other observations for this submitter so that s/he can see the observations after
#--- submitting the current work
#
        [too_data, ddt_data, d30_data] = rol.collect_poc_obs_list(submitter)
        toochk = ddtchk = d30chk = opi = 0

        if len(too_data) > 0:
            toochk = 1
        if len(ddt_data) > 0:
            ddtchk = 1
        if len(d30_data) > 0:
            d30chk = 1

        open_item = rol.check_open_sign_off_item(submitter)
        if len(open_item) > 0:
            opi    = 1
#
#--- create log and send out a notification email
#
        self.reconstruct_original_text(form, achk='all')
#
#--- ra and dec need in degree format
#
        self.dat_dict['org_ra']  =  self.dat_dict['org_dra']
        self.dat_dict['org_dec'] =  self.dat_dict['org_ddec']
        self.dat_dict['ra']      =  ocf.convert_ra_to_decimal(self.dat_dict['ra'])
        self.dat_dict['dec']     =  ocf.convert_dec_to_decimal(self.dat_dict['dec'])
#
#--- if lts date is too close, send warning email
#
        try:
            lts_time = self.dat_dict['lts_lt_plan_b']
            lts_time = lts_time.replace('#$', ' ')
        except:
            lts_time = ''

        [chk, lspan] =  ocf.check_lts_date_coming(lts_time)
        if chk:
            #submitter = self.dat_dict['submitter']
            rev       = oda.set_new_rev(obsid)
            cle.send_lts_warning_email(lspan, submitter, obsid, rev)
#
#--- if lts notice is set out, don't set out or notification
#
        self.dat_dict['or_notice'] = 'no'
#
#--- send out all other emails and then update the database
#
        cle.create_emails_and_save_log(self.dat_dict)


        org_keys = self.extra_pass_dict()
        lrev     = oda.find_the_last_rev(obsid)

        self.wdict = {
            'durl'          : durl,
            'gen_name'      : form, 
            'dbval'         : self.dat_dict,
            'submitter'     : submitter,
            'org_keys'      : org_keys,
            'rev'           : lrev,
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
                oname = 'org_' + pname
                mc1   = re.search('tstart', pname)
                mc2   = re.search('tstop',  pname)

#
#--- indicator parameter will be "NULL". All others are supplied an empty field
#
                if name == const_name:
                    self.dat_dict[pname] = 'NULL'
                    self.dat_dict[oname] = 'NULL'
                elif (mc1 is not None) or (mc2 is not None):
                    self.dat_dict[pname] = ''
                    self.dat_dict[oname] = ''
                else:
                    self.dat_dict[pname] = None
                    self.dat_dict[oname] = None
    
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
        output: dat_dict        --- updated data dictionary (self)
        """
        ordr  = int(float(self.dat_dict[ordr_name]))
        ordr1 = ordr + 1
#
#--- find which rows are marked "NULL"
#
        clist = []
        for i in range(1, ordr1):
            name = const_name + str(i)
            if self.dat_dict[name] in self.non_list:
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
        input:  dat_dict    --- a data dictionary (self)
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
            okey = 'org_' + ent[0]
#
#--- oval is the original parameter value
#
            try:
                oval = self.dat_dict[okey]
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
            elif ent[0]  == 'dec':
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
                oval  = str(self.dat_dict[pname])
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
        mc1  = re.search(';', nval)
        mc2  = re.search(' ', nval)

        if (mc is None) and (mc1 is None) and (mc2 is None):
#
#--- for the case, ra/dec is submitted in degree
#
            nval = nval.replace(',', '.')
            try:
                nval = float(nval)
            except:
                pass
            if ind == 'ra':
                self.dat_dict['dra'] = nval
                self.dat_dict['ra'] = ocf.convert_ra_hms(nval)
                oval = self.dat_dict['org_dra']
                pset = ['dra', 'RA', oval, nval]
            elif ind == 'dec':
                self.dat_dict['ddec'] = nval
                self.dat_dict['dec'] = ocf.convert_ra_hms(nval)
                oval = self.dat_dict['org_ddec']
                pset = ['ddec', 'DEC', oval, nval]
        else:
#
#--- for the case, ra/dec is submitted in HMS/DMS
#
            oind = 'org_d' + ind                     #------(ind : ra or dec)
            oval = str(self.dat_dict[oind])

            if ind == 'ra':
                self.dat_dict['ra'] = nval
                nval = str(round(float(ocf.convert_ra_to_decimal(nval)), 6))
                self.dat_dict['dra'] = nval
                pset = ['dra','RA', oval, nval]
            else:
                self.dat_dict['dec'] = nval
                nval = str(round(float(ocf.convert_dec_to_decimal(nval)), 6))
                self.dat_dict['ddec'] = nval
                pset = ['ddec', 'DEC', oval, nval]

        return pset


#----------------------------------------------------------------------------------
#-- ra_dec_pset: check the input format of ra/dec and create pset                --
#----------------------------------------------------------------------------------

    def ra_dec_pset_org(self, nval,  ind):
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
                oval = self.dat_dict['org_dra']
                pset = ['dra', 'RA', oval, nval]
            elif ind == 'dec':
                oval   = self.dat_dict['org_ddec']
                pset = ['ddec', 'DEC', oval, nval]
        else:
#
#--- for the case, ra/dec is submitted in HMS/DMS
#
            oind = 'org_' + ind                     #------(ind : ra or dec)
            oval = self.dat_dict[oind]

            if ind == 'ra':
                pset = ['ra','RA', oval, nval]
            else:
                mc3 = re.search('\-', str(nval))
                mc4 = re.search('\+', str(nval))

                #if (mc3 is None) and (mc4 is None):
                #    nval = '+' + nval

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
            test = float(self.dat_dict['org_roll_ordr'])
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
            test = float(self.dat_dict['org_ordr'])
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
#-- add_order_pset_to_dat_set: make pset and add to dat_set for ordered cases    --
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
                    sname = name  + str(i) 
                    oname = 'org_' + name  + str(i) 
                    try:
                        oval = self.dat_dict[oname]
                    except:
                        oval = None
    
                    try:
                        nval = dat_dict[sname]
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

                    pset = [sname, dname, oval, nval]
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
            test = float(self.dat_dict['org_time_ordr'])
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

        out  = ocf.convert_back_time_form(name, i, form)
        pset = [out[0], out[0].capitalize(), out[1], out[2]]
#
#--- saving in data dictionary
#
        self.dat_dict[out[0]] = out[2]
        #temp = " ".join(out[2].split('#$'))
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
        self.check_text_comp('title')
        self.check_text_comp('targname')
        self.check_text_comp('soe_st_sched_date')
        self.check_text_comp('lts_lt_plan')
        self.check_text_comp('observatries')
        self.check_text_comp('too_remarks')
        b_list = ['remarks_b', 'comments_b', 'title_b', 'targname_b','soe_st_sched_date_b', 'lts_lt_plan_b', 'observatries_b', 'too_remarks']

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
#
#--- if the monitor list exists, create b list of it
#
        try:
            monitor_list = self.dat_dict['monitor_list']
    
            monitor_list_b = str(monitor_list[0])
            for k in range(1, len(monitor_list)):
                monitor_list_b = monitor_list_b + '#$' + str(monitor_list[k])
        except:
            monitor_list_b =''

        self.dat_dict['monitor_list_b'] = monitor_list_b
        b_list.append('monitor_list_b')

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
        org_pname = 'org_' + pname
        try:
            org_out = self.dat_dict[org_pname].strip()
        except:
            org_out = ''
            self.dat_dict[org_pname] = ''

        try:
            dat_out = self.dat_dict[pname].strip()
        except:
            dat_out = ''
            self.dat_dict[pname] = ''
#
#--- first make a version of all " " removed for a test
#
        if ocf.null_value(org_out):
            org_test = ''
        else:
            org_test = "".join(org_out.split())

        if ocf.null_value(dat_out):
            dat_test = ''
        else:
            dat_test = "".join(dat_out.split())
#
#--- test whether the original and the updated sentences are same without " " 
#
        if org_test == dat_test:
            dat_out = org_out
#
#--- make a backup with "#$"
#
        org_backup   = "#$".join(org_out.split())
        dat_backup   = "#$".join(dat_out.split())
#
#--- save the backup data with a sufix of "_b"
#
        oname1 = pname + '_b'
        oname2 = org_pname + '_b'
        self.dat_dict[oname1] = dat_backup
        self.dat_dict[oname2] = org_backup

#----------------------------------------------------------------------------------
#-- reconstruct_original_text: replace "#$" to " " in the text                  ---
#----------------------------------------------------------------------------------

    def reconstruct_original_text(self, form, achk =''):
        """
        replace "#$" to " " so that a text will have the original " ".
        original form
        input:  form            --- submitted form "dictionary"
                achk            --- whether all text or only original ones are updated, default: achk = '' No
        output: sef.dat_dict    --- updated dat_dictionary
        """
#
#--- the remarks/comments etc with the '#$' are kept in remarks_b/comments_b
#
        nlist = ['org_remarks', 'org_comments']
        if achk == 'all':
            nlist = ['remarks', 'comments'] + nlist

        for name in nlist:
            bname = name + '_b'
            if (bname in form) and (form[bname]):
                self.dat_dict[name] = ocf.put_back_blank_in_line(form[bname])
#
#--- non modifiable but with spaces
#
        nlist = ['too_remarks', 'title', 'targname', 'soe_st_sched_date', 'lts_lt_plan', 'observatries']

        for name in nlist:
            name2 = 'org_' + name
            bname = name + '_b'

            if (bname in form) and (form[bname]):
                self.dat_dict[name]  = ocf.put_back_blank_in_line(form[bname])
                self.dat_dict[name2] = self.dat_dict[name]
            
#
#--- tstart and tstop also have "spaces"
#
        order = self.dat_dict['time_ordr']
        if order > 0:
            for i in range(0, order):
                k = i + 1
                for name in ['tstart', 'tstop']:
                    pname  =  name + str(k)
                    pname1 = 'org_' + pname
                    pname2 = pname1 + '_b'
                    
                    try:
                        mc = re.search('\#\$', form[pname2])
                        if mc is not None:
                            atemp = re.split('\#\$', form[pname2])
                            mon   = ocf.month_convert(atemp[0])
                            day   = int(float(atemp[1]))
                            cday  = str(day)
                            if day < 10:
                                cday = '0' + cday
                            aout  = mon + ':' + cday + ':' + str(atemp[2]) + ':' + str(atemp[3])
                            self.dat_dict[pname1] = aout
                        else:
                            self.dat_dict[pname1] = form[pname2]
                    except:
                        self.dat_dict[pname1] = ''
#
#--- requested value; this does not have #$, but need to be reconstracted
#
                    rname = name + '_month' + str(k)
                    mon   = ocf.month_convert(self.dat_dict[rname])
                    rname = name +  '_date' + str(k)
                    day   = str(self.dat_dict[rname])
                    rname = name +  '_year' + str(k)
                    year  = str(self.dat_dict[rname])
                    rname = name +  '_time' + str(k)
                    time  = str(self.dat_dict[rname])
                    
                    line  = mon + ':' + day + ':' + year + ':' + time

                    self.dat_dict[pname] = line 

#----------------------------------------------------------------------------------
#-- extra_pass_dict: passing data which are not expricitly passed during the submissions 
#----------------------------------------------------------------------------------

    def extra_pass_dict(self):
        """
        passing data which are not expricitly passed during the submissions
        input:  dat_dict    --- data dictionary (self)
        output: org_keys    --- a list of lists [<param name>, <value>]
        """

        org_keys = []
#
#--- passing all "org_" data (data from database)
#
        for ent in self.dat_dict.keys():
            if ent.startswith('org_'):
                org_keys.append([ent, self.dat_dict[ent]])
#
#--- passing  non modifable parameters
#
        for ent in ['head_notificaiton','asis', 'submitter', 'obsid', 'planned_roll']:
            org_keys.append([ent, self.dat_dict[ent]])
#
#--- passing inidcator flags
#
        for ent in ['window_flag', 'roll_flag', 'spwindow_flag']:
            org_keys.append([ent, self.dat_dict[ent]])
#
#--- passing white space removed sentance based parameter values
#
        for ent in ['org_comments_b', 'org_remarks_b', 'comments_b', 'remarks_b', 'title_b', 'targname_b', 'lts_lt_plan_b', 
                        'soe_st_sched_date_b', 'too_remarks_b']:
            org_keys.append([ent, self.dat_dict[ent]])

        for ent in ['chipx', 'chipy']:
#
#--- passing chip coordinates
#
            oent = 'org_' + ent
            org_keys.append([ent,  str(self.dat_dict[ent]).strip()])
            org_keys.append([oent, str(self.dat_dict[oent]).strip()])
#
#--- passing constaint indicators
#
        for k in range(1, 6):
            for constraint in ['widow_contraint', 'roll_constraint']:
                oname = constraint  + str(k)
                try:
                    org_keys.append([oname, self.dat_dict[oname]])
                except:
                    pass
#
#--- passing concatinated monitor list
#
        try:
            if self.dat_dict['monitor_list_b'] != '':
                org_key.append['monitor_list_b', self.dat_dict['monitor_list_b']]
        except:
                pass
#
#--- passing dither in arc seconds
#
        for ename in ['y_amp_asec', 'y_freq_asec', 'z_amp_asec', 'z_freq_asec']:
            try:
                org_keys.append([ename, self.dat_dict[ename]])
            except:
                pass
#
#---- passing time constraint tstart and tstop in month, day, year, and time elements
#
        for k in range(1, 6):
            for head in ['', 'org_']:
                for tname in ['tstart', 'tstop']:
                    for part in ['_month', '_date', '_year', '_time']:
                        oname = head + tname  + part+ str(k)
                        try:
                            org_keys.append([oname, self.dat_dict[oname]])
                        except: 
                            pass
        return org_keys

#----------------------------------------------------------------------------------
