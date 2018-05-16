#################################################################################################
#                                                                                               #
#           forms.py: django forms for Orupdate  Page                                           #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               last update Aug 05, 2015                                                        #
#                                                                                               #
#################################################################################################

import sys
import os

from django         import forms


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

class OrUpdateForm(forms.Form):

    label        = 'general'
    general      = pr_chr_field(label)

    label        = 'acis'
    acis         = pr_chr_field(label)

    label        = 'si_mode'
    si_mode      = pr_chr_field(label)

    label        = 'verify'
    verify       = pr_chr_field(label)

#-----------------------------------------------------------------------------------------------

