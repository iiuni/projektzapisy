#!/bin/bash
source /home/zapisy/deploy/current/venv/bin/activate
cd /home/zapisy/projektzapisy/current/zapisy
python manage.py send_mail
