#########################################################################################################
#                                                                                                       #
#             scheduleSubmitter:django class to create Schedule Submitter Page                          #
#                                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                       #
#               Last update: Feb 23, 2018                                                               #
#                                                                                                       #
#########################################################################################################

import re
import sys
import os
import random
import unittest
import math
import time

from django.views.generic       import View
from django.http                import HttpRequest, HttpResponseRedirect
from django.template            import RequestContext

from django.shortcuts           import render_to_response, get_object_or_404
from django.contrib             import auth
from django.conf                import settings
from django.contrib.auth.models import User
from django.db                  import connection, models

import utils.ocatCommonFunctions as ocf         #--- various functions are saved here
import utils.prepdatdict         as pdd         #--- create data dictionary for the page
import utils.passWordCheck       as pwchk       #--- check user/password
import utils.ocatdatabase_access as oda         #--- accessing tools to ocat data page database
import utils.convertTimeFormat   as tcnv        #--- collections of time related conversion fuction
import utils.create_log_and_email as cle        #--- create a change log and send out eamil

import utils.login               as lp
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
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append path to a private folders
#
sys.path.append(base_dir)
sys.path.append(mta_dir)

import mta_common_functions as mcf
import convertTimeFormat    as tcnv
#
#--- some lists
#
contact_list = oda.get_poc_list()
contact_list = [['', '']] + contact_list + [['tbd', 'TBD']]

year_list    = ocf.make_year_list()

#----------------------------------------------------------------------------------
#-- scheduleSubmitter: class to manage Schedule submitter form                  ---
#----------------------------------------------------------------------------------

class scheduleSubmitter(View):
    """
    class to manage Schedule submitter form 
    """
#
#--- tamplate names
#
    template_name  = 'schedule_submitter/schedule_submitter.html'
    not_found_page = 'schedule_submitter/not_found_page.html'
#
#--- session expiration time in seconds
#
    time_exp = 3600 * 12

    org_list = []

#----------------------------------------------------------------------------------
#-- get: "get" submitted data and display an appropriate page                    --
#----------------------------------------------------------------------------------

    def get(self, request, *args,  **kwargs):
        """
        this  part display the schedule submitter page
        """
#-----------------------------------------------------
#--- LOGIN PAGE 
#-----------------------------------------------------

#
#--- check whether it is still under the same session with the same user. if not display a login page
#
        if request.user:
            s_user = request.user.username + '_session'
            try:
                if request.session[s_user] != 'yes':
                    if not request.user.is_authenticated():
                        return HttpResponseRedirect('/accounts/login/?next=%s' % '/ocatmain/')
            except:
                if not request.user.is_authenticated():
                    return HttpResponseRedirect('/accounts/login/?next=%s' % '/ocatmain/')
#
#--- every time the page is accessed/upated, the expiration clock is reset to the full length
#
            request.session[s_user] = 'yes'
            request.session.set_expiry(self.time_exp)
        else:
            if not request.user.is_authenticated():
                return HttpResponseRedirect('/accounts/login/?next=%s' % '/ocatmain/')

            s_user = request.user.username + '_session'
            request.session[s_user] = 'yes'
            request.session.set_expiry(self.time_exp)
#
#--- record the user's name for the later use
#
        self.submitter = request.user.username
#
#--- check whether the user is still using the default password; if so send back to main page
#
        path = join(BASE_DIR, 'ocatsite/static/compare')
        f    = open(path, 'r')
        test = f.read().strip()
        f.close()
        usert = User.objects.get(username=self.submitter)
        if usert.check_password(test):
            return HttpResponseRedirect('/ocatmain/')

#-----------------------------------------------------
#---- normal porcess starts here                  
#-----------------------------------------------------

        try:
#
#--- read parameters from form
#
            if request.method == 'POST':
                form = request.POST
            else:
                form = request.GET
#
#--- begining of the session
#
            self.prep_data()
            self.org_list = self.data_list
            self.warning  = ''
    
            self.make_wdict()
            return render_to_response(self.template_name, self.wdict, RequestContext(request))
#
#--- if something went wrong,  display the error page
#
        except:
            return render_to_response(self.not_found_page,  RequestContext(request))

#----------------------------------------------------------------------------------
#-- post: moving around data                                                     --
#----------------------------------------------------------------------------------

    def post(self, request, *args, **kwargs):
        """
        post data and save the data
        """
#-----------------------------------------------------
#--- LOGIN PAGE 
#-----------------------------------------------------

#
#--- check whether it is still under the same session with the same user. if not display a login page
#
        if request.user:
            s_user = request.user.username + '_session'
            try:
                if request.session[s_user] != 'yes':
                    if not request.user.is_authenticated():
                        return HttpResponseRedirect('/accounts/login/?next=%s' % '/ocatmain/')
            except:
                if not request.user.is_authenticated():
                    return HttpResponseRedirect('/accounts/login/?next=%s' % '/ocatmain/')
#
#--- every time the page is accessed/upated, the expiration clock is reset to the full length
#
            request.session[s_user] = 'yes'
            request.session.set_expiry(self.time_exp)
        else:
            if not request.user.is_authenticated():
                return HttpResponseRedirect('/accounts/login/?next=%s' % '/ocatmain/')

            s_user = request.user.username + '_session'
            request.session[s_user] = 'yes'
            request.session.set_expiry(self.time_exp)
#
#--- record the user's name for the later use
#
        self.submitter = request.user.username

#-----------------------------------------------------
#-----------------------------------------------------
#-----------------------------------------------------

        try:
#
#--- read parameters from form
#
            if request.method == 'POST':
                form = request.POST
            else:
                form = request.GET
    
            self.submitter = form['submitter']
    
            if ('check' in form) and (form['check']):
