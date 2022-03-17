from crontab import CronTab
import os


cron = CronTab(user='vagrant')
"""Crontab works with absolute paths"""
cron.remove_all(comment='django_cleanup')
cron_command = 'cd /vagrant/zapisy/ && /home/vagrant/env3/bin/python manage.py clearsessions > /tmp/cronlog.txt 2>&1'
job = cron.new(command=cron_command, comment='django_cleanup')
job.hour.on(0)
job.minute.on(0)
job.dow.on('FRI')

cron.write()
