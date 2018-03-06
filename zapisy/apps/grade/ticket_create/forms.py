from django import forms
from django.utils.safestring import SafeText


class PollCombineForm(forms.Form):
    forms.label_suffix = "->"

    def __init__(self, *args, **kwargs):
        polls_by_s = kwargs.pop("polls")
        self.poll_groups = []

        super(PollCombineForm, self).__init__(*args, **kwargs)

        for polls in polls_by_s:
            if len(polls) == 1:
                if not polls[0].group:
                    title = '[' + polls[0].title + '] Ankieta ogólna'
                else:
                    title = '[' + polls[0].title + '] Przedmiot: ' + \
                            polls[0].group.course.name + \
                            ' ' + polls[0].group.get_type_display() + ': ' + \
                            polls[0].group.get_teacher_full_name()
                if polls[0].studies_type: ', studia ' + polls[0].studies_type

                self.poll_groups.append(str(title))
            else:
                if not polls[0].group:
                    title = 'Ankiety ogólne:<ul>'
                    label = 'join_common'
                else:
                    title = 'Przedmiot: ' + polls[0].group.course.name + '<ul>'
                    label = 'join_' + str(polls[0].group.course.pk)
                for poll in polls:
                    if not poll.group:
                        title += '<li>[' + poll.title + ']'
                    else:
                        title += '<li>[' + poll.title + '] ' + \
                                 poll.group.get_type_display() + ': ' + \
                                 poll.group.get_teacher_full_name() + '</li>'
                title += '</ul>'

                field = forms.BooleanField(label=SafeUnicode(title),
                                           required=False,
                                           initial=False,
                                           help_text='Powiąż ocenę'
                                           )  # this is NOT escaped

                self.fields[label] = field

    def as_table(self):
        result = ""
        for name in self.poll_groups:
            result += "<tr><td colspan='2'>" + str(name) + "</td></tr>"
        result += super(PollCombineForm, self).as_table()
        return SafeUnicode(result)


class ContactForm(forms.Form):
    idUser = forms.CharField()
    passwordUser = forms.CharField()
    groupNumber = forms.CharField()
    groupKey = forms.CharField()
