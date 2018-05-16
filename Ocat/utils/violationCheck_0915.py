#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#       violationCheck.py: check whether modifiable parameters satisfy the restrictions             #
#                                                                                                   #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                           #
#                                                                                                   #
#               last update: Sep 08, 2016                                                           #
#                                                                                                   #
#####################################################################################################

import sys
import os
import string
import re
import math
import unittest

#
#--- reading directory list
#
#path = '/data/mta4/CUS/www/Usint/Ocat/ocatsite/static/dir_list_py'
path = './ocatsite/static/dir_list_py'

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
sys.path.append(bin_dir)
sys.path.append(mta_dir)

import ocatCommonFunctions  as ocf
import prepdatdict          as pdd
#
#---  a class object which gives parameter conditions
#
from   ocatParamRange       import OcatParamRange
pr = OcatParamRange()       
#
#--- set a few lists
#
non_list       = ['NA', 'NULL', 'N', 'NONE', '', '\s+', None]
cdo_check_list = ['instrument', 'grating', 'obj_flag', 'multitelescope', 'observatories']
ccd_list       = ['ccdi0_on', 'ccdi1_on', 'ccdi2_on', 'ccdi3_on', 'ccds0_on', 'ccds1_on', \
                  'ccds2_on',  'ccds3_on', 'ccds4_on', 'ccds5_on']

#----------------------------------------------------------------------------------------------------------------
#-- create_normal_warning_list: check whether modifiable parameters satisfy the restrictions                 ----
#----------------------------------------------------------------------------------------------------------------

def create_normal_warning_list(org_dict, dat_dict):
    """
    check whether modifiable parameters satisfy the restrictions
    input:  org_dict    --- original data dictionary
            dat_dict    --- current data dictionary
    output: warning     --- a list of warnings. each item containing [param name, value, condition]
    """

    param_list = dat_dict.keys()
    warning = []
    for param in param_list:
        value = dat_dict[param]
#
#--- check whether this is an ordered parameter; if so remove the number part
#
        test  = str(param)
        if ocf.chkNumeric(test[-1]):
            cparam = test[:-1]
        else:
            cparam = param
#
#--- skip 'window_constraint' and 'roll_constraint', but not 'window_constraint1' etc
#
        if param in ['window_constraint', 'roll_constraint' ]:
            continue
#
#--- check whether the value satisfies the restrictions
#
        test = check_param(cparam, value,  dat_dict)
        if test is not None:
            line = ''
            if isinstance(test, list):
                for ent in test:
                    try:
                        val = dat_dict[ent[0]]
                        if val in non_list:
                            if ent[1] == 'M':
                                line = line + '"' +  str(ent[0]) + '" must have a value.  '
                        else:
                            if ent[1] == 'N':
                                line = line + '"' +  str(ent[0]) + '" should not have a value.  '
                    except:
                        pass

                if line != '':
                    cond = [param, dat_dict[param], line]
                    warning.append(cond) 
                else:
                    pass
            elif test == 'MUST':
                line =  line + 'It must have a value.'
                cond = [param, dat_dict[param], line]
                warning.append(cond)
            else:
#
#--- for the case the value has  numeric range
#
                test = test.replace('<>', ' and ')
                line =  line + 'The value must be between ' + test
                cond = [param, dat_dict[param], line]
                warning.append(cond)
        else:
            pass

    return warning
                

#----------------------------------------------------------------------------------------------------------------
#-- check_param: check the parameter value satisfies the restriction                                         ----
#----------------------------------------------------------------------------------------------------------------

def check_param(param, value,  dat_dict):
    """
    check the parameter value satisfies the restriction
    input:  param       --- parameter name
            dat_dict    --- current data dictionary
    output: violation/None  --- if there is violations, return the condition. otherwise return None
    """

#
#--- check whether this is ordered param
#--- if so, remove the digit part from the param
#
    test = str(param)
    if ocf.chkNumeric(test[-1]):
        param = test[:-1]