#
#--- update/submission requested
#
                if form['check'] == 'Update':
    
                    [data_list, id_list, warning]  = self.update_schedule_entry(form)
    
                    if len(warning) == 0:
                        self.update_schedule_databse(data_list, id_list)
    
                    self.prep_data()        #--- create self.data_list, self.id_list
                    self.org_list = self.data_list
                    self.warning  = ''
    
                    self.make_wdict()       #--- create self.wdict
                    return render_to_response(self.template_name, self.wdict, RequestContext(request))
#
#--- unlock of the data requested
#
            else:
                [sid, nid_list] = self.check_unlock_reqest(form)
    
                if sid is not None:
                    self.warning = self.unlock_the_list(form, sid, nid_list)
                    self.prep_data()
    
                    self.make_wdict()
                    return render_to_response(self.template_name, self.wdict, RequestContext(request))
#
#--- begining of the session
#
                else:
                    self.prep_data()
                    self.org_list = self.data_list
                    self.warning  = ''
    
                    self.make_wdict()
                    return render_to_response(self.template_name, self.wdict, RequestContext(request))
#
#--- if something went wrong,  display the error page
#
        except:
            return render_to_response(self.not_found_page,  RequestContext(request))


###########################################################################################
##                other functions listing starts here                                   ###
###########################################################################################

#----------------------------------------------------------------------------------
#-- make_wdict: make parameter dictionary                                        --
#----------------------------------------------------------------------------------

    def make_wdict(self):
        """
        make parameter dictionary
        input:  none (self)
        output: durl            --- url
                submitter       --- poc id 
                data_list       --- data list
                id_list         --- a list of ids of the data
                contact_lsit    --- a list of contact 
                day_list        --- a list of day (1 to 31)
                day_list2       --- a list of day (1 to 30)
                day_list3       --- a list of day (1 to 29)
                day_list4       --- a list of day (1 to 28)
                year_list       --- a list of year( current year +/- xxx year)
                warning         --- a list of warning
        """
        nlist = self.check_off_start(self.data_list)
        self.wdict = {
            'durl'          : durl,
            'data_list'     : nlist,
            'id_list'       : self.id_list,  
            'contact_list'  : contact_list, 
            'day_list'      : range(1, 32),
            'day_list2'     : range(1, 31), 
            'day_list3'     : range(1, 30), 
            'day_list4'     : range(1, 29),
            'year_list'     : year_list,
            'warning'       : self.warning,
            'submitter'     : self.submitter,
        }

#----------------------------------------------------------------------------------
#-- prep_data: prepare data to for display                                       --
#----------------------------------------------------------------------------------

    def prep_data(self):
        """
        prepare data to for display
        input:  none but read from database
        output: nlist: a list of dictionaries of each entry. 
                        see list_to_dict for content
        """
#
#--- find today's date
#
        tlist = tcnv.currentTime()
        line  = str(tlist[0]) + ':' + str(tlist[7]) + ':00:00:00'
        stime = tcnv.axTimeMTA(line)

        begin = stime -  28 * 86400     #--- 4 weeks before
        stop  = stime + 224 * 86400     #--- 8 months from now
#
#--- extract currently available data from database
#
        rlist = oda.read_schedule_list(begin, stop)
#
#--- separate them to closed and current list
#
        id_list = ''
        alist   = []
        for ent in rlist:
#
#--- use start time as id
#
            if id_list == "":
                id_list = str(ent[0])
            else:
                id_list = id_list + ':' + str(ent[0])
            if ent[1] <= stime:
                self.list_to_dict(ent, 'c')     #--- create self.odict
            else:
                self.list_to_dict(ent, 'n')

            alist.append(self.odict)
#
#--- fill the open list; first find the beginning of the open time
#
        last_entry = alist[-1]
        start   = last_entry['finish']
        s_year  = last_entry['finish_year']

        s_list  = ocf.find_ymd_from_stime(start)
#
#--- get the list of mon/day for the year of the last entry and the next year
#
        s_year  = int(float(s_year))
        w_list  = ocf.find_date_of_wday(s_year)
        n_year  = s_year + 1
        w_list2 = ocf.find_date_of_wday(n_year)
        w_list  = w_list + w_list2

        chk = 0
        for ent in w_list:
#
#--- find the first entry. usually start from Mon, but we do not know; so check it
#
            if chk == 0:
                if ent[0] >  start:
#
#--- fill from the end of the currently available list
#--- tlist = [start, finish, contact, s_mon, s_day, s_year f_mon, f_day, f_year, assigned]
#
                    id_list = id_list + ':' + str(start)
                    finish  = ent[0]
                    f_list  = ocf.find_ymd_from_stime(finish-86400)
                    tlist   = [start, finish, 'TBD'] + s_list + f_list + ['']
                    self.list_to_dict(tlist, 'y')
                    alist.append(self.odict)
#
#--- fill from the first of full Mon - Sun interval
#
                    id_list = id_list + ':' + str(ent[0])
                    s_list  = ocf.find_ymd_from_stime(ent[0])
                    finish  = ent[0] + 7 * 86400
                    f_list  = ocf.find_ymd_from_stime(finish-86400)
                    tlist   = [ent[0], finish, 'TBD'] + s_list + f_list + ['']
                    self.list_to_dict(tlist, 'y')
                    alist.append(self.odict)
                    chk = 1
                else:
                    continue
            else:
#
#--- if the 8 months from now is reached, stop
#
                if ent[0] > stop:
                    break
