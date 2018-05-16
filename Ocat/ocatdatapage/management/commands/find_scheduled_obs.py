#############################################################################################################
#                                                                                                           #
#           find_scheduled_obs.py: extract scheduled obsids and mp who is responsible for those obs         #
#                                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                       #
#                                                                                                           #
#           Last Update: Aug 29, 2016                                                                       #
#                                                                                                           #
#############################################################################################################

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
import utils.ocatdatabase_access  as oda
import utils.mta_common_functions as mcf
import utils.convertTimeFormat    as tcnv
import utils.mta_common_functions as mcf
import utils.ocatCommonFunctions  as ocf
import utils.create_log_and_email as clm
import utils.ocatsql              as osq

import sys
import os
import string
import re
import unittest
import time
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
sys.path.append(base_dir)
sys.path.append(mta_dir)

#
#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

m_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------

class Command(BaseCommand):
    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):

        find_scheduled_obs()

#------------------------------------------------------------------------------------------------------
#-- find_scheduled_obs: extract scheduled obsids and mp who is responsible for those obs             --
#------------------------------------------------------------------------------------------------------

def find_scheduled_obs():
    """
    extract scheduled obsids and mp who is responsible for those obs
    input:  none but read from /data/mpcrit1/mplogs/
    output: <ocatsite>/data_save/scheduled_obs
    """
#
#--- find today date
#
    [year, mon, day]   = find_date()
#
#--- make a dictionary of mp <---> obsid list
#
    [mp_list, mp_dict] =  make_mp_file_list(year, mon, day)
#
#--- open output file
#
    out   = base_dir + 'ocatsite/data_save/scheduled_obs'
    fo    = open(out, 'w')

    for mp in mp_list:
        try:
            olist = mp_dict[mp]
        except:
            continue
#
#--- select obsid which are not observed yet
#
        olist = list(set(olist))
        olist = select_unobserved(olist)
        if len(olist) == 0:
            continue
#
#--- print the results out
#
        for obs in olist:
            line = str(obs) + '\t\t' + str(mp) + '\n'
            fo.write(line)
    fo.close()

#------------------------------------------------------------------------------------------------------
#-- find_date: find today's date                                                                     --
#------------------------------------------------------------------------------------------------------

def find_date():
    """
    find today's date
    input:  none
    ouput:  [year, mon, day] of today
    """

    out = time.strftime("%Y %m %d", time.gmtime())
    atemp = re.split('\s+', out)
    year  = int(float(atemp[0]))
    mon   = int(float(atemp[1]))
    day   = int(float(atemp[2]))

    return [year, mon, day]

#------------------------------------------------------------------------------------------------------
#-- make_mp_file_list: extract the names of mp files and create a dictionay of mp name <---> obsid list 
#------------------------------------------------------------------------------------------------------

def make_mp_file_list(year, mon, day):
    """
    extract the names of mp files and create a dictionay of mp name <---> obsid list
    input:  year    --- year of today
            mon     --- month of today
            day     --- day of today
    output: mp_list --- a list of mp id
            mp_dict --- a dictonary of mp id <---> obsid list
    """
#
#--- find all data directories for this month and the next
#
    [mp_list, file_list] = find_schedule_file(year, mon, day)

    mp_dict = {}
    for k in range(0, len(mp_list)):
        mp    = mp_list[k]
        mfile = file_list[k]

#
#--- extract mp ids and their observations
#
        obsids = extract_obsid_from_file(mfile)
        if len(obsids) > 0:
            try:
                olist = mp_dict[mp]
                olist = olist + obsids
                mp_dict[mp] = olist
            except:
                mp_dict[mp] = obsids
#
#--- create unique mp list
#
    mp_list = list(set(mp_list))

    return [mp_list, mp_dict]

#------------------------------------------------------------------------------------------------------
#-- find_schedule_file: find data directries for this month and the next                            ---
#------------------------------------------------------------------------------------------------------

def find_schedule_file(year, mon, day):
    """
    find data directries for this month and the next
    input:  year    --- year
            mon     --- month 
            day     --- day
    output: data    --- a list of directories
    """
    sday = day - 10
    if sday < 1:
        cmon1 = m_list[mon-2].upper()
        cmon2 =  m_list[mon-1].upper()
        sday = 20
    else:
        cmon1 =  m_list[mon-1].upper()
        cmon2 =  m_list[mon].upper()