#
#---read a value or the list of possible values for the parameter    
#
    vrange = pr.showRange(param)
    v_list = re.split('\,', vrange)

    mchk   = 0
#
#---- first check the value is in the given vrange
#
    if vrange == 'MUST':
        if ocf.null_value(value) != True:
            mchk = 1
            ipos = 0
    elif vrange == 'OPEN' or vrange == 'NA':
        mchk = 1
        ipos = 0
        if ocf.null_value(value):
            mchk = 2
    elif ocf.null_value(value):
#
#--- for the case the "value" is not assigned
#
        for test in non_list:
            if ocf.find_pattern(test, vrange):
                mchk = 2
                ipos = 0
                break
    elif ocf.chkNumeric(value):
#
#--- for the case the value is numeric
#
        for ipos in range(0, len(v_list)):
            if v_list[ipos] == 'NULL':
               if ocf.null_value(value) or ocf.none_value(value): 
                    mchk = 1
                    break
            elif v_list[ipos] == 'OPEN':
                mchk = 1
                break
            elif ocf.find_pattern('<>', v_list[ipos]):
                cond  =  re.split('<>', v_list[ipos])
                vtest = float(value)
                lower = float(cond[0])
                upper = float(cond[1])
                if vtest >= lower and vtest <=upper:
                    mchk = 1
                    break
    else:
#
#---- for the case the value is a word. "OPEN" is one of choice, accept all data
#
        for ipos in range(0, len(v_list)):
            if value == v_list[ipos]:
                mchk = 1
                break
            if v_list[ipos] == 'OPEN':
                mchk = 1
                break        
    if param.lower() == 'dither_flag':
        mchk = 1
        if value == 'Y':
            ipos = 2
        elif value == 'N':
            ipos = 1
        else:
            ipso = 0
#
#--- if the parameter value is in the correct range, check the extra restriction
#
    if mchk > 0 :
        violation = secondary_check(param, value, ipos, dat_dict, mchk)
#
#--- return result
#
    if mchk == 0:
        return vrange
    elif len(violation) > 0:
        return violation
    else:
        return None

#--------------------------------------------------------------------------------------------------------
#-- secondary_check: check the secondary condition for the violation                                  ---
#--------------------------------------------------------------------------------------------------------

def secondary_check(param, value, ipos, dat_dict, mchk):
    """
    check the secondary condition for the violation
    input:  param   --- parameter name
            value   --- value of the parameter
            ipos    --- a position in the violation list which will correspond in the secondary list
            dat_dict--- current data dictionary
    output  violation   --- a list of viorations. each item has [related param name, condition]
    """

#
#--- read the secondary condition list for the given parameter
#
    vcondition = pr.showCondition(param)
#
#--- start reading the list; mainly checking whether other parameters need to be
#--- required for this parameter
#
    violation = []
    if vcondition != 'NA':
        for entry in vcondition:
            if entry[0] == 'NA':
                continue
            try:
                test = dat_dict[entry[0]]
            except:
                test = None

            vcond = entry[1][ipos]
            if vcond == 'O':                                        #--- no restriction
                continue 
            elif vcond == 'C':                                      #--- the condition is custom
                if ocf.null_value(test) or ocf.none_value(test):
                    violation.append([entry[0], 'M'])               #--- the parameter  must have a value 
                else:
                    continue 

            elif vcond == 'N':                                      #--- the parameter should not have a value 
                if ocf.null_value(test) or ocf.none_value(test):
                    continue
                else:
                    violation.append([entry[0], 'N'])
            else:                                                   #--- this is mostly 'M' case
                if mchk == 2:
                    if ocf.null_value(test) or ocf.none_value(test):
                        violation.append([entry[0], 'O'])
                    else:
                        violation.append([entry[0], 'M'])
                else:
                    if ocf.null_value(test) or ocf.none_value(test):
                        violation.append([entry[0], 'M'])
                    else:
                        violation.append([entry[0], 'O'])

    return violation

