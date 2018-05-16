#####################################################################################################
#                                                                                                   #
#           naggem.py: sending out sign off notification to appropriate parties                     #
#                                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                   #
#           Last Update: Aug 29, 2016                                                               #
#                                                                                                   #
#####################################################################################################

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
#
#--- page template
#
template = base_dir + 'ocatsite/templates/others/create_schedule_table_template'

#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------

class Command(BaseCommand):
    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):
#
#--- send out verification request notificaiton to poc
#
        verificaiton_request()
#
#--- send out weekly notification of sign off requests to responsible parties
#
        wday = int(float(time.strftime('%w',time.gmtime())))
#
#--- the email is sent out on Sunday
#
        if wday == 0:
            other_sign_off_request()
        

#------------------------------------------------------------------------------------------------------
#-- verificaiton_request: send out verification request email to poc                                 --
#------------------------------------------------------------------------------------------------------

def verificaiton_request():
    """
    send out verification request email to poc
    input:  none but read from  updates_table list
    output: email sent out
    """
#
#--- extract un-verified data from updates list
#
    unverified = oda.select_non_signed_off('verified')
#
#--- create a dictioany poc <---> obsidrev
#
    pdict    = {}
    poc_list = []
    for ent in unverified:
        obsrev = ent[0]
        gen    = ent[1].lower()
        acis   = ent[2].lower()
        si     = ent[3].lower()
        poc    = ent[6] 
        date   = ent[-1]
#
#--- if the request is older than two months ago, ignore
#
        if check_in_two_months(date) == False:
            continue 
        if (gen == 'na') or (acis == 'na') or (si == 'na'):
            continue

        try:
            olist = pdict[poc]
            olist.append(obsrev)
            pdict[poc] = olist
        except:
            pdict[poc] = [obsrev]
            poc_list.append(poc) 
#
#--- make sure that poc names appear only once in the list
#
    poc_list = list(set(poc_list))

    for poc in  poc_list:
        obs_list = pdict[poc]
        obs_list = list(set(obs_list))

        address = oda.get_email_address(poc)
        subject = "Verification needed for obsid.revs"

        text = "All requested edits have been made for the following obsid.revs:\n\n"
        content = make_sign_off_request_text(text, obs_list)

        send_sign_off_email(obs_list, address, text)

#------------------------------------------------------------------------------------------------------
#-- other_sign_off_request: send out general and acis sign off request email                         --
#------------------------------------------------------------------------------------------------------

def other_sign_off_request():
    """
    send out general and acis sign off request email
    input:  none, but read from updates_table list
    output: email sent out
    """
#
#--- extract entries which general column is not signed off
#
    entries  = oda.select_non_signed_off('general')
    obs_list = create_obs_list(entries)
    address  = "wink@head.cfa.harvard.edu,arots@head.cfa.harvard.edu,mccolml@head.cfa.harvard.edu"
    text     = "This message is a weekly summary of obsid.revs which need general (non-ACIS) changes:\n\n"
    send_sign_off_email(obs_list, address, text)
#
#--- extract entries which acis column is not signed off
#
    entries  = oda.select_non_signed_off('acis')
    obs_list = create_obs_list(entries)
    address  = 'arots\@head.cfa.harvard.edu'
    text     = "This message is a weekly summary of obsid.revs which need ACIS-specific changes:\n\n"
    send_sign_off_email(obs_list, address, text)

#
#--- extract entries which si mode column is not signed off
#
    entries  = oda.select_non_signed_off('si_mode')
    obs_list = create_obs_list(entries)
#
#--- separate them into acis and hrc cases
#
    acis_si  = []
    hrc_si   = []
    for ent in obs_list:
        atemp = re.split('\.', ent)
        db    = osq.OcatDB(int(fllat(atemp[0])))
        inst  = db.origValue('instrument')
        if inst.lower() == 'acis':
            acis_si.append(ent)
        else:
            hrc_si.append(ent)
#
# --- acis si
#
    if len(acis_si) > 0:
        address = 'acisdude@head.cfa.harvard.edu'
        text    = "This message is a weekly summary of obsid.revs which need SI-specific changes:\n\n"
        send_sign_off_email(acis_si, address, text)
#
#--- hrc si
#
    if len(hrc_si) > 0:
        address = 'juda@head.cfa.harvard.edu'
        text    = "This message is a weekly summary of obsid.revs which need SI-specific changes:\n\n"
        send_sign_off_email(acis_si, address, text)



#------------------------------------------------------------------------------------------------------
#-- create_obs_list: create a list of obsrevs                                                        --
#------------------------------------------------------------------------------------------------------

def create_obs_list(entries):
    """
    create a list of obsrevs
    input:  entries     --- a list of lists of [obsidrev, general, acis, si_mode, verified, seqno, poc, date]
    output: obs_list    --- a list of obsrevs
    """

    obs_list   = []
    for ent in entries:
        obsrev = ent[0] 
        date   = ent[-1]
        if check_in_two_months(date):
            obs_list.append(obsrev)

    obs_list = list(set(obs_list))

    return obs_list

#------------------------------------------------------------------------------------------------------
#-- send_sign_off_email: create and send out email                                                   --
#------------------------------------------------------------------------------------------------------

def send_sign_off_email(obs_list, address, text):
    """
    create and send out email
    input:  obs_list    --- a list of obsidrev
            address     --- email addresses ("," delimited)
            text        --- a starting part of email
    """
    if len(obs_list) > 0:

        cc      = "cus@head.cfa.harvard.edu"
        subject = "Updates needed for obsid.revs"

        ### REMOVE REMOVE REMOVE REMOVE ###
        line = address
        line = line.replace('@head.cfa.harvard.edu', '')
        line = line.replace('@cfa.harvard.edu', '')
        subject = subject + '(' + line + ')'
        address = 'tisobe@cfa.harvard.edu'
        ### REMOVE REMOVE REMOVE REMOVE ###

        content = make_sign_off_request_text(text, obs_list)

        ###clm.send_email(address, subject, content, cc=cc)
        clm.send_email(address, subject, content)

#------------------------------------------------------------------------------------------------------
#-- make_sign_off_request_text: create sign off request email                                        --
#------------------------------------------------------------------------------------------------------

def make_sign_off_request_text(text='', obs_list=[]):
    """
    create sign off request email
    input:  text        --- a starting part of the text
            obs_list    --- a list of obsidrevs
    output: text        --- a created text
    """

    for obs in obs_list:
        text = text + '\t\t' + obs + '\n'

    text = text + "\nPlease sign off these requests at this url:\n\n"
    text = text + durl + "/orupdate/.\n"
    text = text + "\nThis message is generated by a cron job, so no reply is necessary.\n"
    text = text + "\n\nIf you have any questions about this email, "
    text = text + "please contact swolk@head.cfa.harvard.edu.\n"

    return text


#------------------------------------------------------------------------------------------------------
#-- check_in_two_months: whether given data (mm/dd/yy) is in the last two months                     --
#------------------------------------------------------------------------------------------------------

def check_in_two_months(date):
    """
    whether given data (mm/dd/yy) is in the last two months
    input:  date    --- data in mm/dd/yy
    output: True/False
    """
#
#--- convert into seconds from 1998.1.1
#
    stime = ocf.convert_mmddyy_to_stime(date)
#
#--- find today's date in second from 1998.1.1
#
    today = tcnv.currentTime(format='SEC1998')
    diff  = today - stime

    if diff < 5184000:
        return True
    else:
        return False
