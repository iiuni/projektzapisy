from apps.grade.poll.models import Section, \
    OpenQuestion, \
    OpenQuestionOrdering, \
    SingleChoiceQuestion, \
    SingleChoiceQuestionOrdering, \
    MultipleChoiceQuestion, \
    MultipleChoiceQuestionOrdering, \
    Option


def choicebox_is_on(value):
    return value == 'on'


def get_questions_from_section_form(position, post):
    question_data = {}
    question_id = "poll[question][" + str(position) + "]"

    question_data['position'] = position
    question_data['type'] = post.get(question_id + "[type]")
    question_data['content'] = post.get(question_id + "[title]")
    question_data['description'] = post.get(question_id + "[description]")
    question_data['is_scale'] = choicebox_is_on(post.get(question_id + "[isScale]"))
    question_data['choice_limit'] = post.get(question_id + "[choiceLimit]", 0)
    question_data['has_other'] = choicebox_is_on(post.get(question_id + "[hasOther]", False))
    question_data['answers'] = []

    hide_section = [int(x) for x in post.getlist(question_id + "[hideOn][]")]
    for i, a in enumerate(post.getlist(question_id + "[answers][]")):
        answer = {}
        if len(a) != 0:
            answer['content'] = a
            answer['hide'] = i in hide_section
            question_data['answers'].append(answer)

    return question_data


def get_section_form_data(post):
    data = {}

    data['title'] = post.get("poll[title]")
    data['old_id'] = post.get("old_id", None)
    data['description'] = post.get("poll[description]")

    data['has_leading_question'] = choicebox_is_on(post.get("poll[leading]"))
    data['questions'] = []

    questions = post.getlist('poll[question][order][]')
    for position in questions:
        question_data = get_questions_from_section_form(position, post)
        data['questions'].append(question_data)

    return data


def validate_question_in_section_form(question):
    errors = []
    if len(question['content']) == 0:
        errors.append("brak tekstu")

    if (question['type'] == 'single' or
        question['type'] == 'multi') and \
       len(question['answers']) == 0:
        errors.append("brak opcji")

    if question['type'] == 'multi':
        try:
            int(question['choice_limit'])
        except ValueError:
            if len(question['choice_limit']) != 0:
                errors.append('pole "Limit odpowiedzi" nie zawiera liczby')

    return errors


def validate_section_form(data):
    errors = {}

    if len(data['title']) == 0:
        errors['title'] = ("Niepoprawny tytuł sekcji")

    if not data['questions']:
        errors['content'] = "Sekcja nie zawiera pytań"
    else:
        errors['questions'] = {}
        for question in data['questions']:
            question_errors = validate_question_in_section_form(question)
            if question_errors:
                errors['questions'][int(question['position'])] = question_errors
        if not errors['questions']:
            del errors['questions']

    return errors


def save_options(answers):
    options = []
    hide_on = []
    for ans in answers:
        o = Option()
        o.content = ans['content']
        try:
            o.save()
        except BaseException:
            for o in options:
                o.delete()
            return None

        options.append(o)
        if ans['hide']:
            hide_on.append(o)
    return (options, hide_on)


def add_options(q, options):
    for o in options:
        q.options.add(o)
    try:
        q.save()
        return True
    except BaseException:
        q.delete()
        for o in options:
            o.delete()
        return False


def single_choice_question_save(section, leading, question):
    q = SingleChoiceQuestion()
    q.content = question['content']
    q.description = question['description']
    q.is_scale = question['is_scale']
    try:
        q.save()
    except BaseException:
        return None

    hide_on = None
    option_data = save_options(question['answers'])
    if option_data:
        options = option_data[0]
        hide_on = option_data[1]
        if not add_options(q, options):
            return None

    p = SingleChoiceQuestionOrdering()
    p.question = q
    p.sections = section
    p.position = int(question['position'])
    try:
        p.save()
    except BaseException:
        q.delete()
        return None

    if p.position == 0 and leading:
        p.is_leading = True
        p.hide_on = hide_on
        try:
            p.save()
        except BaseException:
            q.delete()
            for o in options:
                o.delete()
            return None

    return (q, options, p)


def multiple_choice_question_save(section, question):
    q = MultipleChoiceQuestion()
    q.content = question['content']
    q.description = question['description']
    q.has_other = question['has_other']
    if q.has_other:
        add = 1
    else:
        add = 0
    try:
        limit = int(question['choice_limit'])
        if limit > len(question['answers']) + add:
            limit = len(question['answers']) + add
    except ValueError:
        limit = len(question['answers']) + add
    q.choice_limit = limit
    try:
        q.save()
    except BaseException:
        return None

    option_data = save_options(question['answers'])
    if option_data:
        options = option_data[0]
        if not add_options(q, options):
            return None
    else:
        q.delete()
        return None

    p = MultipleChoiceQuestionOrdering()
    p.sections = section
    p.question = q
    p.position = int(question['position'])
    try:
        p.save()
    except BaseException:
        q.delete()
        for o in options:
            o.delete()
        return None

    return (q, options, p)


def open_question_save(section, question):
    q = OpenQuestion()
    q.content = question['content']
    try:
        q.save()
    except BaseException:
        return None
    p = OpenQuestionOrdering()
    p.sections = section
    p.question = q
    p.position = int(question['position'])
    try:
        p.save()
    except BaseException:
        q.delete()
        return None
    return (q, [], p)


def section_save(data):
    section = Section()
    section.title = data['title']
    section.description = data['description']

    try:
        section.save()
    except BaseException:
        return False

    questions = []
    options = []
    positions = []
    for question in data['questions']:
        q_data = None
        if question['type'] == 'single':
            q_data = single_choice_question_save(section, data['has_leading_question'], question)
        elif question['type'] == 'multi':
            q_data = multiple_choice_question_save(section, question)
        elif question['type'] == 'open':
            q_data = open_question_save(section, question)

        if q_data:
            questions.append(q_data[0])
            options += q_data[1]
            positions.append(q_data[2])
        else:
            for q in questions:
                q.delete()
            for o in options:
                o.detete()
            for p in positions:
                p.delete()
            section.delete()
            return False

    if data['old_id']:
        section = Section.objects.get(pk=data['old_id'])
        section.deleted = True
        section.save()

    return True