#
#--- fill data normally
#
                else:
                    id_list = id_list + ':' + str(ent[0])
                    s_list  = [ent[3], ent[4], ent[2]]
                    finish  = ent[0] + 7 * 86400
                    f_list  = ocf.find_ymd_from_stime(finish - 86400)
                    tlist   = [ent[0], finish, 'TBD'] + s_list + f_list + ['']
                    self.list_to_dict(tlist, 'y')
                    alist.append(self.odict)

        self.data_list = self.ordered_by_time(alist)
        self.id_list   = id_list


#----------------------------------------------------------------------------------
#-- check_unlock_reqest: check unlock request for the specific entry             --
#----------------------------------------------------------------------------------

    def check_unlock_reqest(self, form):
        """
        check unlock request for the specific entry
        input:  form    --- parameter form list
        output: [nid, id_list]  --- nid is the position of the "unlocked" entry
        """
#
#-- convert string into a list of ids
#
        try:
            id_string = form['id_list']
            id_list   = self.id_string_to_id_list(id_string)
        except:
            id_list   = []
#
#--- find which entry has the unlock request
#
        chk = 0
        if len(id_list) > 0:
            for nid in id_list:
                name = 'submit_' + str(nid) 
                if(name in form) and (form[name]):
                    if form[name] == "unlock":
                        chk  = 1
                        break

                    else:
                        continue 
                else:
                    continue

        if chk > 0:
            return  [nid,  id_list]
        else:
            return [ None, id_list]

#----------------------------------------------------------------------------------
#-- unlock_the_list: unlock the entry                                            --
#----------------------------------------------------------------------------------

    def unlock_the_list(self, form, nid, nid_list):
        """
        unlock the entry 
        input:  form        --- parameter form
                nid         --- position of the data with "unlock" request
                nid_list    --- strings of id names separated by ":"
                self.submitter   --- user ID
        output: warning     --- a list of data dictionary if something went wrong
        """
#
#--- read the current database
#
        self.prep_data()
        ndict = self.dat_list_to_dict(self.data_list)

        warning = []                  #--- saving the entries which have conflicts
        nid = int(float(nid))
        if self.submitter == ndict[nid]['assigned']:
            ndict[nid]['name']     = ''
            ndict[nid]['user']     = 'TBD'
            ndict[nid]['assigned'] = ''
            ndict[nid]['ochk']     = 'y'
#
#--- update database so that the row will be open when reloaded
#
            self.update_schedule(ndict[nid])

        else:
            warning.append(ndict[nid])

        return warning

#----------------------------------------------------------------------------------
#-- update_schedule_entry: return an updated list of data dictionaries           --
#----------------------------------------------------------------------------------

    def update_schedule_entry(self, form):
        """
        return an updated list of data dictionaries
        input:  form    --- parameter form
        output: slist   --- a list of data dictionaries
                id_list --- a string of data ids separated by ":"
                warning --- a list of data dictionaries with problems
        """
#
#--- first check whether anyone modified the database while we are trying to update the entries
#
        warning1 = []                  #--- saving the entries which have conflicts
        slist    = []                  #--- saving the entries with no problem
#
#--- read the current database
#
        self.prep_data()
        nid_list           = self.id_string_to_id_list(self.id_list)
        ndict              = self.dat_list_to_dict(self.data_list)
#
#--- update made by the user
#
        [alist, id_string] = self.recover_data_list(form)
        uid_list           = self.id_string_to_id_list(id_string)
        udict              = self.dat_list_to_dict(alist)

        for ind in nid_list:
            adict = ndict[ind]
            try:
                bdict = udict[ind]
            except:
                slist.append(adict)
                continue

            if adict == bdict:
                slist.append(bdict)
            else:
                if bdict['ochk'] == 't':
                    if adict['ochk'] == 'y':
                        slist.append(bdict)
#
#--- if the original data is an opened one, remove it from the database when the data are modified
#
                        if  adict['user'] in ['', 'tbd', 'TBD']:
                            oda.delete_from_schedule(adict['start'])
                    else:
                        warning1.append(adict)
                else:
                    slist.append(adict)
#
#--- check whether interval of the period changed
#
        blist = []
        for adict in slist:
            bdict  = self.check_inteval_change(adict)
            blist.append(bdict)
#
#--- check whether any gaps are created by the interval change
#
        [tlist, warning2] = self.check_gap_period(blist)

#
#--- remove all tbd entries after the last sign up and also the past signed up
#
        tot   = len(tlist)
        slist = []
        chk   = 0
        for k in range(0, tot):
            m = tot -k -1
            if chk == 0 and (tlist[m]['user'] in ['', 'tbd', 'TBD']):
                continue
            else:
                chk = 1
                slist.append(tlist[m])

        slist.reverse()
#
#--- update id_list and return the results
#
        id_list = ''
        for ent in slist:
            if id_list == '':
                id_list = str(ent['id'])
                prev    = str(ent['id'])
            else:
                if str(ent['id']) != prev:
                    id_list = id_list + ':' + str(ent['id'])
                    prev    = str(ent['id'])

        warning = warning1 + warning2

        return [slist, id_list, warning]


#----------------------------------------------------------------------------------
#-- update_schedule_databse: update schedule database for a given data           --
#----------------------------------------------------------------------------------

    def update_schedule_databse(self, data_list, id_string):
        """
        update schedule database for a given data 
        input:  data_list   --- a list of data dictionaries
                in_string   --- a string of data ID separateed by ":"
        ouput:  updated schedule database
        """

        for  adict in data_list:
#
#--- only a user is not NULL, update the data. the user includes "TBD"
#
            if not( adict['user'] in ['']):
                user = adict['user']

                chk = 0
                for ent in ['start', 'finish', 'start_month', 'start_day', 'start_year', \
                            'finish_month', 'finish_day', 'finish_year']:
                    try:
                        exec "%s = adict['%s']" % (ent, ent)
                     
                    except:
                        chk = 1
                        break
                if chk == 1:
                    continue
