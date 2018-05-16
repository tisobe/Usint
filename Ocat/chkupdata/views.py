#########################################################################################################
#                                                                                                       #
#       chkupdata.py: starting Parameter Chacking Page                                                  #
#                                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                   #
#                                                                                                       #
#           last update: Nov 23, 2016                                                                   #
#                                                                                                       #
#########################################################################################################

import re
import sys
import os
import random
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
    var  = atemp[1].strip()
    line = atemp[0].strip()
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
m_list   = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

#----------------------------------------------------------------------------------
#-- chkUpData: the class which starts Parameter Check Page                      ---
#----------------------------------------------------------------------------------

class chkUpData(View):
    """
    This class starts Check Update Page
    """

    form_class    = OcatParamForm
#
#--- tamplate names
#
    template_name  = 'chkupdata/chkupdata.html'
    not_found_page = 'chkupdata/obsidrev_not_found.html'
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
#--- record the user's name for the latter use
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
            test     = float(args[0])
            obsidrev = args[0]
        except:
            try:
                obsidrev = form['obsidrev']
            except:
                obsidrev = self.obsidrev

        try:
#
#---- extract  param_dict, obs_dict, and ocat_dict
#
            self.prep_data_dictionaries(obsidrev)
#
#--- set general parameters
#
            chkval = self.set_parameter_values()
#
#--- create list of paramter/data list ([pname, org_val, req_val, dat_val])
#
            gen_list    = self.created_data_list('general')
            dither_list = self.created_data_list('dither')
            const_list  = self.created_data_list('other')
            too_list    = self.created_data_list('too')
            hrc_list    = self.created_data_list('hrc')
#
#--- time ordr case
#
            try:
                ordr = chkval['time_ordr']
            except:
                ordr = 0
            time_list   = self.created_data_list('time', ordr)
#
#--- roll ordr case
#
            try:
                ordr = chkval['roll_ordr']
            except:
                ordr = 0
            roll_list   = self.created_data_list('roll', ordr)
#
#--- combine all none acis param lists and then check which values are modified
#
            chkval['pchange'] = '0'
    
            full_list   = gen_list  +dither_list + roll_list + time_list +  const_list + hrc_list
            gen_change  = find_modified_entries(full_list)
    
            if len(gen_change):
                chkval['gchange'] = '1'
                chkval['pchange'] = '1'
            else:
                chkval['gchange'] = 0
#
#--- acis parameter case
#
            acis_list   = self.created_data_list('acis')
            acis_change = find_modified_entries(acis_list)
    
            if len(acis_change):
                chkval['achange'] = '1'
                chkval['pchange'] = '1'
            else:
                chkval['achange'] = 0
#
#--- acis window paramter case
#
            try:
                ordr = chkval['ordr']
            except:
                ordr = 0
            awin_list   = self.created_data_list('awin', ordr)
            awin_change = find_modified_entries(awin_list)
    
            if len(awin_change):
                chkval['awchange'] = '1'
                chkval['pchange']  = '1'
            else:
                chkval['awchange'] = 0
#
#--- print the page
#
            return render_to_response(self.template_name, {
                            'durl':         durl,
                            'chkval':       chkval, 
                            'gen_list':     gen_list, 
                            'dither_list':  dither_list,
                            'const_list':   const_list, 
                            'too_list':     too_list, 
                            'hrc_list':     hrc_list,
                            'acis_list':    acis_list,
                            'roll_list':    roll_list,
                            'time_list':    time_list, 
                            'awin_list':    awin_list,
                            'gen_change':   gen_change,
                            'acis_change':  acis_change, 
                            'awin_change':  awin_change}, 
                RequestContext(request))
#
#--- if the submitted obsidrev is not in the database, display the error page
#
        except:
            return render_to_response(self.not_found_page, { 'obsidrev': obsidrev}, RequestContext(request))


#----------------------------------------------------------------------------------
#-- currently "POST" method is not used in this script                          ---
#----------------------------------------------------------------------------------

    def post(self, request, *args, **kwargs):

        return render_to_response(self.final_page, {'dbval': self.dat_dict, }, RequestContext(request))




###########################################################################################
##                other functions listing starts here                                   ###
###########################################################################################


#----------------------------------------------------------------------------------
#--  prep_data_dictionaries: create three data dictionaries for a given obsidrev  -
#----------------------------------------------------------------------------------

    def prep_data_dictionaries(self, obsidrev):
        """
        create three data dictionaries for a given obsidrev
        input:  obsidrev        --- obsid + rev #
        output: self.param_dict --- a dictionary of  category name <--> a list of parameters
                self.obs_dict   --- a dictionary of param <--> [original value, requested value]
                self.ocat_dict  --- a dictionary of param <--> current DB value
        """
