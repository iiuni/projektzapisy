from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django import forms
from django.contrib.auth.models import User
from django.forms import inlineformset_factory

from .models import Defect, DEFECT_MAX_PLACE_SIZE, DEFECT_MAX_NAME_SIZE, DefectImage, DefectManager


class DefectFormBase(forms.ModelForm):
    class Meta:
        model = Defect
        fields = ["name", "place", "description"]

    name = forms.CharField(label="Nazwa (krótki opis)", max_length=DEFECT_MAX_NAME_SIZE)
    place = forms.CharField(label="Miejsce usterki", max_length=DEFECT_MAX_PLACE_SIZE)

    def __init__(self, *args, **kwargs):
        super(DefectFormBase, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class DefectForm(DefectFormBase):
    def __init__(self, *args, **kwargs):
        super(DefectForm, self).__init__(*args, **kwargs)


class DefectImageForm(forms.ModelForm):
    class Meta:
        model = DefectImage
        fields = ('image',)

    def __init__(self, *args, **kwargs):
        super(DefectImageForm, self).__init__(*args, **kwargs)
        self.fields['image'].required = False

        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                'image',
                Div('DELETE', css_class='d-none'),
                css_class="image-form d-none"))


ExtraImagesNumber = 10
DefectImageFormSet = inlineformset_factory(Defect,
                                           DefectImage,
                                           form=DefectImageForm,
                                           extra=ExtraImagesNumber,
                                           can_delete=True)


class InformationFromDefectManagerForm(forms.ModelForm):
    class Meta:
        model = Defect
        fields = ['information_from_defect_manager', 'state']

    def __init__(self, *args, **kwargs):
        super(InformationFromDefectManagerForm, self).__init__(*args, **kwargs)
        self.fields['information_from_defect_manager'].label = ""
        self.helper = FormHelper()
        self.helper.form_tag = False


class DefectManagerAdminForm(forms.ModelForm):
    class Meta:
        model = DefectManager
        fields = ["user_id"]

    @staticmethod
    def label_from_instance(obj):
        return "%s %s" % (obj.first_name, obj.last_name)

    def __init__(self, *args, **kwargs):
        super(DefectManagerAdminForm, self).__init__(*args, **kwargs)
        self.fields['user_id'].queryset = \
            User.objects.select_related('employee').filter(employee__isnull=False).order_by("first_name", "last_name")
        self.fields['user_id'].label_from_instance = self.label_from_instance
