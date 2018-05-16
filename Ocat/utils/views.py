#################################################################################################
#                                                                                               #
#   Ocat utilties: keep all common pages/functions                                              #
#                                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                               #
#       last update: Apr. 22, 2015                                                              #
#                                                                                               #
#################################################################################################

import re
import crypt

from django.views.generic       import View
from django.http                import HttpRequest, HttpResponseRedirect
from django.template            import RequestContext

from django.shortcuts           import render_to_response, get_object_or_404

from utils.forms                import LoginForm

#------------------------------------------------------------------------------------
#-- LoginUser: display login page                                                 ---
#------------------------------------------------------------------------------------

class LoginUser(View):

    """
    get username and password and authenticate
    this one uses the external user database which has different encription from what django uses. 

    input:  redirect_page   --- the page landed when the authentification is successful
    output: directed page, either loggedin or invalid
    """

    form_class    = LoginForm
    initial       = {'username' : '', 'password' : ''}
    template_name = 'registration/auth.html'

#------------------------------------------------------------------------------------

    def __init__(self, redirect_page=''):

        self.auth_page = 'registration/auth.html'

        if redirect_page == '':
            self.redirect_page  = 'registration/auth.html'
        else:
            self.redirect_page  = redirect_page

#------------------------------------------------------------------------------------

    def get(self, request, *args, **kwargs):

        form     = self.form_class(initial = self.initial)
        state    = "Please log in below:"

        return render_to_response(self.auth_page, {'authform': form, 'state':state}, RequestContext(request))

#------------------------------------------------------------------------------------

    def post(self, request, * args, **kwargs):

        page  = self.auth_page

        form = self.form_class(request.POST)
        if form.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')

            check    = self.authenticate(username, password)

            if check == True:
                state = "You're successfully logged in!" 
                page  = self.redirect_page
            else:
                state = "User name and/or password are not correct, Pleas try again:" 

        else:
            state    = "Please log in below:"

        return render_to_response(page, {'authform': form, 'state':state}, RequestContext(request))

#------------------------------------------------------------------------------------

    def authenticate(self, username=None, password=None):
        """
        authenticate user/password combination agaist login list
        input:  username    --- user name
                password    --- plain password
        output: check       --- True/False
        """
#
#--- get a dictionary of username<--->password
#        
        user_dict = self.get_login_list()

        try:
            pkey = user_dict[username]
        except:
            pkey = None

        if pkey:
            check = self.check_password(password, pkey)
            return check
        else:
            return False

#------------------------------------------------------------------------------------

    def get_login_list(self):
        """
        read the external password encription table
        input:  none, but read from the file (see code)
        output: user_dict   --- a dictionary of username <---> encripted password
        """

        f    = open('/data/mta4/CUS/www/Usint/Pass_dir/.htpasswd', 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
        
        user_dict = {}
        for ent  in data:
            atemp = re.split(':', ent)
            user_dict[atemp[0]] = atemp[1]

        return user_dict

#------------------------------------------------------------------------------------

    def check_password(self, password, passkey):
        """
        check password against encripted value
        input:  password    --- plane password
                passkey     --- encripted passowrd
        output: True/False
        """

        if crypt.crypt(password, passkey) == passkey:
            return True
        else:
            return False

#------------------------------------------------------------------------------------
