
#####################################################################################################
#                                                                                                   #
#        create_log_and_email.py: create a log and send out necessray email                         #
#                                                                                                   #
#            author: t. isobe (tisobe@cfa.harvard.edu)                                              #
#                                                                                                   #
#            last update: Nov 22, 2016                                                              #
#                                                                                                   #
#####################################################################################################

import sys
import os
import re
import random
import unittest
import time
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

import mta_common_functions as mcf
import ocatCommonFunctions  as ocf
import ocatsql              as osq
import ocatdatabase_access  as oda

#
#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)
#
#--- email address of admin
#
admin = 'tisobe@cfa.harvard.edu'
#
#--- cc to who??
#
####ccaddress = 'cus@cfa.harvard.edu'
ccaddress = admin
#
#--- http addresses
#
orupdate_html  = durl + '/orupdate/'
#
#--- is this test?
#
test = 'yes'


#----------------------------------------------------------------------------------


###################################################################################
###       send_email: sending out email                                         ###
###################################################################################

def send_email(address, subject, content, cc = '', submitter=''):
    """
    sending out email
    input:  address     --- email address. it can be multiple addresses, delimiated by ','.
            subject     --- head line of the email
            content     --- email content
            cc          --- cc email address; default: <blank> (no cc address)
    outout: email sent out
    """
#
#--- if this is a test, all email is sent to the submitter
#
    if test == 'yes':
        if submitter == '':
            address = admin
        else: 
            address = oda.get_email_address(submitter)
            address = admin

    fo = open(zspace, 'w')
    fo.write(content)
    fo.close()

    if cc == '':
        #cmd = 'cat ' + zspace + ' |mailx -s "Subject: ' + subject + '" ' + ' -b ' + admin + ' '  + address 
        cmd = 'cat ' + zspace + ' |mailx -s "Subject (TEST!!): ' + subject + '" ' + address  
    else:
        #cmd = 'cat ' + zspace + ' |mailx -s "Subject: ' + subject + '" ' + ' -c' + cc  + ' -b ' + admin + ' ' + address
        cmd = 'cat ' + zspace + ' |mailx -s "Subject (TEST!!): ' + subject + '" ' + ' -c' + cc + ' ' + address

    os.system(cmd)

    mcf.rm_file(zspace)

###################################################################################
###                 Ocat Data Page Related                                      ###
###################################################################################

#----------------------------------------------------------------------------------
#-- create_emails_and_save_log: create a log for the upated values and email   ----
#----------------------------------------------------------------------------------

def create_emails_and_save_log(dat_dict):
    """
    create a log for the upated values and send email
    input:  dat_dict    --- updated data dictionary
    output: email       --- email sent to the submitter
            log         --- a log in the form of obsid.revsion
    """
    obsid    = str(dat_dict['obsid'])
    rev      = oda.set_new_rev(obsid)
    obsidrev = str(obsid) + '.' + str(rev)
    user     = dat_dict['submitter']
    email    = oda.get_email_address(user)
#
#--- approved notification -----------------------------------
#   
    if dat_dict['asis'] == 'asis':
#
#--- add to approved list
#
        add_to_approved(dat_dict)
#
#--- add to updates data list/file
#
        oda.add_new_entry_to_update_list(dat_dict)
#
#--- sending out notification email
#
        content  = str(obsid) + ' is added on the approved list for flight. Thank you. \n\n'
        content  = content + oda.print_out_update_entries(obsidrev)
        headline = str(obsid) + ' Is Added On The Approved List For Flight.'
        send_email(email, headline, content)

#
#--- removed notification -----------------------------------
#   
    elif dat_dict['asis'] == 'remove':
#
#--- now delete it from approved list 
#
        oda.delete_from_approved_list(obsid)
#
#--- sending out notification email
#
        content  = str(obsid) + ' is removed from the approved list for flight. Thank you. \n'
        headline = str(obsid) + ' Is Removed From The Approved List For Flight.'
        send_email(email, headline, content)
#
#--- split notification -------------------------------------
#   
    elif dat_dict['asis'] == 'clone':
#
#--- add to updates data list/file
#
        ###oda.add_new_entry_to_update_list(dat_dict)
#
#--- sending out notification email
#
        content  = 'A split request for ' + obsid + ' is created. Thank you. \n'
        headline = 'Split Request For '   + obsid + ' Is Created.'
        send_email(email, headline, content)
