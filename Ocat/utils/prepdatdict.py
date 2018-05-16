#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#       prepdatdict.py: prepare data dictionay for Ocat Data Page                                   #
#                                                                                                   #
#                       use  the fuction: prep_data_dict(obsid)                                     #
#                                                                                                   #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                           #
#                                                                                                   #
#               last update: Sep 06, 2016                                                           #
#                                                                                                   #
#####################################################################################################

import sys
import re
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
import ocatsql             as osq
  
#----------------------------------------------------------------------------------
#-- prep_data_dict: extract data from db and set up a data dictionary           ---
#----------------------------------------------------------------------------------

def prep_data_dict(obsid):
    """
    extract parameters and values from database, and set up a data dictionary
    input:  obsid       --- obsid
    output: dat_dict    --- data dictionary
    """
#
#---- read sql database and create a data dictionary
#
    [dat_dict, db] = get_data_from_db(obsid)
#
#---- set a special notification in the head part
#
    head_notification = set_header_notification(dat_dict)
    dat_dict['head_notificaiton'] = head_notification
#
#--- dither
#
    temp_dict = set_dither(dat_dict)
    dat_dict  = append_dict(dat_dict, temp_dict)
#
#---- time constraints
#
    temp_dict = get_time_ordr(dat_dict, db)
    dat_dict  = append_dict(dat_dict, temp_dict)
#
#---- roll constraints
#
    temp_dict = get_roll_ordr(dat_dict, db)
    dat_dict  = append_dict(dat_dict, temp_dict)
#
#--- acis window constraints
#
    temp_dict = get_spwindow_ordr(dat_dict, db)
    dat_dict  = append_dict(dat_dict, temp_dict)
#
#--- ra/dec adjstment
# 
    temp_dict = set_ra_dec(dat_dict)
    dat_dict  = append_dict(dat_dict, temp_dict)
#
#--- monitor list
#
    temp_dict = find_monitor_obs(dat_dict)
    dat_dict  = append_dict(dat_dict, temp_dict)
#
#--- a few other adjustments
#
    dat_dict['rem_exp_time'] = round(dat_dict['rem_exp_time'], 1)

    temp_dict = define_eventfilter_highest(dat_dict)
    dat_dict  = append_dict(dat_dict, temp_dict)

    try:
        test = dat_dict['asis']
        if test == '':
            dat_dict['asis'] = 'norm'
    except:
        dat_dict['asis'] = 'norm'
#
#--- setting aiming point chip coordinates
#
    try:
        [chipx, chipy] = ocf.find_aiming_point(dat_dict['instrument'], dat_dict['y_det_offset'], dat_dict['z_det_offset'])
    except:
        chipx = 0.0
        chipy = 0.0

    dat_dict['chipx'] = chipx
    dat_dict['chipy'] = chipy
#
#-- now return dat_dict
#
    return dat_dict

#----------------------------------------------------------------------------------
#-- get_data_from_db: create data dictionary from the databse for a given obsid ---
#----------------------------------------------------------------------------------

def get_data_from_db(obsid):
    """
    create data dictionary from the databse for a given obsid
    input:  obsid       --- obsid
    output: dat_dict    --- a dictionary of data
            db          --- database output
    """
#
#--- set up data "db"
#
    db = osq.OcatDB(obsid)
#
#--- get a list of parameters
#
    name_dict = ocf.read_name_list()
    plist     = name_dict.keys()
#
#--- set up dictionary
#
    dat_dict = {'obsid':obsid}
    for ent in plist:
        try:
#
#--- check ordered case (it gives a list); they will be handled separately
#
            val = db.origValue(ent)
            if isinstance(val, list):
                continue

            dat_dict[ent] = val
        except:
            dat_dict[ent] = ''

    return [dat_dict, db]

#----------------------------------------------------------------------------------
#-- et_header_notification: check whether we need to put a special notification --
#----------------------------------------------------------------------------------

def set_header_notification(dat_dict):
    """
    check whether we need to put a special notification at the top of the page
    input:      dat_dict    ---- data dictionary
    output:     head_notification   --- category number:1, 2, or 3
    """
    obsid = dat_dict['obsid']
#
#--- for the case the observation is observed etc
#
    head_notification = ''
    if dat_dict['status'] in ('observed', 'canceled', 'archived', 'untriggered', 'discarded'):
        head_notification = 1
