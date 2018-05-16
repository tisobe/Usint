#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#   ocatsql.py: read data from sql database to fill all Ocat Data Page pamater values       #
#                                                                                           #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                           #
#                                                                                           #
#       last update: Aug 31, 2016                                                           #
#                                                                                           #
#############################################################################################

import sys
import os
import os.path
import string
import re
import copy
import unittest
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
zxc= base_dir + '/utils/'
sys.path.append(zxc)
#sys.path.append(mta_dir)
#
#--- sybase module
#
import DBI as dbi

def call():

    cmd = 'select  seq_nbr, targname, obj_flag, object  from target where obsid=1601'

    readSQL(cmd, 'axafocat', all='all')


#----------------------------------------------------------------------------------------------------------------
#-- readSQL: or a given sql command and database, return result in dictionary form                            ---
#----------------------------------------------------------------------------------------------------------------

def readSQL(cmd, database, all=''):

    """
    for a given sql command and database, return result in dictionary form.

    sqlbeta, sybase 15.5, on ascarc7/solaris
    arcbeta, sybase 15.7, on larcbeta/RHEL6.5


    """

    #db_user = 'browser'
    #server  = 'sqlbeta'
    #server  = 'sqlocc'
    server  = 'ocatsqlsrv'
    server  = 'sqlxtest'

    url     = os.path.realpath('.')
    mc      = re.search('icxc', url)
    if mc is not None:
        db_user = 'mtaops_internal_web'
        line    = pass_dir + '.targpass_internal'
        line    = pass_dir + '.targpass_itest'
    else:
        db_user = 'mtaops_public_web'
        line    = pass_dir + '.targpass_public'
        line    = pass_dir + '.targpass_ptest'

    db_user = 'mtaops_public_web'
    server  = 'sqltest'
    line      = pass_dir + '.targpass_ptest'

    #db_user = 'browser'
    #server  = 'ocatsqlsrv'
    #line      = pass_dir + '.targpass'
    f         = open(line, 'r')
    db_passwd = f.readline().strip()
    f.close()

    db = dbi.DBI(dbi='sybase', server=server, user=db_user, passwd=db_passwd, database=database)

    if all == '':
        outdata = db.fetchone(cmd)
    else:
        outdata = db.fetchall(cmd)

    fo = open('zout', 'w')
    line = str(cmd) + '\n\n'
    fo.write(line)
    line = str(outdata) + '\n'
    fo.write(line)
    fo.write('------------------------------------------\n\n')
    fo.close()

    return outdata

#----------------------------------------------------------------------

if __name__ == '__main__':
    call()
