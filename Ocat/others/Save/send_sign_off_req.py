#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################################
#                                                                                                           #
#           send_sign_off_req.py: sending out sign off notification to poc                                  #
#               THIS IS NOT USED SINCE WE CANNOT WRITE ON THE DATABASE (NO PERMISSION)                      #
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
import sqlite3
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

#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------

def send_sign_off_req():

    get_unsigned_off_data()




#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------

def get_unsigned_off_data():

    database = base_dir + 'db.sqlite3'
#
#--- read the database
#
    conn     = sqlite3.connect(database)
    c        = conn.cursor()

    poc_list   = []
    pid_list   = []
    for row in c.execute('select * from ocatdatapage_updates order by odate'):
        if row[5].lower() != 'na':
            continue

        elif row[2].lower() != 'na' and row[3].lower() != 'na' and row[4].lower() != 'na':
            pid   = row[0]
            poc   = row[7]
            today = time.strftime('%m/%d/%y')
            soff  = poc + ' ' + today
            poc_list.append(soff)
            pid_list.append(pid)

    conn.close()
#
#--- update the database
#
    conn     = sqlite3.connect(database)
    c        = conn.cursor()

    for k in range(0, len(pid_list)):
        pid  = pid_list[k]
        soff = poc_list[k]

        cmd  = 'UPDATE ocatdatapage_updates set VERIFIED = "' + str(soff) + '" where ID=' + str(pid)
        print cmd
        c.execute(cmd)
        conn.commit

    conn.close()


#------------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    send_sign_off_req()
