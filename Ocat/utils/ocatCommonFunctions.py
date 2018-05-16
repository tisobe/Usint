#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################################
#                                                                                                           #
#           ocatCommonFunction.py: a collection of functions used by Ocat Data Page routines                #
#                                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                       #
#                                                                                                           #
#           Last Update: Feb 22, 2018                                                                       #
#                                                                                                           #
#############################################################################################################

import sys
import os
import string
import re
import copy
import math
import Cookie
import unittest
import time
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

import mta_common_functions as mcf
import convertTimeFormat    as tcnv
import ocatdatabase_access  as oda
#
#--- set directory path to files
#
#changable_param_list  = base_dir + 'ocatsite/static/changable_param_list'
changable_param_list  = './ocatsite/static/changable_param_list'

m_list  = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
nm_list = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]

#----------------------------------------------------------------------------------------------------------------
#-- is_approved: check whether the obsid is in the approved list                                              ---
#----------------------------------------------------------------------------------------------------------------

def is_approved(obsid):

    """
    check whether the obsid is in the approved list
    input:  obsid
    output: True/False
    """

    tlist = oda.get_values_from_approved(obsid)
    if tlist[1] == 'na':
        return False
    else:
        return True

#    file = ocat_dir + '/approved'
#    return check_obsid_in_the_list(obsid, file)

#----------------------------------------------------------------------------------------------------------------
#-- is_in_orlist: check whether the obsid is in the OR list                                                   ---
#----------------------------------------------------------------------------------------------------------------

def is_in_orlist(obsid):

    """
    check whether the obsid is in the OR list
    input:  obsid
    output: True/False
    """
    try:
        sfile = obs_ss + '/scheduled_obs'
        return check_obsid_in_the_list(obsid, sfile)
    except:
        return False

#----------------------------------------------------------------------------------------------------------------
#-- check_lts_date_coming: check whether lts date is less than a warning period                                --
#----------------------------------------------------------------------------------------------------------------

def check_lts_date_coming(lts_lt_plan):
    """
    check whether lts date is less than a warning period 
    input:  lts_lt_plan --- lts date e.g., in forat of Jun 21 2010 12:00AM
    output: True/False
    """

    if lts_lt_plan == '':
        return 0;
#
#--- convert the lts date into fractional year
#
    lts = lts_date_to_fyear(lts_lt_plan)
    if lts == 0:
        return [False, 1000]
    
    else:
#
#--- today's date
#
        today = time.strftime('%j-%Y-%w')
        atemp = re.split('-', today)
        ydate = float(atemp[0])
        year  = int(float(atemp[1]))
        wday  = int(float(atemp[2]))
#
#--- convert today's date in fractional year
#
        if tcnv.isLeapYear(year):
            base = 366.0
        else:
            base = 365.0
    
        tyear = year + ydate/base
#
#--- warning date: how many more day left to lts date
#
        diff     = lts - tyear
        lts_diff = int(diff * base)
#
#--- setting the warning start date to the Monday before the real lts date
#
        if wday == 0:
            sday = 6;
        else:
            sday = wday -1
#
#-- 11 day + M  interval in fractional year
#
        interval = (11.0 + sday) / base
    
        if diff <= interval:
            return [True, lts_diff]
        else:
            return [False, lts_diff]


#----------------------------------------------------------------------------------------------------------------
#-- lts_date_to_fyear: convert  <mmm> <dd> <yyyy> <hh>:<mm><PM> to a fractional year                          ---
#----------------------------------------------------------------------------------------------------------------

def lts_date_to_fyear(lts_lt_plan):
    """
    convert  <mmm> <dd> <yyyy> <hh>:<mm><PM> to a fractional year (ignore hours)
    input:  lts_lt_plan --- lts plan date
    ouput:  lts date in fractional year
    """

    atemp = re.split('\s+', lts_lt_plan)
#
#--- check lts date format
#
    if len(atemp) < 4:
        return 0.0

    else:
        lmon  = atemp[0]
        day   = float(atemp[1])
        year  = int(float(atemp[2]))
    
        aday  = 0
        for k in range(0, 12):
            if lmon.lower() == m_list[k].lower():
                aday = nm_list[k]
#
#--- check whether it is a leap year
#
                if tcnv.isLeapYear(year) == 1: 
                    base = 366.0
                    if (aday >= 59):
                        aday += 1
                else:
                    base = 365.0

                break

        tyear = year + (day + aday) / base
    
        return tyear


#----------------------------------------------------------------------------------
#-- mp_contact_email: find mp contact id for a give obsid if the obs in OR list  --
#----------------------------------------------------------------------------------

def mp_contact_email(obsid):
    """
    find mp contact id for a give obsid if the obs in OR list
    input:  obsid       --- obsid
    output: mp_contact  --- mp person ID
    """

    file = obs_ss + '/scheduled_obs'
    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    mp_contact = None
    for ent in data:
        atemp = re.split('\s+', ent)
        if atemp[0] == obsid:
            mp_contact = atemp[1]
            break

    return mp_contact


#----------------------------------------------------------------------------------
#-- chkNumeric: check the entry is numeric. If so return True, else False.       --
#----------------------------------------------------------------------------------

def chkNumeric(elm):

    """
    check the entry is numeric. If so return True, else False.
    """

    try:
        test = float(elm)
    except:
        return False
    else:
        return True


#----------------------------------------------------------------------------------
#-- check_numeric_float_or_int: check whether values are numeric values    --------
#----------------------------------------------------------------------------------

def check_numeric_float_or_int(oval, nval):
    """
    check whether values are numeric values and, if so, the updated 
    value has the same format of the original vlaule (e.g., int or float)
    input:  oval    --- original value
            nval    --- updated value
    output: nval    --- format adjusted updated value
    """

    if chkNumeric(oval):
        if chkNumeric(nval):
            nval = float(nval)
#
#--- if there is a dicial point, we assume that it is float
#
            mc   = re.search('\.', str(oval))
            if mc is not None:
                nval = str(nval)
            else:
                nval = str(int(nval))

    return nval


#----------------------------------------------------------------------------------------------------------------
#-- find_planned_roll: find a planned roll angle                                                              ---
#----------------------------------------------------------------------------------------------------------------

def find_planned_roll(obsid):

    """
    find a planned roll angle
    input:  obsid
    output: planned_rol --- planned_roll angle
    """

    obsid = str(obsid)
    file = obs_ss + '/mp_long_term_roll'
    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    planned_roll = ''
    for ent in data:
        atemp = re.split(':', ent)
        if obsid == atemp[0]:
            try:
                val1 = float(atemp[1])
                val2 = float(atemp[2])
                if val1 < val2:
                    planned_roll = atemp[1] + ' -- ' +  atemp[2]
                else:
                    planned_roll = atemp[2] + ' -- ' +  atemp[1]
                break
            except:
                pass

    return planned_roll