#
#--- standard notification to the submitter ------------------
#
    elif dat_dict['asis'] == 'norm':
#
#--- add to updates data list/file
#
        oda.add_new_entry_to_update_list(dat_dict)
#
#--- sending out notification email
#
        content  = oda.print_out_update_entries(obsidrev)
        headline = 'Prameter Change Log: ' + obsidrev
        send_email(email, headline, content)
#
#--- OR notification ----------------------------------------
#
    try:
        check = dat_dict['or_notice']
        if check == 'yes':
            send_or_notification(obsid, rev, user, email)
    except:
        pass

#----------------------------------------------------------------------------------
#-- send_or_notification: create and send out OR notification                   ---
#----------------------------------------------------------------------------------

def send_or_notification(obsid, rev, user, email):
    """
    create and send out OR notification
    input: obsid    --- obsid
           rev      --- revision number
           user     --- submitter
           email    --- submitter's email
    output: eamil will be set to mp person who is responsible to the observation
    """
    sot_contact = 'swolk@cfa.harvard.edu'

    content = 'User: ' + user + ' submitted change of OBSID: ' + str(obsid)
    content = content + ' which is in the current OR list. '
    content = content + 'The contact email_address address is: ' + email + '\n\n'
    content = content + 'If you like to see what were changed: \n'
    content = content + durl + '/'  + chkupdata + str(obsid) + '.' + rev + '\n\n\n'
    content = content + 'If you have any question about this email, please contact '
    content = content + sot_contact + '\n'

    #mp_contact = ocf.mp_contact_email(obsid)
    mp_email   = 'mp@cfa.harvard.edu'

    headline   = 'Change to Obsid :' + str(obsid) + ' Which Is In Acitve OR List'

    if test == 'yes':
        headline   =  headline + ' (' + mp_email + ')'

    send_email(mp_email, headline, content, submitter=user)

#----------------------------------------------------------------------------------
#-- add_to_approved: add an approved observation in approved list                --
#----------------------------------------------------------------------------------

def add_to_approved(dat_dict):
    """
    add an approved observation in approved list
    input:  dat_dict
    output: none but updated approve list sql database
    """
    obsid = dat_dict['obsid']
    seqno = dat_dict['seq_nbr']
    poc   = dat_dict['submitter']
    date  = oda.today_date()

    oda.add_to_approved_list(obsid, seqno, poc, date)

#
#--- LTS Late Submission ------------------------------------
#
#--------------------------------------------------------------------------------
#-- send_lts_warning_email: send out lts late submission warning email         --
#--------------------------------------------------------------------------------

def send_lts_warning_email(lts_diff, submitter, obsid, rev):
    """
    send out lts late submission warning email
    input:  lts_diff    --- the numbers of days to lts date
            submitter   --- poc
            obsid       --- obsid
            rev         --- rev #
    output: warning email
    """
#
#--- poc email address
#
    email_address = oda.get_email_address(submitter)
#
#--- find out who is the mp contact person for this obsid
#
    mp_contact = ''
    mfile = obs_ss + 'scheduled_obs'
    f     = open(mfile, 'r')
    data  = [line.strip() for line in f.readlines()]
    f.close()

    for ent in data:
        atemp = re.split('\s+', ent)
        msave = atemp[1]
        if str(obsid) == atemp[0]:
            mp_contact = atemp[1]
            break
#
#--- if no mp is assigned for this obsid, use the last person listed on the list
#
    if mp_contact  == '':
        mp_contact = msave

    mp_email = 'mp@cfa.harvard.edu'
#
#--- create email content
#
    content  =  "Its Ocat Data Page is:\n"
    content  = content + durl + "/ocatdatapage/" + str(obsid) + "\n\n\n"
    content  = content + "If you like to see what were changed:\n"
    content  = content + durl + "/chkupdata/" + str(obsid) + '.' + str(rev) + "\n\n\n"
    content  = content + "If you have any question about this email, please contact "
    content  = content + "swolk@head.cfa.harvard.edu.\n\n\n"
#
#--- email to mp contact
#
    content2 =  "\n\nA user: " + submitter +" submitted changes of  "
    content2 = content2 + "OBSID: " + str(obsid) + " which is scheduled in " + str(lts_diff) + " days.\n\n"
    content2 = content2 + "The contact email_address address is: " + email_address + "\n\n"
    content2 = content2 + content