#
#--- for the case the observation is already in OR list
#
    elif ocf.is_in_orlist(obsid):
        head_notification = 2
#
#--- for the case the observation is already approved
#
    elif ocf.is_approved(obsid):
        head_notification = 3
#
#--- for the case the lts date is less than the warning period
#
    else:
        if dat_dict['lts_lt_plan'] and dat_dict['lts_lt_plan'] != '':
            try:
                [chk, lspan]  =  ocf.check_lts_date_coming(dat_dict['lts_lt_plan'])
            except:
                chk = ''
            if chk and chk !='':
                head_notification = 4
                dat_dict['lts_span'] = lspan
            else:
                dat_dict['lts_span'] = ''

    return head_notification

#----------------------------------------------------------------------------------
#-- set_dither: set dither related quantities and save in a dictionary           --
#----------------------------------------------------------------------------------

def set_dither(dat_dict):
    """
    set dither related quantities and save in a dictionary
    input:  dat_dict    ---- data dictionary    
    output: temp_dict   ---- a dictionary related dither quantities
    """
    temp_dict = {}

    try:
        test = dat_dict['dither_flag']
    except:
        temp_dict['dither_flag'] = 'N'

    if dat_dict['dither_flag'] == 'Y':
        y_amp  = dat_dict['y_amp'] 
        z_amp  = dat_dict['z_amp'] 
        y_freq = dat_dict['y_freq'] 
        z_freq = dat_dict['z_freq'] 
        
        temp_dict['y_amp_asec']  = ocf.convert_deg_to_sec(y_amp)
        temp_dict['z_amp_asec']  = ocf.convert_deg_to_sec(z_amp)
        temp_dict['y_freq_asec'] = ocf.convert_deg_to_sec(y_freq)
        temp_dict['z_freq_asec'] = ocf.convert_deg_to_sec(z_freq)
#
#--- round out to 6th digit (around 1.0 arcsec accuracy)
#
        try:
            temp_dict['y_amp']   = round(y_amp, 6)        
            temp_dict['z_amp']   = round(z_amp, 6)        
        except:
            pass

    else:
        temp_dict['dither_flag'] = 'N'

    return temp_dict

#----------------------------------------------------------------------------------
#-- get_time_ordr: check time order entries and create a dictionary for the entries
#----------------------------------------------------------------------------------

def get_time_ordr(dat_dict, db):
    """
    check time order entries and create a dictionary for the entries
    input: dat_dict     ---- data dictionary    
           db           ---- database
    output: temp_dict   ---- data dictionary for time_order related parameters
    """
#
#--- check whether this is time ordered case
#
    temp_dict = {}

    try:
        test = dat_dict['window_flag']
    except:
        temp_dict['window_flag'] = 'N'

    try:
        ordr = int(float(dat_dict['time_ordr']))
    except:
        temp_dict['time_rodr'] = 0
        ordr = 0


    for k in range(0, ordr):
        name  = 'window_constraint'
        val   = db.origValue(name)[k]
        j     = k + 1
        dname = name + str(j)
        temp_dict[dname] = val
#
#--- tstart and tstop need to be devided into month, data, year, and time
#
        tname = ('month', 'date', 'year', 'time')
        for name in ('tstart', 'tstop'):
            j     = k + 1
            val   = db.origValue(name)[k]


            tlist = re.split('\s+', str(val))
#
#--- convert time in 24 hr system
#
            time  = ocf.time_format_convert(tlist[3])
            tlist[3] = time

            for m  in range(0, 4):
                dname = name + '_' + tname[m] +  str(j)
                temp_dict[dname] = tlist[m]
#
#--- set original tstart and tstop in 24 hrs system
#
            try:
                val = float(tlist[1])
                if val < 10:
                    tlist[1] = ' ' + tlist[1]
            except:
                pass
            if len(tlist[3]) < 8:
                tlist[3] = ' ' + tlist[3]

            dtime = tlist[0] + ' ' + tlist[1] + ' ' + tlist[2] + ' ' + tlist[3]
            pname = name + str(j)
            temp_dict[pname] = dtime
            

    return temp_dict

#----------------------------------------------------------------------------------
#-- get_roll_ordr: get roll order related data                                  ---
#----------------------------------------------------------------------------------

