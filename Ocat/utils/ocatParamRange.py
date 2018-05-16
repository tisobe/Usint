#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################################
#                                                                                                       #
#   OcatParamRange.py: create class Object which gives back parameter value range                       #
#                      and possible restriction conditions                                              #
#                                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                   #
#                                                                                                       #
#           Last Update: Aug 31, 2016                                                                   #
#                                                                                                       #
#########################################################################################################

import sys
import os
import string
import re
import copy
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
sys.path.append(bin_dir)
sys.path.append(mta_dir)

import mta_common_functions as mcf
import ocatCommonFunctions  as ocf

#----------------------------------------------------------------------------------------------------------------
#-- create class Object which gives back parameter value range and possible restriction conditions            ---
#----------------------------------------------------------------------------------------------------------------

class OcatParamRange(object):
    """
    read ocat_test_condition_table, and create class Object which gives back parameter value range, 
    and possible restriction conditions.
    Usage:
    pr = OcatParamRange()
    pr.showParamList()              ---- return all parameter names in a list form
    pr.showRange('grating')         ---- return possible value range ('NONE,LETG,HETG')
    pr.showCondition('grating')     ---- return possible restriction codition ([['est_cnt_rate', ['N', 'M', 'M']], ['forder_cnt_rate', ['N', 'M', 'M']])
    pr.choiceList('grating')        ---- return a vrange list (['NONE', 'LETG', 'HETG'])
    pr.checkValue('start_row', 200) ---- return [1, 1] if the value is in range, [0, 1] if it is not. Return 'na' if the value is not numeric, except NULL
    """
#---------------------------------------------------------

    def __init__(self):

        [self.parameter_list, self.vrange, self.cond] = read_test_table()

#---------------------------------------------------------

    def showParamList(self):
        """
        return all parameter names in a list form
        """

        return self.parameter_list

#---------------------------------------------------------

    def showRange(self, param):
        """
        for a given parameter list, return possible value vrange
        """
        try:
            val = self.vrange[param]
        except:
            val = 'NA'

        return val

#---------------------------------------------------------

    def showCondition(self, param):
        """
        for a give parameter name, return possible restriction codition
        it is a list and each entry is [<affected parameter name>, [<condtions]]
        the condtion is: N: must be null, M: must exist, C: custom input: O: open (take anything)
        if there is no restriction, it reutnr 'NONE'
        """

        try:
            val = self.cond[param]
        except:
            val = 'NA'

        return val

#---------------------------------------------------------

    def choiceList(self, param):
        """
        for a given parameter name, return a vrange list. if there is none, return ''
        """

        val = self.showRange(param)
        m   = re.search('<>', val)
        if val == 'OPEN' or val == 'REST' or val == 'NONE':
            return ''
        elif m is not None:
            return ''
        else:
            clist = re.split('\,', val)
            return clist

#---------------------------------------------------------

    def checkValue(self, param, value):
        """
        for a given parameter and numeric value, return whether the value is in the range
        this also include 'NULL' value
        """
        vrange = self.showRange(param)            #--- a value or the list of possible values for the parameter
        v_list = re.split('\,', vrange)

        mchk  = 0                               #--- whether the value is in the vrange. if so 1. if 2, skip the secondary test.
        
        if vrange == 'MUST':
            if ocf.null_value(value) != True:
                mchk = 1
                ipos = 0
        
        elif vrange == 'OPEN' or vrange == 'NA':
            mchk = 1
            ipos = 0
            if ocf.null_value(value):
                mchk = 2
        
        elif ocf.null_value(value):                             #--- value is "NULL" case
            if ocf.find_pattern('NULL', vrange):
                mchk = 1
                ipos = 0
        
        elif mcf.chkNumeric(value):                         #--- value is a numeric case
            for ipos in range(0, len(v_list)):
                if v_list[ipos] == 'OPEN':
                    mchk = 1
                    break
                elif ocf.find_pattern('<>', v_list[ipos]):
                    cond  =  re.split('<>', v_list[ipos])
                    vtest = float(value)
                    lower = float(cond[0])
                    upper = float(cond[1])
                    if vtest >= lower and vtest <=upper:
                        mchk = 1
                        break
        else:                                               #--- value is a word case
            for ipos in range(0, len(v_list)):
                if value == v_list[ipos]:
                    mchk = 1
                    break

        return [mchk , ipos]

