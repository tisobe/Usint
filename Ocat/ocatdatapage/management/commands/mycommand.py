#####################################################################################
#                                                                                   #
#   mycommand.py: run a custom command with manage.py                               #
#       (https://docs.djangoproject.com/en/1.10/howto/custom-management-commands/)  #
#                                                                                   #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                   #
#       last update Sep 21, 2016                                                    #
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
#
#--- move the "clean" database to the active location
# 
        db1 = '/data/mta4/CUS/www/Usint/Ocat/ocatsite/db.sqlite3~'
        db2 = '/data/mta4/CUS/www/Usint/Ocat/ocatsite/db.sqlite3'

        db3 = '/proj/web-r2d2-v/lib/python2.7/site-packages/r2d2-v/ocatsite/db.sqlite3~'
        db4 = '/proj/web-r2d2-v/lib/python2.7/site-packages/r2d2-v/ocatsite/db.sqlite3'

        cmd = 'mv ' + db1 + ' ' + db2
        os.system(cmd)

        oda.add_approved_list_to_sql()      #---- copy approved sql data to sql data
        oda.add_updates_list_to_sql()       #---- copy update_table.list and update/<obsid>.<rev> to sql data
        #oda.add_updates_entry_to_sql()      #---- copy update/<obsid>.<rev> to sql data
        oda.add_schedule_entries_to_sql()   #---- copy schedule to sql data
        oda.obs_plan_list_to_sql()          #---- copy new_obs_list to sql data
#
#--- copy the updated one to "clean" save location
#
        cmd = 'cp ' + db2 + ' ' + db1
        os.system(cmd)

        cmd = 'cp ' + db1 + ' ' + db3
        os.system(cmd)
        cmd = 'cp ' + db2 + ' ' + db4
        os.system(cmd)