#
#--- assigned can be blank, but not other entires
# 
                try:
                    assigned = adict['assigned']
                except:
                    assigned = ''

                oda.add_to_schedule_list(start, finish, user, start_month, start_day, start_year,\
                                     finish_month, finish_day, finish_year, assigned)


#----------------------------------------------------------------------------------
#-- id_string_to_id_list: convert id_string separated by ":" into a list         --
#----------------------------------------------------------------------------------

    def id_string_to_id_list(self, id_string):
        """
        convert id_string separated by ":" into a list
        input:  id_string   --- string containing ID separated by ":"
        outpu:  id_list     --- a list of IDs
        """

        atemp  = re.split(':', id_string)
        id_list = []
        for ent in atemp:
            if ent == '':
                continue
            else:
                id_list.append(int(float(ent)))

        return id_list

#----------------------------------------------------------------------------------
#-- dat_list_to_dict: convert a list of dictionaries to a dictionary of dictionaries  
#----------------------------------------------------------------------------------

    def dat_list_to_dict(self, dat_list):
        """
        convert a list of dictionaries to a dictionary of dictionaries
        input:  dat_list    --- a list of dictionaries
        output: adict       --- a dictionary of data dictionaries. 
                                key is a starting time in seconds from 1998.1.1
        """
        adict = {}
        for ent in dat_list:
            sid = ent['id']
            adict[sid] = ent

        return adict

#----------------------------------------------------------------------------------
#-- update_schedule: update schedule database                                   ---
#----------------------------------------------------------------------------------

    def update_schedule(self, edict):
        """
        update schedule database 
        input:  edict   --- a dictionary containing updated data
        output: schedule database updated
        """

        contact      = edict['user']
        start_month  = edict['start_month']
        start_day    = edict['start_day']
        start_year   = edict['start_year']
        finish_month = edict['finish_month']
        finish_day   = edict['finish_day']
        finish_year  = edict['finish_year']
        assigned     = edict['assigned']
        start        = edict['start']
        finish       = edict['finish']

        oda.add_to_schedule_list(start, finish, contact, start_month, start_day, start_year, \
                         finish_month, finish_day, finish_year, assigned)

#----------------------------------------------------------------------------------
#-- find_stime: find time in seconds from 19981.1 for given year, month, and day --
#----------------------------------------------------------------------------------

    def find_stime(self, year, month, day):
        """
        find time in seconds from 19981.1 for given year, month, and day
        input:  year    --- year in 4 digits
                month   --- month
                day     --- day of month
        output: stime   --- time in seconds from 1998.1.1
        """

        year   = int(float(year))
        mon    = int(float(month))
        date   = int(float(day))

        stime  = tcnv.convertDateToCTime(year, mon, date, 0, 0, 0)

        return stime

#----------------------------------------------------------------------------------
#-- check_inteval_change: find interval change from the original settings        --
#----------------------------------------------------------------------------------

    def check_inteval_change(self, adict):
        """
        find interval change from the original settings
        input:  adict   --- a data dictionary
        output: orgid   --- the id of the original dictionary
                            if there is no change, orgid = ''
                adict   --- modified data dictionary according to interval changes
        """

        start   = adict['start']
        finish  = adict['finish']

        year    = adict['start_year']
        mon     = adict['start_month']
        day     = adict['start_day']
        day     = self.check_date_in_mon(year, mon, day)
        nstart  = self.find_stime(year, mon, day)

        year    = adict['finish_year']
        mon     = adict['finish_month']
        day     = adict['finish_day']
        day     = self.check_date_in_mon(year, mon, day)
        nfinish = self.find_stime(year, mon, day) + 86400

        adict['start']  = nstart
        adict['finish'] = nfinish 

        orgid   = ''
        if start != nstart:
            orgid = adict['id']
            adict['id'] =  str(nstart)
            
        return adict

#----------------------------------------------------------------------------------
#-- check_date_in_mon: check the day is beyond the last day of the month given   --
#----------------------------------------------------------------------------------

    def check_date_in_mon(self, year, mon, day):
        """
        check the day is beyond the last day of the month given
        input:  year    --- year
                mon     --- month
                day     --- day
        output: day     --- adjusted day (either 28, 29, 30, or 31)
        """
        year = int(float(year))
        mon  = int(float(mon))
        day  = int(float(day))

        lday = self.find_last_day_of_month(year, mon)

        if day > lday:
            return lday
        else:
            return day

#----------------------------------------------------------------------------------
#-- find_last_day_of_month: find the numbers of day in the given month           --
#----------------------------------------------------------------------------------

    def find_last_day_of_month(self, year, mon):
        """
        find the numbers of day in the given month
        input:  year    --- year
                mon     --- month
        output: lday    --- the numbers of the day in the month
        """
        
        if mon == 2:
            if  tcnv.isLeapYear(year) == 1:
                lday = 29
            else:
                lday = 28
        elif mon in [1, 3, 5, 7, 8, 10, 12]:
            lday = 31
        else:
            lday = 30

        return lday

#----------------------------------------------------------------------------------
#-- check_gap_period: find the time gaps in the data list and fill with a blank data 
#----------------------------------------------------------------------------------

    def check_gap_period(self, alist):
        """
        find the time gaps in the data list and fill with a blank data
        input:  alist   --- a list of data dictionaries
        output: alist   --- a list of data dictionaries with the gaps fileed/overlap fixed
                warning --- a list of data dictionary with potential problems
        """

        warning = []                    #--- data dictionaries with problems will be saved in this

        for i in range(1, len(alist)-1):
            wchk = 0                    #--- warning indicator 0: ok, 1: something wrong
