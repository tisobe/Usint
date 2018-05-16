#!/usr/bin/env /proj/sot/ska/bin/python
#####################################################################################################
#                                                                                                   #
#   read_updates_list.py: read updates_table.list entries and prepare for the display               #
#                                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                   #
#           last update:    Aug 31, 2016                                                            #
#                                                                                                   #
#####################################################################################################

import sys
import os
import time
import re
import random
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
sys.path.append(base_dir)
sys.path.append(mta_dir)

import ocatCommonFunctions as ocf
import convertTimeFormat   as tcnv
import ocatsql             as osq
import ocatdatabase_access as oda

#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)

#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------

def extract_data_for_display():

    current = tcnv.currentTime('SEC1998')
    dayago  = current -172800

    update_list = oda.read_updates_list()

    display_list = []
    for ent in update_list:
        verify   = ent[4]
        sdate    = ent[7]
        if verify == 'NA':
           display_list.append(ent)
        else:
            stime = tcnv.convert_mmddyy_to_stime(sdate)
            if stime > dayago:
                display_list.append(ent)

    return display_list

#----------------------------------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST  ---
#----------------------------------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):

    def test_extract_data_for_display():
        """
        test test test
        """
        d_list = extract_data_for_display()
        print str(d_list)

#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

if __name__ == "__main__":

    """
    if you just run this script, it will run a test mode.
    """
    unittest.main()