#
#--- checking this month
#
    cmd1 = 'ls -ld  /data/mpcrit1/mplogs/' + str(year) + '/' + m_list[mon-1].upper() + '*/pre_scheduled/*.or > ' + zspace
    os.system(cmd1)
#
#--- if 10 days ago is the last month, check the last month
#
    if sday < 1:
        lmon  = mon - 1
        lyear = year 
        if lmon < 1:
            lmon  = 12
            lyear = year -1
        cmd2 = 'ls -ld /data/mpcrit1/mplogs/' + str(lyear) + '/' + m_list[lmon-1].upper() + '*/pre_scheduled/*.or >> ' + zspace
        os.system(cmd2)
#
#--- check the next month
#
    else:
        nmon = mon + 1
        if nmon > 12:
            nmon  = 1
            year += 1
        cmd2 = 'ls -ld /data/mpcrit1/mplogs/' + str(year) + '/' + m_list[nmon-1].upper() + '*/pre_scheduled/*.or >> ' + zspace
        os.system(cmd2)
#
#--- read the file
#
    f    = open(zspace, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    mcf.rm_file(zspace)
    
    mp_list   = []
    file_list = []
    for ent in data:
        mc = re.search('No match', ent)
        if mc is not None:
            continue 
#
#--- find mp id and a file name from the path name
#
        atemp = re.split('\s+', ent)
        mp    = atemp[2]
        mfile = atemp[-1]
#
#--- check the file is in the given date limit
#
        if check_date(mfile, sday, cmon1, cmon2) == 1:
            mp_list.append(mp)
            file_list.append(mfile)

    return [mp_list, file_list]

#------------------------------------------------------------------------------------------------------
#-- check_date: check the file is in the range of given period                                     ----
#------------------------------------------------------------------------------------------------------

def check_date(cfile, cday, cmon1, cmon2):
    """
    check the file is in the range of given period
    input:  cfile   --- file name
            cday    --- the cut of date
            cmon1   --- the first month (possibly the last month or this month)
            cmon2   --- the second month(possibly this month of the next month)
    output: 0 or 1 (1: yes)
    """
#
#--- the file name is something like: .../AUG0116_SOT.or
#
    atemp = re.split('\/', cfile)
    btemp = re.split('_SOT', atemp[-1])
    bmon  = btemp[0][0] + btemp[0][1] + btemp[0][2]
    bday  = btemp[0][3] + btemp[0][4]
    bday  = int(float(bday))
#
#--- the first month has a cut of day
#
    if bmon == cmon1:
        if bday >= cday:
            return 1
        else:
            return 0
#
#--- the second month
#
    elif bmon == cmon2:
            return 1
    else:
        return 0

#------------------------------------------------------------------------------------------------------
#-- extract_obsid_from_file: find mp person and her responsible observations                        ---
#------------------------------------------------------------------------------------------------------

def extract_obsid_from_file(mfile):
    """
    find mp person and her responsible observations
    input:  mfile   --- a file name
    output: obsids  --- a list of obsids
    """
#
#--- find  obsids
#
    f    = open(mfile, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    obsids = []
    chk    = 0
    for ent in data:
        if chk == 0:
#
#--- the obsid list starts from "OR QUICK..." and ends "OR QUICK..."
#
            mc = re.search('OR QUICK LOOK START', ent)
            if mc is not None:
                chk = 1
            continue
        else:
            mc = re.search('OR QUICK LOOK END', ent)
            if mc is not None:
                break
            else:
                atemp = re.split('\s+', ent)
                if len(atemp) == 0:
                   continue
                else:   
                    try:
                        val = int(float(atemp[1]))
                        obsids.append(val)
                    except:
                        pass

    return obsids
                         
#------------------------------------------------------------------------------------------------------
#-- select_unobserved: check whether the obsids in the list is unobserved                           ---
#------------------------------------------------------------------------------------------------------

def select_unobserved(olist):
    """
    check whether the obsids in the list is unobserved
    input:  olist       --- a list of obsids
    output: selected    --- a list of obsids which are not observed yet
    """

    selected = []
    for obsid in olist:
        db     = osq.OcatDB(int(float(obsid)))
        status = db.origValue('status').lower()
        if status in ['unobserved', 'scheduled']:
            selected.append(obsid)

    return selected

