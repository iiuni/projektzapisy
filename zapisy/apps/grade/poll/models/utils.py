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
