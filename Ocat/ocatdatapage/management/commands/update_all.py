#####################################################################################
#                                                                                   #
#   update_all.py: run a custom command with manage.py                              #
#       (https://docs.djangoproject.com/en/1.10/howto/custom-management-commands/)  #
#                                                                                   #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                   #
#       last update Aug 26, 2016                                                    #
#                                                                                   #
#####################################################################################

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
import utils.ocatdatabase_access as oda
import sys
import os

class Command(BaseCommand):
    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):

        #oda.add_approved_list_to_sql()      #---- copy approved sql data to sql data
        #oda.add_updates_list_to_sql(alld='yes')       #---- copy update_table.list and update/<obsid>.<rev> to sql data
        oda.add_updates_entry_to_sql(alld='yes')      #---- copy update/<obsid>.<rev> to sql data
        #oda.add_schedule_entries_to_sql()   #---- copy schedule to sql data
        #oda.obs_plan_list_to_sql()          #---- copy new_obs_list to sql data