def get_roll_ordr(dat_dict,  db):
    """
    get roll order related data
    input:  dat_dict    --- data dictionary
            db          --- db
    output: temp_dict   --- data dictionary for roll_order related parameters
    """
    temp_dict = {}

    try:
        test = dat_dict['roll_flag']
    except:
        temp_dict['roll_flag'] = 'N'


    try:
        ordr = int(float(dat_dict['roll_ordr']))
    except:
        temp_dict['roll_ordr'] = 0
        ordr = 0

    for k in range(0, ordr):
        for name in ('roll_constraint', 'roll_180', 'roll', 'roll_tolerance'):
            val   = db.newValue(name)[k]
            j     = k + 1
            dname = name + str(j)
            temp_dict[dname] = val

    return temp_dict

#----------------------------------------------------------------------------------
#-- get_spwindow_ordr: get acis window constraint related data                  ---
#----------------------------------------------------------------------------------

def get_spwindow_ordr(dat_dict, db):
    """
    get acis window constraint related data
    input:  dat_dict    --- data dictionary
            db          --- db
    output: temp_dict   --- data dictionary for acis window constraint related parameters
    """

    temp_dict = {}

    try:
        test = dat_dict['spwindow_flag']
    except:
        temp_dict['spwindow_flag'] = 'N'

    try:
        ordr = int(float(dat_dict['ordr']))
    except:
        temp_dict['ordr'] = 0
        ordr = 0


    for k in range(0, ordr):
        for name in ('chip', 'start_row', 'start_column', 'height', 'width', \
                     'lower_threshold',   'pha_range',    'sample'):
            val   = db.newValue(name)[k]
            j     = k + 1
            dname = name + str(j)
            temp_dict[dname] = val

    return temp_dict

#----------------------------------------------------------------------------------
#-- set_ra_dec: convert ra/dec in hh:mm:ss format                                --
#----------------------------------------------------------------------------------

def set_ra_dec(dat_dict):
    """
    convert ra/dec in hh:mm:ss format
    input:  dat_dict    ---- data dictonary
    output: temp_dict   ---- ra/dec related data dictionary
    """

    temp_dict     = {}
#
#--- ra/dec are in degree, save them in "dra" and "ddec"
#
    val = float(dat_dict['ra'])
    temp_dict['dra']  = round(val, 6)
    val = float(dat_dict['dec'])
    temp_dict['ddec'] = round(val, 6)
#
#--- convert ra/dec in hh:mm:ss format
#
    [tra, tdec]       = ocf.convert_ra_dec_hms(dat_dict['ra'], dat_dict['dec'])
#
#--- and save them in 'ra' and 'dec'
#
    temp_dict['ra']   = tra
    temp_dict['dec']  = tdec

    return temp_dict

#----------------------------------------------------------------------------------
#-- find_monitor_obs: ind observations in the list of monitor/group              --
#----------------------------------------------------------------------------------

def find_monitor_obs(dat_dict):
    """
    find observations in the list of monitor/group
    input:  dat_dict    ---- data dictionary
    output: temp_dict   ---- monitor/group list related data dictionary
    """
#
#--- find all monitoring/group ids
#
    temp_dict = {}
    try:
        monitor_list = osq.find_monitor_obs(dat_dict['obsid'])
    except:
        monitor_list = []
#
#--- if group_id exits, monitor_flag must be "N"
#
    if dat_dict['group_id'] in [None, 'NULL', 'N']:

        if len(monitor_list) > 0:
            monitor_flag = 'Y'
        else:
            monitor_flag = ''
    else:
        monitor_flag = 'N'
#
#--- if this is monitoring case, remove already observed and cancelled observations from the list
#
    if monitor_flag == 'Y':
        clean_list = []
        for otest in monitor_list:
            db  = osq.OcatDB(otest)
            val = db.newValue('status')
            if val.lower() in ['unobserved', 'scheduled']:
                clean_list.append(otest)

        monitor_list = clean_list

    temp_dict['monitor_flag'] = monitor_flag
    temp_dict['monitor_list'] = monitor_list

    return temp_dict

#----------------------------------------------------------------------------------
#-- append_dict: combine two dictionary. if there is the same key in both dict  ---
#----------------------------------------------------------------------------------

def append_dict(dict1, dict2):

    """
    combine two dictionary. if there is the same key in both dict, 
    the value of the second dict will replace the first one.

    input:  dict1   --- dictionary 1
            dict2   --- dictionary 2
    output: dict1   --- combined dictonary
    """

    for key in dict2.keys():
        dict1[key] = dict2[key]

    return dict1
        
