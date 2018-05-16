#############################################################################################
#                                                                                           #
#       backend.py: customized AUTHENTICATION_BACKENDS class object                         #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Jun 10, 2015                                                       #
#                                                                                           #
#############################################################################################

from django.conf                import settings
from django.contrib.auth.models import User, check_password

import  utils.passWordCheck     as pwchk


#----------------------------------------------------------------------------------
#-- SettingBackend: customized AUTHENTICATION_BACKENDS class object              --
#----------------------------------------------------------------------------------

class SettingBackend(object):
    """
    customized AUTHENTICATION_BACKENDS class object
    used in ocatsite/settings.py
    """

#----------------------------------------------------------------------------------
#-- authenticate: authenticate the username based on system user name/password   --
#----------------------------------------------------------------------------------

    def authenticate(self, username=None, password=None):
        """
        authenticate the username based on system user name/password combination
        input:  username    --- system user name
                password    --- system password
        output: User        --- user object registered in the system
        """
#
#--- the following object gives system username/password access
#
        pdb = pwchk.CheckUser()

        if pdb.login_check(username, password):
            try:
                user = User.objects.get(username=username)

            except User.DoesNotExist:
                user = User(username=username, passowrd=password)
                user.is_staff     = False
                user.is_superuser = False
                user.save()

            return user

        return None


#----------------------------------------------------------------------------------
#-- get_user: check whether the user is registered in the system                 --
#----------------------------------------------------------------------------------

    def get_user(self, user_id):
        """
        check whether the user is registered in the system
        input:  user_id     ---- user name or user id
        output: User        ---- User Ojbects registered in the system
        """
        try:
            return User.objects.get(pk=user_id)

        except User.DoesNotExist:

            return None

