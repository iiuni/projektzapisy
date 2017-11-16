#!/bin/bash
source /home/zapisy/env27/bin/activate
cd /home/zapisy/projektzapisy/current/zapisy
python manage.py runscript slack_info
