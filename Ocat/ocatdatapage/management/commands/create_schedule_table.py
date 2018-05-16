#############################################################################################################
#                                                                                                           #
#           create_schedule_table.py: create schedule web page and also send out notificaiton email         #
#                                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                       #
#                                                                                                           #
#           Last Update: Aug 31, 2016                                                                       #
#                                                                                                           #
#############################################################################################################

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

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

import mta_common_functions as mcf
import convertTimeFormat    as tcnv
import ocatdatabase_access  as oda
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
#
#-- location of the html page
#
web_dir  = '/data/mta4/CUS/www/Usint/Ocat/'             #--- this will be removed later
#
#--- admin
#
#admin = 'tisobe@cfa.harvard.edu,swolk@cfa.harvard.edu'
admin = 'tisobe@cfa.harvard.edu'
cus   = 'cus@head.cfa.harvard.edu'

#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------

class Command(BaseCommand):
    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):
        create_schedule_pate()

#------------------------------------------------------------------------------------------------------
#-- create_schedule_pate: update too_contact_schedule.html page and send out notification email      --
#------------------------------------------------------------------------------------------------------

def create_schedule_pate():
    """
    update too_contact_schedule.html page and send out notification email
    input:  none but the data are read from the database
    output: <web_dir>/too_contact_schedule.html
            notification emails
    """
#
#--- get user information 
#
    [users, name, email, office, cell, home, duty] = get_user_info()

    f    = open(template, 'r')
    page = f.read()
    f.close()

    today = tcnv.currentTime('sec1998')
    [start, stop,contact, start_mon, start_day, start_year, stop_mon, stop_day] = get_schedule_table()

    line = ''
    tbd_list = []
    for k in range(0, len(start)):

        user   = str(contact[k].lower())
#
#--- check whether user is 'tbd':
#
        if user.lower() == 'tbd' or user == '':
            tbd_list.append(k)


        if today >= start[k] and today <=stop[k]:
#
#--- update TOO-POC file so that outsider knows who is an responsible today
#
            update_too_poc_file(user)

            line = line + '<tr style="background-color:lime;">\n'
#
#--- check whether it is time to send out a reminder to the next poc
#
            pos = k + 1
            poc = str(contact[k+1].lower())
            send_duty_notification(today, pos, poc, start, start_mon, start_day, stop_mon, stop_day, office, cell, home, email)
        else:
            line = line + '<tr>\n'

        s1     = int(float(start_mon[k])) - 1
        s2     = int(float(stop_mon[k]))  - 1
        period = m_list[s1] + ' ' + start_day[k] + ' - ' + m_list[s2] + ' ' + stop_day[k]

        line = line + '\t<th>' + period  + '</th>\n'
        try:
            line = line + '\t<td>' + name[user] + '</td>\n'
        except:
            line = line + '\t<td>TBD</td>\n'
        try:
            line = line + '\t<td>' + office[user] + '</td>\n'
        except:
            line = line + '\t<td>&#160;</td>\n'
        try:
            line = line + '\t<td>' + cell[user]   + '</td>\n'
        except:
            line = line + '\t<td>&#160;</td>\n'
        try:
            line = line + '\t<td>' + home[user]   + '</td>\n'
        except:
            line = line + '\t<td>&#160;</td>\n'
        try:
            line = line + '\t<td>' + '<a href="' + email[user] +'">' + email[user] + '</a></td>\n'
        except:
            line = line + '\t<td>&#160;</td>\n'
        
        line = line + '</tr>\n\n'

    update = time.strftime("%d %b %Y", time.gmtime())

    page  = page.replace('#TABLE#',  line)
    page  = page.replace('#UPDATE#', update)

    wfile = web_dir + 'too_contact_schedule.html'
    fo = open(wfile, 'w')
    fo.write(page)
    fo.close()
#
#---- check how many more assignment left and if less than 8 left, send out warning email
#
    send_need_assignment_email(pos, tbd_list, start, start_mon, start_day, stop_mon, stop_day)