#----------------------------------------------------------------------------------
#-- define_eventfilter_highest: define evenfilter highest energy value          ---
#----------------------------------------------------------------------------------

def define_eventfilter_highest(dat_dict):
    """
    define evenfilter highest energy value
    input:  dat_dict    --- data dictionary
    output: temp_dict   --- a dictionary for eventfilter_highest
    """

    temp_dict = {}
    chk  = 1
    try:
        energy_low = float(dat_dict['eventfilter_lower'])
    except:
        energy_low = 0.0
        chk = 0
    try:
        eventfilter_higher = float(dat_dict['eventfilter_higher'])
    except:
        eventfilter_higher = 0.0
        chk = 0

    eventfilter_highest = energy_low + eventfilter_higher
    if chk == 1:
        temp_dict['eventfilter_highest'] = eventfilter_highest
    else:   
        if  eventfilter_highest > 0:
            temp_dict['eventfilter_highest'] = eventfilter_highest
        else:
            temp_dict['eventfilter_highest'] = ""

    return temp_dict
    
#----------------------------------------------------------------------------------
#-- create_blank_dat_dict: create a blank dat_dict. all keys have a value of ""  --
#----------------------------------------------------------------------------------

def create_blank_dat_dict():
    """
    create a blank dat_dict. all keys have a value of ""
    input: none
    output: dat_dict    ---- a blank data dictionary
    """
#
#--- get a list of parameters
#
    name_dict = ocf.read_name_list()
    plist     = name_dict.keys()
#
#--- create empty dat_dict
#
    dat_dict = {}
    for key in plist:
        dat_dict[key] = ""

    return dat_dict
    
#----------------------------------------------------------------------------------
#-- read_non_changable_param_list: get a list of none changable parameter list  ---
#----------------------------------------------------------------------------------

def read_non_changable_param_list():
    """
    get a list of none changable parameter list
    input:  None but read from the file
    output: nlist   --- a list of none changable parameters
    """

    file  = house_keeping + 'non_changable_param_list'
    f     = open(file, 'r')
    nlist = [line.strip() for line in f.readlines()]
    f.close()
    
    return nlist

#----------------------------------------------------------------------------------
#-- return_non_changerble_param_list: create a list of parameter/value pairs ------
#----------------------------------------------------------------------------------

def return_non_changerble_param_list(data_dict):
    """
    create a list of parameter/value pairs for all none changiable parameters
    input:  data_dict   ---- a dictionary of data
    outpu:  rlist       ---- a list of [param/value]
    """

    nlist = read_non_changable_param_list()

    rlist = []
    for ent in nlist:
        rlist.append([ent, data_dict[ent]])

    return  rlist 

#----------------------------------------------------------------------------------
#-- return_changerble_param_list: create a list of parameter/value pairs      -----
#----------------------------------------------------------------------------------

def return_changerble_param_list():
    """
    create a list of parameter/value pairs for all none changiable parameters
    input:  data_dict   ---- a dictionary of data
    outpu:  rlist       ---- a list of (param name, descriptive name)
    """

    non_changble_list = read_non_changable_param_list()

    file  = house_keeping + 'changable_param_list'
    f     = open(file, 'r')
    nlist = [line.strip() for line in f.readlines()]
    f.close()

    rlist = []
    for ent in nlist:
        if ent[0] == '#':
            continue

        atemp = re.split('::', ent)
        chk = 0
        for comp in non_changble_list:
            if atemp[1] == comp:
                chk = 1
                break
        if chk == 0:
            rlist.append((atemp[0], atemp[1]))
        
    return  rlist

#----------------------------------------------------------------------------------
#-- return_final_display_param_list: create a list of categories and parameters  --
#----------------------------------------------------------------------------------

def return_final_display_param_list():
    """
    create a list of categories and a list of lists of parameters in that category
    input: none but read from changable_param_list
    output: dlist   --- a list of discriptive names of the category
            rlist   --- a list of lists of parameter names
    """

    file  = house_keeping + 'changable_param_list'
    f     = open(file, 'r')
    nlist = [line.strip() for line in f.readlines()]
    f.close()

    rlist = []
    dlist = []
    for ent in nlist:
