#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################################
#                                                                                                           #
#           find_planned_roll.py: find roll angle and the range from currently planned table                #
#                                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                       #
#                                                                                                           #
#           Last Update: Aug 29, 2016                                                                       #
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

#------------------------------------------------------------------------------------------------------
#-- find_planned_roll: find roll angle and the range from currently planned table                    --
#------------------------------------------------------------------------------------------------------

def find_planned_roll():
    """
    find roll angle and the range from currently planned table 
    input:  none but read from /proj/web-icxc/htdocs/mp/lts/lts-current.html
    output: <out_dir>/mp_long_term_roll --- a list of obsid:roll:range
    """

    f     = open('/proj/web-icxc/htdocs/mp/lts/lts-current.html', 'r')
    data  = [line.strip() for line in f.readlines()]
    f.close()

    ofile = base_dir + 'ocatsite/data_save/mp_long_term_roll'
    fo    = open(ofile, 'w')


    for ent in data:
#
#--- after "LTS changes", the file list different information
#
        mc = re.search('LTS changes', ent)
        if mc is not None:
            break
#
#--- find obsid
#
        mc = re.search('target.cgi', ent)
        if mc is not None:
            atemp = re.split('target_param.cgi\?', ent)
            btemp = re.split('">', atemp[1])
            obsid = btemp[0]
#
#--- find the positions of roll/range information
#
            btemp = re.split('\s+', ent)
            bcnt  = 0
            for test in btemp:
                mc1 = re.search('ACIS', test)
                mc2 = re.search('HRC',  test)
                if (mc1 is not None) or (mc2 is not None):
                    break
                else:
                    bcnt += 1
#
#--- count back from the instrument column to find the information needed
#
            pl_roll  = btemp[bcnt - 4]
            pl_range = btemp[bcnt - 3]

            line = obsid + ':' + pl_roll + ':' + pl_range + '\n'
            fo.write(line)

    fo.close()


#------------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    find_planned_roll()
