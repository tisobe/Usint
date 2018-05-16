#####################################################################################
#                                                                                   #
#   updates_sign_off.py:  sign off "verified" column if all others are signed off   #
#       (https://docs.djangoproject.com/en/1.10/howto/custom-management-commands/)  #
#                                                                                   #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                   #
#       last update Aug 15, 2016                                                    #
#                                                                                   #
#####################################################################################

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
import utils.ocatdatabase_access as oda

class Command(BaseCommand):
    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):
        oda.sign_off_verified_column()