#
#--- category names are marked by ## at the top of the line
#
        if ent[0] == '#':
            if ent[1] == '#':
                atemp  = re.split('##', ent)
                if len(plist) > 0:
                    rlist.append(plist)

                btemp  = re.split(':', atemp[1])
                mark   = btemp[0]
                discrp = btemp[1]
                plist  = []
                dlist.append(discrp)
            continue
        else:
#
#--- finding the name of the parameters
#
            atemp = re.split(':', ent)
            plist.append(atemp[0])


    return [dlist, rlist]

#----------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST        --
#----------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
#------------------------------------------------------------

    def test_get_data_from_db(self):

        obsid = 16245
        [dat_dict, db] = get_data_from_db(obsid)

        self.assertEquals(dat_dict['status'],       'archived')
        self.assertEquals(dat_dict['type'],         'TOO')
        self.assertEquals(dat_dict['dither_flag'],  'Y')
        self.assertEquals(dat_dict['pre_max_lead'], 1.5)

#------------------------------------------------------------

    def test_set_header_notification(self):

        obsid = 16245
        [dat_dict, db] = get_data_from_db(obsid)

        notification    = set_header_notification(dat_dict)
        self.assertEquals(notification, 1)

#------------------------------------------------------------

    def test_set_dither(self):

        obsid = 16245
        [dat_dict, db] = get_data_from_db(obsid)

        test_dict      = set_dither(dat_dict)
        self.assertEquals(test_dict['y_freq_asec'], 1296.0)
        self.assertEquals(test_dict['z_freq_asec'], 1832.76)

#------------------------------------------------------------

    def test_spwindow_ordr(self):

        obsid = 16245
        [dat_dict, db] = get_data_from_db(obsid)

        test_dict      = get_spwindow_ordr(dat_dict, db)
        self.assertEquals(test_dict['chip1'], 'S3')
        self.assertEquals(test_dict['height1'], 300)
        self.assertEquals(test_dict['lower_threshold1'], 0.3)

        self.assertEquals(test_dict['start_row2'], 1)
        self.assertEquals(test_dict['height2'], 1024)
        self.assertEquals(test_dict['pha_range2'], 11.0)

#------------------------------------------------------------

    def test_set_ra_dec(self):

        obsid = 16245
        [dat_dict, db] = get_data_from_db(obsid)

        test_dict      = set_ra_dec(dat_dict)
        self.assertEquals(test_dict['ra'],  '05:34:31.6000')
        self.assertEquals(test_dict['dec'], '+22:00:56.4000')

#------------------------------------------------------------

    def test_define_eventfilter_highest(self):

        obsid = 16245
        [dat_dict, db] = get_data_from_db(obsid)

        test_dict      = define_eventfilter_highest(dat_dict)
        self.assertEquals(test_dict['eventfilter_highest'], 11.3)
        
#------------------------------------------------------------

    def test_get_time_ordr(self):

        obsid = 12109
        [in_dict, tdb] = get_data_from_db(obsid)

        test_dict      = get_time_ordr(in_dict, tdb)
        self.assertEquals(test_dict['window_constraint1'], 'Y')
        self.assertEquals(test_dict['tstart_month1'], 'Feb')
        self.assertEquals(test_dict['tstop_year1'],    '2010')
        self.assertEquals(test_dict['tstart_date2'],   '1')
        self.assertEquals(test_dict['tstop_time2'],    '23:59:00')
        
#------------------------------------------------------------

    def test_get_roll_ordr(self):

        obsid = 1601
        [in_dict, tdb] = get_data_from_db(obsid)

        test_dict      = get_roll_ordr(in_dict, tdb)
        self.assertEquals(test_dict['roll_constraint1'], 'Y')
        self.assertEquals(test_dict['roll_1801'],        'N')
        self.assertEquals(test_dict['roll1'],          307.0)
        self.assertEquals(test_dict['roll_tolerance1'],  1.0)

#------------------------------------------------------------

    def test_find_monitor_obs(self):

        obsid = 15442
        clist = [15430 , 15431 , 15432 , 15433 , 15434 , 15435 , 15436 , 15437 , 15438 , 15439 , 15440 , 15441 , 15442 , 15443 , 15444 , 15445 , 15446 , 15447 , 15448 , 15449 , 15450]
        [in_dict, tdb] = get_data_from_db(obsid)
        test_dict      = find_monitor_obs(in_dict)
        self.assertEquals(test_dict['monitor_list'], clist )

#------------------------------------------------------------


#---------------------------------------------------------------------------

if __name__ == "__main__":

    unittest.main()



