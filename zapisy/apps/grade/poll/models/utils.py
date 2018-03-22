def getGroups(semester, group=None, type=None, course=None):
    if course == -1:
        return {}
    if group:
        return group
    if type:
        if course:
            groups = Group.objects.filter(type=type, course=course)
        else:
            groups = Group.objects.filter(type=type)
    else:
        if course:
            groups = Group.objects.filter(course=course)
        else:
            groups = Group.objects.filter(course__semester=semester)
    return groups


def ordering_cmp(ord_1, ord_2):
    if ord_1.position == ord_2.position:
        if str(type(ord_1)) == \
           "<class 'apps.grade.poll.models.single_choice_question.SingleChoiceQuestionOrdering'>":
            return -1
        elif str(type(ord_2)) == \
                "<class 'apps.grade.poll.models.single_choice_question.SingleChoiceQuestionOrdering'>":
            return 1
        elif str(type(ord_1)) == \
                "<class 'apps.grade.poll.models.multiple_choice_question.MultipleChoiceQuestionOrdering'>":
            return -1
        elif str(type(ord_2)) == \
                "<class 'apps.grade.poll.models.multiple_choice_question.MultipleChoiceQuestionOrdering'>":
            return 1
        elif str(type(ord_1)) == \
                "<class 'apps.grade.poll.models.open_question.OpenQuestionOrdering'>":
            return -1
        else:
            return 1
    else:
        return -1 if ord_1.position < ord_2.position else 1
