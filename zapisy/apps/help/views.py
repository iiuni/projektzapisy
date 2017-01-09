# -*- coding: utf-8 -*-

"""
    Help views
"""

from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from django.contrib.admin.views.decorators import staff_member_required
from apps.users.decorators import employee_required

from rq import Queue
from redis import Redis
from .tasks import dummy_task

def main_page( request ):
    return render_to_response('help/base.html', {}, context_instance = RequestContext(request))

def terms( request ):
    return render_to_response('help/terms.html', {}, context_instance = RequestContext(request))

def rules( request ):
    return render_to_response('help/rules.html', {}, context_instance = RequestContext(request))

def enrollment( request ):
    return render_to_response('help/enrollment.html', {}, context_instance = RequestContext(request))

def grade( request ):
    return render_to_response('help/grade.html', {}, context_instance = RequestContext(request))

def mobile( request ):
    return render_to_response('help/mobile.html', {}, context_instance = RequestContext(request))

def export( request ):
    return render_to_response('help/export.html', {}, context_instance = RequestContext(request))

def offer( request ):
    return render_to_response('help/offer.html', {}, context_instance = RequestContext(request))

def errorpage( request ):
    raise Exception('Example exception')

def rqtestpage( request ):
    redis_conn = Redis()
    queue = Queue(connection = redis_conn)
    job = queue.enqueue(dummy_task, 5)
    return HttpResponse("Dodalem do kolejki taska")

@staff_member_required
def admin( request ):
    return render_to_response('help/admin.html', {}, context_instance = RequestContext(request))

@employee_required
def employee( request ):
    return render_to_response('help/employee.html', {}, context_instance = RequestContext(request))

