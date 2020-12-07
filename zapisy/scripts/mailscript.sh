#!/bin/bash
source /home/zapisy/deploy/current/venv/bin/activate
cd /home/zapisy/deploy/current/zapisy
python manage.py send_mail
