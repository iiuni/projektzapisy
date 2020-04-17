import json
import tempfile
import os


from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone


from apps.theses.enums import ThesisKind, ThesisStatus, ThesisVote
from apps.theses.forms import EditThesisForm, RemarkForm, ThesisForm, VoteForm, RejecterForm
from apps.theses.models import Remark, Thesis, Vote
from apps.theses.users import get_theses_board, is_theses_board_member, is_master_rejecter
from apps.users.decorators import employee_required
from apps.users.models import Employee, Student


@login_required
def list_all(request):
    """Display list of all visible theses"""

    visible_theses = Thesis.objects.visible(request.user)
    board_member = is_theses_board_member(request.user)

    theses_list = []
    for p in visible_theses:
        title = p.title
        is_available = not p.is_reserved
        kind = p.get_kind_display()
        status = p.get_status_display()
        has_been_accepted = p.has_been_accepted
        is_mine = p.is_mine(request.user) or p.is_student_assigned(
            request.user) or p.is_supporting_advisor_assigned(request.user)
        advisor = p.advisor.__str__()
        advisor_last_name = p.advisor.user.last_name if p.advisor else p.advisor.__str__()
        url = reverse('theses:selected_thesis', None, [str(p.id)])

        record = {"id": p.id, "title": title, "is_available": is_available, "kind": kind,
                  "status": status, "has_been_accepted": has_been_accepted, "is_mine": is_mine, "url": url,
                  "advisor": advisor, "advisor_last_name": advisor_last_name, "modified": p.modified.timestamp()}

        theses_list.append(record)

    return render(request, 'theses/list_all.html', {
        'theses_list': theses_list,
        'board_member': board_member,
    })


@login_required
def view_thesis(request, id):
    """Show subpage for one thesis"""

    thesis = get_object_or_404(Thesis, id=id)
    not_has_been_accepted = not thesis.has_been_accepted
    board_member = is_theses_board_member(request.user)

    if (not_has_been_accepted and
        not request.user.is_staff and
        not thesis.is_mine(request.user) and
        not thesis.is_supporting_advisor_assigned(request.user) and
            not board_member):
        raise PermissionDenied
    can_see_remarks = (board_member or
                       request.user.is_staff or
                       thesis.is_mine(request.user) or
                       thesis.is_supporting_advisor_assigned(request.user))
    can_edit_thesis = (request.user.is_staff or thesis.is_mine(request.user))
    save_and_verify = thesis.is_mine(request.user) and thesis.is_returned
    can_vote = thesis.is_voting_active and board_member
    show_master_rejecter = is_master_rejecter(request.user) and (
        thesis.is_voting_active or thesis.is_returned)
    can_download_declarations = (request.user.is_staff or
                                 thesis.is_mine(request.user) or
                                 thesis.is_student_assigned(request.user) or
                                 thesis.is_supporting_advisor_assigned(request.user))

    students = thesis.students.all()

    all_voters = get_theses_board()
    votes = []
    voters = []
    for vote in thesis.thesis_votes.all():
        voters.append(vote.owner)
        votes.append({'owner': vote.owner,
                      'vote': vote.get_vote_display()})

    for voter in all_voters:
        if voter not in voters:
            votes.append({'owner': voter,
                          'vote': ThesisVote.NONE.display})

    for vote in votes:
        if vote['owner'].user == request.user:
            votes.remove(vote)
            votes.insert(0, vote)

    vote_form_accepted = VoteForm(vote=ThesisVote.ACCEPTED)
    vote_form_rejected = VoteForm(vote=ThesisVote.REJECTED)
    vote_form_none = VoteForm(vote=ThesisVote.NONE)

    rejecter_accepted = RejecterForm(status=ThesisStatus.ACCEPTED)
    if thesis.is_voting_active:
        rejecter_rejected = RejecterForm(
            status=ThesisStatus.RETURNED_FOR_CORRECTIONS)
    else:
        rejecter_rejected = RejecterForm(
            status=ThesisStatus.BEING_EVALUATED
        )

    remarks = None
    remarkform = None

    if board_member and not_has_been_accepted:
        remarks = thesis.thesis_remarks.all().exclude(
            author=request.user.employee).exclude(text="")
        remarkform = RemarkForm(thesis=thesis, user=request.user)
    elif can_see_remarks:
        remarks = thesis.thesis_remarks.all().exclude(text="")

    remarks_exist = not_has_been_accepted or remarks

    return render(request, 'theses/thesis.html', {'thesis': thesis,
                                                  'students': students,
                                                  'board_member': board_member,
                                                  'show_master_rejecter': show_master_rejecter,
                                                  'can_see_remarks': can_see_remarks,
                                                  'save_and_verify': save_and_verify,
                                                  'can_vote': can_vote,
                                                  'can_edit_thesis': can_edit_thesis,
                                                  'can_download_declarations': can_download_declarations,
                                                  'not_has_been_accepted': not_has_been_accepted,
                                                  'remarks': remarks,
                                                  'remark_form': remarkform,
                                                  'remarks_exist': remarks_exist,
                                                  'votes': votes,
                                                  'vote_form_accepted': vote_form_accepted,
                                                  'vote_form_rejected': vote_form_rejected,
                                                  'vote_form_none': vote_form_none,
                                                  'rejecter_accepted': rejecter_accepted,
                                                  'rejecter_rejected': rejecter_rejected})