#
#--- create paramater dictioary
#
        self.param_dict = make_parameter_lists()
#
#---- crate original and request value dictionary
#
        self.obs_dict   = oda.read_updates_entries_to_dictionary(obsidrev)
        self.obs_dict['obsidrev'] = [obsidrev, obsidrev]
#
#--- adjust older order input format
#
        org_ordr = self.obs_dict['time_ordr'][0]
        req_ordr = self.obs_dict['time_ordr'][1]
        if self.obs_dict['window_flag'][0] in non_list:
            org_ordr = 0
        if self.obs_dict['window_flag'][1] in non_list:
            req_ordr = 0
        self.obs_dict['time_ordr'] = [org_ordr, req_ordr]
    
        org_ordr = self.obs_dict['roll_ordr'][0]
        req_ordr = self.obs_dict['roll_ordr'][1]
        if self.obs_dict['roll_flag'][0] in non_list:
            org_ordr = 0
        if self.obs_dict['roll_flag'][1] in non_list:
            req_ordr = 0
        self.obs_dict['roll_ordr'] = [org_ordr, req_ordr]
    
        org_ordr = self.obs_dict['ordr'][0]
        req_ordr = self.obs_dict['ordr'][1]
        if self.obs_dict['spwindow_flag'][0] in non_list:
            org_ordr = 0
        if self.obs_dict['spwindow_flag'][1] in non_list:
            req_ordr = 0
        self.obs_dict['ordr'] = [org_ordr, req_ordr]
#
#--- get the current database values
#
        atemp           = re.split('\.', obsidrev)
        obsid           = atemp[0]
        self.ocat_dict  = pdd.prep_data_dict(obsid)
#
#--- modifying time_order start and stop time format
#
        self.check_time_order_cases()

        #return (param_dict, obs_dict, ocat_dict)

#----------------------------------------------------------------------------------
#-- check_time_order_cases: convert the current order time format to <mm>:<dd>:<yyyy>:<hh>:<mm>:<ss>
#----------------------------------------------------------------------------------

    def check_time_order_cases(self):
        """
        convert the current time order time format to <mm>:<dd>:<yyyy>:<hh>:<mm>:<ss>
        input:  obs_dict    --- a dictionary of original and requested value
                ocat_dict   --- a dictionary of valued from the database
        output: ocat_dict   --- updated dictionary of current values
        """
#
#--- check whether this is a time order case
#
        [org_ordr, req_ordr] = self.obs_dict['time_ordr']
        try:
            org_ordr = int(float(org_ordr))
        except:
            org_ordr = 0
        try:
            req_ordr = int(float(req_ordr))
        except:
            req_ordr = 0
#
#--- choose the larger order value
#
        ordr = 0
        if org_ordr >= req_ordr and org_ordr != 0:
            ordr = org_ordr
        elif org_ordr <= req_ordr and req_ordr != 0:
            ordr = req_ordr
#
#--- convert current time order value format from Nov 25 2013 00:00:00  to 11:25:13:00:00:00
# 
        if ordr > 0:
            for k in range(0, ordr):
                rank = k  + 1
                for tname in ('tstart', 'tstop'):
                    tout  = tname + str(rank)
                    stime = self.ocat_dict[tout]
                    date  = ocf.modify_date_format_to_num(stime)

                    self.ocat_dict[tout] = date
                    
#----------------------------------------------------------------------------------
#-- set_parameter_values: set serveral paramter values and put in the dictionary --
#----------------------------------------------------------------------------------

    def set_parameter_values(self):
        """
        set serveral paramter values and put in the dictionary
        input:  pram_dict   --- a dictionary of paramg roup <---> a list of parameters
                obs_dict    --- a dictionary of param <--> [original value, requested value]
                ocat_dict   --- a dictionary of param <--> current DB value
        output: chkval      --- a dictionary of param <--> value

        """

        try:
            date     = self.obs_dict['date'][0]
            date     = ocf.modify_date_format(date)
        except:
            date     = ''
        obsidrev = self.obs_dict['obsidrev'][0]
        atemp    = re.split('\.', obsidrev)

        chkval             = {}
        chkval['date']     = date
        chkval['obsidrev'] = obsidrev
        chkval['obsid']    = self.obs_dict['obsid'][0]
        chkval['revision'] = atemp[1]
        chkval['seq_nbr']  = self.obs_dict['seq_nbr'][0]
        chkval['prop_num'] = self.obs_dict['prop_num'][0]
        chkval['target']   = self.obs_dict['targname'][0]
        chkval['asis']     = self.obs_dict['asis'][0]
        chkval['poc']      = self.obs_dict['poc'][0]
        chkval['ao_nbr']   = self.ocat_dict['obs_ao_str']
        chkval['pi_name']  = self.ocat_dict['pi_name']

        try:
            chkval['group_id'] = self.ocat_dict['group_id'][1]
        except:
            chkval['group_id'] = ''

        test = self.obs_dict['instrument']
        mc   = re.search('acis', test[1].lower())
        if mc is not None:
            inst = 'acis'
        else:   
            inst = 'hrc'

        chkval['instrument'] = test[1]
        chkval['inst']       = inst