#--------------------------------------------------------------------------------------------------------
#-- cdo_checks: check the cases which requires CDO approval                                            --
#--------------------------------------------------------------------------------------------------------

def cdo_checks(org_dict, dat_dict):
    """
    check the cases which requires CDO approval
    input:  org_dict    --- data dictionary containing the original values
            dat_dict    --- current data dictionary
    output: cdo_list    --- a list of cdo warnings
    """

    cdo_list = []
    chk  = 0
    for pname in cdo_check_list:
        try:
            new = dat_dict[pname]
            org = org_dict[pname]
        except:
            continue

        if dat_dict[pname] != org_dict[pname]:
            line = pname.capitalize() + ' changed from: ' + str(org_dict[pname]) 
            line = line + ' to ' + str(dat_dict[pname])
            cdo_list.append(line)
#
#--- special check for ACIS<---> HRC change
#
            if pname == 'instrument':
                if check_acis_hrc_change(dat_dict[pname],  org_dict[pname]):
                    atemp = re.split('-', dat_dict[pname])
                    line = 'Make sure to fill all required ' + atemp[0] + ' parameters'
                    atemp = re.split('-', org_dict[pname])
                    line = line + ' and nullify all ' + org_dict[pname] + ' parameters.'
                    cdo_list.append(line)
            chk += 1
#
#--- check a large positional change
#
    try:
        ora  = float(org_dict['dra'])
        odec = float(org_dict['ddec'])
        nra  = float(dat_dict['dra'])
        ndec = float(dat_dict['ddec'])
        diff_ra  = ora  - nra
        diff_dec = odec - ndec
        diff_pos =  math.sqrt(diff_ra * diff_ra + diff_dec * diff_dec)
        if diff_pos > 0.1333:
            ora  = org_dict['ra']
            odec = org_dict['dec']
            nra  = dat_dict['ra']
            ndec = dat_dict['dec']
            line = 'Large positiona change: ra/dec from '
            line = line + str(ora) + '/' + str(odec) + ' to ' + str(nra) +'/' + str(ndec)
            cdo_list.append(line)
            chk += 1
    except:
        pass 

    if chk == 0:
        cdo_list = []
    return cdo_list

#--------------------------------------------------------------------------------------------------------
#-- check_acis_hrc_change: check instrument change between acis and hrc                               ---
#--------------------------------------------------------------------------------------------------------

def check_acis_hrc_change(org, new):
    """
    check instrument change between acis and hrc
    input:  org     --- oritinal instrument
            new     --- current instrument
    output: if the instrument is changed between acis and hrc,True. otherwise False
    """

    mc = re.search('AICS|acis', org)
    if mc is not None:
        mc2 = re.search('HRC|hrc', org)
        if mc2 is not None:
            return True
    else:
        mc2 = re.search('ACIS|acis', org)
        if mc2 is not None:
            return True
        
    return False

#--------------------------------------------------------------------------------------------------------
#-- check_ccds: check selection of acis ccd array                                                     ---
#--------------------------------------------------------------------------------------------------------

def check_ccds(dat_dict):

    """
    check selection of acis ccd array
    input:  dat_dict    --- current data dictionary
    output: warning     --- a list of warnings
    """

    warning = []