#------------------------------------------------------------------------------------------------------
#-- get_schedule_table: extract scheudle information                                                ---
#------------------------------------------------------------------------------------------------------

def get_schedule_table():
    """
    extract scheudle information
    input:  none
    output: start       --- start time in sec from 1998.1.1
            stop        --- stop time in sec from 1998.1.1
            contact     --- user/poc name
            start_mon   --- start month in digit
            start_day   --- start day
            start_year  --- start year
            stop_mon    --- stop month in digit
            stop_day    --- stop day
            stop_year   --- stop year
    """

    start       = []
    stop        = []
    contact     = []
    start_mon   = []
    start_day   = []
    start_year  = []
    stop_mon    = []
    stop_day    = []
    stop_year   = []
#
#--- set the starting time to 3.5 weeks before today's date
#
    begin = tcnv.currentTime('sec1998') - 2116800
    end   = begin + 86400 * 365 * 2             #---- two year range

    schedule   = oda.read_schedule_list(begin, end)

    for ent in schedule:
        start.append(float(ent[0]))
        stop.append(float(ent[1]))
        contact.append(str(ent[2]))
        start_mon.append(str(ent[3]))
        start_day.append(str(ent[4]))
        start_year.append(str(ent[5]))
        stop_mon.append(str(ent[6]))
        stop_day.append(str(ent[7]))
        stop_year.append(str(ent[8]))
        

    return [start, stop,contact, start_mon, start_day, start_year, stop_mon, stop_day]

#------------------------------------------------------------------------------------------------------
#-- get_user_info:  extract user information                                                         --
#------------------------------------------------------------------------------------------------------

def get_user_info():
    """
    extract user information 
    input: none
    output: user    --- user name
            name    --- full name
            email   --- email
            office  --- office telephone #
            cell    --- cell phone #
            home    --- home telephone #
            duty    --- duty
    """

    users  = oda.get_usernames()

    name   = {}
    email  = {}
    office = {}
    cell   = {}
    home   = {}
    duty   = {}

    for user in users:
        out1 = oda.get_user_profile(user)
        out2 = oda.get_userphones(user)

        name[user]   = out1.first_name + ' ' + out1.last_name
        email[user]  = out1.email
        office[user] = out2.office
        cell[user]   = out2.cell
        home[user]   = out2.home
        duty[user]   = out2.duty

    return [users, name, email, office, cell, home, duty]

#------------------------------------------------------------------------------------------------------
#-- user_name: some users use different name at the different place; adjust for this database        --
#------------------------------------------------------------------------------------------------------

def user_name(name):
    """
    some users use different name at the different place; adjust for this database
    input:  name    --- name in user database
            user    --- name in scheduler
    """
    user = str(name).lower()

    if user == 'swolk':
        user = 'wolk'

    elif user == 'jeanconn':
        user = 'connelly'
    
    elif user == 'brad':
        user = 'spitzbart'

    return user

#------------------------------------------------------------------------------------------------------
#-- send_duty_notification: send out a reminder to the next poc about a day before the duty starts   --
#------------------------------------------------------------------------------------------------------

