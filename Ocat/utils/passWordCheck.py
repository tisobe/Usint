#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#       passWordCheck.py: check login user /password combination                            #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last updated Aug 31, 2016                                                       #
#                                                                                           #
#############################################################################################

import sys
import os
import string
import re
import math
import crypt, getpass, pwd
import Cookie

from django.http    import HttpRequest, HttpResponseRedirect

#
#--- reading directory list
#
#path = '/data/mta4/CUS/www/Usint/Ocat_sub/house_keeping/dir_list_py'
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

#----------------------------------------------------------------------------------------------------------------
#-- CheckUser: login user/password check                                                                     ----
#----------------------------------------------------------------------------------------------------------------

class CheckUser(object):
    """
    login user/password check 
    Usage:
        pdb = CheckUser()
        pdb.limit_pass_trial(trial=3)   --- give three try to make the user/password match right. default trial: 3
                                            return True/False
        pdb.login_check(user, passwd)   --- login match
                                            return True/False. na: user not found, stop: login failed <trial> times
    """

#---------------------------------------------------------

    def __init__(self):

        self.pwdb      =  self.read_user_pass_list()
        self.usint     =  self.read_usint_list()
        self.trial_cnt = 0

#---------------------------------------------------------

    def read_user_pass_list(self):
        """
        read registered user /password list
        input:  none    but read from a file
        output: pdict   --- dictionary of user / passwd
        """
        pwfile = pass_dir + '.htpasswd'
        f      = open(pwfile, 'r')
        data   = [line.strip() for line in f.readlines()]
        f.close()
        pdict  = {}
        for ent in data:
            atemp = re.split(':', ent)
            pdict[atemp[0]] = atemp[1]

        return pdict

#---------------------------------------------------------

    def read_usint_list(self):
        """
        read useint user list
        input: none but read from a file
        output: usint --- a list of usint users
        """
        file = pass_dir + 'usint_users'
        f    = open(file, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()

        usint = []
        for ent in data:
            atemp = re.split('\s+', ent)
            usint.append(atemp[0])

        usint.append('mta')

        return usint

#---------------------------------------------------------

    def login_check(self, user, passcode, trial=3):
        """
        login check 
        input:  user        --- user name
                passcode    --- password
                trial       --- how many times the user can try; default: 3
        Output: True/False  --- matched/not matched
                na          --- the user is not in the list
                stop        --- the trial failed <trial> times.
        """

        if self.check_usint_user(user) == False:
            return 'na'

        try:
            passwd  = self.pwdb[user]
            ptest   = crypt.crypt(passcode, passwd)
            if ptest == passwd:
                return True
            else:
                self.trial_cnt += 1
                if self.trial_cnt >= trial:
                    return "stop"           #---- password failed three times
                return False
        except:
            return 'na'                     #---- no user found

#---------------------------------------------------------

    def check_usint_user(self, user):
        """
        check whether the user name is in USINT list
        Input: user     --- user name (email name)
        Output: True/False
        """
        for ent in self.usint:
            if user == ent:
                return True
                break
        return False

#---------------------------------------------------------

    def limit_pass_trial(self, trial = 3):
        """
        login input routine
        input:  trial   --- how many times that the user can fail. default: 3
        output: True/False
        """
#
#--- check the user and passwd are in cookie, if not ask them
#
        out = read_pwd_cookie()
        if (self.trial_cnt == 0) and out:
            [user, pa] = out
        else:
            user = raw_input("user name: ")
            pa   = getpass.getpass()

        chk  = self.login_check(user, pa, trial)
#
#--- the user name is not found
#
        if chk == 'na':
            print 'User: "' + str(user) + '" is not found in USINT user list.'
            self.limit_pass_trial(trial=trial)
#
#--- trial failed three times
#
        elif chk == 'stop':
            print "NOT MATCHED. TRY LATER"
            return False
#
#--- user/passwd matched, reset cookie
#
        elif chk == True:
            print "MATCHED!!"
            set_pwd_cookie(user, pa)
            return True
#
#--- match failed, try agin
#
        else:
            print "NOT MATCHED!"
            self.limit_pass_trial(trial=trial)

#----------------------------------------------------------------------------------------------------------------
#-- set_pwd_cookie: set cookie for user name and password                                                      --
#----------------------------------------------------------------------------------------------------------------

def set_pwd_cookie(user, passwd):

    """
    set cookie for user name and password. they will expire in 24 hrs
    Input:  user / password
    """
#
#--- set cookie
#
    cookie = Cookie.SimpleCookie()
    cookie['user']   = user
    cookie['passwd'] = passwd
#
#--- set exp time span to 24 hrs = 86400 sec
#
    cookie['user']['max-age']   = 86400
    cookie['passwd']['max-age'] = 86400


#----------------------------------------------------------------------------------------------------------------
#-- read_pwd_cooke: read user name and password from cookie                                                   ---
#----------------------------------------------------------------------------------------------------------------

def read_pwd_cookie():

    """
    read user name and password from cookie
    Input: none
    Output: [user, passwd] or False (if it is not set or expired)
    """
    try:
        cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
        user   = cookie['user']
        passwd = cookie['passwd']
        return [user, passwd]
    except:
        return False

    
#---------------------------------------------------------

if __name__ == "__main__":

    pdb = CheckUser()
    pdb.limit_pass_trial()
    