#
#--- if the instrument is HRC, ignore this violation checking
#
    chk = dat_dict['instrument']
    mc  = re.search('HRC', chk)
    if mc is not None:
        return warning

    o1 = 0; o2 = 0; o3 = 0; o4 = 0; o5 = 0; ocnt = 0; ycnt = 0; ncnt = 0

    for ccd in ccd_list:
        value = dat_dict[ccd]

        if value   == 'O1':
            o1 += 1
            ocnt += 1
        elif value == 'O2':
            o2 += 1
            ocnt += 1
        elif value == 'O3':
            o3 += 1
            ocnt += 1
        elif value == 'O4':
            o4 += 1
            ocnt += 1
        elif value == 'O5':
            o5 += 1
            ocnt += 1
        elif value == 'Y':
            ycnt += 1
        elif value == 'N':
            ncnt += 1

    total = ocnt + ycnt
    if total > 6:
        warning.append('You can use only 6 or less CCDs.')

    if ycnt == 0:
        warning.append('There must be at least one CCD with YES.')

    if o1 > 1 or o2 > 1 or o3 > 1 or o4 > 1 or o5 > 1:
        warning.append('You cannot assign the same opt # to multiple CCDs.')

    if o5 > 0 and (o1 == 0 or o2 == 0 or o3 == 0 or o4 == 0):
        warning.append('Please do not skip OPT#: Use 1, 2, 3, 4, and 5 in order.')
    elif o4 > 0 and (o1 == 0 or o2 == 0 or o3 == 0):
        warning.append('Please do not skip OPT#: Use 1, 2, 3, and 4 in order.')
    elif o3 > 0 and (o1 == 0 or o2 == 0):
        warning.append('Please do not skip OPT#: Use 1, 2, and 3 in order.')
    elif o2 > 0 and o1 == 0:
        warning.append('Please do not skip OPT#: Use 1 and 2 in order.')

    return warning


#----------------------------------------------------------------------------------------------------------------
#-- check_special_cases: check the cases which need more than standard condition checkings                    ---
#----------------------------------------------------------------------------------------------------------------

def check_special_cases(org_dict, dat_dict):
    """
    check the cases which need more than standard condition checkings 
    input:  org_dict    --- data dictionary containing the original values
            dat_idct    --- current data dictionary
    output: warning     --- a list of warnings
    """

    warning = []
#
#--- check time constraint changes and order of start and stop time
#
    tval = int(float(dat_dict['time_ordr']))
    if tval > 0:
        wchk = 0
        for j in range(0, tval):
            k = j + 1
            [tstart, ostart, nstart] = ocf.convert_back_time_form('tstart', k,  org_dict, dat_dict)
            [tstop,  ostop,  nstop]  = ocf.convert_back_time_form('tstop',  k,  org_dict, dat_dict)

            try:
                start = ocf.convert_time_in_axaf_time(nstart)
            except:
                start = 0
            try:
                stop  = ocf.convert_time_in_axaf_time(nstop)
            except:
                stop  = 0

            if start >= stop:
                line =  'The observation starting time is later than the observation '
                line = line + 'ending time in rank ' + str(k) + ': '
                line = line + 'tstart: ' + str(nstart) + ' /  tstop: ' + str(nstop)
                warning.append(line)

            if (wchk == 0) and  (ostart != nstart or ostop != nstop):
                line = 'Changes in window constraint impact constraints or preferences.'
                line = line + ' Verify you have indicated CDO approval in the comments.'
                warning.append(line)
                wchk = 1
#
#--- check pha range
#
    try:
        val = float(dat_dict['pha_range'])
        if val > 13:
            line = 'In many configurations, an Energy Range above 13 keV will risk telemetry saturation.'
            line = line + ' pha_range: ' + str(val)
            warning.append(line)
    except:
        pass
#
#--- check energy filter low
#
    try:
        val = float(dat_dict['eventfilter_lower'])
        if (val > 0.5) and ocf.null_value(dat_dict['ordr']):
            line = 'If eventfilter_lower > 0.5, ACIS spatial window parameters must be filled.'
            warning.append(line)
    except:
        pass
