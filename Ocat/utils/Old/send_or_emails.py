#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#       send_or_emails.py:  sendout appropriated orupdate sign off/verified email                   #
#                                                                                                   #
#            author: t. isobe (tisobe@cfa.harvard.edu)                                              #
#                                                                                                   #
#            last update: Aug 10, 2015                                                              #
#                                                                                                   #
#####################################################################################################

import sys
import os
import re
import random
import unittest
#
#--- reading directory list
#
path = '/data/mta4/CUS/www/Usint/Ocat/ocatsite/static/dir_list_py'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
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
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)
#
#--- a few other directory/files..
#
log_dir               = '/data/mta4/CUS/www/Usint/Ocat/'          #---- where to save logs
changable_param_list  = '/data/mta4/CUS/www/Usint/Ocat/ocatsite/static/changable_param_list'

person_in_charge      = '/data/mta4/CUS/www/Usint/ocat/Info_save/too_contact_info/this_week_person_in_charge'
mp_schedule           = '/data/mta4/obs_ss/scheduled_obs_list'    #---- obsid<-->mp person list
usint_persons         = '/data/mta4/CUS/www/Usint/ocat/Info_save/too_contact_info/usint_personal'
#
#--- email address of admin
#
admin = 'tisobe@cfa.harvard.edu'
#
#--- ccd to who??
#
####ccaddress = 'cus@cfa.harvard.edu'
ccaddress = admin
#
#--- http addresses
#
orupdate_html = 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/orupdate.cgi'
ocat_html     = 'http://127.0.0.1:8000/ocatdatapage/ocatdatapage/'

#----------------------------------------------------------------------------------
#-- send_or_email: sending out orupdate email                                    --
#----------------------------------------------------------------------------------

def send_or_email(type, case, status,  poc, obsidrev):
    """
    sending out orupdate email
    input:  case    --- which one is just sign off
            status  --- status of gen/acis/si mode/verify sign off
            poc     --- person in charge
            type    --- observation type. too or ddt
            obsidrev--- obsid + revision #
    output: email sent out to an appropriate email address
    """

    fo = open('test_out', 'w')
    line = str(case) + '<-->' + str(status) + '<--->' + str(poc) + '<--->' + str(type) + '<--->' + str(obsidrev) + '\n'
    fo.write(line)
    fo.close()

#
#--- if this is too or ddt observations, send out notification
#
    if type in ('too', 'ddt'):
        send_or_too_ddt_email(type, case, status,  poc, obsidrev)

#
#--- if this is hrc case, send si mode verify request
#
    if (case == 1) and (status[2] == 'NULL'):
        send_hrc_si_email(obsidrev)        

#
#--- verified case; if approved stage, app_status = 1 else, 0
#
    if case == 4:
        if (status[1] == 'NULL') and (status[2] == 'NULL') and (status[3] == 'NULL'):
            app_status  = 1
        else:
            app_status  = 0

        send_verified_email(obsidrev, app_status, poc)

#----------------------------------------------------------------------------------
#-- send_or_too_ddt_email: sending out orupdate sign off request email  for too/ddt case
#----------------------------------------------------------------------------------

def send_or_too_ddt_email(type, case, status,  poc, obsidrev):
    """
    sending out orupdate sign off request email for too/ddt case
    input:  case    --- which one is just sign off
            status  --- status of gen/acis/si mode/verify sign off
            poc     --- person in charge
            type    --- observation type. too or ddt
            obsidrev--- obsid + revision #
    output: email sent out to an appropriate email address
    """

    out = too_ddt_prep_email(case, status,  poc, type, obsidrev)

    if out != None:
        [address, subject, content] = out
        send_email(address, subject, content, cc =ccaddress)


#----------------------------------------------------------------------------------
#-- too_ddt_prep_email: preparing to send out too/ddt signing off notification   --
#----------------------------------------------------------------------------------