#
#--- recheck ordr values and set them correctly. older record may have "1" even there are
#--- no recoreds
#
        chkval['time_ordr']  = self.ordr_check('time', 'time_ordr')
        chkval['roll_ordr']  = self.ordr_check('roll', 'roll_ordr')
        chkval['ordr']       = self.ordr_check('awin', 'ordr')
#
#--- compare remarks and comments
#
        temp  = self.obs_dict['remarks']
        org_remarks = temp[0]
        req_remarks = temp[1]
#
#--- chk indicates whether the texts are changed
#
        chk         = ocf.compare_texts(org_remarks, req_remarks)

        chkval['org_remarks'] = org_remarks
        chkval['req_remarks'] = req_remarks

        temp =  self.ocat_dict['remarks']

        if temp == None:
            temp = ''
        chkval['dat_remarks'] = temp
        chkval['remarks_chk'] = chk


        temp  = self.obs_dict['comments']
        org_comments = temp[0]
        req_comments = temp[1]
        chk          = ocf.compare_texts(org_comments, req_comments)

        chkval['org_comments'] = org_comments
        chkval['req_comments'] = req_comments

        temp =  self.ocat_dict['comments']

        if temp == None:
            temp = ''
        chkval['dat_comments'] = temp
        chkval['comments_chk'] = chk


        return chkval
        
#----------------------------------------------------------------------------------
#-- ordr_check: set order value                                                 ---
#----------------------------------------------------------------------------------

    def ordr_check(self, ogroup, ordr):
        """
        set order value ; older record may have ordr = 1, even there are no data
        input:  o_list  --- a list of the parameters in the ordered group
                ordr    --- a parameter name of the ordr of the group
                obs_dict--- a dictionary of param <--> [original value, requested value]
        output: ordr    --- a value of order. if there in none, return 0
        """
#
#--- get a parameter list for a given order group
#
        o_list = self.param_dict[ogroup]

        chk = 0
        for ent  in o_list:
            param = ent[0]
#
#--- first check whether any of the parameters in the ordred list have values
#
            ####name = param + '1'
            name = param
            try:
                test = self.obs_dict[name]
            except:
                continue

            if test[0].strip() == '' and test[1].strip() == '':
                continue
            else:
                chk = 1
                break
        if chk == 0:
            return 0

        else:
#
#--- if they do, find order value
#
            org_ordr = self.obs_dict[ordr][0]
            try:
                org_ordr = int(float(org_ordr))
            except:
                org_ordr = 0
    
            req_ordr = self.obs_dict[ordr][1]
            try:
                req_ordr = int(float(req_ordr))
            except:
                req_ordr = 0
    
            if req_ordr == 0 and org_ordr == 0:
                return 0
    
            elif req_ordr > org_ordr:
                return req_ordr
     
            else:   
                if org_ordr == 0:
                    return 0
                else:
                    return org_ordr

#----------------------------------------------------------------------------------
#-- created_data_list: create a list of lists [pname, org_val, req_val, dat_val] --
#----------------------------------------------------------------------------------

    def created_data_list(self, group_name, ordr = 0):
        """
        create a list of lists in the form of [pname, org_val, req_val, dat_val]
        input:  group_name  --- a name of the parameter group
                obs_dict    --- a dictionary of param <--> [original value, requested value]
                ocat_dict   --- a dictionary of param <--> current DB value
                ordr        --- a order value; default = 0
        output: data_list   --- a list of lists:  [pname, org_val, req_val, dat_val]
        """

        sub_param_list = self.param_dict[group_name]
        data_list      = []

        if ordr == 0:
#
#--- normal cases
#
            for ent in sub_param_list:
                pname = ent[0]
                cname = ent[1]