def send_duty_notification(today, pos,  poc, start,  start_mon, start_day, stop_mon, stop_day, office, cell, home, email):
    """
    send out a reminder to the next poc about a day before the duty starts
    input:  today       --- today date in sec from 1998.1.1
            pos         --- index of the next duty cycle
            users       --- a list of users
            start       --- a list of start time in sec from 1998.1.1
            start_mon   --- a list of start month
            start_day   --- a list of start day
            stop_mon    --- a list of stop month
            stop_day    --- a list of stop day
            office      --- a list of office telephone #
            cell        --- a list of cell phone #
            home        --- a list of home phone #
            emial       --- a list of email
    output: sending out remider email
    """

    diff = start[pos] - today

    if diff < 129600 and diff > 43200:           #--- 1.5 day before but not less than a half day

        s1   = int(float(start_mon[pos])) - 1
        s2   = int(float(stop_mon[pos]))  - 1
        line = 'From midnight of ' +  m_list[s1] + ' ' + start_day[pos] + ' to ' + m_list[s2] + ' ' + stop_day[pos]
        #poc  = users[pos]
        line = line + 'the POC will be '  + poc  + '.\n'
        line = line + '\tOffice phone:\t' + office[poc] + '\n'
        line = line + '\tCell phone:\t'   + cell[poc]   + '\n'
        line = line + '\tHome phone:\t'   + home[poc]   + '\n'
        line = line + '\tEmail address:\t'+ email[poc]  + '\n\n'
        line = line + "If you have any questions about this email, please contact to Scott Wolk "
        line = line + "(swolk@head.cfa.harvard.edu), as no one will read email sent to the account.\n"

        fo   = open(zspace, 'w')
        fo.write(line)
        fo.close()

        #cmd = 'cat ' + zspace + '| mailx -s"Subject:TEST!!:  USINT TOO Point of Contact Updated\n\" -b' + admin + ' -c' + cus + ' ' + email[pos]
        cmd = 'cat ' + zspace + '| mailx -s"Subject:TEST!!:  USINT TOO Point of Contact Updated\n\"  ' + admin
        os.system(cmd)

#------------------------------------------------------------------------------------------------------
#-- send_need_assignment_email: send out need more sign up notification to admin                    ---
#------------------------------------------------------------------------------------------------------

def send_need_assignment_email(pos, tbd_list, start, start_mon, start_day, stop_mon, stop_day):
    """
    send out need more sign up notification to admin
    input:  pos         --- index of today's data position
            tbd_list    --- a list of indecies of location of tbd user
            start       --- a list of start in sec from 1998.1.1
            start_mon   --- a list of start month
            start_day   --- a list of start day
            stop_mon    --- a list of stop month
            stop_day    --- a list of stop day
    output: sending out a warning email
    """
#
#--- first check whether there are assignment gaps
#
    last = len(start)
    lpos = last -1
    line = ''
    if len(tbd_list) > 0:
        line = line +  'Point of Contact for the following period has not been assigned yet.\n\n'
        for k in tbd_list:

            if k == lpos:
                if last == 1:
                    line = ''
                break

            s1   = int(float(start_mon[k])) - 1
            s2   = int(float(stop_mon[k]))  - 1
            line = line +  m_list[s1] + ' ' + start_day[k] + ' - ' + m_list[s2] + ' ' + stop_day[k] + '\n'
#
#--- second check whether there are enough assignments left
#
    diff = last - pos
    if diff < 8:
        if line == '':
            line = line + 'There are not many assigned periods left.\n'
        else:
            line = line + '\n It is also that there are not many assigned periods left.\n'
#
#--- if the notification is created and this is Monday, send out email to admin
#
    today = time.strftime('%w')
    wday  = int(float(today))               #--- wday = 0: sunday
    
    if line != '' and wday == 1:
        line = line + '\nPlease notify all pocs to sign up for more periods.\n\n'

        fo   = open(zspace, 'w')
        fo.write(line)
        fo.close()

        cmd = 'cat ' + zspace + '| mailx -s"Subject:TEST!!:  POC Scheduler Needs More Sign-Ups\n\"  ' + admin
        os.system(cmd)


#------------------------------------------------------------------------------------------------------
#-- update_too_poc_file: write today's poc email address to TOO-POC file                             --
#------------------------------------------------------------------------------------------------------

def update_too_poc_file(poc):
    """
    write today's poc email address to TOO-POC file
    input:  poc         --- poc
    output  TOO-POC     --- a file contain email address of the poc
    """

    email = oda.get_email_address(poc)
#
#--- write it out
#
    ###ofile = '/home/mta/TOO-POC'
    ofile = base_dir + 'ocatsite/data_save/' + 'TOO-POC'

    f     = open(ofile, 'w')
    f.write(email)
    f.write('\n')
    f.close()
    
    cmd = 'chmod 644 ' + ofile
    os.system(cmd)