#
#--- check ACIS window constrain: lower_threshold:
#
    try:
        ordr = float(dat_dict['ordr'])
        ordr = int(ordr)
    except:
        ordr = 0
    if ordr >= 1:
        val2 = dat_dict['eventfilter_lower']
        for j in range(0, ordr):
            k = j + 1
            pname = 'lower_threshold' + str(k)
            try:
                val1 = float(dat_dict[pname])
            except:
                val1 = None

            if (ocf.null_value(val2) or ocf.none_value(val2)) and (val1 != None):
                line = 'ACIS window constraint lower_threshold has a value: '
                line = line + 'eventfilter_lower must have a value smaller than lower_threshold.'
                warning.append(line)
            else:
                try:
                    val2 = float(val2)
                    if val1 > val2:
                        line = 'ACIS window constraint lower_threshold must be '
                        line = line + 'larger than eventfilter_lower: ' + str(val2)
                        warning.append(line)
                except:
                    pass
#
#--- montioring and group observations
#
    if dat_dict['monitor_flag'] == 'Y':
        if dat_dict['group_id'] !='' and dat_dict['group_id'] != 'None':
        #if dat_dict['group_id']:
            warning['group_id'] = 'Group_id is set. A monitor_flag must be NULL.'
        else:
            if ocf.null_value(dat_dict['pre_id']) or ocf.null_value(dat_dict['pre_min_lead'])  \
                or ocf.null_value(dat_dict['pre_max_lead']):
                if dat_dict['time_ordr'] == 0:
                    line = 'If this is a montoring observation, '
                    line = line + ' you need to fill  pre_id, pre_min_lead, and pre_max_lead.'
                    warning.append(line)

    else:
        if dat_dict['group_id']:
            if ocf.null_value(dat_dict['pre_id']) or ocf.null_value(dat_dict['pre_min_lead']) \
                or ocf.null_value(dat_dict['pre_max_lead']):

                if dat_dict['time_ordr'] == 0:
                    line = 'group_id is set. You need to fill pre_id,  pre_min_lead and pre_max_lead.'
                    warning.append(line)

    if dat_dict['pre_id'] == dat_dict['obsid']:
        line = 'pre_id cannot be same as obsid: ' + str(db.newValue('obsid'))
        warning.append(line)

    try:
        val1 = float(dat_dict['pre_min_lead'])
        val2 = float(dat_dict['pre_max_lead'])
    except:
        val1 = val2 = 0

    if val1 > val2:
        line = 'pre_min_lead should be smaller than pre_max_lead: ' + str(db.newValue('pre_max_lead'))
        warning.append(line)
#
#--- si mode change
#
    change_list = []
    if  dat_dict['si_mode'] == 'New Value Requsted':
        for param in ['est_cnt_rate', 'forder_cnt_rate', 'raster_scan', \
                       'grating', 'instrument', 'dither_flag']:

            if org_dict[param] != dat_dict[param]:
                change_list.append(param)

        clen = len(change_list)
        if clen == 1:
            line = 'SI Mode is reset to "New Value Requsted" because the parameter  '
        else:
            line = 'SI Mode is reset to "New Value Requsted" because the  parameters '

        for pname in change_list:
            line = line + ' "' + str(pname) + '", '

        if clen == 1:
            line = line + ' is modified.'
        else:
            line = line + ' are modified.'

        warning.append(line)
#
#--- dither amplitude check. if amplitudes are too small (<0.1), poc could input them in degree.
#
    if dat_dict['dither_flag'] == 'Y':
        y_amp = float(dat_dict['y_amp'])
        z_amp = float(dat_dict['z_amp'])
        if y_amp < 0.0001 or z_amp < 0.0001:
            line = 'Please check Dither Y/Z Amplitude. They must be in arc-sec.'
            warning.append(line)

    return warning


#----------------------------------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST  ---
#----------------------------------------------------------------------------------------------------------------

class TestFunction(unittest.TestCase):

    def test_check_param(self):

        param_list    = pdd.return_changerble_param_list()
        value  = 'None'
        for ent in param_list:
            try:
                test = check_param(ent[0], value)
                print ent[0] + " : " + str(value) + '<--->' + str(test)
            except:
                pass
        
#----------------------------------------------------------------------------------------------

if __name__ == "__main__":

    unittest.main()
    
