#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#       related_obs_list.py:    for a given poc name, extract too, ddt and observations happens     #
#                               in the next 30 days                                                 #
#                                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                   #
#           last update: Aug 29, 2016                                                               #
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


#----------------------------------------------------------------------------------------------------------------
#-- collect_poc_obs_list: extract too, ddt and observations happens in the next 30 days                       ---
#----------------------------------------------------------------------------------------------------------------

def collect_poc_obs_list(poc):
    """
    for a given poc name, extract too, ddt and observations happens in the next 30 days
    input:  poc     --- person in charge
    output: [too_data, ddt_data, d30_data] a list of lists 
            each contain another list of [seq#, obsid, status, obs date]
    """
#
#--- convert poc name in the databases
#
    poc = check_poc_name(poc)

    too_data = read_data('too_list', poc)
    ddt_data = read_data('ddt_list', poc)

    d30_data = read_data('obs_in_30days', poc)

    return [too_data, ddt_data, d30_data]


#----------------------------------------------------------------------------------------------------------------
#-- read_data: read data and create a list of lists containing  [seq#, obsid, status, obs date]               ---
#----------------------------------------------------------------------------------------------------------------

def read_data(type, poc):
    """
    read data and create a list of lists containing  [seq#, obsid, status, obs date]
    input:  type    --- file name such as too_list, ddt_list, and obs_in_30days
            poc     --- person in charge
    output: a list of lists containing [seq#, obsid, status, obs date]
    """
#
#-- read approved list
#
    file    = ocat_dir + 'approved'
    f       = open(file, 'r')
    data    = [line.strip() for line in f.readlines()]
    f.close()

    approved = []
    for ent in data:
        atemp = re.split('\t+|\s+/', ent)
        try:
            approved.append(float(atemp[0]))
        except:
            pass

#
#-- set the directory path to the file
#
    too_dir = data_dir + 'too_contact_info/'
    file    = too_dir + type
    f       = open(file, 'r')
    data    = [line.strip() for line in f.readlines()]
    f.close()

    save = []
    for ent in data:
        atemp = re.split('\t+', ent)
        if atemp[4] == poc:
#
#-- save only unobserved and scheduled observations
#
            if atemp[3] in ['unobserved', 'scheduled']:

                chk = 'No'
                for comp in approved:
                    if comp == float(atemp[2]):
                        chk = 'Yes' 
                        break 

                save.append([atemp[1], atemp[2], atemp[3], atemp[6], chk])

    return save

#----------------------------------------------------------------------------------------------------------------
#-- check_poc_name: modify poc name if the poc in the files are different from email user name               ----
#----------------------------------------------------------------------------------------------------------------

def check_poc_name(poc):
    """
    modify poc name if the poc in the files are different from email user name
    input:  poc     --- person in charge in email user name
    output: poc     --- poc in the database/file
    """

    poc = poc.lower()

    if poc in ['nss', 'hermanm']:
        poc = 'hetg'
    elif poc in ['jdrake', 'jd']:
        poc = 'letg'
    elif poc == 'swolk':
        poc ='sjw'
    elif poc == 'zhao':
        poc = 'ping'

    return poc
        
#----------------------------------------------------------------------------------------------------------------
#-- check_open_sign_off_item: check whether the previously submitted items are still open                      --
#----------------------------------------------------------------------------------------------------------------

def check_open_sign_off_item(poc):
    """
    check whether the previously submitted items are still open
    input:  poc
    output: open_item   --- a list of "obsid.version" of open observation, e.g., 18112.001
    """

    file    = ocat_dir + 'updates_table.list'
    f       = open(file, 'r')
    data    = [line.strip() for line in f.readlines()]
    f.close()

    open_item = []
    for ent in data:
        try:
            atemp = re.split('\t+', ent)
            if atemp[4] == 'NULL':
                if atemp[6] == poc:
                    open_item.append(atemp[0])
        except: 
            pass

    return open_item
    

#----------------------------------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST  ---
#----------------------------------------------------------------------------------------------------------------

class TestFunction(unittest.TestCase):

    def test_collect_poc_obs_list(self):

        poc = 'swolk'

        [too, ddt, d30]  = collect_poc_obs_list(poc)

        for ent in too:
            print 'too: ' +  ent[0] + ', ' + ent[1] + ', ' +ent [2] + ', ' + ent[3]

        for ent in ddt:
            print 'ddt: ' +  ent[0] + ', ' + ent[1] + ', ' +ent [2] + ', ' + ent[3]

        for ent in d30:
            print 'd30: ' +  ent[0] + ', ' + ent[1] + ', ' +ent [2] + ', ' + ent[3]


#----------------------------------------------------------------------------------------------

if __name__ == "__main__":

    unittest.main()
    