#
#--- email to poc
#
    content3 =  "\n\nA You submitted changes of  "
    content3 = content3 + "OBSID: " + str(obsid) + " which is scheduled in " + str(lts_diff) + " days.\n\n"
    content3 = content3 + "The email_address of MP of this observation: " + mp_email + '\n\n'
    content3 = content3 + content
#
#--- send email out
#
    headline   = 'Change to Obsid $obsid Which Is Scheduled in ' + str(lts_diff) + ' days'
    send_email(mp_email,      headline, content2, submitter=submitter)

    if test == 'yes':
        headline   = 'Change to Obsid $obsid Which Is Scheduled in' +  str(lts_diff) + ' days (' + mp_email + ')'

    send_email(email_address, headline, content3, submitter=submitter)

#####################################################################################################
###                Orupdate Page Related                                                          ###
#####################################################################################################

#----------------------------------------------------------------------------------
#-- send_or_email: sending out orupdate email                                    --
#----------------------------------------------------------------------------------

def send_or_email(otype, case, status,  poc, obsidrev, inst='ACIS'):
    """
    sending out orupdate email
    input:  otype   --- type of observation, e.g. too, ddt etc
            case    --- which one is just sign off
            status  --- a list of status of gen/acis/si mode/verify sign off
            poc     --- person in charge/submitter
            obsidrev--- obsid + revision #
    output: email sent out to an appropriate email address
    """
#
#--- if this is too or ddt observations, send out notification
#
    if otype in ('too', 'ddt'):
        send_or_too_ddt_email(otype, case, status,  poc, obsidrev)
#
#--- if this is hrc case, send si mode verify request
#
    if (case == 1) and (status[2] == 'NULL'):
        if (inst == 'HRC') and (status[3] == 'NA'):
            send_hrc_si_email(obsidrev, poc=poc)        
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

def send_or_too_ddt_email(otype, case, status,  poc, obsidrev):
    """
    sending out orupdate sign off request email for too/ddt case
    input:  case    --- which one is just sign off
            status  --- status of gen/acis/si mode/verify sign off
            poc     --- person in charge
            otype   --- observation type. too or ddt
            obsidrev--- obsid + revision #
    output: email sent out to an appropriate email address
    """

    out = too_ddt_prep_email(case, status,  poc, otype, obsidrev)

    if out != None:
        [address, subject, content] = out
        send_email(address, subject, content, submitter=poc)


#----------------------------------------------------------------------------------
#-- too_ddt_prep_email: preparing to send out too/ddt signing off notification   --
#----------------------------------------------------------------------------------

def too_ddt_prep_email(case, status,  poc, otype, obsidrev):
    """
    preparing to send out too/ddt signing off notification
    input:  case    --- which one is just sign off
            status  --- status of gen/acis/si mode/verify sign off
            poc     --- person in charge
            otype   --- observation type. too or ddt
            obsidrev--- obsid + revision #
    output: [address, subject, content]
    """
    acis_text = "Editing of ACIS entries of " + str(obsidrev)  + " were finished and signed off. Please update SI Mode entries, then go to: " + orupdate_html + " and sign off SI Mode Status."

    si_text = "Editing of General entries of " + str(obsidrev) + " were finished and signed off. Please update SI Mode entries, then go to: " + orupdate_html + " and sign off SI Mode Status. "

    verify_text = "Editing of all entries of " + str(obsidrev) + " were finished and signed off. Please verify it, then go to: " + orupdate_html + " and sign off 'Verified By' column."

    obsidrev = str(obsidrev)
    atemp    = re.split('\.', obsidrev)
    obsid    = atemp[0]
#
#--- if this is general/acis sign off, ask to sign off si mode, unless si mode is already signed off
#--- if that is the case, ask poc to verify
#
    if case in [1, 2]:
        if status[3] == 'NA':
            address = 'acisdude@head.cfa.harvard.edu'
            subject = otype.upper() + ' SI Status Signed Off Request: OBSID: ' + str(obsid)
            if case == 1:
                content = si_text
            else:
                content = acis_text
        else:
            address = oda.get_email_address(poc)
            subject = otype.upper() + ' Verification Signed Off Request: OBSID: ' + str(obsid)
            content = verify_text