#
#--- there are two types of 'ra', 'dec' combination. Ignore one of them.
#
                if pname in ('dra', 'ddec'):
                    continue

                dlist = self.assign_dict_values(pname, cname, self.obs_dict, self.ocat_dict)
                data_list.append(dlist)
        else:
#
#--- ordered cases
#
            chk = 0
            for k in range(0, ordr):
                rank = k + 1
                for ent in sub_param_list:
                    pname = ent[0]
                    cname = ent[1]

                    mc1 = re.search('ordr', pname)
                    mc2 = re.search('flag', pname)

                    if(mc1 is not None) or (mc2 is not None):
                        if (chk == 0):
#
#--- "ordr" and "flag" does not have ranks
#
                            dlist = self.assign_dict_values(pname, cname, self.obs_dict, self.ocat_dict)
                            data_list.append(dlist)
                            chk = 1
                        continue
                    else:
#
#--- ordered values
#
                        name = pname + str(rank)
                        name2= cname + ' Ordr ' + str(rank)
    
                        dlist = self.assign_dict_values(name, name2, self.obs_dict, self.ocat_dict)
                        data_list.append(dlist)

        return data_list

#----------------------------------------------------------------------------------
#-- assign_dict_values: create a list of [pram name, orig val, req val, datbase val] 
#----------------------------------------------------------------------------------

    def assign_dict_values(self, pname, cname, obs_dict, ocat_dict):
        """
        create a list of [pram name, orig val, req val, datbase val]
        input:  pname       --- parameter name
                cname       --- descriptive name
                obs_dict    --- a dictionary of param <--> [original value, requested value]
                ocat_dict   --- a dictionary of param <--> current DB value
        output: a list of [pname, org_val, req_val, dat_val]
        """
#
#--- display name: "descriptive name (parameter name)"
#
        name = cname + ' (' + pname + ')'

        try:
            org_val = obs_dict[pname][0]
            req_val = obs_dict[pname][1]
        except:
            org_val = None
            req_val = None

        try:
            if pname == 'ra':
#                org_val = check_ra_dec_format(pname, org_val)
#                req_val = check_ra_dec_format(pname, req_val)

                tname    = 'dra'
                dat_val  = str(ocat_dict[tname])
#                dat_val = str(convert_ra_dec_val(pname, ocat_dict[tname]))
                name = 'RA (ra)'
            elif pname == 'dec':
#                org_val = check_ra_dec_format(pname, org_val)
#                req_val = check_ra_dec_format(pname, req_val)

                tname    = 'ddec'
                dat_val  = str(ocat_dict[tname])
#                dat_val = str(convert_ra_dec_val(pname, ocat_dict[tname]))
                name = 'Dec (dec)'
            else:
                dat_val = str(ocat_dict[pname])
        except:
            dat_val = None

#
#--- adjust display values
#
        [org_val, req_val, dat_val] = adjust_display_value(name, org_val, req_val, dat_val)
#
#--- occasionally observatories have several names; remove the white spaces between names
#
        if pname == 'observatories':
            org_val = org_val.replace(' ', '')
            req_val = req_val.replace(' ', '')
            dat_val = dat_val.replace(' ', '')

        return [name, org_val, req_val, dat_val]

#########################################################################################
###                    Non class function start here                                #####
#########################################################################################

#----------------------------------------------------------------------------------
#-- find_modified_entries: find the cases that requested value is different from the original value 
#----------------------------------------------------------------------------------

def find_modified_entries(data_list):
    """
    find the cases that requested value is different from the original value
    input:  data_list   --- a list of [pname, org_val, req_val, dat_val]
    output: m_list      --- a list of lists [pname, org_val, req_val]
    """
    
    m_list = []
    for ent in data_list:
        if ent[1] != ent[2]:
            m_list.append([ent[0], ent[1], ent[2]])

    return m_list

#----------------------------------------------------------------------------------
#-- check_ra_dec_format: check whether the format of ra/dec is in degree or not and change to appropriate format
#----------------------------------------------------------------------------------

def check_ra_dec_format(pname, val):
    """
    check whether the format of ra/dec is in degree or not and change to appropriate format
    input:  pname   --- ra or dec
            val     --- the value of ra/dec
    output: va      --- in the format of <xx>:<yy>:<zz>
    """

    mc = re.search(':', val)
    if mc is None:
        val = str(convert_ra_dec_val(pname, val))

    return val

#----------------------------------------------------------------------------------
#-- convert_ra_dec_val: cnvert decimal dec or ra value  to dd:mm:ss format       --
#----------------------------------------------------------------------------------