def too_ddt_prep_email(case, status,  poc, type, obsidrev):
    """
    preparing to send out too/ddt signing off notification
    input:  case    --- which one is just sign off
            status  --- status of gen/acis/si mode/verify sign off
            poc     --- person in charge
            type    --- observation type. too or ddt
            obsidrev--- obsid + revision #
    output: [address, subject, content]
    """
    acis_text = "Editing of ACIS entries of " + str(obsidrev) + "  were finished and signed off. Please update SI Mode entries, then go to: " + orupdate_html + " and sign off SI Mode Status."

    si_text = "Editing of General entries of " + str(obsidrev) + " were finished and signed off. Please update SI Mode entries, then go to: " + orupdate_html + " and sign off SI Mode Status. "

    verify_text = "Editing of all entries of " + str(obsidrev) + "  were finished and signed off. Please verify it, then go to: " + orupdate_html + " and sign off 'Verified By' column."

    obsidrev = str(obsidrev)
    atemp    = re.split('\.', obsidrev)
    obsid    = atemp[0]

#
#--- if this is general/acis sign off, ask to sign off si mode, unless si mode is already signed off
#--- if that is the case, ask poc to verify
#
    if case in [1, 2]:
        if status[3] == 'NA':
            #####address = 'acisdude@head.cfa.harvard.edu'
            address = admin
            subject = type.upper() + ' SI Status Signed Off Request: OBSID: ' + str(obsid)
            if case == 1:
                content = si_text
            else:
                content = acis_text
        else:
            address = find_poc_email(poc)
            subject = type.upper() + ' Verification Signed Off Request: OBSID: ' + str(obsid)
            content = verify_text
#
#--- if this is si mode sign off, ask poc to verify
#
    elif case == 3:
        address = find_poc_email(poc)
        subject = type.upper() + ' Verification Signed Off Request: OBSID: ' + str(obsid)
        content = verify_text

    else:
        return None

    return [address, subject, content]

#----------------------------------------------------------------------------------
#-- send_hrc_si_email: sending si_mode sign off request to hrc                   --
#----------------------------------------------------------------------------------

def send_hrc_si_email(obsidrev):
    """
    sending si_mode sign off request to hrc
    input:  obsidrev    ---- obsid + revision #
    output: email to hrc poc (juda)
    """

    obsidrev = str(obsidrev)
    atemp    = re.split('\.', obsidrev)
    obsid    = atemp[0]

    address = 'juda@head.cfa.harvard.edu'
    subject = 'Signed Off Notice: ' + str(obsidrev)
    content = 'Please sign off SI Mode for obsid.rev: ' + str(obsidrev)
    content = content + 'at ' + orupdate_html + '. \n\n'
    content = content + 'This message is generated by a sign-off web page, so no reply is necessary.\n'

    send_email(address, subject, content, cc = ccaddress)

#----------------------------------------------------------------------------------
#-- send_verified_email: sending out this observation parameters are verified   ---
#----------------------------------------------------------------------------------

def send_verified_email(obsidrev, app_status, poc):
    """
    sending out this observation parameters are verified
    input:  obsidrev    --- obsid + revision #
            app_status  --- is this approved state? if so 1, else 0
            poc         --- person in charge
    output: email sent to poc
    """

    obsidrev = str(obsidrev)
    atemp    = re.split('\.', obsidrev)
    obsid    = atemp[0]

    address = find_poc_email(poc)

    subject = 'Subject: Signed Off Notice: ' + str(obsid)

    text1   = 'All requested edits have been made for the following obsid.rev: ' + str(obsidrev) + '. '
    test2   = 'This observation will be automatically approved in 24 hrs. '
    text3   = '\n\nPlease remember you still need to approve the observation at: ' + ocat_html + str(obsid)
    text4   = '\n\nThis message is generated by a sign-off web page, so no reply is necessary.\n'

    if app_status == 1:
        content = text1 + text2 + text4
    else:
        content = text1 + text3 + text4

    send_email(address, subject, content, cc = ccaddress)

