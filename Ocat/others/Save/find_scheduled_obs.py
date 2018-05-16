#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################################
#                                                                                                           #
#           find_scheduled_obs.py: extract scheduled obsids and mp who is responsible for those obs         #
#                                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                       #
#                                                                                                           #
#           Last Update: Aug 17, 2016                                                                       #
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
path = '/data/mta4/CUS/www/Usint/Ocat/ocatsite/static/dir_list_py'

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
#
#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

m_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
#
#--- page template
#
template = base_dir + 'ocatsite/templates/others/create_schedule_table_template'

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
    out = time.strftime("%Y %m", time.gmtime())
    atemp = re.split('\s+', out)
    year  = int(float(atemp[0]))
    mon   = int(float(atemp[1]))
#
#--- find all data directories for this month and the next
#
    dirs  = find_schedule_file(year, mon)

    out   = base_dir + 'ocatsite/data_save/scheduled_obs'
    fo    = open(out, 'w')
    for ent in dirs:

        mc = re.search('No match', ent)
        if mc is not None:
            continue 
#
#--- extract mp ids and their observations
#
        [mp, obsids] = extract_obsid_from_file(ent)
#
#--- print the results out
#
        for obs in obsids:
            line = str(mp) + '\t\t' + str(obs) + '\n'
            fo.write(line)
    fo.close()

#------------------------------------------------------------------------------------------------------
#-- find_schedule_file: find data directries for this month and the next                            ---
#------------------------------------------------------------------------------------------------------

def find_schedule_file(year, mon):
    """
    find data directries for this month and the next
    input:  year    --- year
            mon     --- month 
    output: data    --- a list of directories
    """
#
#--- checking this month
#
    cmd1 = 'ls -d  /data/mpcrit1/mplogs/' + str(year) + '/' + m_list[mon-1].upper() + '*/pre_scheduled > ' + zspace
#
#--- check the next month
#
    nmon = mon + 1
    if nmon > 12:
        nmon  = 1
        year += 1
    cmd2 = 'ls -d /data/mpcrit1/mplogs/' + str(year) + '/' + m_list[nmon-1].upper() + '*/scheduled    >> ' + zspace
    os.system(cmd1)
    os.system(cmd2)

    f    = open(zspace, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    
    return data

#------------------------------------------------------------------------------------------------------
#-- extract_obsid_from_file: find mp person and her responsible observations                        ---
#------------------------------------------------------------------------------------------------------

def extract_obsid_from_file(indir):
    """
    find mp person and her responsible observations
    input:  indir   --- the directory name
    output: mp      --- mp id
            obsids  --- a list of obsids
    """
#
#--- find mp person
#
    cmd = 'ls -l ' + indir +  ' > ' + zspace
    os.system(cmd)

    f     = open(zspace, 'r')
    data  = [line.strip() for line in f.readlines()]
    f.close()
    mcf.rm_file(zspace)

    try:
        atemp = re.split('\s+', data[1])
        mp    = atemp[2]
    except:
        return ['', []]
#
#--- find  obsids
#
    orfile = ''
    for test in data:
        mc = re.search('.or', test)
        if mc is not None:
            atemp = re.split('\s+', test)
            orfile =  indir + '/' +  atemp[-1]
            break

    if orfile == '':
        return [mp, []]

    f    = open(orfile, 'r')
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

    return [mp, obsids]
                         

#------------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    find_scheduled_obs()
