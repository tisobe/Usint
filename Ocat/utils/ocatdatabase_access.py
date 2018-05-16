#####################################################################################################
#                                                                                                   #
#       ocatdatabase_access.py: access to ocat data page sql databse                                #
#                                                                                                   #
#            author: t. isobe (tisobe@cfa.harvard.edu)                                              #
#                                                                                                   #
#           How to update database                                                                  #
#           -----------------------                                                                 #
#                                                                                                   #
#           source /proj/sot/ska/bin/ska_envs.csh                                                   #
#           python manage.py shell                                                                  #
#           import utils.ocatdatabase_access as oda                                                 #
#           oda.add_approved_list_to_sql()                                                          #
#           oda.add_updates_list_to_sql()                                                           #
#                       oda.add_updates_list_to_sql(alld='yes') --- full copy case                  #
#           oda.add_updates_entry_to_sql()  ---- usually you don't need to run this                 #
#           oda.add_schedule_entries_to_sql()                                                       #
#           oda.obs_plan_list_to_sql()                                                              #
#                                                                                                   #
#           clean up of test data:                                                                  #
#               oda.clean_up_ocat_databases()                                                       #
#                                                                                                   #
#            last update: Jan 05, 2017                                                              #
#                                                                                                   #
#####################################################################################################

import sys
import os
import re
import random
import time
import unittest

from ocatdatapage.models        import Approved, Updates, Data_tables, Obs_plan, UserProfile
from schedule_submitter.models  import Schedule
#from usint.models               import Usint
from django.contrib.auth.models import User, Group
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

import ocatCommonFunctions      as ocf
import convertTimeFormat        as tcnv
import ocatsql                  as osq
import read_updates_table_entry as rut

#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)
#
#-- original data/directory 
#-- ONCE THIS VERSION GOES TO LIVE, YOU MAY WANT TO REMOVE THE FOLLOWINGS AND DISABLE RELATED FUNCTIONS
#
approved_list = '/data/mta4/CUS/www/Usint/ocat/approved'
updates_table = '/data/mta4/CUS/www/Usint/ocat/updates_table.list'
updates_dir   = '/data/mta4/CUS/www/Usint/ocat/updates/'
schedule_list = '/data/mta4/CUS/www/Usint/ocat/Info_save/too_contact_info/schedule'
new_obs_list  = '/data/mta4/CUS/www/Usint/ocat/Info_save/too_contact_info/new_obs_list'
#
#--- output files names 
#
outfile   = '/data/mta4/CUS/www/Usint/Ocat/approved'
outfile2  = '/data/mta4/CUS/www/Usint/Ocat/updates_table.list'

#
#--- various parameter lists
#
file  = house_keeping + 'data_table_params'
f     = open(file, 'r')
param_list = [line.strip() for line in f.readlines()]
f.close()

extra      = ['obsidrev', 'obsid', 'targid', 'seq_nbr', 'prop_num', 'targname', 'title', 'poc', 'asis', 'rev','date', 'odate', \
            'tooid', 'too_trig', 'too_type', 'too_start', 'too_stop', 'too_remarks']
acis_list  = ['exp_mode', 'bep_pack', 'frame_time', 'most_efficient', 'standard_chips', 'ccdi0_on', \
            'ccdi1_on',  'ccdi2_on', 'ccdi3_on', 'ccds0_on', 'ccds1_on', 'ccds2_on', 'ccds3_on', \
            'ccds4_on', 'ccds5_on', 'subarray', 'subarray_start_row', 'subarray_row_count',       \
            'subarray_frame_time', 'duty_cycle', 'secondary_exp_count', 'primary_exp_time',      \
            'secondary_exp_time', 'onchip_sum', 'onchip_row_count', 'onchip_column_count',       \
            'eventfilter', 'eventfilter_lower', 'eventfilter_higher', 'multiple_spectral_lines', \
            'spectra_max_count']
awin_list  = ['chip', 'start_row',  'start_column', 'height', 'width', 'lower_threshold', \
                     'pha_range', 'sample']
time_list  = ['window_constraint', 'tstart', 'tstop']
roll_list  = ['roll_constraint', 'roll_180', 'roll', 'roll_tolerance'] 

#
#
m_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

###################################################################################
#                      approved related functions                                 #
###################################################################################


#----------------------------------------------------------------------------------
#-- add_approved_list_to_sql: copy approved data and update sql database         --
#----------------------------------------------------------------------------------

