from typing import Dict

from django import forms

from apps.grade.poll.models import Submission


class TicketsEntryForm(forms.Form):
    """A form used for inserting tickets."""

    tickets = forms.CharField(widget=forms.Textarea, label="Klucze do głosowania")


class SubmissionEntryForm(forms.ModelForm):
    """A form responsible for processing submissions for polls.

    The main logic for detecting and parsing the schema for various
    question types is defined in the `__determine_field_by_type()`
    method. Out of the box, this method provides support for textareas
    (for both short and long answers) as well as radioselects.

    The save() method can only process the data when grade is active
    for a semester corresponding to the poll's semester.
    When the grade either is not active or it is active for a different
    semester, all data will be displayed as `readonly` without the
    opportunity to introduce new changes.
    """

    def __init__(self, *args, **kwargs):
        self.jsonfields = kwargs.pop("jsonfields", None)
        super().__init__(*args, **kwargs)
        self.is_grade_active = self.instance.poll.get_semester.is_grade_active
        for index, field in enumerate(self.jsonfields):
            form_field = self.__determine_field_by_type(
                field=field, active=self.is_grade_active
            )

            self.fields[f"field_{index}"] = form_field

    def save(self, commit=True):
        """Updates the submission.

        This method performs the actual operation only if the grade
        is active for the poll's semester.
        """
        if self.is_grade_active:
            updated_answers = self.instance.answers
            for index, field in enumerate(self.jsonfields):
                field_name = f"field_{index}"
                answer = updated_answers["schema"][index]["answer"] = self.cleaned_data.get(field_name)

            self.instance.submitted = True
            self.instance.answers = updated_answers

            return super().save(commit)

    @staticmethod
    def __determine_field_by_type(field: Dict, active=True):
        """Uses the `question_type` to correctly identify what field
        should be used according to the rules defined in schema.

        :param field: a single entry in JSON Schema that defines the field.
        :param active: whether the field will be active or disabled.
        :returns: a Django Forms field.
        """
        if field["type"] == "textarea":
            form_field = forms.CharField(
                widget=forms.Textarea, label=field["question"], required=False
            )
        elif field["type"] == "radio" and "choices" in field:
            attrs = {"disabled": "disabled"} if not active else {}
            choices = tuple(zip(field["choices"], field["choices"]))
            form_field = forms.ChoiceField(
                choices=choices,
                label=field["question"],
                widget=forms.RadioSelect(choices=choices, attrs=attrs),
                required=False,
            )
        elif field["type"] == "checkbox" and "choices" in field:
            attrs = {"disabled": "disabled"} if not active else {}
            choices = tuple(zip(field["choices"], field["choices"]))
            form_field = forms.ChoiceField(
                choices=choices,
                label=field["question"],
                widget=forms.CheckboxSelectMultiple(choices=choices, attrs=attrs),
                required=False,
            )
        else:
            form_field = forms.CharField(label=field["question"], required=False)

        if not active:
            form_field.widget.attrs["readonly"] = True
        return form_field

    class Meta:
        model = Submission
        fields = []