#
#--- check only those just modified
#
            adict1 = alist[i]
            if adict1['ochk'] is not 't':
                continue

            start   = adict1['start']
            finish  = adict1['finish']
#
#--- extract data sets one before and one after
#
            adict0  = alist[i-1]
            adict2  = alist[i+1]
            pfinish = adict0['finish']
            nstart  = adict2['start']
#
#--- checking whether the given period set correctly
#            
            diff   = finish - start
#
#---- for the case the start and finish times are set in a reverse order
#
            if diff < 86400:
#
#--- try to set the correct starting and finishing time from the previous and next data sets
#
                if nstart >= pfinish:
                    [adict1, wchk] = self.change_start_stop_time(adict1, begin=pfinish, end=nstart)
                else:
                    wchk = 1
            else:
#
#--- check whether there are gaps or overlaps between the previous/next entries
#
                pchk    = 0
#
#--- there is an overlap with the previous period
#
                if start < pfinish:
                    alist = self.update_overlapped_period(alist, i,  'p')
                    pchk = 1
#
#--- there is a gap with the previous period
#
                elif start > pfinish:
                    alist = self.adjust_gap(alist, i, 'p')
                    pchk = 1
#
#--- there is an overlap with the next period
#
                if nstart < finish:
                    alist = self.update_overlapped_period(alist, i,  'n')
                    pchk = 1
#
#--- there is a gap with the next period
#
                elif nstart > finish:
                    alist = self.adjust_gap(alist, i, 'n')
                    pchk = 1
#
#--- the interval is set correctly
#
                if pchk == 0:
                    adict1['ochk'] = 'n'
                    alist[i]       = adict1
                    continue

        return [alist, warning]

#----------------------------------------------------------------------------------
#-- update_overlapped_period: check overlap cases and adjust boundaries of adjuscent entries
#----------------------------------------------------------------------------------

    def update_overlapped_period(self, alist, loc,  pos):
        """
        check overlap cases and adjust boundaries of adjuscent entries
        input:  alist   --- a list of data dictionaries
                loc     --- the indix of the main data dictioanry
                pos     --- if p, the overlap is with one before, if n, one after
        output: alist   --- updated alist and als adjucted database
        """

        if pos == 'p':
            sdict1 = alist[loc-1]
            sdict2 = alist[loc]
        else:
            sdict1 = alist[loc]
            sdict2 = alist[loc+1]
            nstart = sdict2['start']
#
#--- check whether they are fully overlapped or not
#
        schk = self.check_occulted_data(sdict1, sdict2)
#
#--- they are partially overlapped: adjust boundary if it can be done
#
        if schk == 0:
            [tdict1, tdict2, wout] = self.modify_dict_time_span(sdict1, sdict2, pos)
            if wout == 0:
                if pos == 'p':
                    alist[loc-1] = tdict1
                    alist[loc]   = tdict2
                else:
                    alist[loc]   = tdict1
                    alist[loc+1] = tdict2
#
#--- for the case that the overlap with the next entry, remove it before updating the data
#
                    oda.delete_from_schedule(nstart)
#
#--- adjustment cannot be done. put this set into warning list
#
            else:
                if pos == 'p':
                    warning.append(tdict2)
                else:
                    warning.append(tdict1)
#
#--- the sdict1 is fully occulted by the sdict2; if it is not signed up, remove sdict1
#
        elif schk == 1:
            if pos == 'p' and sdict1['user'] in ['', 'tbd', 'TBD']:
#
#--- make sure that the occultation does not go beyond the neighbour
#
                [sdict2, wchk] = self.change_start_stop_time(sdict2, begin=sdict1['start'], end=sdict2['finish'])
                alist[loc]     = sdict2
#
#--- remove the occulted one
#
                alist      = self.remove_entry_from_list(alist, loc-1)
#
#--- the sdict2 is fully occulted by the sdict1; if it is not signed up, remove sdict2
#
        elif schk == 2:
            if pos == 'n' and sdict2['user'] in ['', 'tbd', 'TBD']:
                [sdict1, wchk] = self.change_start_stop_time(sdict1, begin=sdict1['start'], end=sdict2['finish'])
                alist[loc]     = sdict1
                alist          = self.remove_entry_from_list(alist, loc+1)
        else:
            if pos == 'p':
                warning.append(sdict2)
            else:
                warning.append(sdict1)

        return alist

#----------------------------------------------------------------------------------
#-- remove_entry_from_list: removing the data from the list and the database     --
#----------------------------------------------------------------------------------

    def remove_entry_from_list(self, alist, loc):
        """
        removing the data from the list and the database
        input:  alist   --- a list of data dictionaries
                loc     --- the index of the main dictioanry position
        output: alist   --- updated alist and also updated database
        """
#
#--- remove the entry from the database
#
        oda.delete_non_assigned_from_schedule(alist[loc]['start'])
#
#--- remove the element from the current list
#
        del alist[loc]

        return alist

#----------------------------------------------------------------------------------
#-- adjust_gap: check the gaps between adjuscent data and fill the gaps          --
#----------------------------------------------------------------------------------

    def adjust_gap(self, alist, loc, pos):
        """
        check the gaps between adjuscent data and fill the gaps
        input:  alist   --- a list of data dictionaries
                loc     --- index of the main data dictionay location
                pos     --- if y, check the gap with the previous one, if n, the next one
        output: alist   --- updated alist
        """

