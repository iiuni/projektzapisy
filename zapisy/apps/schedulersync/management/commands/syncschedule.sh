#!/bin/bash
source /home/zapisy/env36/bin/activate
cd /home/zapisy/projektzapisy/current/zapisy
python manage.py import_schedule http://scheduler.ii.uni.wroc.pl/scheduler/api/config/2020-zima-1/ http://scheduler.gtch.eu/scheduler/api/task/f29f280c-28ed-422a-a9d2-316b98eb83e6/ --semester 1 --slack >> logs/import_schedule.log