#
#--- if this is si mode sign off, ask poc to verify
#
    elif case == 3:
        address = oda.get_email_address(poc)
        subject = otype.upper() + ' Verification Signed Off Request: OBSID: ' + str(obsid)
        content = verify_text

    else:
        return None

    return [address, subject, content]

#----------------------------------------------------------------------------------
#-- send_hrc_si_email: sending si_mode sign off request to hrc                   --
#----------------------------------------------------------------------------------

def send_hrc_si_email(obsidrev, poc=''):
    """
    sending si_mode sign off request to hrc
    input:  obsidrev    ---- obsid + revision #
            poc         ---- poc
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

    if test == 'yes':
        subject = subject + ' (to ' + address + ')'

    send_email(address, subject, content, submitter=poc)

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

    address = oda.get_email_address(poc)

    subject = 'Subject: Signed Off Notice: ' + str(obsid)

    text1   = 'All requested edits have been made for the following obsid.rev: ' + str(obsidrev) + '. '
    text2   = 'This observation will be automatically approved in 24 hrs. '
    text3   = '\n\nPlease remember you still need to approve the observation at: ' 
    text3   = text3 + durl + '/ocatdatapage/' + str(obsid)
    text4   = '\n\nThis message is generated by a sign-off web page, so no reply is necessary.\n'

    if app_status == 1:
        content = text1 + text2 + text4
    else:
        content = text1 + text3 + text4

    send_email(address, subject, content, submitter=poc)

#####################################################################################################
##            Express Approval Related                                                            ###
#####################################################################################################


#----------------------------------------------------------------------------------
#-- send_out_email_for_express_approval: sending out express approval related emails 
#----------------------------------------------------------------------------------

def send_out_email_for_express_approval(alist, poc):
    """
    sending out express approval related emails
    input:  alist   ---  a list of approved obsids
            poc     --- poc
    output:  email sent to poc and possibly mp_contact
    
    """

    if len(alist) == 0:
            return None
#
#--- check any of the observations are on OR list
#
    or_list = []
    for obsid in alist:
        if ocf.is_in_orlist(obsid):
            or_list.append(obsid)
#
#--- if obsids are on OR list, send email to MP contact
#
    if len(or_list) > 0:
        for obsid in or_list:
            rev        = oda.set_new_rev(obsid)
            mp_contact = ocf.mp_contact_email(obsid)
            mp_email   = mp_contact + '@head.cfa.harvard.edu'

            send_or_notification(obsid, rev, poc, mp_email)
#
#--- send a confirmation email to POC
#
    send_out_exp_app_confirmation_email(alist, or_list, poc)


#----------------------------------------------------------------------------------
#-- send_out_exp_app_confirmation_email: send out approved confirmation email    --
#----------------------------------------------------------------------------------

def send_out_exp_app_confirmation_email(alist, or_list, poc):
    """
    send out approved confirmation email
    input:  alist   --- a list of obsids
            or_list --- a list of obsids which are on OR list
            poc     --- POC
    output: email to POC
        """
#
#--- find poc email address
#
    email = oda.get_email_address(poc)
#
#--- check whether there are more than one entry
#
    if len(alist) == 1:
        content = "\n\nThe following obsid is added on the approved list, and ready for the flight.\n\n"
    else:
        content = "\n\nThe following obsids are added on the approved list, and ready for the flight.\n\n"
#
#--- create a list of obsid/obsidrev
#
    for obsid in alist:
        rev  = oda.find_the_last_rev(obsid)
        obsidrev = str(obsid) + '.' + str(rev)
        content = content + '\t\t' + str(obsid) + ': '
        content = content + durl + '/chkupdata/'  + str(obsidrev)  + '\n'
        if obsid in or_list:
            content = content + ' --- On OR list\n'
        else:
            content = content + '\n'

    subject = 'Approved Observation Notification'

    send_email(email, subject, content, submitter=poc)


#----------------------------------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST  ---
#----------------------------------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
#----------------------------------------------------------------------------------------------------------------
#---   orupdate related test                                                                                  ---
#----------------------------------------------------------------------------------------------------------------

    def test_send_email(self):

        address = 'tisobe@cfa.harvard.edu,isobe@head.cfa.harvard.edu'
        cc      = 'isobe@head.cfa.harvard.edu'
        subject = 'Test email'
        content = 'Testing email function "send_email". '

        ###send_email(address, subject, content, cc)

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