#
#--- if the previous one is not signed up yet, just extend the period
#
        if pos == 'p':
            adict1 = alist[loc-1]
            adict2 = alist[loc]
            chk    = 0

            if adict1['user'] in ['', 'tbd', 'TBD']:
                pstart  = adict1['start']
                pfinish = adict2['start']
#
#--- if the previous one is already signed up, add a new period
#
            else:
                pstart  = adict1['finish']
                pfinish =  adict2['start']
                chk     = 1

            ndict = self.add_blank_dict(pstart, pfinish)
            ndict['user']     = 'tbd'
            ndict['name']     = ''
            ndict['assigned'] = 'TBD'

            if chk == 0:
                alist[loc-1]    = ndict
            else:
                alist.insert(loc-1, ndict)

        else: 
            adict1 = alist[loc]
            adict2 = alist[loc+1]
            chk    = 0
#
#--- if the next one is not signed up yet, just extend the period
#
            if adict2['user'] in ['', 'tbd', 'TBD']:
                pstart  = adict1['finish']
                pfinish = adict2['finish']
                oda.delete_non_assigned_from_schedule(adict2['start'])
#
#--- if the next one is already signed up, add a new period
#
            else:
                pstart  = adict1['finish']
                pfinish = adict2['start']
                chk     = 1

            ndict = self.add_blank_dict(pstart, pfinish)
            ndict['user']     = 'tbd'
            ndict['name']     = ''
            ndict['assigned'] = 'TBD'

            if chk == 0:
                alist[loc+1]    = ndict
            else:
                alist.insert(loc+1, ndict)
    
        return alist


#----------------------------------------------------------------------------------
#-- modify_dict_time_span: adjust time intervals of two adjucent  data dictionaries to remove a gap 
#----------------------------------------------------------------------------------

    def modify_dict_time_span(self, mdict, cdict, pos):
        """
        adjust time intervals of two adjucent  data dictionaries to remove a gap
        input:  mdict  --- data dictionary to be modified first
                cdict  --- data dictionary to be modified if mdict modification failed
                pos    --- position fo the data to be modified (p: first one. n: the second one)
        output: mdict  --- possibly modified data dictionary
                cdict  --- possibly modified data dictionary
                wchk   --- indicator of problem, 0: no problem, 1: problem

        """
        wchk = 0
        if pos == 'p':
#
#--- first one is editable
#
            if mdict['user'] in ['', 'tbd', 'TBD']:

                if mdict['finish'] > cdict['start']:
                    mdict['finish'] = cdict['start']
                    [mdict, wchk] = self.change_start_stop_time(mdict, begin=mdict['start'], end=mdict['finish'])
#
#--- first one is not editable
#
            else:
                cdict['start'] = mdict['finish']
                [cdict, wchk] = self.change_start_stop_time(cdict, begin=cdict['start'], end=cdict['finish'])

        elif pos == 'n':
            if cdict['user'] in ['', 'tbd', 'TBD']:
#
#--- second one is editable
#
                if mdict['finish'] > cdict['start']:
                    cdict['start']  = mdict['finish']
                    [cdict, wchk] = self.change_start_stop_time(cdict, begin=cdict['start'], end=cdict['finish'])
#
#--- second one is not editable
#
            else:
                mdict['finish'] = cdict['start']
                [mdict, wchk] = self.change_start_stop_time(mdict, begin=mdict['start'], end=mdict['finish'])
        else:
            wchk = 1


        return [mdict, cdict, wchk]

#----------------------------------------------------------------------------------
#-- check_occulted_data: check whether a data dictionary when the period is fully occulted by the period of another data
#----------------------------------------------------------------------------------

    def check_occulted_data(self, tdict1, tdict2):
        """
        check whether a data dictionary when the period is fully occulted by the period of another data 
        input: tdict1   --- a data dictionary set 1
               tidct2   --- a data dictionary set 2
        output: chk     --- if 0: not fully occulted, 1: the first one is occulted, 2: the second one is occulted
        """
        start1 = tdict1['start']
        stop1  = tdict1['finish']
        start2 = tdict2['start']
        stop2  = tdict2['finish']

        warning = []
        chk     = 0
   
        if start2 >= start1 and stop2 <= stop1:
            chk = 2
       
        if start1 >= start2 and stop1 <= stop2:
            chk = 1

        return chk

#----------------------------------------------------------------------------------
#-- change_start_stop_time: change starting and/or finishing time of the data dictionary 
#----------------------------------------------------------------------------------

    def change_start_stop_time(self, adict, begin=0, end=0):
        """
        change starting and/or finishing time of the data dictionary
        input:  adict   --- a data dictionary
                begin   --- starting time in second from 1998.1.1; defalut = 0
                end     --- finishing time in second from 1998.1.1; default = 0
        output: adict   --- the updated data dictionary
                wchk    --- indicator of problems; 0: no problem found, 1: there is problems
        """

        wchk = 0
#
#--- starting time change requested
#
        if begin != 0:
            finish = adict['finish']
            if end != 0:
                finish = end

            if begin <= finish - 86400:
                adict['start'] = begin
                [mon, day, year] = ocf.find_ymd_from_stime(begin)
                adict['start_month'] = mon
                adict['start_day']   = day
                adict['start_year']  = year
            else:
                wchk = 1
#
#--- finishing time change requested
#        
        if end != 0:
            start  = adict['start']
            if  end >= start + 86400:
                adict['finish'] = end
                mend = end - 43200
                [mon, day, year] = ocf.find_ymd_from_stime(mend)
                adict['finish_month'] = mon
                adict['finish_day']   = day
                adict['finish_year']  = year
            else:
                wchk = 1

        adict['id'] = int(float(adict['start']))

        return [adict, wchk]