@login_required
def gen_form(request, id, studentid):
    """Display form to print for specific student assigned to a thesis"""

    thesis = get_object_or_404(Thesis, id=id)
    try:
        first_student = thesis.students.get(id=studentid)
    except Student.DoesNotExist:
        raise Http404("No Student matches the given query.")

    if not request.user.is_staff and not thesis.is_mine(request.user) and \
       not thesis.is_student_assigned(request.user) and \
       not thesis.is_supporting_advisor_assigned(request.user):
        raise PermissionDenied

    students = []
    for student in thesis.students.all():
        if(student.id != studentid):
            students.append(student)

    students_num = len(students) + 1

    return render(
        request, 'theses/form_pdf.html', {
            'thesis': thesis,
            'first_student': first_student,
            'students': students,
            'students_num': students_num
        })


@login_required
@employee_required
def edit_thesis(request, id):
    """Show form for edit selected thesis"""

    thesis = get_object_or_404(Thesis, id=id)

    if not request.user.is_staff and not thesis.is_mine(request.user):
        raise PermissionDenied

    if request.method == "POST":
        form = EditThesisForm(request.user, request.POST, instance=thesis)
        # check whether it's valid:
        if form.is_valid():
            form.save(commit=True)
            messages.success(request, 'Zapisano zmiany')
            return redirect('theses:selected_thesis', id=id)

    else:
        form = EditThesisForm(request.user, instance=thesis)

    return render(request, 'theses/thesis_form.html', {
        'thesis_form': form,
        'title': thesis.title,
        'id': id
    })


@login_required
@employee_required
def new_thesis(request):
    """Show form for create new thesis"""

    if request.method == "POST":
        form = ThesisForm(request.user, request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.save(commit=True)
            messages.success(request, 'Dodano nową pracę')
            return redirect('theses:main')
    else:
        form = ThesisForm(request.user)

    return render(request, 'theses/thesis_form.html', {'thesis_form': form, 'new_thesis': True})


@login_required
@employee_required
def edit_remark(request, id):
    """Edit remark for selected thesis"""

    if not is_theses_board_member(request.user):
        raise PermissionDenied

    thesis = get_object_or_404(Thesis, id=id)

    if thesis.has_been_accepted:
        raise PermissionDenied

    if request.method == "POST":
        form = RemarkForm(request.POST, thesis=thesis, user=request.user)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            messages.success(request, 'Zapisano uwagę')

    return redirect('theses:selected_thesis', id=id)


@login_required
@employee_required
def vote_for_thesis(request, id):
    """Vote for selected thesis"""

    if not is_theses_board_member(request.user):
        raise PermissionDenied

    thesis = get_object_or_404(Thesis, id=id)

    if thesis.has_been_accepted:
        raise PermissionDenied

    if request.method == "POST":
        form = VoteForm(request.POST, thesis=thesis, user=request.user)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            messages.success(request, 'Zapisano głos')

    return redirect('theses:selected_thesis', id=id)


@login_required
@employee_required
def rejecter_decision(request, id):
    """Change status of selected thesis"""

    if not is_master_rejecter(request.user):
        raise PermissionDenied

    thesis = get_object_or_404(Thesis, id=id)

    if thesis.has_been_accepted:
        raise PermissionDenied

    if request.method == "POST":
        form = RejecterForm(request.POST, instance=thesis)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            messages.success(request, 'Zapisano decyzję')

    return redirect('theses:selected_thesis', id=id)


@login_required
@employee_required
def delete_thesis(request, id):
    """Delete selected thesis"""

    thesis = get_object_or_404(Thesis, id=id)

    if (request.method != "POST" or
            (not request.user.is_staff and not thesis.is_mine(request.user))):
        raise PermissionDenied

    thesis.delete()

    messages.success(request, 'Pomyślnie usunięto pracę dyplomową')

    return redirect('theses:main')