def add_approved_list_to_sql():
    """
    copy approved data and update sql database
    input:  none but read from /data/mta4/CUS/www/Usint/ocat/approved
    output: sql Approved
    """
    f    = open(approved_list, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    for ent in data:
        atemp = re.split('\t+|\s+', ent)
        try:
            obsid = atemp[0]
            seqno = atemp[1]
            poc   = atemp[2]
            date  = atemp[3]
    
            add_to_approved_list(obsid, seqno, poc, date)
        except:
            pass

#----------------------------------------------------------------------------------
#-- add_to_approved_list: add or update sql approved list                       ---
#----------------------------------------------------------------------------------

def add_to_approved_list(obsid, seqno, poc, date):
    """
    add or update sql approved list
    input:  obsid   --- obsid
            seqno   --- sequence number
            poc     --- poc
            date    --- approved date
    output: updated sql approved list
    """
#
#--- the data is already in sql database
#
    try:
        approved = Approved.objects.get(obsid = obsid)
#
#--- the new data to add to sql database
    except:
        approved = Approved(obsid = obsid)

    approved.seqno = seqno
    approved.poc   = poc
    approved.date  = date

    odate = change_date_format(date)
    approved.odate = odate

    approved.save()

#----------------------------------------------------------------------------------
#-- add_missing_data_in_approved_list: update sqlite approved list               --
#----------------------------------------------------------------------------------

def add_missing_data_in_approved_list():
    """
    compare the old approved list to the sqlite version and add missing ones
    input:  none but read from approved list (and sql database)
    output: updated sqlite database
    """

    f    = open(approved_list, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    apps = Approved.objects.all()

    obsid_dict = {}
    for ent in apps:
        obsid_dict[ent.obsid] = True

    missing_list = []
    for ent in data:
        atemp = re.split('\s+', ent)
        obsid = atemp[0]
        seqno = atemp[1]
        poc   = atemp[2]
        date  = atemp[3]
#
#--- if the data is already in sql database, it gives back True
#
        try:
            test = obsid_dict[obsid]
        except:
            add_to_approved_list(obsid, seqno, poc, date)

    
#----------------------------------------------------------------------------------
#-- convert_approved_list_to_ascii: read sql approved list and create an ascii version 
#----------------------------------------------------------------------------------

def convert_approved_list_to_ascii():
    """
    read sql approved list and create an ascii version
    input:  none but read from the database
    output: outfile 
    """

    apps = Approved.objects.all()

    fo   = open(outfile, 'w')
    for ent in apps:
        line = ent.obsid        + '\t'
        line = line + ent.seqno + '\t'
        line = line + ent.poc   + '\t'
        line = line + ent.date  + '\n'

        fo.write(line)

    fo.close()

#----------------------------------------------------------------------------------
#-- get_values_from_approved: extract data corresponding to obsid               ---
#----------------------------------------------------------------------------------

def get_values_from_approved(obsid):
    """
    extract data corresponding to obsid
    input:  obsid   --- obsid
    output: a list : [obsid, seqno, poc, date]
    """

    try:
        app = Approved.objects.get(obsid = obsid)
        list = [obsid, app.seqno, app.poc, app.date]
    except:
        list = [obsid, 'na', 'na', 'na']

    return list

#----------------------------------------------------------------------------------
#-- delete_from_approved_list: delete sql approved list entry                   ---
#----------------------------------------------------------------------------------

def delete_from_approved_list(obsid):
    """
    delete sql approved list entry
    input:  obsid   --- obsid
    output: updated sql approved list
    """

    try:
        app = Approved.objects.get(obsid=obsid)
        app.delete()
    except:
        pass




###################################################################################
#                   updates_table.list related functions                          #
###################################################################################


#----------------------------------------------------------------------------------
#-- add_updates_list_to_sql: copy updates data and update sql database         --
#----------------------------------------------------------------------------------

def add_updates_list_to_sql(alld='', get_file='yes'):
    """
    copy updates_table.list data and update sql database
    input:  alld        --- if 'yes', the all data are updated, otherwise add only new ones  dafualt: ""
            get_file    --- if 'yes', it also update <obsid>.<rev> data files. default: 'yes'
            read from /data/mta4/CUS/www/Usint/ocat/updates_table.list
    output: sql Updates
            sql Data_tables (if get_fie == 'yes')
    """
#
#--- create a list of obsid rev and a dictionay for given obsidrev <---> verified status from the current database
#
    cdata = read_updates_list()
    prev_list = []
    pdict     = {}
    for k in range(0, len(cdata)):
        prev_list.append(cdata[k][0])
        pdict[cdata[k][0]] = cdata[k][4].lower()
#
#--- read the ascii table "updates_table.list"
#
    f    = open(updates_table, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    for ent in data:
        atemp    = re.split('\t+', ent)

        if len(atemp) < 7:
            print ent               #---- something wrong; print out the line
            continue

        obsidrev = atemp[0]
        general  = atemp[1]
        acis     = atemp[2]
        si_mode  = atemp[3]
        verified = atemp[4]
        seqno    = atemp[5]
        poc      = atemp[6]
#
#--- if clean update is requested, don't skip any
#
        if alld != 'yes':
#
#--- else, if it is already in the list and if it is already verified, skip
#
            if obsidrev in prev_list:
                if (pdict[obsidrev] != 'na'):
                    continue

        dfile    = '/data/mta4/CUS/www/Usint/ocat/updates/' + str(obsidrev)
        cdate    =  ocf.find_file_modified_date(dfile)

        mdate    = find_date(atemp)

        if cdate == None:
            cdate = mdate
#
#--- udate table list
#
        add_to_updates_list(obsidrev, general, acis, si_mode, verified, seqno, poc, cdate, mdate)
#
#--- update data files
#
        if get_file == 'yes':
            add_data_in_updates_entry_sql(obsidrev)

#----------------------------------------------------------------------------------
#-- add_new_entry_to_update_list: add a new entry to sql database                --
#----------------------------------------------------------------------------------

def add_new_entry_to_update_list(dat_dict):
    """
    add a new entry to sql database
    input: dat_dict --- current data dictionary
    output: updated sql database
    """
    obsid    = dat_dict['obsid']
    rev      = set_new_rev(obsid)
    obsidrev = str(obsid) + '.' + str(rev)
    poc      = dat_dict['submitter']
    date     = today_date()
    seqno    = dat_dict['seq_nbr']
    asis     = dat_dict['asis']
#
#--- if it is submitted as "asis" approve it and fill poc name
#
    if dat_dict['asis'] == 'asis':
        general  = 'NULL'
        acis     = 'NULL'
        si_mode  = 'NULL'
        verified = poc + ' ' + date
#
#--- if only hrc_si change is requested, si mode and verified columns are open
#
    elif dat_dict['hrc_si_select'] == 'yes':
        general  = 'NULL'
        acis     = 'NULL'
        si_mode  = 'NA'
        verified = 'NA'
    else:
        general  = find_general_status(dat_dict)
        acis     = find_acis_status(dat_dict)
        si_mode  = find_si_mode_status(dat_dict)
        verified = 'NA'
#
#--- add to updates_table.list (sql version)
#
    add_to_updates_list(obsidrev, general, acis, si_mode, verified, seqno, poc, date, date)
#
#--- add to udpates data file (sql version: equivalent of updates/16234.001)
#
    pdict = {}
    check_list = extra + param_list
    for key in check_list:
        okey = 'org_' + key
        try:
            pdict[key] = [str(dat_dict[okey]), str(dat_dict[key])]
        except:
            pdict[key] = [None, None]
#
#--- add several other parameters
#
    pdict['poc']      = [poc, poc]
    pdict['obsidrev'] = [obsidrev, obsidrev]
    pdict['rev']      = [rev, rev]
    pdict['date']     = [date, date]
    odate             = ocf.disp_date_to_odate(date)
    pdict['odate']    = [odate, odate]
    pdict['asis']     = [asis, asis]

    add_to_update_entry(pdict, obsidrev)

#----------------------------------------------------------------------------------
#-- add_to_updates_list: add or update sql updates list                         ---
#----------------------------------------------------------------------------------

def add_to_updates_list(obsidrev, general, acis, si_mode, verified, seqno, poc, cdate, mdate):
    """
    add or update sql updates_table.list list
    input:  obsidrev   --- obsid.rev (obsid and revision #)
            general    --- general sign off (poc name and date)
            acis       --- acis sign off
            si_mode    --- si_mode sign off
            verified   --- sign off verified by poc/date
            seqno      --- sequence number
            poc        --- poc of the observation
            cdate      --- the date of the data creation
            mdate      --- the date of the data modified
    output: updated sql updates_table.list
    """
    [obsid, rev] = re.split('\.+', str(obsidrev))
    
#
#--- data is already there; just update
#
    try:
        updates = Updates.objects.get(obsidrev = obsidrev)
#
#--- new data to be added
#
    except:
        updates = Updates(obsidrev = obsidrev)

    updates.obsidrev = obsidrev
    updates.general  = general 
    updates.acis     = acis     
    updates.si_mode  = si_mode
    updates.verified = verified 
    updates.seqno    = seqno
    updates.poc      = poc
    updates.obsid    = obsid
    updates.rev      = rev
    updates.date     = cdate

    odate = change_date_format(mdate)
    updates.odate    = odate

    updates.save()

#----------------------------------------------------------------------------------
#-- find_date: find the latest date in which the input was modified              --
#----------------------------------------------------------------------------------

def find_date(alist):
    """
    find the latest date in which the input was modified
    input:  alinst  --- data line, e.g. 
            17686.001   NULL    NULL    NULL    lpd 06/25/15    890115  lpd
    output: signoff --- the lasted date in which the line was modified
    """
    dlist = []
    for ent in alist:
#
#--- look for the date by "/" as the date in in the format of mm/dd/yy
#
        nc = re.search('\/', ent)
        if nc is not None:
            try:
                atemp = re.split('\s+', ent)
                date  = atemp[1]
                date.strip()
                dlist.append(date)
            except:
                pass
        else:
            continue

    if len(dlist) > 0:
#
#--- find the last date which the line was modified
#
        signoff = dlist[0]
        ldate   = convert_to_sdate(dlist[0])
        for ent in dlist:
            sdate = convert_to_sdate(ent)
            if sdate > ldate:
                ldate = sdate
                signoff = ent
            else:
                continue
    else:
#
#--- if there is no date, put today's date
#
        signoff = today_date()

    return signoff
        
#----------------------------------------------------------------------------------
#-- convert_to_sdate: convert date in mm/dd/yy into time in seconds from 1998.1.1 -
#----------------------------------------------------------------------------------
            
def convert_to_sdate(mdate):
    """
    convert date in mm/dd/yy into time in seconds from 1998.1.1
    input:  mdate   --- date in the format of mm/dd/yy
    output: stime   --- time in seconds from 1998.1.1
    """

    try:
        [mon, day, syr] = re.split('\/', mdate)
    
        mon = int(float(mon))
        day = int(float(day))
        syr = int(float(syr))
        if syr < 80:
            syr += 2000
        else:
            syr += 1900
    
        stime = tcnv.convertDateToTime2(syr, mon, day)
    except:
        stime = 0

    return stime
        
#----------------------------------------------------------------------------------
#-- today_date: today's date in mm/dd/yy format                                  --
#----------------------------------------------------------------------------------
            
def today_date():
    """
    today's date in mm/dd/yy (e.g.06/25/15) format
    input:  none
    output: ldate   --- date in mm/dd/yy
    """

    tlist = tcnv.currentTime()
    year  = str(tlist[0])
    mon   = tlist[1]
    day   = tlist[2]

    syear = year[2] + year[3]
    smon  = str(mon)
    if mon < 10:
        smon = '0' + smon
    sday  = str(day)
    if day < 10:
        sday = '0' + sday

    ldate = smon + '/' + sday + '/' + syear

    return ldate

#----------------------------------------------------------------------------------
#-- convert_updates_list_to_ascii: read sql updates list and create an ascii version 
#----------------------------------------------------------------------------------

def convert_updates_list_to_ascii():
    """
    read sql updates list and create an ascii version
    input:  none but read from the database
    output: outfile 
    """

    apps = Updates.objects.all()

    fo   = open(outfile2, 'w')
    for ent in apps:
        line = ent.obsidrev        + '\t'
        line = line + ent.general  + '\t'
        line = line + ent.acis     + '\t'
        line = line + ent.si_mode  + '\t'
        line = line + ent.verified + '\t'
        line = line + ent.seqno    + '\t'
        line = line + ent.poc      + '\n'

        fo.write(line)

    fo.close()

#----------------------------------------------------------------------------------
#-- read_updates_list: read sql updates list and put the results in a list       --
#----------------------------------------------------------------------------------

def read_updates_list():
    """
    read sql updates list and put the results in a list
    input:  none but read from the database
    output: update_list --- a list of lists [obsidrev, general, acis, si_mode, verified, seqno, poc, date]
    """

    #updates = Updates.objects.all().order_by('odate')
    updates = Updates.objects.all()

    update_list = make_update_list(updates)

    return update_list


#----------------------------------------------------------------------------------
#-- select_data_for_obsidrev: select entries a give obsidrev                     --
#----------------------------------------------------------------------------------

def select_data_for_obsidrev(obsidrev):
    """
    select entries a give obsidrev
    input:  obsidrev    --- obsid + rev #
    output: update_list --- a list of lists [obsidrev, general, acis, si_mode, verified, seqno, poc, date]
    """

    updates = Updates.objects.filter(obsidrev=obsidrev)

    update_list = make_update_list(updates)

    return update_list


#----------------------------------------------------------------------------------
#-- select_data_for_obsid: select entries for a given obsid                      --
#----------------------------------------------------------------------------------

def select_data_for_obsid(obsid):
    """
    select entries for a given obsid
    input:  obsid       --- obsid
    output: update_list --- a list of lists [obsidrev, general, acis, si_mode, verified, seqno, poc, date]
    """

    updates = Updates.objects.filter(obsid=obsid)

    update_list = make_update_list(updates)

    return update_list


#----------------------------------------------------------------------------------
#-- select_data_for_seqno: select entries for a given sequence number            --
#----------------------------------------------------------------------------------

def select_data_for_seqno(seqno):
    """
    select entries for a given sequence number 
    input:  seqno       --- sequence number
    output: update_list --- a list of lists [obsidrev, general, acis, si_mode, verified, seqno, poc, date]
    """

    updates = Updates.objects.filter(seqno=seqno)

    update_list = make_update_list(updates)

    return update_list

#----------------------------------------------------------------------------------
#-- select_non_signed_off: select entries in which a given column is not signed off
#----------------------------------------------------------------------------------

def select_non_signed_off(col):
    """
    select entries in which a given column is not signed off
    input: col  --- column name (general, acis, si_mode, verified) 
                read from sql database
    output: update_list --- a list of lists [obsidrev, general, acis, si_mode, verified, seqno, poc, date]
    """

    exec "updates = Updates.objects.filter(%s = 'NA')" % (col)

    update_list = make_update_list(updates)

    return update_list


#----------------------------------------------------------------------------------
#-- get_data_marked_with_date: select entries modified on  pdate                 --
#----------------------------------------------------------------------------------

def get_data_marked_with_date(pdate):
    """
    select entries modified on  pdate
    input:  pdate   --- in the form of 150716 (yymmdd)
    output: update_list --- a list of lists [obsidrev, general, acis, si_mode, verified, seqno, poc, date]
    """

    updates = Updates.objects.filter(odate = pdate)

    update_list = make_update_list(updates)

    return update_list

#----------------------------------------------------------------------------------
#--  get_data_newer_than_date: select entries modified after or equal to pdate  ---
#----------------------------------------------------------------------------------

def get_data_newer_than_date(pdate):
    """
    select entries modified after or equal to pdate
    input:  pdate   --- in the form of 150716 (yymmdd)
    output: update_list --- a list of lists [obsidrev, general, acis, si_mode, verified, seqno, poc, date]
    """

    updates = Updates.objects.filter(odate__gte =  pdate)

    update_list = make_update_list(updates)

    return update_list

#----------------------------------------------------------------------------------
#-- get_verified_cases: select entries modified after or equal to pdate          --
#----------------------------------------------------------------------------------

def get_verified_cases():
    """
    select entries modified after or equal to pdate
    input:  pdate   --- in the form of 150716 (yymmdd)
    output: update_list --- a list of lists [obsidrev, general, acis, si_mode, verified, seqno, poc, date]
    """

    updates = Updates.objects.all().order_by('odate')

    selected = []
    for ent in updates:
        if ent.verified != 'NA':
            selected.append(ent)

    update_list = make_update_list(selected)

    return update_list

#----------------------------------------------------------------------------------
#-- make_update_list: make a list of lists of updates_list table entries from database output
#----------------------------------------------------------------------------------

def make_update_list(updates):
    """
    make a list of lists of updates_list table entries from database output
    input:   updates    --- database output
    output: update_list --- a list of lists [obsidrev, general, acis, si_mode, verified, seqno, poc, date]
    """

    update_list = []
    for ent in updates:
        temp_list = []
        temp_list.append(ent.obsidrev)
        temp_list.append(ent.general)
        temp_list.append(ent.acis)
        temp_list.append(ent.si_mode)
        temp_list.append(ent.verified)
        temp_list.append(ent.seqno)
        temp_list.append(ent.poc)
        temp_list.append(ent.date)
        update_list.append(temp_list)

    return update_list

#----------------------------------------------------------------------------------
#-- add_missing_data_in_updates_list: add/update of updateas_list                --
#----------------------------------------------------------------------------------

def add_missing_data_in_updates_list():
    """
    compare the old approved list to the sqlite version and add missing ones
    input:  none but read from approved list (and sql database)
    output: updated sqlite and data file  database
    """

    f    = open(updates_table, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    updates = Updates.objects.all()
#
#--- make dictionary of obsidrev <---> date
#
    obsidrev_dict = {}
    for ent in updates:
        obsidrev_dict[ent.obsidrev] = ent.date

    missing_list = []
    mchk = 0
    for ent in data:
        atemp = re.split('\t+', ent)
#
#--- if the entry is less than 7, something is wrong with the input
#
        if len(atemp) < 7:
            continue 

        btemp = re.split('\.', atemp[0])

        obsidrev = atemp[0]
        general  = atemp[1]
        acis     = atemp[2]
        si_mode  = atemp[3]
        verified = atemp[4]
        seqno    = atemp[5]
        poc      = atemp[6]
        obsid    = btemp[0]
        rev      = btemp[1]
        file     = '/data/mta4/CUS/www/Usint/ocat/updates/' + str(obsidrev)
        cdate    = ocf.find_file_modified_date(file)
        mdate    = find_date(atemp)
        if cdate == None:
            cdate = mdate
#
#--- entry was changed from the last time that the script checked the list
#
        try:
            pdate = obsidrev_dict[obsidrev]
            if pdate != mdate:
                add_to_updates_list(obsidrev, general, acis, si_mode, verified, seqno, poc, cdate, mdate)
#
#--- new entry is found; add to the database
#
        except:
            add_to_updates_list(obsidrev, general, acis, si_mode, verified, seqno, poc, cdate, mdate)
#
#--- also update full parameter database
#
            try:
                add_data_in_updates_entry_sql(obsidrev)
                mchk  = 1
            except:
                pass
#
#--- during the test phase, you need to copy updates_table.list every time data is
#--- updated so that you can go back to the original when clean out test entries
#
    if mchk > 0:
        cmd = 'cp ' + updates_table + ' ' +  temp_updates
        os.system(cmd)

#----------------------------------------------------------------------------------
#-- get_values_from_updates: extract data corresponding to obsidrev             ---
#----------------------------------------------------------------------------------

def get_values_from_updates(obsidrev):
    """
    extract data corresponding to obsid
    input:  obsidrev   --- obsid.rev
    output: a list :  [obsidrev, general, acis, si_mode, verified, update.seqno, update.poc]
    """

    try:
        updates = Updates.objects.get(obsidrev = obsidrev)
        list = [obsidrev, updates.general, updates.acis, updates.si_mode, updates.verified, updates.seqno, updates.poc]
    except:
        list = [obsidrev, 'na', 'na', 'na', 'na', 'na', 'na']

    return list

#----------------------------------------------------------------------------------
#-- delete_from_updates_list: delete sql updates list entry                     ---
#----------------------------------------------------------------------------------

def delete_from_updates_list(obsidrev):
    """
    delete sql updates_table.list entry
    input:  obsidrev   --- obsid.rev
    output: updated sql updates list
    """

    app = Updates.objects.get(obsidrev=obsidrev)

    app.delete()
#
#--- we also need to remove the data file from data_tables database
#
    try:
        delete_from_updates_entry(obsidrev)
    except:
        pass

#----------------------------------------------------------------------------------
#-- set_new_rev: set revision number one after the last one                     ---
#----------------------------------------------------------------------------------

def set_new_rev(obsid):
    """
    set revision number one after the last one
    input:  obsid   --- obsid
    output: srev    --- revision # in the form of '003', set the one after the last one
    """
#
#--- find the last revision #
#
    lrev = find_the_last_rev(obsid)

    rev  = int(float(lrev)) + 1
    srev = str(rev)
    if rev < 10:
        srev = '00' + srev
    elif rev < 100:
        srev = '0'  + srev

    return srev

#----------------------------------------------------------------------------------
#-- find_the_last_rev: find the last revision # of the given obsid               --
#----------------------------------------------------------------------------------

def find_the_last_rev(obsid):
    """
    find the last revision # of the given obsid
    input:  obsid   --- obsid
    output: rev     --- revision # in the form of "003"
    """

    obsid = str(obsid)

    try:
        list = Updates.objects.filter(obsid=obsid).order_by('rev')
        rev  = list[len(list)-1].rev
    except:
#
#--- if there is no record, just return '000'
#
        rev  = '000'

    return rev


#----------------------------------------------------------------------------------
#-- change_date_format: change date format from 12/01/15 to 151201               --
#----------------------------------------------------------------------------------

def change_date_format(date):
    """
    change date format from 12/01/15 to 151201
    input:  date    --- original date
    output: odate   --- modified date
    """
    
    try:
        atemp = re.split('\/', date)
        odate = atemp[2] + atemp[0] + atemp[1]
    except:
        odate = date

    return odate

#----------------------------------------------------------------------------------
#-- find_general_status: check general paremeter change status                  ---
#----------------------------------------------------------------------------------

def find_general_status(dat_dict):
    """
    check general paremeter change status
    input:  dat_dict    --- current data dictionary
    output: gen_status  --- generalstatus
    """

    [acis_list, time_list, roll_list, awin_list, gen_list] = ocf.get_param_lists()
    gen_status = 'NULL'
    for ent in gen_list:
        oent = 'org_' + ent
        if dat_dict[oent] != dat_dict[ent]:
            gen_status = 'NA'
            break
    if gen_status == 'NULL':
        try:
#
#--- time window parameter check
#
            ordr = int(float(dat_dict['time_ordr']))
            k = ordr + 1
            for i in range(1, k):
                for ent in time_list:
                    if ent == 'time_ordr':
                        continue
                    pannme = ent + str(i)
                    oname  = 'org_' + pname
                    if dat_dict[oname] != dat_dict[pname]:
                        gen_status = 'NA'
                        break
                if gen_status == 'NA':
                    break
        except:
            pass

        try:
#
#--- roll parameter check
#
            ordr = int(float(dat_dict['roll_ordr']))
            k = ordr + 1
            for i in range(1, k):
                for ent in roll_list:
                    if ent == 'roll_ordr':
                        continue
                    pname = ent + str(i)
                    oname = 'org_' + pname
                    if dat_dict[oname] != dat_dict[pname]:
                        gen_status = 'NA'
                        break
                if gen_status == 'NA':
                    break
        except:
            pass

    return gen_status

#----------------------------------------------------------------------------------
#-- find_acis_status: acis paremeter change status                               --
#----------------------------------------------------------------------------------

def find_acis_status(dat_dict):
    """
    check acis paremeter change status
    input:  dat_dict    --- current data dictionary
    output: acis_status --- acis status
    """
#
#--- check general acis parameters
#
    acis_status = 'NULL'
    for pname in acis_list:
        oname = 'org_' + pname

        chk = check_value_change(pname, dat_dict)
        if chk == 1:
            acis_status = 'NA'
            break
#
#--- check acis window ordered parameters
#
    if acis_status == 'NULL':
        try:
            ordr = int(float(dat_dict['ordr']))
            k = ordr + 1
            for i in range(1, k):
                for ent in awin_list:
                    if ent == 'ordr':
                        continue
                    pannme = ent + str(i)
                    if dat_dict[oname] != dat_dict[pname]:
                        acis_status = 'NA'
                        break
                if acis_status == 'NA':
                    break
        except:
            pass

    return acis_status
        
#----------------------------------------------------------------------------------
#-- find_si_mode_status: check si mode status                                   ---
#----------------------------------------------------------------------------------

def find_si_mode_status(dat_dict):
    """
    check si mode status
    input:  dat_dict    --- current data dictionary
    output: si_status   --- si mode status
    """
#
#--- NULL means no needs to check. NA meand that it requres checking of the change
#
    si_status = 'NULL'
    for pname in ['si_mode', 'instrument', 'est_cnt_rate', 'forder_cnt_rate', 'dither_flag']:

        chk = check_value_change(pname, dat_dict)
        if chk == 1:
            si_status = 'NA'
#
#--- checking extra for hrc case
#
    instrument = dat_dict['instrument']

    mc = re.search('hrc', instrument)
    if mc is not None:
        for pname in ['hrc_si_mode', 'hrc_config', 'hrc_zero_block']:

            chk = check_value_change(pname, dat_dict)
            if chk == 1:
                si_status = 'NA'
#
#--- this (acis case) does not happen as we cannot change target name, but it is in a requriement
#
    else:
        chk = check_value_change('targname', dat_dict)
        if chk == 1:
            chk1 = check_value_change('ra',  dat_dict)
            chk2 = check_value_change('dec', dat_dict)
            if chk1 == 1 or chk2 == 1:
                si_mode = 'NA'

    return si_status
        
#----------------------------------------------------------------------------------
#-- check_value_change: check whether parameter value changed from the original  --
#----------------------------------------------------------------------------------

def check_value_change(pname, dat_dict):
    """
    check whether parameter value changed from the original
    input:  pname       --- parameter name
            dat_dict    --- current data dictioinary
    ouput:  status      --- 1 if the value is changed, otherwise 0
    """

    oname = 'org_' + pname
    try:
        oval = dat_dict[oname]
    except:
        oval = None
    try:
        nval = dat_dict[pname]
    except:
        nval = None

    if oval != nval:
        status = 1 
    else:
        status = 0

    return status


#----------------------------------------------------------------------------------
#-- delete_from_updates_table_list: delete sql updates_table list entry          --
#----------------------------------------------------------------------------------

def delete_from_updates_table_list(obsidrev):
    """
    delete sql updates_table list entry
    input:  obsidrev   --- obsidrev
    output: updated sql updatestable list
    """

    try:
        app = Updates.objects.get(obsidrev=str(obsidrev))
        app.delete()
    except:
        pass

#----------------------------------------------------------------------------------
#-- sign_off_verified_column: sign off "verified" column if all others are signed off 
#----------------------------------------------------------------------------------

def sign_off_verified_column():
    """
    sign off "verified" column if all others are signed off
    it also sign off if higher rev version is already approved
    input:  none
    output: updated sql updatastable list
    """
#
#--- set today's date
#
    today    = time.strftime('%m/%d/%y')
#
#--- find which one is not verified yet
#
    olist = select_non_signed_off('verified')
    for ent in olist:
        obsidrev  = ent[0]
        general   = ent[1]
        acis      = ent[2]
        si_mode   = ent[3]
        verifired = ent[4]
        seqno     = ent[5]
        poc       = ent[6]
        date      = ent[7]
#
#--- check whether all others are signed off
#
        if general.lower() != 'na' and  acis.lower() != 'na' and si_mode.lower() != 'na':

            verified = poc  + ' ' + today
#
#--- update the sql database --- we are not doing automatic sign off (Oct 27. 2016) ----
#
            #add_to_updates_list(obsidrev, general, acis, si_mode, verified, seqno, poc, date, today)
#
#--- check this obsid is already in approved list (higher rev was already approved)
#--- if so, just sign off all of the entries including verified
#
        else:
            atemp = re.split('\.', obsidrev)
            obsid = atemp[0]

            olist = get_values_from_approved(obsid)

            if olist[1] != 'na':
                verified = poc  + ' ' + today

                if general.lower() == 'na':
                    general = verified

                if acis.lower()    == 'na':
                    acis    = verified

                if si_mode.lower() == 'na':
                    si_mode = verified

                add_to_updates_list(obsidrev, general, acis, si_mode, verified, seqno, poc, date, today)
                        


###################################################################################
#                  updates file related functions                                 #
###################################################################################


#----------------------------------------------------------------------------------
#-- add_updates_entry_to_sql: read data from updates directory and put them in sql database
#----------------------------------------------------------------------------------

def add_updates_entry_to_sql(alld =''):
    """
    read data from updates directory and put them in sql database
    input:  alld --- optional. if set to yes, all obsidrev data will be update.
            read from /data/mta4/CUS/www/Usint/ocat/updates_table.list
            and /data/mta4/CUS/www/Usint/ocat/updates/<obsid>.<rev>
    output: sqlite database
    """
#
#--- go through each data and add/update them to the database
#
    o_list = select_unique_obsidrev(alld)

    for obsidrev in o_list:
        try:
            add_data_in_updates_entry_sql(obsidrev)
        except:
            pass

#----------------------------------------------------------------------------------
#-- select_unique_obsidrev: create obsidrev list for all or only newly added    ---
#----------------------------------------------------------------------------------

def select_unique_obsidrev(alld=''):
    """
    create obsidrev list for all or only newly added
    input   alld --- if 'yes', it will create a list of all <obsid>.<rev>. else, only newly added ones
    output: unique_list --- a list of <obsid>.<rev>, either all of them or those just added
            
    """
#
#--- read entry list from updates_table.list
#

    f    = open(updates_table, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    new_list = []
    for ent in data:
        atemp = re.split('\s+', ent)
        new_list.append(atemp[0])

#
#--- if it is asked to re read all, return "data"
#
    if alld == 'yes':
        return new_list 
#
#--- else, just return a list with the new entry
#
    else:
        cdata = read_updates_list()
        prev_list = []
        for k in range(0, len(cdata)):
            prev_list.append(cdata[k][0])
    
        unique_list = [x for x in new_list if x not in prev_list]
    
        return unique_list
    
#----------------------------------------------------------------------------------
#-- add_data_in_updates_entry_sql: read one obsidrev data and add to sql database -
#----------------------------------------------------------------------------------

def add_data_in_updates_entry_sql(obsidrev):
    """
    read one obsidrev data and add to sql database
    input:  obsidrev    --- obsid + revision #
    outout: updated sqlite database
            it also returns True/False depending on the update worked or not
    """
#
#--- create the data dictionary for obsidrev
#
    try:
        pdict = rut.read_updates_table_list(obsidrev)
        add_to_update_entry(pdict, obsidrev)

        return  True
    except:
        return  False

#----------------------------------------------------------------------------------
#-- add_to_update_entry: add a new data entry to sqlite database                ---
#----------------------------------------------------------------------------------

def add_to_update_entry(pdict, obsidrev):
    """
    add a new data entry to sqlite database
    input: pdict    --- data dictionary containing all data
           obsidrev --- obsid + revision #
    outout: sqlite database update
    """
#
#-- find whether the data entry is already in the database.
#-- if so, just update values. otherwise creates a new entry
#
    try:
        data_list = Data_tables.objects.get(obsidrev = str(obsidrev))
    except:
        data_list = Data_tables(obsidrev = str(obsidrev))
#
#--- non updatable parameters
#
    data_list.title = pdict['title'][0]

    for pname in extra:
        try:
            try:
                val = str(pdict[pname][0])
            except:
                val = None
            exec 'data_list.%s = u"%s"' % (pname, val)
        except:
            exec 'data_list.%s = ""' % (pname)
#
#--- updatable parameters
#
    for pname in param_list:
        oname = 'org_' + pname
        rname = 'req_' + pname
        try:
            try:
                val = str(pdict[pname][0])
            except:
                val = None
            exec 'data_list.%s = u"%s"' % (oname, val)
        except:
            exec 'data_list.%s = u"" ' % (oname)
        try:
            try:
                val = str(pdict[pname][1])
            except:
                val = None
            exec 'data_list.%s = u"%s"' % (rname, val)
        except:
            exec 'data_list.%s = u"" ' % (rname)

#
#--- if the date is not set, find out today's data and add it
#
    try:
        test = pdict['date'][0]
    except:
        date  = today_date()
        odate = change_date_format(date)

        data_list.date  = date
        data_list.odate = odate
#
#--- save the update
#
    data_list.save()
        
#----------------------------------------------------------------------------------
#-- delete_from_updates_entry: delete sql updates entry of obsidrev              --
#----------------------------------------------------------------------------------

def delete_from_updates_entry(obsidrev):
    """
    delete sql updates entry of obsidrev
    input:  obsidrev   --- obsidrev
    output: database without the obsidrev data
    """

    try:
        data_list = Data_tables.objects.get(obsidrev = obsidrev)
        data_lsit.delete()
    except:
        pass

#----------------------------------------------------------------------------------
#-- read_updates_entries_to_dictionary: read data from sqlite database and put them into dictionary format
#----------------------------------------------------------------------------------

def read_updates_entries_to_dictionary(obsidrev):
    """
    read data from sqlite database and put them into dictionary format
    input:  obsidrev    ---- obsid + revision #
    output: pdict       ---- data dictionary
    """

    pdict = {}
#
#--- open the database
#
    try:
        data_list = Data_tables.objects.get(obsidrev = obsidrev)
#
#--- first no updatable parameters
#
        for pname in extra:
            try:
                exec 'val = data_list.%s' % (pname)
            except:
                val = None
            pdict[pname] = [val, val] 
#
#--- second, updatable parameters
#
        for pname in param_list:
            oname = 'org_' + pname
            rname = 'req_' + pname
            try:
                exec 'oval = data_list.%s' % (oname)
            except:
                oval = None
            try:
                exec 'nval = data_list.%s' % (rname)
            except:
                nval = None
    
            pdict[pname] = [oval, nval]
#
#--- if the data is not in the database, return blank data dictionary
#
    except:
        for pname in extra:
            pdict[pname] = ['', '']
        for pname in param_list:
            pdict[pname] = ['', '']


    return pdict


#----------------------------------------------------------------------------------
#-- print_out_update_entries: print out the data in human readable format       ---
#----------------------------------------------------------------------------------

def print_out_update_entries(obsidrev, outfile = ''):
    """
    print out the data in human readable format
    input:  obsidrev    ---- obsid + revision #
            outfile     ---- output directory/file path; if <blank> return content
    output: a file named "./obsidrev'
    """

    pdict = read_updates_entries_to_dictionary(obsidrev)
#
#--- get identification information first
#
    line  = ''
    line  = line + 'OBSID     = ' + pdict['obsid'][0] + '\n'
    line  = line + 'SEQNUM    = ' + pdict['seq_nbr'][0] + '\n'
    line  = line + 'TARGET    = ' + pdict['targname'][0] + '\n'
    line  = line + 'USER NAME = ' + pdict['poc'][0] + '\n'
    line  = line + 'VERIFIED AS ' + pdict['asis'][0] + '\n\n'
#
#--- comments
#
    line  = line + '\nPAST COMMENTS = \n'
    oval  = pdict['comments'][0]
    line  = line + oval
#
#--- if the new comment is identical to the original, skip it
#
    nval  = pdict['comments'][1]
    if nval != oval:
        line  = line + '\nNEW COMMENTS = \n'
        line  = line + nval + '\n'

    line  = line + '\nPAST REMARKS = \n'
    oval  = pdict['remarks'][0]
    line  = line + oval

    nval  = pdict['remarks'][1]
    if nval != oval:
        line  = line + '\nNEW REMARKS = \n'
        line  = line + nval + '\n'
#
#--- create acis related parameters since we need to handle them separately
#
    acis_related = acis_list + awin_list
#
#--- general information
#
    line  = line + '\n\nGENERAL CHANGES: \n'

    for pname in param_list:
        if pname in acis_related:
            continue
        if pname in ['comments', 'remarks']:
            continue

        try:
            oval = pdict[pname][0]
            nval = pdict[pname][1]
        except:
            continue

        if oval == nval:
            continue
        else:
            line = line + pname.upper()                + ocf.add_tab(pname, space=28)
            line = line + ' changed from ' + str(oval) + ocf.add_tab(str(oval), 15)
            line = line + ' to '           + str(nval) + '\n'
#
#--- acis parameters
#
    line  = line + '\nACIS CHANGES: \n'

    for pname in acis_list:

        try:
            oval = pdict[pname][0]
            nval = pdict[pname][1]
        except:
            continue

        if oval == nval:
            continue
        else:
            line = line + pname.upper()                + ocf.add_tab(pname, space=28)
            line = line + ' changed from ' + str(oval) + ocf.add_tab(str(oval), 15)
            line = line + ' to '           + str(nval) + '\n'
#
#--- acis window parameters
#
    line  = line + '\nACIS WINDOW CHANGES: \n'

    for pname in awin_list:

        try:
            oval = pdict[pname][0]
            nval = pdict[pname][1]
        except:
            continue 

        if oval == nval:
            continue
        else:
            line = line + pname.upper()                + ocf.add_tab(pname, space=28)
            line = line + ' changed from ' + str(oval) + ocf.add_tab(str(oval), 15)
            line = line + ' to '           + str(nval) + '\n'
#
#--- now print all parameters and their values
#

    line  = line + '\n\n'
    line  = line + '------------------------------------------------------------------------------------------\n'
    line  = line + 'Below is a listing of user modifiable obscat parameter values at the time of submission, \n'
    line  = line + 'as well as new values submitted from the form.  \n'
    line  = line + 'Note that new RA and Dec may be slightly off due to rounding errors in double conversion. \n'
    line  = line + ' \n'
    line  = line + 'PARAM NAME                  ORIGINAL VALUE              REQUESTED VALUE \n'
    line  = line + '------------------------------------------------------------------------------------------\n'
#
#--- removing order cases from the list; they will be handled seprately
#
    dlist  = remove_order_names(param_list, time_list, roll_list, awin_list)

    for pname in dlist:
        uname = pname.upper()
        try:
            oval  = pdict[pname][0]
        except:
            oval  = None
        try:
            nval  = pdict[pname][1]
        except:
            nval  = None
            
        line = create_each_line(pname, oval, nval, line)
#
#-- order cases (time_ordr, roll_ordr, ordr)
#
        if pname in ['window_flag', 'roll_flag', 'spwindow_flag']:
            oflag = oval
            nflag = nval

        if pname == 'time_ordr':
            aline = order_cases(oflag, nflag, 'time_ordr', time_list, pdict)
            line  = line + aline

        if pname == 'roll_ordr':
            aline = order_cases(oflag, nflag, 'roll_ordr', roll_list, pdict)
            line  = line + aline

        if pname == 'ordr':
            aline = order_cases(oflag, nflag, 'ordr',      awin_list, pdict)
            line  = line + aline
#
#--- return or write out the result
#
    if outfile == '':
        return  line
    else:
        fo    = open(outfile, 'w')
        fo.write(line)
        fo.close()

#----------------------------------------------------------------------------------
#-- extract_data_for_propnum: extract obsidrev for a give prop_num               --
#----------------------------------------------------------------------------------

def extract_data_for_propnum(prop_num):
    """
    extract obsidrev for a give prop_num
    input:  prop_num    --- proposal number
    output: alist       --- a list of obsidrev
    """

    data_list = Data_tables.objects.filter(prop_num = prop_num)
    alist = []
    for ent in data_list:
        alist.append(ent.obsidrev)

    return alist


#----------------------------------------------------------------------------------
#--  extract_values_for_given_obsidrev: extract vluaes of a given obsidrev       --
#----------------------------------------------------------------------------------

def extract_values_for_given_obsidrev(obsidrev):
    """
    extract vluaes of a given obsidrev
    input:  obsidrev    --- obsid + rev #
    output: data        --- the values of the obsidrev
    """

    data = Data_tables.objects.get(obsidrev=obsidrev)

    return data

#----------------------------------------------------------------------------------
#-- remove_order_names: removing ordered paramters from the full parameter list ---
#----------------------------------------------------------------------------------

def remove_order_names(olist, list1, list2, list3):
    """
    removing ordered paramters from the full parameter list
    input:  olist   --- the full parameter list
            list1, list2, list3     --- time order, roll order, and swpindow order param lists
    output: clist   --- the parameter list without ordered parameters
    """
    remove_list = []
    blist = list1 + list2 + list3
#
#--- order is between 1 and 6
#
    for i in range(1, 7):
        for name in blist:
            rname = name + str(i)
            remove_list.append(rname)

    clist  = create_missing_list(olist, remove_list)

    return clist
         

#----------------------------------------------------------------------------------
#-- order_cases: check order flag and if not N, print out all order              --
#----------------------------------------------------------------------------------

def order_cases(oflag, nflag, ordr_name, entry_list, pdict):
    """
    check order flag and if not N, print out all order
    input:  oflag       --- original flag value
            nflag       --- new flag value
            ordr_name   --- parameter name of the ordr (time_ordr, roll_ordr, rodr)
            entry_list  --- a list of parameters of that ordr case
            pdict       --- data dictionary
    output: line        --- printable results

    """

    line = ''
#
#--- for the case original and requested flag is 'N', just print names of parameters
#
    if oflag == 'N' and nflag == 'N':
        for oname in entry_list:
            line = line + oname.upper() + ocf.add_tab(oname, space=28)
            line = line + ocf.add_tab(' ')  + ocf.add_tab(' ')
            line = line + '\n'

            line = create_each_line(oname, ' ', ' ', line)
#
#--- in the older data, order is set 1 even if flag is N. So change order to 0 if that is the case
#
    else:
        pordr = ordr_value_to_numeric(pdict[ordr_name][0], oflag)
        nordr = ordr_value_to_numeric(pdict[ordr_name][1], nflag)
#
#--- user larger order values between original and current order
#
        ordr = pordr
        if nordr > pordr:
            ordr = nordr

        if ordr > 0:
            ordr1 = ordr + 1

            for i in range(1, ordr1):
                for name in entry_list:
                    oname = name + str(i)
                    oval  = pdict[oname][0]
                    nval  = pdict[oname][1]
    
                    if ocf.null_value(oval) or ocf.none_value(oval):
                        oval = ''
                    if ocf.null_value(nval) or ocf.none_value(nval):
                        nval = ''
     
                    line = create_each_line(oname, oval, nval, line)
#
#--- if ordr = 0, just print out the parameter names
#
        else: 
            for oname in entry_list:
                line = create_each_line(oname, ' ', ' ', line)

    return line

#----------------------------------------------------------------------------------
#-- ordr_value_to_numeric: convert ordr value into numeric value                 --
#----------------------------------------------------------------------------------

def ordr_value_to_numeric(ordr, flag):
    """
    convert ordr value into numeric value
    input:  ordr    ---- order value in string
            flag    ---- a flag of whether there should be order
    outout: ordr    ---- numerica order value
    """

    if flag == 'N':
        ordr = 0
    else:
        try:
            ordr = int(float(ordr))
        except:
            ordr = 0

    return ordr

#----------------------------------------------------------------------------------
#-- create_each_line: create display line for each entry                         --
#----------------------------------------------------------------------------------

def create_each_line(name, oval, nval, line):
    """
    create display line for each entry
    input:  name    --- parameter name
            oval    --- original value
            nval    --- current value
            line    --- string from the previous part
    output: line    --- line with the new entry
    """

    line = line + name.upper() + ocf.add_tab(name, space=28)
    line = line + str(oval)    + ocf.add_tab(str(oval))
    line = line + str(nval)    + ocf.add_tab(str(nval))
    line = line + '\n'

    return line

#----------------------------------------------------------------------------------
#-- create_missing_list: compare two list and find elements only in list1        --
#----------------------------------------------------------------------------------

def create_missing_list(list1, list2):
    """
    compare two list and find elements only in list1
    input:  list1, list2    --- two lists to be compared
    output: missing_list    --- a list with elements only in list1
    """
    missing_list     = [item for item in list1  if item not in list2]

    return missing_list



###################################################################################
#              update obs plan database related functions                         #
###################################################################################

#----------------------------------------------------------------------------------
#-- obs_plan_list_to_sql: update obs_plan sql database                          ---
#----------------------------------------------------------------------------------

def obs_plan_list_to_sql():
    """
    update obs_plan sql database
    input:  none but read from ascii table new_obs_list
    output: updated obs_plan sql databasse
    """
    f    = open(new_obs_list, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    for ent in data:
        atemp = re.split('\t+', ent)
        try:
            otype = atemp[0]
            seqno = atemp[1]
            obsid = atemp[2]
            status= atemp[3]
            poc   = ocf.poc_check(atemp[4])
            ao    = atemp[5]
            date  = atemp[6]

            replace_obs_plan_list(otype, seqno, obsid, status, poc, ao, date)
        except:
            pass
#
#---- remove achived and cancelled observations
#
    #delete_from_plan('archived')
    #delete_from_plan('canceled')

#----------------------------------------------------------------------------------
#-- replace_obs_plan_list: add or update sql  obs_plan list                     ---
#----------------------------------------------------------------------------------

def replace_obs_plan_list(otype, seqno, obsid, status, poc, ao, date):
    """
    add or update sql  obs_plan list
    input:  otype   --- observation type
            seqno   --- sequence number
            obsid   --- obsid
            status  --- status of the observation
            poc     --- poc
            ao      --- ao #
            date    --- planned observation date
    output: updated sql obs_plan list
    """
#
#--- the data is already in sql database
#
    try:
        obs_plan = Obs_plan.objects.get(obsid = str(obsid))
#
#--- the new data to add to sql database
    except:
        obs_plan = Obs_plan(obsid = str(obsid))

    obs_plan.otype = otype
    obs_plan.seqno = seqno
    obs_plan.poc   = poc
    obs_plan.ao    = ao
    obs_plan.date  = date
    obs_plan.status = status

    odate = change_date_format2(date)
    obs_plan.odate = odate

    obs_plan.save()

#----------------------------------------------------------------------------------
#-- change_date_format2: change date format from Jun 14 2016  3:48AM to 160614   --
#----------------------------------------------------------------------------------

def change_date_format2(date):
    """
    change date format from Jun 14 2016  3:48AM to 160614
    input:  date    --- original date
    output: odate   --- modified date
    """
    
    atemp = re.split('\s+', date)
    if len(atemp) > 3:
        mon  = atemp[0]
        day  = atemp[1]
        year = atemp[2]
        time = atemp[3]

        for i in range(0, 12):
            if mon == m_list[i]:
                imon = i + 1
                if imon < 10:
                    mon = '0' + str(imon)
                else:
                    mon = str(imon)
                break

        iday = float(day)
        if iday < 10:
            day = '0' + day

        
        odate = year[2] + year[3] + mon + day

    else:
        odate = date

    return odate


#----------------------------------------------------------------------------------
#-- delete_from_plan: delete  otype = dtype observation from the list            --
#----------------------------------------------------------------------------------

def delete_from_plan(dtype):
    """
    delete  otype = dtype observation from the list
    input:  dtype   --- type of the observation, usually archived or canceled
    output: updated obs_plan database
    """
    try:
        app = Obs_plan.objects.filter(otype=dtype)
        app.delete()
    except:
        pass


#----------------------------------------------------------------------------------
#-- extract_obs_plan: extract observation plan data for a given criteria         --
#----------------------------------------------------------------------------------

def extract_obs_plan(col, criteria):
    """
    extract observation plan data for a given criteria
    input:  col         --- column name
            criteria    --- selection criteria
    output: out_list    --- a list of lists of the data
    """

    dout  = Obs_plan.objects.filter(poc=criteria)

    out_list = []
    for ent in dout:
        temp_list = []
        temp_list.append(ent.obsid)
        temp_list.append(ent.seqno)
        temp_list.append(ent.otype)
        temp_list.append(ent.poc)
        temp_list.append(ent.status)
        temp_list.append(ent.ao)
        temp_list.append(ent.date)
        temp_list.append(ent.odate)
        out_list.append(temp_list)

    return out_list

#----------------------------------------------------------------------------------

###################################################################################
## User related database functions                                               ##
###################################################################################

#----------------------------------------------------------------------------------
#-- get_email_address: get poc email adfess from database                        --
#----------------------------------------------------------------------------------

def get_email_address(user):
    """
    get poc email adfess from database
    input:  user    ---- user ID
    output: email   ---- email address
    """

    try:
        profile = get_user_profile(user)
        email   = profile.email
    except:
        email   = ''
    return email


#----------------------------------------------------------------------------------
#-- get_userphones: get user's telephone #s and duty                            ---
#----------------------------------------------------------------------------------

def get_userphones(user):
    """
    get user profile information
    input:  user    --- user id
    output: profile.office  --- office telephone #
            profile.cell    --- cell telephone #
            pfofile.home    --- home telemphone #
            profile.duty    --- duty
    """

    out     = get_user_profile(user)
    profile = UserProfile.objects.get(id= out.id)

    return profile

#----------------------------------------------------------------------------------
#-- get_user_profile: get user profile from database                             --
#----------------------------------------------------------------------------------

def get_user_profile(user):
    """
    get user profile from database
    input:  user    --- user ID
            profile --- first name, last name, email address
    """

    profile = User.objects.get(username = user)

    return profile


#----------------------------------------------------------------------------------
#-- is_user_in_the_group: find whether the user belongs to the group             --
#----------------------------------------------------------------------------------

def is_user_in_the_group(user, group = 'POC'):
    """
    find whether the user belongs to the group
    input:  user    --- user name
            group   --- group name; defalut: POC
    output: True/False

    """
#
#--- cus is a super user and belong to POC
#
    if user == 'cus' and group == 'POC':
        return True
    else:
        group = Group.objects.get(name=group)
        user  = User.objects.get(username=user)
    
        if group in user.groups.all():
            return True
        else:
            return False

#------------------------------------------------------------------------------
#-- get_poc_list: retrun a list of POC                                       --
#------------------------------------------------------------------------------

def get_poc_list():
    """
    retrun a list of POC
    input:  none
    output: poc_list    --- a list of poc [user name, full name]
    """
    
    user_list = get_usernames()
    poc_list  = []
    for user in user_list:
        if is_user_in_the_group(user):
            full_name = get_full_name_from_username(user)
            poc_list.append([user, full_name])

    return poc_list

#------------------------------------------------------------------------------
#-- get_usernames: make a list of user names                                 --
#------------------------------------------------------------------------------

def get_usernames():
    """
    make a list of user names
    input:  none
    output: ulist   --- a list of user names
    """

    users = User.objects.all()

    ulist = []
    for ent in users:
        username = ent.username
        ulist.append(username)


    return ulist

#------------------------------------------------------------------------------
#-- make_username_dict: make a username dictionary cotaining name and email address 
#------------------------------------------------------------------------------

def make_username_dict(group=''):
    """
    make a username dictionary cotaining name and email address
    input:  none
    output: udict   --- a dictionary of list of ['first name', 'last name', 'email address']
    """

    users = User.objects.all()

    udict = {}
    for ent in users:
        username = ent.username
        if group != '':
           if is_user_in_the_group(username, group = group) :
                first    = ent.first_name
                last     = ent.last_name
                email    = ent.email
                tlist    = [first, last, email]
                udict[username] = tlist
           else:
                continue
        else:
            continue

    return udict

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

def get_userid_from_name(first, last):

    try:
        out = User.objects.filter(first_name=first).filter(last_name=last)
        out = str(out[0])
    except:
        out = last.lower()
    
    return out

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

def get_full_name_from_username(user):

    try:
        out = User.objects.get(username=user)
        first = out.first_name
        last  = out.last_name

        name  = first + ' ' + last
    except:
        name  = user

    return name

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

def add_usint_list():

    user_list = get_usernames()

    for username in user_list:
        try:
            usint = Usint.objects.get(username=username)
        except:
            usint = Usint(username=username)

        usint.status = 'usint'

    usint.save()



###################################################################################
### schedule related database functions                                         ###
###################################################################################


#----------------------------------------------------------------------------------
#-- add_schedule_entries_to_sql: read data from schedule table and add/update sql schedule database 
#----------------------------------------------------------------------------------

def add_schedule_entries_to_sql():
    """
    read data from schedule table and add/update sql schedule database
    input:  none
    output: updated schedule sql database

    """
    f    = open(schedule_list, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    for ent in data:
        atemp = re.split('\t+', ent)
        try:
            try:
                contact      = get_username(atemp[0])
                assigned     = atemp[7]
            except:
                contact  = 'TBD'
                assigned = ''
    
            start_month  = atemp[1]
            start_day    = atemp[2]
            start_year   = atemp[3]
            finish_month = atemp[4]
            finish_day   = atemp[5]
            finish_year  = atemp[6]
    
            mon    = int(float(start_month))
            date   = int(float(start_day))
            year   = int(float(start_year))
            start  = tcnv.convertDateToCTime(year, mon, date, 0, 0, 0)
    
            mon    = int(float(finish_month))
            date   = int(float(finish_day))
            year   = int(float(finish_year))
            finish = tcnv.convertDateToCTime(year, mon, date, 23, 59, 59) + 1.0
    
            add_to_schedule_list(start, finish, contact, start_month, start_day, start_year, \
                         finish_month, finish_day, finish_year, assigned)
        except:
            pass

#------------------------------------------------------------------------------
#-- get_username: find userid from given name ("<first name> <last name>")    -
#------------------------------------------------------------------------------

def get_username(name):
    """
    find userid from given name ("<first name> <last name>")
    input:  name    --- name in "<first name> <last name>"  e.g. "Scott Wolk"
    output: user    --- user id                             e.g. swolk
    """

    atemp = re.split('\s+', name)
    if len(atemp) == 1:
        user = name.lower()
    elif len(atemp) == 2:
        user = get_userid_from_name(atemp[0], atemp[1])
    elif len(atemp) == 3:
        first = atemp[0]
        last  = atemp[1] + ' ' + atemp[2]
        user  = get_userid_from_name(first, last)
    else:
        user = get_userid_from_name(atemp[0], atemp[1])

    return user
        

#----------------------------------------------------------------------------------
#-- add_to_schedule_list: add or update sql schedule list                       ---
#----------------------------------------------------------------------------------

def add_to_schedule_list(start, finish, contact, start_month, start_day, start_year,\
                           finish_month, finish_day, finish_year, assigned):
    """
    add or update sql schedule list
    input:  start       --- start time in sec from 1998.1.1
            finish      --- finish time in sec from 1998.1.1
            contact     --- poc 
            start_month --- start month 
            start_day   --- start day of the month
            start_year  --- start year
            finish_month--- finish month
            finish_day  --- finish day of the month
            finish_year --- finish year
            assigned    --- the id of the person who assigned the contact
    """
#
#--- the data is already in sql database
#
    try:
        schedule = Schedule.objects.get(start=start)
#
#--- the new data to add to sql database
    except:
        schedule = Schedule(start=start)

    schedule.start        = start
    schedule.finish       = finish
    schedule.contact      = contact
    schedule.start_month  = start_month
    schedule.start_day    = start_day
    schedule.start_year   = start_year
    schedule.finish_month = finish_month
    schedule.finish_day   = finish_day
    schedule.finish_year  = finish_year
    schedule.assigned     = assigned

    schedule.save()


#----------------------------------------------------------------------------------
#-- read_schedule_list: extract schedule from the database                       --
#----------------------------------------------------------------------------------

def read_schedule_list(begin, end):
    """
    extract schedule from the database
    input:  begin       --- beginning time in seconds from 1998.1.1
            end         --- ending time in seconds from 1998.1.1
    output: rlist       --- a list of lists:
                                [start, finish, contact, start_month, start_day, start_year, 
                                 finish_month, finish_day, finish_year, assigned]
    """

    schedule_list = Schedule.objects.filter(start__gte = begin).filter(finish__lte = end).order_by('start')

    rlist = []
    for schedule in schedule_list:
        start        = int(float(schedule.start))
        finish       = int(float(schedule.finish))
        start_month  = int(float(schedule.start_month))
        start_day    = int(float(schedule.start_day))
        start_year   = int(float(schedule.start_year))
        finish_month = int(float(schedule.finish_month))
        finish_day   = int(float(schedule.finish_day))
        finish_year  = int(float(schedule.finish_year))
        contact      = schedule.contact      
        assigned     = schedule.assigned     

        tlist = [start, finish, contact, start_month, start_day, start_year, \
                 finish_month, finish_day, finish_year, assigned]
        rlist.append(tlist)


    return rlist


#----------------------------------------------------------------------------------
#-- get_schedule_data: extract data from database and make a data dictionary     --
#----------------------------------------------------------------------------------

def get_schedule_data(start):
    """
    extract data from database and make a data dictionary
    input:  start   --- start time in seconds from 1998.1.1
    outpu:  rdict   --- data dictionary
    """

    data = Schedule.objects.get(start = start)

    rdict = {}
    for name in ['start', 'finish', 'contact', 'start_month', 'start_day', 'start_year',\
                     'finish_month', 'finish_day', 'finish_year', 'assigned']:

        rdict[name] = data.name


    return rdict

#----------------------------------------------------------------------------------
#-- delete_non_assigned_from_schedule: delete start=start data if assigned entry is empty 
#----------------------------------------------------------------------------------

def delete_non_assigned_from_schedule(start):
    """
    delete start=start data if assigned entry is empty
    input:  start   --- start time in seconds from 1998.1.1
    output: updated schedule database
    """
    try:
        app = Schedule.objects.filter(start=start).filter(assigned='')
        app.delete()
    except:
        pass

#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

def delete_from_schedule(start):
    """
    delete start=start data if assigned entry is empty
    input:  start   --- start time in seconds from 1998.1.1
    output: updated schedule database
    """
    try:
        app = Schedule.objects.filter(start=start)
        app.delete()
    except:
        pass

#----------------------------------------------------------------------------------
#-- get_schedule_date_for_poc: find the next duty period for poc                 --
#----------------------------------------------------------------------------------

def get_schedule_date_for_poc(poc):
    """
    find the next duty period for poc
    input:  poc     --- poc
    output: period  --- duty period
    """

    today = tcnv.currentTime('SEC1998')
#
#--- check all duty periods after today's date
#
    data =  Schedule.objects.filter(contact=poc).filter(start__gte = today).order_by('start')
#
#--- check whether the poc is currently in duty period
#
    test =  Schedule.objects.filter(contact=poc).filter(start__lte = today).filter(finish__gte = today)
    
    try:
        if len(test) > 0:
            pdate =  test[0]
        else:
            pdate =  data[0]

        smon  = pdate.start_month
        imon  = int(float(smon))
        smon  = m_list[imon-1]
        sday  = pdate.start_day
        syear = pdate.start_year
    
        emon  = pdate.finish_month
        imon  = int(float(emon))
        emon  = m_list[imon-1]
        eday  = pdate.finish_day
        eyear = pdate.finish_year

        period = smon + ' ' + sday + ', ' + syear + ' - ' + emon + ' ' + eday + ', ' + eyear

    except:
        period = 'No Duty Period Listed'

    return period


###################################################################################
###################################################################################
###################################################################################

#----------------------------------------------------------------------------------
#--clean_up_ocat_databases: remove all test trial data from database             --
#----------------------------------------------------------------------------------

def clean_up_ocat_databases():
    """
    remove all test trial data from database
    input:  none
    output: cleaned databases
    """
#
#--- clean up approved list
#
    update_approved_list()
#
#---- clean up updates_table list  database 
#
    clean_up_updates_list()
#
#---- clean up updates_table data entry database 
#
    clean_up_update_data_entry()
#
#--- copy the data
#        
    cmd = 'cp ' + updates_table + ' ' + temp_updates
    os.system(cmd)

#----------------------------------------------------------------------------------
#-- update_approved_list: clean up and update  approved list database            --
#----------------------------------------------------------------------------------

def update_approved_list():
    """
    clean up and update  approved list database
    input: none but read from databasse and the current approved_list
    output:updated database
    """

#
#--- read the previous approved list
#
    obsid_list1 = create_obs_ind_list(temp_approved)
#
#--- read the current approved list
#
    obsid_list2 = create_obs_ind_list(approved_list)
#
#--- read the approved data from sql database
#
    apps = Approved.objects.all()

    obsid_list3 = []
    for ent in apps:
        obsid_list3.append(ent.obsid)
#
#-- first remove test trial entries from sql database
#
    remove_list = create_missing_list(obsid_list3, obsid_list1)
#
#-- second add new approved entires to sql database
#
    add_list    = create_missing_list(obsid_list2, obsid_list1)

    clean_up_approved_list(remove_list, add_list)
#
#--- copy  approved list to ocatsite/temp/ directory  for the next update use
#
    cmd = 'cp ' + approved_list + ' ' + temp_approved
    os.system(cmd)



#----------------------------------------------------------------------------------
#-- clean_up_updates_list: cleaning up updates list                              --
#----------------------------------------------------------------------------------

def clean_up_updates_list():
    """
    cleaning up updates list 
    remove test entries created during the test phase, 
    """
#
#--- read the previous updates_list. this one is also contained modified results
#
    [changed_list, previous_list] = create_previous_list()
#
#--- remove added and changed entries from sql database
#
    for ent in changed_list:
        obsidrev = ent[0]
        delete_from_updates_table_list(obsidrev)
#
#--- read the current updates_table.list 
#
    current_list  = updates_list_lines(updates_table, cut=7, lform=1)
#
#--- compare the current and previous list and extract newly added ones
#
    replace_list  = create_missing_list(current_list, previous_list)

    for ent in replace_list:

        obsidrev = ent[0]
        general  = ent[1]
        acis     = ent[2]
        si_mode  = ent[3]
        verified = ent[4]
        seqno    = ent[5]
        poc      = ent[6]

        file     = '/data/mta4/CUS/www/Usint/ocat/updates/' + str(obsidrev)
        cdate    = ocf. find_file_modified_date(file)

        mdate    = find_date(ent)

        if cdate == None:
            cdate = mdate
        

        add_to_updates_list(obsidrev, general, acis, si_mode, verified, seqno, poc, cdate, mdate)

#----------------------------------------------------------------------------------
#-- create_previous_list: read and update the previously save updates_list file  --
#----------------------------------------------------------------------------------

def create_previous_list():
    """
    read and update the previously save updates_list file. 
    updated parts are those modified between the last time and now. 
    input:  none but read from ocatsite/temp/updates_table.list
    output: previous_list   --- a list of lists of the data
    """
#
#--- read the previous updates_table.list 
#
    previous_list = updates_list_lines(temp_updates,  cut=7, lform = 1)
#
#--- read database entries
#
    dbase_list    = read_updates_list()
#
#--- compare two of them and find entries changed from the last time
#--- test only the last 100 entries to save the time
#
    alist1 = previous_list[-100:]
    alist2 = dbase_list[-100:]

    changed_list = []

    for ent in alist2:
        chk = 1
        for comp in alist1:
            if ent[0] == comp[0]:
                chk = 0
                for k in range(1, 5):
                    if ent[k] != comp[k]:
                        chk = 1
                        break
        if chk > 0:
            changed_list.append(ent[:7])
#
#--- replace the changed entries in previous_list 
#
    if len(changed_list) > 0:
        temp_list = []
        for ent in previous_list:
            chk = 0
            for comp in changed_list:
                if ent[0] == comp[0]:
                    chk = 1
                    break
            if chk == 0:
                temp_list.append(ent)

        previous_list = temp_list

    return [changed_list, previous_list]

#----------------------------------------------------------------------------------
#-- clean_up_update_data_entry: clean up update data entry database             ---
#----------------------------------------------------------------------------------

def clean_up_update_data_entry():
    """
    clean up update data entry database
    input:  none, but read from database and files under updates directory
    outpu:  updated database
    """

#
#--- read the previous updates_table.list 
#
    obsidrev_list1 = create_obs_ind_list(temp_updates,  cut=7)
#
#--- read the current updates_table.list 
#
    obsidrev_list2 = create_obs_ind_list(updates_table, cut=7)
#
#--- read the obsidrev from updates data entry sql database
#
    obsidrev_list3 = []
    data_list = Data_tables.objects.all()
    for ent in data_list:
        obsidrev_list3.append(ent.obsidrev)
#
#-- create remove list for updates data entry list (these are added as "test" entries)
#
    remove_list  = create_missing_list(obsidrev_list3, obsidrev_list1)
#
#-- create add_list (these are added after the previous update)
#
    add_list     = create_missing_list(obsidrev_list2, obsidrev_list1)
#
#--- clean up update data entries
#
    clean_up_updates_entry(remove_list, add_list)

#----------------------------------------------------------------------------------
#-- create_obs_ind_list: read a file and make a list of the first element        --
#----------------------------------------------------------------------------------

def create_obs_ind_list(file, cut = 1):
    """
    read a file and make a list of the first element
    input:  file    --- file name
            cut     --- if given, remove the entry if the number of the elements
                        is smaller than the given value; defalut = 1
    output: olist   --- a list of the first element of the input file
    """
    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    olist = []
    for ent in data:
        atemp = re.split('\t+', ent)

        if len(atemp) < cut:
            continue

        olist.append(atemp[0])

    return olist

#----------------------------------------------------------------------------------
#-- clean_up_approved_list: cleaning up test cases out of approved list          --
#----------------------------------------------------------------------------------

def clean_up_approved_list(remove_list, add_list):
    """
    cleaning up test cases out of approved list
    this one is used during the test phase.
    input:  none, but the data will be read from the approve list and sql database
    output: clean up and updated sql approve list data
    """
#
#-- first remove test trial entries from sql database
#
    for obsid in  remove_list:
        delete_from_approved_list(obsid)
#
#-- second add new approved entires to sql database
#
    f    = open(approved_list, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    tdict = {}
    for ent in data:
        atemp = re.split('\t+|\s+', ent)
        tdict[atemp[0]] = ent

    for obsid in add_list:
        try:
            ent   = tdict[obsid]
        except:
            continue

        atemp = re.split('\t+|\s+', ent)
        obsid = atemp[0]
        seqno = atemp[1]
        poc   = atemp[2]
        date  = atemp[3]

        add_to_approved_list(obsid, seqno, poc, date)

#----------------------------------------------------------------------------------
#-- updates_list_lines: read updates_table.list and save each line               --
#----------------------------------------------------------------------------------

def updates_list_lines(file, cut=1, lform=0):
    """
    read updates_table.list and save each line
    input:  file    --- file name of the input
            cut     --- how many entries need to be the line has corrent # of data
            lform   --- if 0, save strings, if > 0, save lists ; defalut: 0
    output: olist   --- a list of entries
    """

    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    olist = []
    for ent in data:
        atemp = re.split('\t+', ent)

        if len(atemp) < cut:
            continue

        if lform > 0:
            olist.append(atemp)
        else:
            olist.append(ent)

    return olist

#----------------------------------------------------------------------------------
#-- clean_up_updates_entry: cleaning up updates record entry                     --
#----------------------------------------------------------------------------------

def clean_up_updates_entry(remove_list, add_list):
    """
    cleaning up updates record entry
    remove test entries created during the test phase, 
    """
#
#-- first remove the test trial data from the sql database
#
    for obsidrev in  remove_list:
        delete_from_updates_entry(obsidrev)
#
#-- second add the previously unknown data to the sql database
#
    for obsidrev in  add_list:
        add_data_in_updates_entry_sql(obsidrev)