#----------------------------------------------------------------------------------
#-- add_blank_dict: create a blank dictionary for given time interval            --
#----------------------------------------------------------------------------------

    def add_blank_dict(self, start, finish):
        """
        create a blank dictionary for given time interval
        input:  start   --- start time in seconds from 1998.1.1
                finish  --- finish time in seconds from 1998.1.1
        output: adict   --- data dictionary
        """

        adict                 = {}       
        adict['start']        = start
        adict['finish']       = finish

        [mon, day, year]      = ocf.find_ymd_from_stime(start)
        adict['start_year']   = year
        adict['start_month']  = mon 
        adict['start_day']    = day 

        [mon, day, year]      = ocf.find_ymd_from_stime(finish - 86400)
        adict['finish_year']  = year
        adict['finish_month'] = mon 
        adict['finish_day']   = day 

        adict['id']           = int(float(start))
        adict['name']         = ''
        adict['user']         = 'tbd'
        adict['assigined']    = 'tbd'
        adict['ochk']         = 'y'

        return adict
            
#----------------------------------------------------------------------------------
#-- ordered_by_time: order the dictionary entry by time element                 ---
#----------------------------------------------------------------------------------

    def ordered_by_time(self, alist):
        """
        order the dictionary entry by time element
        input:  alist   --- a list of dictionaries
        output: nlist   --- a list of dictionaries rearrange by time order
        """

        start_time_list = []
        tdict           = {}
#
#--- ent is a dictionary and 'id' element is starting time in sec from 1998.1.1
#
        for ent in alist:
            start_time_list.append(ent['id'])
            tdict[ent['id']] = ent

        start_time_list.sort()
        nlist = []
        for sid in start_time_list:
            nlist.append(tdict[sid])

        return nlist

#----------------------------------------------------------------------------------
#-- list_to_dict: make a data dictionary from a given list                       --
#----------------------------------------------------------------------------------

    def list_to_dict(self, alist, status):
        """
        make a data dictionary from a given list
        input:  alist   --- a list: 
                        [start, finish, contact, s_mon, s_day, s_year
                         f_mon, f_day, f_year, assigned]
        output: self.odict   --- a dictionary with:
                        'name', 'start_month', 'start_day', 'start_year',
                        'finish_month', 'finish_day', 'finish_year', 
                        'assigned', 'id' 'name_id', 'start_month_id', 'start_day_id',
                        'start_year_id', 'finish_month_id', 'finish_day_id', 
                        'finish_year_id', 'assigned_id', 'ochk'
                            --- where id is start time in seconds from 1998.1.1
                            ---       ochk indicates: 'c': closed, 'n' : not open, 'y' :open
                                                      't': someone just signed
        """

        adict = {}

        adict['name']            = oda.get_full_name_from_username(alist[2])
        adict['user']            = alist[2]
        adict['start_month']     = alist[3]
        adict['start_day']       = alist[4]
        adict['start_year']      = alist[5]
        adict['finish_month']    = alist[6]
        adict['finish_day']      = alist[7]
        adict['finish_year']     = alist[8]
        adict['assigned']        = alist[9]
        adict['start']           = int(float(alist[0]))
        adict['finish']          = int(float(alist[1]))
        adict['id']              = int(float(alist[0]))
        adict['ochk']            = status 
        adict['submit']          = 'submit_' + str(alist[0])
#
#---- depending on month, the length of the day list changes (28, 29, 30, or 31)
#
        year  = int(float(alist[5]))
        mon   = int(float(alist[3]))
        dind1 = self.find_last_day_of_month(year, mon)

        year  = int(float(alist[8]))
        mon   = int(float(alist[6]))
        dind2 = self.find_last_day_of_month(year, mon)

        adict['dind_st']         = str(dind1)
        adict['dind_en']         = str(dind2)
#
#--- if user is still 'TBD' or if it is not signed, keep the entry status "open" and field editable
#
        if alist[2].lower() == 'tbd' or alist[0] == '':
            adict['ochk']            = 'y'

            adict['name_id']         = 'name_'         + str(alist[0])
            adict['user_id']         = 'user_'         + str(alist[0])
            adict['start_month_id']  = 'start_month_'  + str(alist[0])
            adict['start_day_id']    = 'start_day_'    + str(alist[0])
            adict['start_year_id']   = 'start_year_'   + str(alist[0])
            adict['finish_month_id'] = 'finish_month_' + str(alist[0])
            adict['finish_day_id']   = 'finish_day_'   + str(alist[0])
            adict['finish_year_id']  = 'finish_year_'  + str(alist[0])
            adict['assigned_id']     = 'assigned_'     + str(alist[0])
            adict['start_id']        = 'start_'        + str(alist[0])
            adict['finish_id']       = 'finish_'       + str(alist[0])
            adict['id_id']           = 'id_'           + str(alist[0])
            adict['ochk_id']         = 'ochk_'         + str(alist[0])
            adict['submit']          = 'submit_'       + str(alist[0])
        
        self.odict = adict

#----------------------------------------------------------------------------------
#-- recover_data_list: reconstruct input data list from the form passed         ---
#----------------------------------------------------------------------------------

    def recover_data_list(self, form):
        """
        reconstruct input data list from the form passed
        input:  form        --- form passed
        output: alist       --- a list of dictionaries which have data for each entry
                id_stinrg   --- a sting of ids separated by ":"
        """

        d_list = ['start_month', 'start_day', 'start_year', \
                   'finish_month', 'finish_day', 'finish_year',  \
                   'start', 'finish','id' ]
        n_list = ['name', 'user', 'assigned', 'ochk']
