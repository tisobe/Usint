#################################################################################################
#                                                                                               #
#           forms.py: django forms for Schedule Submitter                                       #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               last update Aug 24, 2015                                                        #
#                                                                                               #
#################################################################################################

import sys
import os

from django   import forms

import utils.ocatdatabase_access as oda

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

import ocatCommonFunctions      as ocf
import convertTimeFormat        as tcnv


maxno  = 30       #---- max length of acceptable text length of char field
maxsp  = 10       #---- max size of the standard text area of char field 
maxsp1 = 15       #---- max size of the long text area of char field
maxsp2 = 8        #---- max size of the short text area of char field

#-----------------------------------------------------------------------------------------------
#-- pr_chr_field: CharField with variable text area size                                     ---
#-----------------------------------------------------------------------------------------------

def pr_chr_field(label, mxsp=maxsp):
    """
    change the size of CharField
    input:  label   --- the name of the field
    ouput:  CharField
    """

    return  forms.CharField(label=label, max_length=maxno, widget=forms.TextInput(attrs={'size':mxsp}))

#-----------------------------------------------------------------------------------------------
#-- OcatParamForm: define form entry of parameters                                            --
#-----------------------------------------------------------------------------------------------

class Schedule_submitter(forms.Form):

    poc_list   =  oda.get_poc_list()
    month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', \
                  'September', 'October', 'November', 'December']
    year_list  = self.make_year_list()

    for i in range(1, 2000):
        label        = 'contact' + str(i)
        choice       = poc_list
        exec    "%s = forms.ChoiceField(label=%s, choices=[(x, x) for x in choice])" %(label, label)
    
        label        = 'start_month' + str(i)
        choice       = month_list
        exec    "%s = forms.ChoiceField(label=%s, choices=[(x, x) for x in choice])" %(label, label)
    
        label        = 'start_day' + str(i)
        exec    "%s  = pr_chr_field(%s)" % (label, label)
    
        label        = 'start_year' + str(i)
        choice       = year_list
        exec    "%s = forms.ChoiceField(label=%s, choices=[(x, x) for x in choice])" %(label, label)
    
    
        label        = 'finish_month' + str(i)
        choice       = month_list
        exec    "%s = forms.ChoiceField(label=%s, choices=[(x, x) for x in choice])" %(label, label)
    
        label        = 'finish_day' + str(i)
        exec    "%s  = pr_chr_field(%s)" % (label, label)
    
        label        = 'finish_year' + str(i)
        choice       = year_list
        exec    "%s = forms.ChoiceField(label=%s, choices=[(x, x) for x in choice])" %(label, label)
    
        label        = 'verify' + str(i)
        exec    "%s  = pr_chr_field(%s)" % (label, label)

#-----------------------------------------------------------------------------------------------

    def make_year_list(self):

        tlist = tcnv.currentTime()
        tyear = int(float(tlist[0]))

        year_list = []

        for year in range(tyear-1, tyear+10):
            year_list.append(str(year))


        return year_list

        
