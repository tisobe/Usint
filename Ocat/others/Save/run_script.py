#!/usr/bin/env /proj/sot/ska/bin/python

import sys
import os

from django.core.management import setup_environ
import settings
setup_environ(settings)

import utils.ocatdatabase_access as oda


def handle(self, *args, **options):
    #oda.add_approved_list_to_sql()
    #oda.add_updates_list_to_sql()
    #oda.add_updates_entry_to_sql()
    oda.add_schedule_entries_to_sql()
    oda.obs_plan_list_to_sql()