def convert_ra_dec_val(pname, ent):
    """
    cnvert decimal dec or ra value  to dd:mm:ss format
    input:  pname   --- dec or ra
            ent     --- value
    output: val     --- converted value
    """

    try:
        val = float(ent)
        if pname == 'ra':
            val /= 15.0

        if val < 0.0:
            sign = -1
        else:
            sign = 1
        val = abs(val)
        deg = int(val)
        sdeg = str(deg)
        if deg < 10:
            sdeg = '0' + sdeg

        res = 60*(val - deg)
        mm  = int(res)
        smm  = str(mm)
        if mm < 10:
            smm = '0' + smm

        sss = 60*(res - mm)
        sss = '%.4f' % round(sss, 4)
#
#--- sometime it does not round up cleanly; so fix it 'manually' e.g., 55.9999 to 56.0000
#
        if re.search('9999', sss) is not None:
            sss = 60*(res - mm) + 0.0001
            sss = '%.4f' % round(sss, 4)

        try:
            ss  = float(sss)
        except:
            ss  = 0.0
        if ss < 10:
            sss = '0' + sss

        if sign < 0:
            val = '-' + sdeg + ':'  + smm + ':' + sss
        else:
            val =       sdeg + ':'  + smm + ':' + sss

        return val
    except:
        return ent
                
#----------------------------------------------------------------------------------
#-- adjust_display_value:  clean up the display values                          ---
#----------------------------------------------------------------------------------

def adjust_display_value(name, org_val, req_val, dat_val):
    """
    clean up the display values
    input:  name    --- parameter name
            org_val --- original value
            req_val --- requested value
            dat_val --- database value
    output: org_val --- modified original value
            req_val --- modified requested value
            dat_val --- modified database value
    """
#
#-- if the value is None (or something like that), set to <blank>
#
    if org_val in non_list:
        org_val = ''
    if str(org_val).lower() == '<blank>':
        org_val = ''
    if req_val in non_list:
        req_val = ''
#
#--- if req_val and dat_val in non_list, make them <blank>
#
    if (req_val in non_list) and (dat_val in non_list):
        dat_val = req_val
#
#--- if they are numeric, adjust digit (round to 6 digits) and compare
#
    elif ocf.chkNumeric(dat_val):
#
#--- special treatment for pre_id/observatories
#
        mc  = re.search('pre_id',        name)
        
        try:
            val0    = float(org_val)
            org_val = round(val0, 6)
            if mc is not None:
                org_val = int(org_val)
        except:
            pass
        try:
            val1    = float(req_val)
            req_val = round(val1, 6)
            if mc is not None:
                req_val = int(req_val)
        except:
            pass
        try:
            val2    = float(dat_val)
            dat_val = round(val2, 6)
            if mc is not None:
                dat_val = int(dat_val)
        except:
            pass
#
#--- if order = 0, replace them to <blank>
#        
    mc = re.search('ordr', name)
    if mc is not None:
        if org_val in [0, '0']:
            org_val = ''
        if req_val in [0, '0']:
            req_val = ''
        if dat_val in [0, '0']:
            dat_val = ''

    return [org_val, req_val, dat_val]

#----------------------------------------------------------------------------------
#-- make_parameter_lists: create a dictionary of parameter lists                ---
#----------------------------------------------------------------------------------

def make_parameter_lists():
    """
    create a dictionary of parameter lists
    input:  none but read from "ocat_name_table"
    output: param_dict  --- a dictionary of category name <--> a list of [parameters,discriptive names]
    """

    file = house_keeping + '/changable_param_list'
    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    param_dict = {}
    key        = ''
    plist      = []
    for ent in data:
        mc  = re.search('#-', ent)
        mc2 = re.search('##', ent)
        if mc is not None:
            continue 

        elif mc2 is not None:

            if key != '':
                param_dict[key] = plist
                plist           = []

            atemp = re.split('##', ent)
            btemp = re.split(':',  atemp[1])
            key   = btemp[0]
        
        else:
            atemp = re.split('::', ent)
            plist.append([atemp[0].strip(),atemp[1].strip()])
#
#--- add too parameters which ara not modifiable, but useful to know
#
    param_dict['too'] = [['too_id', 'too di'],['too_trig', 'too trigger'], \
                         ['too_type', 'too type'], ['too_start','too start'], \
                         ['too_stop', 'too stop'], ['too_followup','#  of Follow-up Observations'], \
                         ['too_remarks', 'too remarks']]

    return  param_dict


#----------------------------------------------------------------------------------