#----------------------------------------------------------------------------------
#-- find_poc_email: find email address of poc                                    --
#----------------------------------------------------------------------------------

def find_poc_email(poc):
    """
    find email address of poc
    input:  poc     --- person in charge
    output: email   --- email address of poc
    """
    
    f    = open(usint_persons, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    email = ''
    for ent in data:
        mc = re.search(poc, ent)
        if mc is not None:
            atemp = re.split(':', ent)
            email = atemp[-1]
            break

#------ REMOVE LATER TEST TEST TEST ---------
    email = admin
#------ REMOVE LATER TEST TEST TEST ---------

    return email


#----------------------------------------------------------------------------------
#-- send_email: sending out email                                                --
#----------------------------------------------------------------------------------

def send_email(address, subject, content, cc = ''):
    """
    sending out email
    input:  address     --- email address. it can be multiple addresses, delimiated by ','.
            subject     --- head line of the email
            content     --- email content
            cc          --- cc email address; default: <blank> (no cc address)
    outout: email sent out
    """

    fo = open(zspace, 'w')
    fo.write(content)
    fo.close()

    if cc == '':
        cmd = 'cat ' + zspace + ' |mailx -s "Subject (TEST!!): ' + subject + '" ' + address  
    else:
        cmd = 'cat ' + zspace + ' |mailx -s "Subject (TEST!!): ' + subject + '" ' + ' -c' + cc + ' ' + address

    os.system(cmd)

    cmd = 'rm -rf ' + zspace
    os.system(cmd)


#----------------------------------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST  ---
#----------------------------------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """

    def test_send_email(self):

        address = 'tisobe@cfa.harvard.edu,isobe@head.cfa.harvard.edu'
        cc      = 'isobe@head.cfa.harvard.edu'
        subject = 'Test email'
        content = 'Testing email function "send_email". '

        ###send_email(address, subject, content, cc)

#---------------------------------------------------------------------------

    def test_find_poc_email(self):

        poc     = 'das'        
        address = find_poc_email(poc)
        self.assertEquals(address, 'das@cfa.harvard.edu')

        poc     = 'cal'        
        address = find_poc_email(poc)
        self.assertEquals(address, 'lpd@cfa.harvard.edu')

#---------------------------------------------------------------------------

    def test_too_ddt_prep_email(self):

        case = 1
        status   = ['12416.001', 'xxx', 'NA', 'NA', 'NA']
        poc      = 'das'
        type     = 'too'
        obsidrev = '12416.001'
        [address, subject, content] = too_ddt_prep_email(case, status,  poc, type, obsidrev)

        ######test1 = 'acisdude@head.cfa.harvard.edu'
        test1 = 'isobe@head.cfa.harvard.edu'
        test2 = 'TOO SI Status Signed Off Request: OBSID: 12416'
        test3 = 'Editing of General entries of 12416.001 were finished and signed off. Please update SI Mode entries, then go to: ' + orupdate_html + ' and sign off SI Mode Status. '

        self.assertEquals(address, test1)
        self.assertEquals(subject, test2)
        self.assertEquals(content, test3)

        case = 3
        status   = ['12416.001', 'xxx', 'xxx', 'xxx', 'NA']
        poc      = 'swolk'
        type     = 'too'
        obsidrev = '12416.001'
        [address, subject, content] = too_ddt_prep_email(case, status,  poc, type, obsidrev)

        print address
        print subject
        print content

        test1 = 'swolk@cfa.harvard.edu'
        test2 = 'TOO Verification Signed Off Request: OBSID: 12416'
        test3 = "Editing of all entries of 12416.001  were finished and signed off. Please verify it, then go to: " + orupdate_html + " and sign off 'Verified By' column."

        self.assertEquals(address, test1)
        self.assertEquals(subject, test2)
        self.assertEquals(content, test3)

        
#---------------------------------------------------------------------------

if __name__ == "__main__":

    unittest.main()

