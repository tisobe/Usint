#####################################################################################
#                                                                                   #
#       clean_up_site.py: clean up the database and start from scratch              #
#       (https://docs.djangoproject.com/en/1.10/howto/custom-management-commands/)  #
#                                                                                   #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                   #
#       last update Aug 29, 2016                                                    #
#                                                                                   #
#####################################################################################

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
import utils.ocatdatabase_access as oda

class Command(BaseCommand):
    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):
        oda.clean_up_ocat_databases()