#----------------------------------------------------------------------------------------------------------------
#-- check_obsid_in_the_list: whether a given obsid is listed in the file                                       --
#----------------------------------------------------------------------------------------------------------------

def check_obsid_in_the_list(obsid, infile, col = 0):

    """
    check whether a given obsid is listed in the file
    input:  obsid    ----- obsid
            infile   ----- a file name; obsids are list sted at <col> columns
            col      ----- column # of the column which list obsids; default: 0
    output: True/False
    """
    f    = open(infile, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    for ent in data:
        atemp = re.split('\s+', ent)
        if str(obsid) == atemp[col]:
            return True
            break

    return False

#----------------------------------------------------------------------------------------------------------------
#-- convert_list_readable: convert database option names into web page human reable form                       --
#----------------------------------------------------------------------------------------------------------------

def convert_list_readable(input, param):

    """
    convert database option names into web page human reable form
    input:  input   --- a string of the option delimited by ","
            param   --- a name of the parameter
    output: rlist   --- a list of options for the web page
    """

    mc = re.search('<>', input)         #---- checking whether the entry is numeric
    if mc is not None:
        return []
    elif input == 'OPEN':
        return []
    elif input == 'NA':
        return []
    else:
        alist = re.split('\,', input)
        rlist = []
        for ent in alist:
            rlist.append(convert_dbval_to_readable(ent, param))

    return rlist

#----------------------------------------------------------------------------------------------------------------
#-- convert_dbval_to_readable: convert database value into web page human reable form                         ---
#----------------------------------------------------------------------------------------------------------------

def convert_dbval_to_readable(val, param):

    """
    convert database value into web page human reable form
    input:  input   --- a string of the option 
            param   --- a name of the parameter
    output: wbval   --- a value readble at web site
    """
    mc  = re.search('constraint', param)
    if   ent == 'N':
        wbval = 'NO'
    elif (ent == 'Y') and (mc is not None):
        wbval = 'CONSTRAINT'
    elif ent == 'Y':
        wbval = 'YES'
    elif ent == 'P':
        wbval = 'PREFERENCE'
    elif ent == 'O1':
        wbval = 'OPT1'
    elif ent == 'O2':
        wbval = 'OPT2'
    elif ent == 'O3':
        wbval = 'OPT3'
    elif ent == 'O3':
        wbval = 'OPT4'
    elif ent == 'O5':
        wbval = 'OPT5'
    elif ent == 'CUSTOM':
        wbval = 'YES'
    else:
        wbval = ent

    return wbval

#----------------------------------------------------------------------------------------------------------------
#-- convert_val_to_dbval: convert the web page option choice/input into database form                         ---
#----------------------------------------------------------------------------------------------------------------

def convert_val_to_dbval(val):

    """
    convert the web page option choice/input into database form
    input:  val     --- the selected option/input on the web page
    output: dbval   --- the database value
    """
    
    if val   == 'YES':
        dbval = 'Y'
    elif val == 'CONSTRAINT':
        dbval = 'Y'
    elif val == 'NO':
        dbval = 'N'
    elif val == 'PREFERENCE':
        dbval = 'P'
    elif val == 'OPT1':
        dbval = 'O1'
    elif val == 'OPT2':
        dbval = 'O2'
    elif val == 'OPT3':
        dbval = 'O3'
    elif val == 'OPT4':
        dbval = 'O4'
    elif val == 'OPT5':
        dbval = 'O5'
    else:
        dbval = val

    return dbval

#----------------------------------------------------------------------------------------------------------------
#-- convert_ra_dec_hms: convert decimal ra dec expression to hh:mm:ss format                                  ---
#----------------------------------------------------------------------------------------------------------------

def convert_ra_dec_hms(ra, dec):

    """
    convert decimal ra dec expression to hh:mm:ss format
    input:  ra, dec in decimal expression 
    output: [ra, dec] in hh:mm:ss format
    """
    tra  = convert_ra_hms(ra)
    tdec = convert_dec_hms(dec)

    return [tra, tdec]

#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------

def convert_ra_hms(ra):
    try:
        ra = float(ra)
        ra = round(ra, 6)
        hf = ra/15.0
        hh = int(hf)
        mf = 60 * (hf - hh)
        mm = int(mf)
        ss = 60 * (mf - mm) 
     
        chh = str(hh)
        if hh < 10:
            chh = '0' + chh
        cmm = str(mm)
        if mm < 10:
            cmm = '0' + cmm
        css = str("%6.4f" % round(ss, 4))
        if ss < 10:
            css = '0' + css
        tra = chh + ':' + cmm + ':' + css
    except:
        tra = ra

    return tra

#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------

def convert_dec_hms(dec):

    try:
        dec = float(dec)
        dec = round(dec, 6)
        if dec < 0:
            sign = '-'
            dec *= -1.0
        else:
            sign = ''

        dd = int(dec)
        mf = 60.0 * (dec - float(dd))
        mm = int(mf)
        ss = 60.0 * (mf - float(mm))
        if ss > 60:
            ss -= 60
            mm += 1
        if mm > 60:
            mm -= 60
            dd + 1
     
        cdd = str(dd)
        if dd < 10:
            cdd = '0' + cdd
        cmm = str(mm)
        if mm < 10:
            cmm = '0' + cmm
        css = str("%6.4f" % round(ss, 5))
        if ss < 10:
            css = '0' + css
        tdec = sign + cdd + ':' + cmm + ':' + css
    except:
        tdec = dec
        tdec = tdec.replace('+', '')

    return tdec

#----------------------------------------------------------------------------------------------------------------
#-- convert_ra_dec_decimal: convert hh:mm:ss format ra and dec into decial format                              --
#----------------------------------------------------------------------------------------------------------------

def convert_ra_dec_decimal(ra, dec):

    """
    convert hh:mm:ss format ra and dec into decial format
    input:  ra, dec  in hh:mm:ss format
    output: [ra, dec] in decimal format
    """
    dra  = convert_ra_to_decimal(ra)
    ddec = convert_dec_to_decimal(dec)

    return [dra, ddec]

#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------

def convert_ra_to_decimal(ra):

    try:
        dra = 15.0 *  convert_hhmmss(ra)
        dra = '%3.6f' % round(dra,6)
    except:
        dra = ra

    return dra


#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------

def convert_dec_to_decimal(dec):

    try:
        mc = re.search('\+', dec)                       #--- if there is "+", drop it
        if mc is not None:
            dec = dec.replace('\+', '')

        ddec = convert_hhmmss(dec)
        ddec = '%3.6f' % round(ddec,6)
    except:
        ddec =  dec

    return ddec

#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------

def check_val_in_dict(adict, key):

    try:
        out = adict[key]
        return True
    except:
        return False

#----------------------------------------------------------------------------------------------------------------
#-- convert_hhmmss: convert hh:mm:ss into degree                                                              ---
#----------------------------------------------------------------------------------------------------------------

def convert_hhmmss(val):

    """
    convert hh:mm:ss into degree
    input:  val     value in hh:mm:ss
    output: dval    value in degree
    """

    mc = re.search(';', val)                        #---- just in a case it is delimited by ";" convert it into ':'
    if mc is not None:
        val = val.replace(';', ':')

    mc = re.search(':', val)                        #---- delimited by ":"
    if mc is not None:
        atemp = re.split(':', val)
    else:
        atemp = re.split('\s+', val)                #---- delimited by " " (space)

    hh   = float(atemp[0])
    mm   = float(atemp[1])
    ss   = float(atemp[2])
    if hh < 0.0:
        dval =  hh - (mm / 60.0 + ss / 3600.0)
    else:
        dval =  hh + mm / 60.0 + ss / 3600.0

    return dval

#----------------------------------------------------------------------------------------------------------------
#-- convert_deg_to_sec: cnvert degree to arcseconds                                                           ---
#----------------------------------------------------------------------------------------------------------------

def convert_deg_to_sec(val):
    """
    cnvert degree to arcseconds
    input:  val     value in degree
    output: val     value in arcsec
    """
#   probably this one is used for dither related values:   dither_name_list = ['y_amp', 'z_amp', 'y_freq', 'z_freq']
    try:
        val  = float(val)
        val *= 3600.0
        return val
    except:
        val  = 0
        return val

#----------------------------------------------------------------------------------------------------------------
#-- convert_to_sec_to_deg: cnvert arcsec to degree                                                            ---
#----------------------------------------------------------------------------------------------------------------

def convert_to_sec_to_deg(val):
    """
    cnvert arcsec to degree
    input:  val     value in arcsec
    output: val     value in degree
    """
#   probably this one is used for dither related values:   dither_name_list = ['y_amp', 'z_amp', 'y_freq', 'z_freq']

    try: 
        val  = float(val)
        val /= 3600.0
        return val
    except:
        val  = 0
        return val

#----------------------------------------------------------------------------------------------------------------
#-- separate_date_line: seperate date line into month, day, year, and time                                    ---
#----------------------------------------------------------------------------------------------------------------

def separate_date_line(date):

    """
    seperate date line into month, day, year, and time
    input:  date    in the format of e.g., 03:15:2011:05:11:12
    output: a list of date time: e.g. ['03', '15', '2011', '05:11:12']
    """

    atemp = re.split(':', date)
    month = atemp[0]
    month = month_convert(month)
    day   = atemp[1]
    year  = atemp[2]
    try:
        time  = atemp[3] + ':' + atemp[4] + ':' + atemp[5]
        time  = time_format_convert(time)
    except:
        time  = '00:00:00'

    return [month, day, year, time]

#----------------------------------------------------------------------------------------------------------------
#-- combine_date_line: combine month, day, year, time in a single date line                                   ---
#----------------------------------------------------------------------------------------------------------------

def combine_date_line(month, day, year, time):

    """
    combine month, day, year, time in a single date line
    input: month, day, year, time, e.g., '03', '15', '2011', '05:11:12'
    output: date:                  e.g., '03:15:2011:05:11:12'
    """

    month = month_convert(month)

    day   = time_digit_to_lett(day)

    try:
        year = float(year)
        if year < 1900:
            if year > 80:
                year += 1900
            else:
                year += 2000
        year = str(int(year))
    except:
        year = '1900'

    time  = time_format_convert(time)

    return month + ':' + day + ':' + year + ':' + time


#----------------------------------------------------------------------------------------------------------------
#-- month_convert: convert month format to either letters or in digits                                        ---
#----------------------------------------------------------------------------------------------------------------

def month_convert(mon):

    """
    convert month format to either letters or in digits
    input:  mon     --- month in letters or digits
    output  cmon    --- month in letters or digits
    """

    m_list = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    if str.isdigit(str(mon)):
        pos = mon -1
        if (pos < 0) or (pos > 11):
            cmon = 'NA'
        else:
            cmon = m_list[pos]
    else:
        cmon = 'NA'
        for dmon in range(0, 12):
            if m_list[dmon].lower() == mon.lower():
                cmon = dmon + 1
            if cmon < 10:
                cmon = '0' + str(cmon)
            else:
                cmon = str(cmon)

    return cmon

#----------------------------------------------------------------------------------------------------------------
#-- time_format_convert: check time format and convert to 24 hrs system with ":" delimited format             ---
#----------------------------------------------------------------------------------------------------------------

def time_format_convert(time):

    """
    check time format and convert to 24 hrs system with ":" delimited format
    input:  time        --- time in hours mins and secs, possibly delimited by ":", ";", " ", "-" etc
    output: time        --- time in 24 hrs system. e.g., 14:13:24
    """

    time  = time.strip()
    atemp = re.split('\W+', time) 
    mc1   = re.search('AM|am', time)
    mc2   = re.search('PM|pm', time)
    pchk  = 0
    if (mc1 is not None):
        pchk = 1
    if (mc2 is not None):
        pchk = 2

    tcnt  = len(atemp)
    hours = '00'
    mins  = '00'
    secs  = '00'

    if tcnt == 1:
        hours = hour_conversion(atemp[0], pchk)
    elif tcnt == 2:
        hours = hour_conversion(atemp[0], pchk)
        if atemp[1] != 'PM|pm|AM|am':
            mout = re.sub('PM|pm|AM|am', '', atemp[1])
            mins = time_digit_to_lett(mout)
            secs = '00'
    elif tcnt == 3:
        hours = hour_conversion(atemp[0], pchk)
        if atemp[1] == 'PM|pm|AM|am':
            mins = time_digit_to_lett(atemp[2])
        else:
            mins = time_digit_to_lett(atemp[1])
            sout = re.sub('PM|pm|AM|am', '', atemp[2])
            secs = time_digit_to_lett(sout)
    elif tcnt == 4:
        hours = hour_conversion(atemp[0], pchk)
        mins = time_digit_to_lett(atemp[1])
        secs = time_digit_to_lett(atemp[2])

    return hours + ':' + mins + ':' + secs

#----------------------------------------------------------------------------------------------------------------
#-- hour_conversion: check and convert time into 24 hr system                                                  --
#----------------------------------------------------------------------------------------------------------------

def hour_conversion(hours, pchk):

    """
    check and convert time into 24 hr system
    input:  hours   --- hour with possibly with am/pm e.g. 11pm
            pchck   --- indicator of whether am/pm attached. if 0: no, 1: am, 2: pm
    output: hours   --- hours in 24 hr system
    """

    if  pchk > 0:
        hours = re.sub('PM|pm|AM|am', '', hours)
    try:
        hours = float(hours)
    except:
        hours = 0
#
#--- we assume that 12:00am means 00:00 in 24 hrs
#
    if (pchk == 1) and (hours == 12):
        hours = 0 
    if pchk == 2:
        hours += 12

    hours = time_digit_to_lett(hours)

    return hours

#----------------------------------------------------------------------------------------------------------------
#-- time_digit_to_lett: convert time in digits to two letter description                                       --
#----------------------------------------------------------------------------------------------------------------

def time_digit_to_lett(input):

    """
    convert time in digits to two letter description
    input:  input  ---- time    e.g. 1 or 23
    output: time   ---- time    e.g. 01 or 23
    """

    val = str(input)
    try:
        dval = int(float(input))
        if dval  < 10:
            val = '0' + str(int(dval))
            return val
        else:
            return  str(int(dval))
    except: 
        return '00'


#----------------------------------------------------------------------------------------------------------------
#-- find_pattern: find a pattern in the string and return True of False                                       ---
#----------------------------------------------------------------------------------------------------------------

def find_pattern(pattern, string):

    """
    find a pattern in the string and return True of False
    Input:  pattern, string
    Output: True/False
    """
    
    mc = re.search(pattern, string)
    if mc is not None:
        return True
    else:
        return False

#----------------------------------------------------------------------------------------------------------------
#-- null_value: check whether the value is Null or empty value---
#----------------------------------------------------------------------------------------------------------------

def null_value(value):

    """
    check whether the value is Null or emptyr value
    Input:  value   --- the value to be checked
    Output: True/False
    """
    
    try:
        if value.lower() in ('null', 'na', 'none'):
            return True
        elif value in ('', ' ', [], '\s+', '\t+',  None):
            return True
        else:
            return False
    except:
        if value in ('', ' ', [], '\s+', '\t+',  None):
            return True
        else:
            return False

#----------------------------------------------------------------------------------------------------------------
#-- none_value: check whether the value is NONE   ---
#----------------------------------------------------------------------------------------------------------------


def none_value(value):

    """
    check whether the value is NONE or emptyr value
    Input:  value   --- the value to be checked
    Output: True/False
    """
    
    try:
        if   value.lower() == 'none'  or value.lower() == 'n' :
            return True
        else:
            return False
    except:
        return False

#----------------------------------------------------------------------------------------------------------------
#-- convert_time_in_axaf_time: convert ocat time format to seconds from 1998.1.1                               --
#----------------------------------------------------------------------------------------------------------------

def convert_time_in_axaf_time(tline):

    """
    convert ocat time format to seconds from 1998.1.1
    Input   ocat time format,  e.g., Feb 22 2013 12:31AM
    Output  time in seconds from 1998.1.1
    """

    atemp = re.split('\s+', tline)

    month = tcnv.changeMonthFormat(atemp[0])
    day   = float(atemp[1])
    year  = float(atemp[2])
    ydate = convert_month_to_ydate(year, month, day)

    m1    = re.search('AM|am|Am', atemp[3])
    m2    = re.search('PM|pm|Pm', atemp[3])

    if m1 is not None:
        time = re.sub('AM|am|Am', '', atemp[3])
        add  = 0
    elif m2 is not None:
        time = re.sub('PM|pm|Pm', '', atemp[3])
        add  = 12
    else:
	time = atemp[3]
        add  = 0

    btemp = re.split(':', time)

    hours = float(btemp[0])
    minutes = float(btemp[1])
    try:
        seconds = float(btemp[2])
    except:
        seconds = 0.0

    ntime = tcnv.convertDateToCTime(year, ydate, hours, minutes, seconds)

    return ntime

#----------------------------------------------------------------------------------------------------------------
#-- convert_month_to_ydate: convert month, mday into ydate                                                    ---
#----------------------------------------------------------------------------------------------------------------

def convert_month_to_ydate(year, month, mday):

    """
    convert month, mday into ydate
    Input    year, month, date
    Output   ydate
    """

    m_sub      = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    m_sub_leap = [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]    # a list for leap year

    if tcnv.isLeapYear(year) == 1:
        m_list = m_sub_leap
    else:
        m_list = m_sub

    ydate = m_list[month-1] + mday 

    return ydate

#----------------------------------------------------------------------------------------------------------------
#-- change_12hr_system: check time format and change to 24 hr system to 12 hrs system                        ----
#----------------------------------------------------------------------------------------------------------------

def change_12hr_system(atime):
    """
    check time format and change to 24 hr system to 12 hrs system
    input: time in 24 hr system
    output: time in 12 hr system

    """

    atime = str(atime)
    mc    = re.search(':', atime)
    m1    = re.search('pm|am', atime)      #--- checking whether the time is already 12 hr system

    if (mc is not None):
        atemp = re.split(':', atime)
        tlen  = len(atemp)
        if(m1 is None):
    
            hour  = int(float(atemp[0]))
#
#--- conver 24hr system to 12hr system
#
            if hour >= 12: 
                hour -= 12
                tail  = 'pm'
            else:
                tail  = 'am'
#
#--- adjust format
#
            if hour < 10: 
                shour = '0' + str(hour)
            else:
                shour = str(hour)
    
            if tlen == 1:  
                atime = shour + ':00:00' + tial
            elif tlen == 2:
                atime = shour + ':' + atemp[1] + ':00' + tail
            else:
                atime = shour + ':' + atemp[1] + ':' + atemp[2] + tail
        else:
            if tlen == 1:
                atime = atime.replace('am', ':00:00am')
                atime = atime.replace('pm', ':00:00pm')
            elif tlen == 2:
                atime = atime.replace('am', ':00am')
                atime = atime.replace('pm', ':00pm')

    else:
        if atime != '':
            if m1 is not None:
                atime = atime.replace('am', ':00:00am')
                atime = atime.replace('pm', ':00:00pm')

            elif mcf.chkNumeric(atime):
                val = int(float(atime))
                if val >= 12:
                    val -= 12
                    if val < 10:
                        atime = '0' + str(val) +':00:00pm'
                    else:
                        atime = str(val) +':00:00pm'
                else:
                    if val < 10:
                        atime = '0' + atime + ':00:00am'
                    else:
                        atime = atime + ':00:00am'
            else:
                atime = '00:00:00am' 
        else:
            atime = '00:00:00am' 

    return atime

#----------------------------------------------------------------------------------
#-- read_param_names: read a parameter list for a given category                 --
#----------------------------------------------------------------------------------

def read_param_names(category):
    """
    read a parameter list for a given category
    input:  category    --- the name of the category
    output: plist       --- a list of parameters
    """
    file = base_dir + '/ocatsite/static/ocat_name_table'
    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    plist = []
    for ent in data:
        mc = re.search(category, ent)
        if mc is not None:
            atemp = re.split(':', ent)
            plist = re.split(',', atemp[1])
            return plist


#----------------------------------------------------------------------------------
#-- read_name_list: read a parameter/name list and create dictionary             --
#----------------------------------------------------------------------------------

def read_name_list():
    """
    read a parameter/name list and create dictionary
    input:  none
    output: name_dict   --- dictionary of param name<-->display name
    """
    file = base_dir + '/ocatsite/static/table_name_list'
    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    name_dict = {}
    for ent in data:

        atemp = re.split('::', ent)
        name_dict[atemp[1]] = atemp[0]

    return name_dict

#----------------------------------------------------------------------------------
#-- convert_back_time_form: combine month, date, year, and time entries into one --
#----------------------------------------------------------------------------------

def convert_back_time_form(name, i, d_dict):
    """ 
    combine month, date, year, and time entries into one (either tstart or tstop)
    and create pset of [param name, display name, original value, updated value]
    input:  name    --- either start or tstop
            i       --- order of the entry
            d_dict  --- updated data dictionary
    output: pset    --- a list of the results [p name, original val, new val]
    """

    tname = name            + str(i)

    mon   = name + '_month' + str(i)
    date  = name + '_date'  + str(i)
    year  = name + '_year'  + str(i)
    time  = name + '_time'  + str(i)

    var   = combine_time_form(d_dict,  mon, date, year, time)

    mon   = 'org_' + name + '_month' + str(i)
    date  = 'org_' + name + '_date'  + str(i)
    year  = 'org_' + name + '_year'  + str(i)
    time  = 'org_' + name + '_time'  + str(i)

    old   = combine_time_form(d_dict,  mon, date, year, time)

    pset  = [tname, old, var]

    return pset

#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

def combine_time_form(d_dict,  mon, date, year, time):

    try:
        mdate  = modify_date(d_dict[date])
#
#--- if time part came with "", add "00:00:00"
#
        time   = str(d_dict[time])
        if time == '': 
            time = '00:00:00'
        if len(time) < 8:
            time = ' ' + time

        var    = d_dict[mon] + ' ' + mdate + ' ' + str(d_dict[year]) + ' ' + time
    except:
        var    = None

    return var

#----------------------------------------------------------------------------------
#-- modify_date:  modidify data format from "01" to "1"                         ---
#----------------------------------------------------------------------------------

def modify_date(date):
    """
    modidify data format from "01" to "1"
    input:  date    --- date
    output: date    --- modified date
    """

    try:
        date = float(date)
        date = int(date)
        cdate = str(date)
        if date < 10:
            cdate = ' ' + cdate
        return cdate
    except:
            return str(date)

#----------------------------------------------------------------------------------
#-- convert_to_24hr_system: convert 12 hr system to 24 hr system                ---
#----------------------------------------------------------------------------------

def convert_to_24hr_system(otime):
    """
    convert 12 hr system to 24 hr system
    input: otime    --- time in the format of Feb 1 2010 1:00:00PM
    output:save     --- time in the format of Feb 1 2010 13:00:00:00
                if there is no second part, it adds ":00"
    """

    atemp = re.split('\s+', otime)
    save  = ""
    for ent in atemp:
        mc = re.search('am|AM|pm|PM', ent)
        if mc is not None:
            time = time_format_convert(ent)
            save = save + time
        else:
            save = save + ent + ' '

    return save

#----------------------------------------------------------------------------------
#-- replace_blank_with_marker: replace " " with "#$" in the string               --
#----------------------------------------------------------------------------------

def replace_blank_with_marker(text):
    """
    since form cannot pass sentences well, replace " " with "#$" in the string
    input:  text    --- original string
    output: backup  --- string with blanks replaced with "#$"
    """
    if len(str(text)) == 0:
        return text
    elif text == None:
        return text
    else:
#
#--- make a backup with "#$"
#
        backup   = "#$".join(text.split())
        return backup

#----------------------------------------------------------------------------------
#-- put_back_blank_in_line: replace "#$" to " " in the text                     ---
#----------------------------------------------------------------------------------

def put_back_blank_in_line(backup):
    """
    replace "#$" to " " so that a text will have the original " ".
    input:  backup  --- string with blanks replaced with "#$"
    output: text    --- original string
    """
    if len(str(backup)) == 0:
        return backup
    elif backup == None:
        return backup
    else:
        text = " ".join(backup.split('#$'))
        return text


#----------------------------------------------------------------------------------
#-- convert_mmddyy_to_stime: convert date format from mmddyy to seconds from 1998.1.1 
#----------------------------------------------------------------------------------

def convert_mmddyy_to_stime(sdate):
    """
    convert date format from mmddyy to seconds from 1998.1.1
    input:  date    ---  mmddyy can be mm/dd/yy, mm-dd-yy, mm:dd:yy
    output: stime   --- time in seconds from 1998.1.1
    """

    mc1 = re.search('\/', sdate)
    mc2 = re.search('-', sdate)
    mc3 = re.search(':', sdate)

    spliter = ''
    if mc1 is not None:
        spliter = '\/'
    elif mc2 is not None:
        spliter = '-'
    elif mc3 is not None:
        spliter = ':'

    if spliter != '':
        atemp = re.split(spliter, sdate)
            
        mon = atemp[0]
        day = atemp[1]
        pyr = atemp[2]
    else:
        mon = sdate[0] + sdate[1]
        day = sdate[2] + sdate[3]
        pyr = sdate[4] + sdate[5]


    try:
        mon = int(float(mon))
    except:
        mon = 1
    try:
        day = int(float(day))
    except:
        day = 1
    try:
        pyr = int(float(pyr))
    except:
        pyr = 0
            
    if pyr < 80:
        pyr += 2000
    else:
        pyr += 1999

    stime = tcnv.convertDateToCTime(pyr, mon, day, 0, 0, 0)

    return stime

#----------------------------------------------------------------------------------
#-- modify_date_format: convert date format from 11/25/13 to Nov 25 2013         --
#----------------------------------------------------------------------------------

def modify_date_format(date):
    """
    convert date format from 11/25/13 to Nov 25 2013
    input:  date    --- date in the format of 11/25/13
    output: date    --- date in the format of Nov 25 2013
    """
    atemp = re.split('\/', date)
    val   = int(float(atemp[0]))
    mon   = tcnv.changeMonthFormat(val)
#
#-- day part
#
    val   = int(float(atemp[1]))
    day   = str(val)
    if val < 10:
        day = '0' + day
#
#-- year part
#
    val   = int(float(atemp[2]))
    if val < 80:
        val += 2000
    else:
        val += 1900
    year = str(val)

    date = mon + ' ' + day + ' ' + year

    return date

#----------------------------------------------------------------------------------
#-- modify_date_format_to_num: convert date format from Nov 25 2013 00:00:00  to 11:25:13:00:00:00 
#----------------------------------------------------------------------------------

def modify_date_format_to_num(date):
    """
    convert date format from Nov 25 2013 00:00:00  to 11:25:13:00:00:00
    input:  date    --- date in the format of  Nov 25 2013 00:00:00
    output: date    --- date in the format of 11:25:13:00:00:00
    """
    atemp = re.split('\s+', date)
    smon  = atemp[0]
    lday  = atemp[1]
    year  = atemp[2]
    time  = atemp[3]

    for m in range(0, 12):
        if smon == m_list[m]:
            mon = m + 1
            break
    lmon = str(mon)
    if mon < 10:
        lmon = '0' + lmon

    day = int(float(lday))
    lday = str(day)
    if day < 10:
        lday = '0' + lday

    date = lmon + ':' + lday + ':' + year + ':' + time

    return date

#----------------------------------------------------------------------------------
#-- find_file_modified_date: find the file modified date and return in mm/dd/yy format 
#----------------------------------------------------------------------------------

def find_file_modified_date(file):

    """
    find the file modified date and return in mm/dd/yy format
    input:  file    --- file name (full path)
    output: day     --- date in mm/dd/yy format
    """

    try:
        date = time.ctime(os.path.getmtime(file))

        atemp = re.split('\s+', date)
        mon   = atemp[1]
        dmon  = tcnv.changeMonthFormat(mon)
        smon  = str(dmon)
        if dmon < 10:
            smon = '0' + smon
    
        sdate = atemp[2]
        date  = int(float(sdate))
        if date < 10:
            sdate = '0' + sdate
    
        year  = atemp[4]
        syear = year[2] + year[3]
    
        day   = smon + '/' + sdate + '/' + syear

    except:
        day = None

    return day

#----------------------------------------------------------------------------------
#-- find_date_of_interval_date_before: find odate of interval date before from today 
#----------------------------------------------------------------------------------

def find_date_of_interval_date_before(interval):
    """
    find odate of interval date before from today
    input: interval --- how far you want to go "back" from today
    output: odate   --- odate (yymmdd) interval day before today
    """
#
#-- find today's date
#
    temp = tcnv.currentTime()
    year = temp[0]
    mon  = temp[1]
    day  = temp[2]
#
#-- find data for the past "interval" date and extract them
#
    [year, mon, day] = find_days_before(year, mon, day, interval)
#
#-- odate is 150813 for 08/13/15
#
    odate = create_odate(year, mon, day)

    return odate 

#----------------------------------------------------------------------------------
#-- find_days_before: find a year mon and day of interval day before today      ---
#----------------------------------------------------------------------------------

def find_days_before(year, mon, day, interval=1):

    """
    find a year mon and day of interval day before today 
    input:  year, mon, day  --- today's date
    output: year, mon, day  --- yesterday's date
    """
#
#--- convert time in seconds from 1998.1.1
#
    stime  = tcnv.convertDateToTime2(year, mon, day)
    stime -= interval * 86400
#
#--- convert back to year and ydate
#
    ntime  = tcnv.axTimeMTA(stime)
    atemp  = re.split(':', ntime)
    year   = int(float(atemp[0]))
#
#--- convert ydate into month and day
#
    ydate  = int(float(atemp[1]))
    [mon, day] = tcnv.changeYdateToMonDate(year, ydate)

    return (year, mon, day)

#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

def find_days_before_in_odate(odate, interval=1):

    odate = str(odate)
    year  = odate[0] + odate[1]
    year  = int(float(year))
    if year < 80:
        year += 2000
    else:
        year += 1900

    mon  = odate[2] + odate[3]
    mon  = int(float(mon))

    day  = odate[4] + odate[5]
    day  = int(float(day))

    (year, mon, day) = find_days_before(year, mon, day)

    odate = create_odate(year, mon, day)     

    return odate

#----------------------------------------------------------------------------------
#-- create_odate: modify the date format to yymmdd                               --
#----------------------------------------------------------------------------------

def create_odate(year, mon, day):
    """
    modify the date format to yymmdd
    input:  year    --- year
            mon     --- month
            day     --- day
    output: pdate   ---- date in yymmdd format                
    """
    syr  = str(year)
    if len(syr) == 4:
        pyr  = syr[2] + syr[3]
    else:
        pyr  = syr

    smon = str(mon)
    if mon < 10:
        smon = '0' + smon

    sday = str(day)
    if day < 10:
        sday = '0' + sday

    pdate = pyr + smon + sday
    pdate = int(float(pdate))

    return pdate

#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

def disp_date_to_odate(date):

    atemp = re.split('\/', date)
    mon   = int(float(atemp[0]))
    day   = int(float(atemp[1]))
    year  = int(float(atemp[2]))

    odate = create_odate(year, mon, day)

    return odate

#----------------------------------------------------------------------------------
#-- today_date: set today's date in mm/dd/yy format                             ---
#----------------------------------------------------------------------------------

def today_date():
    """
    set today's date in mm/dd/yy format
    input:  none
    output: stime   --- date in mm/dd/yy format
    """
    tlist = tcnv.currentTime()
    year  = str(tlist[0])
    syr   = year[2] + year[3]

    mon   = int(float(tlist[1]))
    smon  = str(mon)
    if mon < 10:
        smon = '0' + smon

    date  = int(float(tlist[2]))
    sday  = str(date)
    if date < 10:
        sday = '0' + sday

    stime = smon + '/' + sday + '/' + syr

    return stime


#----------------------------------------------------------------------------------
#-- find_unique_entries: remove duplicated entries from a list                  ---
#----------------------------------------------------------------------------------

def find_unique_entries(alist):
    """
    remove duplicated entries from a list
    input:  alist   --- a list
    output: alist   --- a list with all unique entries
    """

    if len(alist) > 0:
        tlist = [alist[0]]
        for ent in alist:
            for comp in tlist:
                if ent == comp:
                    chk = 0
                    break
                else:
                    chk = 1
            if chk == 0:
                continue
            else:
                tlist.append(ent)

        alist = tlist

    return alist

#----------------------------------------------------------------------------------
#-- compare_texts: compare two texts to check whether they are same              --
#----------------------------------------------------------------------------------

def compare_texts(text1, text2):
    """
    compare two texts to check whether they are same
    input:  text1, text2    --- two texts
    output: chk     --- 0: if both texts are blank
                        1: if both texts are not blank and same
                        2: if text1 is blank but not text2
                        3: if text2 is blank but not text1
                        4: if both texts are not blank and different
    """

    test1 = text1.replace('\s+|\t+|\n+', '')
    test2 = text2.replace('\s+|\t+|\n+', '')

    chk = 0
    if test1 == test2:
        if test1 == '':
            chk = 0
        else:
            chk = 1
    else:
        if test1 == '':
            chk = 2
        elif test2 == '':
            chk = 3
        else:
            chk = 4

    return chk


#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

def extract_unique_entries(alist):

    temp_set = set(alist)
    alist    = list(temp_set)

    return alist

#----------------------------------------------------------------------------------
#-- extract_group_parameters: extract group names and parameter names in those  ---
#----------------------------------------------------------------------------------

def extract_group_parameters():
    """
    extract group names and parameter names in those groups
    input:  none, but read from ocat_name_tlabe
    output: title_dict  --- a dictionary of group id <---> group name (e.g. target_table,  General Information)
            entry_dict  --- a dictionary of group id <---> a list of parameter names
    """

    f    = open(changable_param_list, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    title_dict = {}
    entry_dict = {}
    slist      = []
    title      = ''

    for ent in data:
#
#--- find group id and group title
#
        mc = re.search('#', ent)
        if mc is not None:
            mc2 = re.search('##', ent)
            if mc2 is not None:
                if title != '':
                    entry_dict[nid] = slist
#
#--- title information is marked with '##'
#
                atemp = re.split('##', ent)
                btemp = re.split(':', atemp[1].strip())
                nid   = btemp[0]
                title = btemp[1]
                slist = []
                title_dict[nid] = title
            continue
        else:
#
#--- get parameter names
#
            atemp = re.split(':', ent)
            slist.append(atemp[0])
#
#--- save the last round of the parameters
#
    entry_dict[nid] = slist

    return [title_dict, entry_dict]

#----------------------------------------------------------------------------------
#-- get_param_lists: put parameters in each section into a separate list         --
#----------------------------------------------------------------------------------

def get_param_lists():
    """
    put parameters in each section into a separate list
    input:  none
    output: [acis_list, time_list, roll_list, awin_list, gen_list]
    """

    [title_dict, group_dict] = extract_group_parameters()

    acis_list = group_dict['acis']
    time_list = group_dict['time']
    roll_list = group_dict['roll']
    awin_list = group_dict['awin']

    gen_list  = group_dict['general']
    gen_list  = gen_list + group_dict['dither'] + group_dict['other']
    gen_list  = gen_list + group_dict['hrc']    + group_dict['c&r']

    return [acis_list, time_list, roll_list, awin_list, gen_list]

#----------------------------------------------------------------------------------
#-- find_tab_number: set number of tab spacing                                   --
#----------------------------------------------------------------------------------

def find_tab_number(alist):
    """
    set number of tab spacing
    input:  alist   --- a list of entries
    output: ltab    --- a tab number which can cover the longest entry
    """

    lmax = 0
    for ent in alist:
        size = len(str(ent))
        if size > lmax:
            lmax = size

    ltab = int(lmax / 4) + 1

    return ltab

#----------------------------------------------------------------------------------
#-- add_tab: add tabs to fill character spac                                    ---
#----------------------------------------------------------------------------------

def add_tab(word, space = 24):
    """
    add tabs to fill character space, default: 24 character space
    input:  word    --- the word
    output: add     --- tabs
    """

    try:
        ltab = (len(word) / 4) + 1
    except:
        ltab = 0

    tend = int(space / 4) + 1

    add  = ''
    for i in range(ltab, tend):
        add = add + '\t'

    return add


#----------------------------------------------------------------------------------
#-- find_date_of_wday:  make a list of all mon/mday of week day for the year     --
#----------------------------------------------------------------------------------

def find_date_of_wday(year, oday=0):
    """
    make a list of all mon/mday of week day for the year
    input:  year    --- year
            oday    --- week day in # 0 is Monday and 7 is Sunday
    output: alist   --- a list of lists:
                            [stime, yday, year, mon, day]
    """

    first_day = '1 1 ' + str(year)
    test = time.strptime(first_day, '%d %m %Y')
    wday = test.tm_wday

    if wday <= oday:
        begin = oday - wday + 1
    else:
        begin = 8 - (wday - oday)

    if tcnv.isLeapYear(year):
        base = 366
    else:
        base = 365

    yday  = begin
    alist = []
    i     = 0
    while(yday <= base):
        yday  = begin + 7 * i 
        i += 1
        if yday > base:
            break
        line  =  str(yday) + ' ' + str(year)
        out   = time.strptime(line, "%j %Y")
        day   = out.tm_mday
        mon   = out.tm_mon

        tline = str(year) + ':' + str(yday) + ':00:00:00'
        stime = tcnv.axTimeMTA(tline)
        
        tlist = [stime, yday, year, mon, day]
        alist.append(tlist)

    return alist


#----------------------------------------------------------------------------------
#-- test_wday: test whether the given date is a given week day                   --
#----------------------------------------------------------------------------------

def test_wday(year, mon, day, wday=0):
    """
    test whether the given date is a given week day
    input:  year    --- year in full 4 digits
            mon     --- mon in digit
            day     --- day
            wday    --- week day in #: 0 for Mon, 7 for Sun
    output: True/False
    """

    line = str(year) + ' ' + str(mon) + ' ' + str(day)
    try:
        test = time.strptime(line, "%Y %m %d")
    except:
        return False

    tday = test.tm_wday

    if tday == wday:
        return True
    else:
        return False

#----------------------------------------------------------------------------------
#-- test_wday_stime: test whether the given date in sec is a given week day      --
#----------------------------------------------------------------------------------

def test_wday_stime(stime, wday=0):
    """
    test whether the given date in second from 1998.1.1 is a given week day
    input:  stime   --- time in seconds from 1998.1.1
            wday    --- week day in #: 0 for Mon, 7 for Sun
    output: True/False
    """

    out = tcnv.axTimeMTA(stime)
    atemp = re.split(':', out)

    line = str(atemp[0]) + ' ' + str(atemp[1])
    try:
        test = time.strptime(line, "%Y %j")
    except:
        return False

    tday = test.tm_wday

    if tday == wday:
        return True
    else:
        return False

#----------------------------------------------------------------------------------
#-- find_ymd_from_stime: convert time in seconds from 1998.1.1 to year, mon, mday -
#----------------------------------------------------------------------------------

def find_ymd_from_stime(stime):
    """
    convert time in seconds from 1998.1.1 to year, mon, mday
    input:  stime   --- time in seconds from 1998.1.1
    outout: [s_mon, s_day, s_year]
    """

    out     = tcnv.axTimeMTA(stime)
    atemp   = re.split(':', out)

    line    = atemp[0] + ' ' + atemp[1]
    out     = time.strptime(line, "%Y %j")

    s_year  = out.tm_year
    s_mon   = out.tm_mon
    s_day   = out.tm_mday

    return [s_mon, s_day, s_year]


#----------------------------------------------------------------------------------
#-- find_aiming_point: find aiming point in chip coordinates                     --
#----------------------------------------------------------------------------------

def  find_aiming_point(instrument, y_offset, z_offset):
    """
    find aiming point in chip coordinates
    input:  instrument  --- instrument
            y_offset    --- y off set
            z_offset    --- z off set
    output: chipx       --- chip x
            chipy       --- chip y
    """
    y_offset = float(y_offset)
    z_offset = float(z_offset)
#
#--- find which instrument
#
    mc1 = re.search('acis-i', instrument.lower())
    mc2 = re.search('acis-s', instrument.lower())
    mc3 = re.search('hrc-i',  instrument.lower())
    mc4 = re.search('hrc-s',  instrument.lower())

    if mc1 is not None:
        chipx  = 930.2;
        chipy  = 1009.6;
        factor = 2.0333;

    elif mc2 is not None:
        chipx  = 200.7;
        chipy  = 476.9;
        factor = 2.0333;

    elif mc3 is not None:
        chipx  = 7591.0;
        chipy  = 7936.1;
        factor = 7.5901;

    elif mc4 is not None:
        chipx  = 2041.0;
        chipy  = 9062.7;
        factor = 7.5901;

#
#--- convert offset from arcmin to acrsec then to pixels
#
    chipx -= factor * y_offset * 60.0
    chipy += factor * z_offset * 60.0

    chipx  = round(chipx, 1)
    chipy  = round(chipy, 1)

    return [chipx, chipy]

#----------------------------------------------------------------------------------
#-- poc_check: change poc name to a standard one                                 --
#----------------------------------------------------------------------------------

def poc_check(poc):
    """
    change poc name to a standard one
    input:  poc --- poc id
    output: poc --- updated poc id
    """

    if poc == 'sjw':
        poc = 'swolk'
    elif poc == 'ping':
        poc = 'zhao'

    return poc

#----------------------------------------------------------------------------------
#-- make_year_list: make a list of year from the last year to 5 yrs from this year 
#----------------------------------------------------------------------------------

def make_year_list():
    """
    make a list of year from the last year to 5 yrs from this year
    input:  none
    output: year_list   --- a list of years
    """

    tlist = tcnv.currentTime()
    tyear = tlist[0]
    start = tyear - 1
    end   = tyear + 5
    year_list = []
    for  year in range(start, end):
       year_list.append(year)

    return year_list

	
#----------------------------------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST  ---
#----------------------------------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """

#------------------------------------------------------------

    def test_find_pattern(self):
        pattern = 'this'
        string  = 'this is a test.'
        self.assertEquals(find_pattern(pattern, string), True)


#------------------------------------------------------------

    def test_null_value(self):
        value = ''
        self.assertEquals(null_value(value), True)
        value = ' '
        self.assertEquals(null_value(value), True)
        value = '\s'
        self.assertEquals(null_value(value), True)
        value = []
        self.assertEquals(null_value(value), True)
        value = 'NULL'
        self.assertEquals(null_value(value), True)
        value = 'NA'
        self.assertEquals(null_value(value), True)
        value = None
        self.assertEquals(null_value(value), True)

        value = 'NONE'
        self.assertEquals(none_value(value), True)
        value = 'N'
        self.assertEquals(none_value(value), True)

#------------------------------------------------------------

    def test_convert_month_to_ydate(self):

        year  = 2011; month = 4; mday  = 23
        ydate = convert_month_to_ydate(year, month, mday)
        self.assertEquals(ydate, 113)

        year  = 2012; month = 4; mday  = 23
        ydate = convert_month_to_ydate(year, month, mday)
        self.assertEquals(ydate, 114)

#------------------------------------------------------------

    def test_convert_time_in_axaf_time(self):

        tline = 'Apr 23 2012 12:00AM'
        stime = convert_time_in_axaf_time(tline)
        self.assertEquals(stime, 451569600.0)

#------------------------------------------------------------

    def test_is_approved(self):

        chk = is_approved('15998')
        self.assertEquals(chk, True)


#------------------------------------------------------------

    def test_convert_val_to_dbval(self):

        chk = convert_val_to_dbval('YES')
        self.assertEquals(chk, 'Y')
        chk = convert_val_to_dbval('OPT4')
        self.assertEquals(chk, 'O4')
        chk = convert_val_to_dbval('PREFERENCE')
        self.assertEquals(chk, 'P')
        chk = convert_val_to_dbval('CONSTRAINT')
        self.assertEquals(chk, 'Y')

#------------------------------------------------------------

    def test_convert_ra_dec_hms(self):

        ra  = 214.154167
        dec = 23.422806
        loc = convert_ra_dec_hms(ra, dec)
        self.assertEquals(loc, ['14:16:37.0001', '+23:25:22.1016'])


#------------------------------------------------------------

    def test_convert_ra_dec_decimal(self):

        ra  = '14:16:37.0001'
        dec = '23:25:22.1016'
        loc = convert_ra_dec_decimal(ra, dec)
        self.assertEquals(loc, ['214.154167', '23.422806'])

        ra  = '14;16;37.0001'
        dec = '23;25;22.1016'
        loc = convert_ra_dec_decimal(ra, dec)
        self.assertEquals(loc, ['214.154167', '23.422806'])

        ra  = '14 16 37.0001'
        dec = '+23 25 22.1016'
        loc = convert_ra_dec_decimal(ra, dec)
        self.assertEquals(loc, ['214.154167', '23.422806'])

#------------------------------------------------------------

    def test_month_convert(self):

        mon = 'Aug'
        cmon= month_convert(mon)
        self.assertEquals(cmon, '08')

        mon = 8
        cmon= month_convert(mon)
        self.assertEquals(cmon, 'AUG')

#------------------------------------------------------------

    def test_time_format_convert(self):

        otime = '11:30pm'
        tout = time_format_convert(otime)
        self.assertEquals(tout, '23:30:00')

        otime = '11:30:15AM'
        tout = time_format_convert(otime)
        self.assertEquals(tout, '11:30:15')

        otime = '11;30;15AM'
        tout = time_format_convert(otime)
        self.assertEquals(tout, '11:30:15')

        otime = '11:30:15 AM'
        tout = time_format_convert(otime)
        self.assertEquals(tout, '11:30:15')

        otime = '11 AM'
        tout = time_format_convert(otime)
        self.assertEquals(tout, '11:00:00')

#------------------------------------------------------------

    def test_change_12hr_system(self):

        atime = '11:30:00'
        tout  = change_12hr_system(atime)
        self.assertEquals(tout, '11:30:00am')

        atime = '23:30:00'
        tout  = change_12hr_system(atime)
        self.assertEquals(tout, '11:30:00pm')

        atime = '11:30:00pm'
        tout  = change_12hr_system(atime)
        self.assertEquals(tout, '11:30:00pm')

        atime = '23:30'
        tout  = change_12hr_system(atime)
        self.assertEquals(tout, '11:30:00pm')

        atime = '11'
        tout  = change_12hr_system(atime)
        self.assertEquals(tout, '11:00:00am')

#------------------------------------------------------------

    def test_read_name_list(self):

        tdict = read_name_list()
        self.assertEquals(tdict['roll_obsr'], 'Roll Observed')

#---------------------------------------------------------------------------

if __name__ == "__main__":

    unittest.main()