#
#--- id_list is passed with a string; make it into a list
#
        id_string = form['id_list']
        atemp     = re.split(':', id_string)
        id_list   = []
        for ent in atemp:
            if ent != '':
                id_list.append(ent)

        alist = []

        for sid in id_list:

            adict = {}
#
#--- update numeric input; make them integer
#
            for pname in d_list:
                adict = self.update_dict_for_input(adict, sid, form, pname, dchk='y')
#
#--- update non-numeric input
#
            for pname in n_list:
                adict = self.update_dict_for_input(adict, sid, form, pname)
#
#--- add assigned person's id
#
            if not (adict['name'] in ['','tbd', 'TBD']) and (adict['assigned'] in ['', 'tbd', 'TBD']):
                adict['assigned'] = self.submitter
#
#--- put the full name instead of user name
#       
            test = oda.get_full_name_from_username(adict['user'])
            if test == '' or test == 'tbd' or test == 'TBD':
                try:
                    uname = adict['name']
                except:
                    uname = 'TBD'
#
#--- dict['name'] orginally holds user name, but copy that to dict['user'] and fill dict['name'] with full name
#
                adict['user'] =  uname.lower()
                test = oda.get_full_name_from_username(adict['user'])

                if test in ['', 'tbd', 'TBD']:
                    adict['name']  =  ""
                else:
                    adict['name']  = test
#
#--- if someone signed in, check ochk to 't'
#
            if adict['ochk'] == 'y':
                if adict['assigned'] in ['','tbd', 'TBD']:
                    adict['user'] = 'TBD'
                else:
                    adict['ochk'] = 't'

            alist.append(adict)
#
#--- remove all tbd entries after the last sign up and also the past signed up
#
        tot   = len(alist)
        slist = []
        chk   = 0
        for k in range(0, tot):
            m = tot -k -1
            if chk == 0 and (alist[m]['user'] in ['', 'tbd', 'TBD']):
                continue
            else:
                chk = 1
                slist.append(alist[m])

        slist.reverse()

        if len(slist) > 0:
            nid_string = slist[0]['id']
            for i in range(1, len(slist)):
                val = alist[i]['id']
                nid_string = str(nid_string) + ':' + str(val)
        else:
            nid_string = ''

        return [slist, nid_string]


#----------------------------------------------------------------------------------
#-- update_dict_for_input: update data dictionary cotent                         --
#----------------------------------------------------------------------------------

    def update_dict_for_input(self, adict, sid, form, pname, dchk='n'):
        """
        update data dictionary cotent
        input:  adict   --- data dicionary
                sid     --- id of the input line
                form    --- data form passed
                pname   --- parameter name
                dchk    --- indicator of whether input is digit. if so "y"; default: 'n'
        output: adict   --- updated data dictionary
        """
        iname = pname + '_' + str(sid)
        try:
            if dchk == 'y':
                adict[pname]  = int(float(form[iname]))
            else:
                adict[pname]  = form[iname]
        except:
            adict[pname]  = ''

        sname = pname + '_id'
        adict[sname] = iname
            
        return adict

#----------------------------------------------------------------------------------
#-- add_tbd_to_non_filled: find assignment gaps and change the contact name to 'TBD'-
#----------------------------------------------------------------------------------

    def add_tbd_to_non_filled(self, alist):
        """
            ***** THIS IS NOT USED IN THIS SCRIPT ANYMORE *****
        find assignment gaps and change the contact name to 'TBD'
        input:  alist   --- a list of data dictionaries
        output: slist   --- a list of updated data dictionaries
        """
#
#--- ordered it by time
#
        slist = self.ordered_by_time(alist)
#
#--- find data position  with fully assigned
#
        olist = []
        for i in range(0, len(slist)):
            adict = slist[i]
            chk = adict['ochk']
            if chk == 'c' or chk == 'n' or chk == 't':
                olist.append(i)
#
#--- find the largest position and make a list starting 0 up to the max
#
        vmax = max(olist) + 1
        mlist = []
        for i in range(0, vmax):
            mlist.append(i)
#
#--- find missing positions
#
        missing = [item for item in mlist if item not in olist]
        line = 'missing: ' + str(missing) + '\n'
#
#--- if there are gaps, indicate that by setting contact name by 'TBD'
#
        for pos in missing:
            adict = slist[pos]
            try:
                user = adict['user']
            except:
                user = ''
            if user == '':
                #adict['name'] = 'TBD'
                #adict['user'] = 'tbd'
                adict['name'] = ''
                adict['user'] = ''
                slist[pos] = adict

        return slist

#----------------------------------------------------------------------------------
#-- check_off_start: add indicators which tell none standard start/finish periods to the list of the data dictionary
#----------------------------------------------------------------------------------

    def check_off_start(self, nlist):
        """
        add indicators which tell none standard start/finish periods to the list of the data dictionary
        input:  nlist   --- a list of the data dictionaries
        output: ulist   --- a list of the data dictionaries with the indicator of none standard start/finish
        """

        ulist = []
        for adict in nlist:
            start = adict['start']
            stop  = adict['finish'] - 43200     #--- set stop time to the middle of the ending day
#
#--- check whether the starting date is on Monday
#
            try:
                if ocf.test_wday_stime(start):
                    color_st = 'm'
                else:
                    color_st = 'd'
            except:
                color_st = 'x'
#
#--- check whether the finishing date is on Sunday
#
            try:
                if ocf.test_wday_stime(stop, wday=6):
                    color_en = 'm'
                else:
                    color_en = 'd'
            except:
                color_en = 'x'
#
#--- update the dictionay and put back in the list
#
            adict['color_st'] = color_st
            adict['color_en'] = color_en

            ulist.append(adict)

        return ulist