#----------------------------------------------------------------------------------------------------------------
#-- read_test_table: read a table which lists parameter range and possible restrictions--
#----------------------------------------------------------------------------------------------------------------

def read_test_table():

    """
    read a table which lists parameter range and possible restrictions
    Input:  none but read <house_keeping>/ocat_test_codition_table'
    Output: [parameter_list, dict_vrange, dict_cond]
                parameter_list: a list of all parameter names
                dict_vrange:     a dictionary of possible parameter range
                dict_cond:      a dictionary of possible restrictions. each entry is in the form of:  
                                [<affected param name>, [<condition>]]
    """

    file = house_keeping + '/ocat_test_condition_table'
    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    dict_vrange    = {}             #--- a dictionary to keep parameter range
    dict_cond      = {}             #--- a dictionary to keep parameter restriction
    parameter_list = []             #--- a list to keep parameter names

    for ent in data:
#
#--- skip commented lines
#
        m1 = re.search('#', ent)
        if m1 is not None:
            continue
#
#--- line is delimited by ":" to param name : vrange : condtion
#
        atemp     = re.split(':', ent)
        parameter = atemp[0].strip()
        vrange    = atemp[1].strip()
        condition = atemp[2].strip()

        parameter_list.append(parameter)
#
#--- save parameter vrange in dict_vrange
#
        dict_vrange[parameter] = vrange
#
#--- check the extra conditions
#
        if condition == 'NA':
            restriction = 'NA'
        else:
#
#--- first create a general case codition: if the parameter value is NULL set to 'N'. all other case to 'M'
#
            cvrange_list = re.split('\,', vrange)
            test_list   = []
            test_list2  = []
            for chk in cvrange_list:
                if chk in ['NULL', 'NONE', 'N', '']:
                    test_list.append('N')
                else:
                    test_list.append('M')
#
#--- now look into each case
#
            restriction = []
            cparam_list = re.split('\,', condition)
            for schk in cparam_list:
#
#--- if a special codition is given in the Extra Restriciton column, use that condition
#
                m  = re.search('=', schk)
                if m is not None:
                    ctemp       = re.split('=', schk)
                    custom_list = list(ctemp[1])
#
#--- the condition is kept in a form of [<affected param name>, [<conditiond>]]
#
                    tlist       = [ctemp[0], custom_list]
                    restriction.append(tlist)
#
#--- otherwise, use the generic cotion 
#
                else:
                    tlist = [schk, test_list]
                    restriction.append(tlist)
#
#---- a list of codtions is save in a dictionary form: dict_cond
#
        dict_cond[parameter] = restriction

    return [parameter_list, dict_vrange, dict_cond]

#----------------------------------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST  ---
#----------------------------------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
    def test_read_test_table(self):
        [parameter_list, dict_vrange, dict_cond] = read_test_table()

        self.assertEquals(parameter_list[2], 'si_mode')
        self.assertEquals(dict_vrange['uninterrupt'],'NULL,N,P,Y')
        self.assertEquals(dict_vrange['y_det_offset'],'-120<>120')
        self.assertEquals(dict_cond['dither_flag'][0],['y_amp', ['N', 'N', 'M']])

#------------------------------------------------------------

class TestCalssMethods(unittest.TestCase):
    """
    testing  class methods
    """

    def test_all_method(self):
        pr = OcatParamRange()
        
        alist = pr.showParamList()
        self.assertEquals(alist[2], 'si_mode')
        self.assertEquals(pr.showRange('grating'), 'NONE,LETG,HETG')
        self.assertEquals(pr.showCondition('grating')[0], ['est_cnt_rate', ['O', 'M', 'M']])
        self.assertEquals(pr.choiceList('grating'),['NONE', 'LETG', 'HETG'])
        self.assertEquals(pr.checkValue('start_row',  200), [1, 1])
        self.assertEquals(pr.checkValue('start_row', -300), [0, 1])

        print 'dither_flag: ' + str(pr.showCondition('dither_flag'))
#---------------------------------------------------------------------------

if __name__ == "__main__":

    unittest.main()

