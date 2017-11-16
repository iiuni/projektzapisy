# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from apps.enrollment.courses.models.course import CourseEntity, CourseDescription
from django.conf import settings
from mailer.models import Message


def proposal_for_offer(slug):
    if slug:
        try:
            return CourseEntity.get_proposal(slug)
        except ObjectDoesNotExist:
            raise Http404

    return None


def employee_proposal(user, slug):
    if slug:
        try:
            proposal = CourseEntity.get_employee_proposal(user, slug)
            proposal.information = CourseDescription.objects.filter(entity=proposal).order_by('-id')[0]
        except (ObjectDoesNotExist, IndexError) as e:
            raise Http404
    else:
        proposal = None

    return proposal


def send_notification_to_3d(proposal, new=False):
    address = 'mabi@cs.uni.wroc.pl'
    subject = 'Nowa propozycja: '+proposal.name
    if new == False:
        subject = 'Zmieniona propozycja: '+proposal.name
    body = u'Cześć,\n\nw Systemie Zapisów masz do zaakceptowania propozycję:\n'+'Nazwa: '+proposal.name+'\n'+'Link do edycji: '+'https://zapisy.ii.uni.wroc.pl/offer/'+proposal.slug+'/edit'+'\n\n'+u'Zarządzanie propozycjami: https://zapisy.ii.uni.wroc.pl/offer/manage/proposals'+u'\n\nPozdrowienia,\nZespół zapisy.ii.uni.wroc.pl\n\n'
    Message.objects.create(to_address=address, from_address=settings.SERVER_EMAIL, subject=subject, message_body=body)
