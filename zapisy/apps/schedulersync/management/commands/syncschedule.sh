#!/bin/bash
source /home/zapisy/env27/bin/activate
cd /home/zapisy/projektzapisy/current/zapisy
python manage.py import_schedule /scheduler/api/config/2017-18-lato3-2/ http://scheduler.gtch.eu/scheduler/api/task/07164b02-de37-4ddc-b81b-ddedab533fec/ --slack --delete-groups >> logs/import_schedule.log