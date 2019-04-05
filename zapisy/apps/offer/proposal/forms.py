from crispy_forms.helper import FormHelper
from crispy_forms.layout import (Column, Div, HTML, Layout, Row, Submit, Field, Fieldset)
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms.models import ModelForm

from apps.enrollment.courses.models.course import (CourseDescription,
                                                   CourseEntity)
from apps.offer.proposal.models import Proposal, StudentWork, Syllabus


class ProposalForm(ModelForm):
    ects = forms.IntegerField(label='ECTS')

    def __init__(self, *args, **kwargs):
        full_edit = kwargs.pop('full_edit', False)
        super(ProposalForm, self).__init__(*args, **kwargs)
        if not full_edit:
            self.fields['lectures'].widget.attrs['readonly'] = True
            self.fields['repetitions'].widget.attrs['readonly'] = True
            self.fields['exercises'].widget.attrs['readonly'] = True
            self.fields['laboratories'].widget.attrs['readonly'] = True
            self.fields['exercises_laboratiories'].widget.attrs['readonly'] = True
            self.fields['seminars'].widget.attrs['readonly'] = True
            self.fields['ects'].widget.attrs['readonly'] = True

        # allow editing status if proposal is accepted
        instance = kwargs.pop('instance', None)
        if instance is None:
            self.fields.pop('status')
        else:
            excluded_statuses = [CourseEntity.STATUS_PROPOSITION, CourseEntity.STATUS_FOR_REVIEW]
            if instance.status in excluded_statuses:
                self.fields.pop('status')
            else:
                self.fields['status'].choices = [
                    x for x in self.fields['status'].choices if x[0] not in excluded_statuses]

    class Meta:
        fields = (
            'name',
            'name_en',
            'status',
            'type',
            'exam',
            'english',
            'semester',
            'web_page',
            'effects',
            'repetitions',
            'lectures',
            'exercises',
            'laboratories',
            'exercises_laboratiories',
            'seminars')
        model = CourseEntity
        widgets = {
            'effects': FilteredSelectMultiple("efekty kształcenia", is_stacked=False)
        }


class ProposalDescriptionForm(ModelForm):
    class Meta:
        fields = ('description', 'requirements')
        model = CourseDescription
        widgets = {
            'description': forms.Textarea(attrs={'class': 'tinymce'}),
            'requirements': FilteredSelectMultiple("wymagania", is_stacked=False)
        }


class SyllabusForm(ModelForm):
    class Meta:
        fields = (
            'requirements',
            'studies_type',
            'year',
            'requirements',
            'objectives',
            'effects_txt',
            'contents',
            'learning_methods',
            'literature',
            'passing_form',
            'exam_hours',
            'tests_hours',
            'project_presentation_hours')
        model = Syllabus
        widgets = {
            'learning_methods': FilteredSelectMultiple("Metody kształcenia", is_stacked=False)
        }


class SelectVotingForm(forms.Form):
    courses = forms.MultipleChoiceField(widget=FilteredSelectMultiple("courses", is_stacked=False))


class TextareaBoundField(forms.BoundField):
    """Extends BoundField for easy access to placeholder value."""

    @property
    def placeholder(self):
        widget = self.field.widget
        if widget:
            return widget.attrs.get('placeholder', "")
        return ""


class TextareaField(forms.CharField):
    widget = forms.Textarea

    def get_bound_field(self, form, field_name):
        return TextareaBoundField(form, self, field_name)


class EditProposalForm(forms.ModelForm):
    """Form for editing a Proposal model.

    A CourseInformation object should only be modified by the regular users
    using this form. It will take care to keep the current instance of the
    course up to date with the proposal.
    """
    ects = forms.IntegerField(
        max_value=15,
        label="ECTS",
        required=False,
        disabled=True,
        help_text="To pole wypełni się samo na podstawie typu przedmiotu.")

    def status_choices(self):
        def choices_pair(c: Proposal.ProposalStatus):
            return (c, c.display)

        def limit_choices():
            """Defines allowed status transitions.

            Initially an employee may only set the status to DRAFT or PROPOSAL.
            PROPOSAL is accepted by the head of teaching (who changes the status
            to IN_OFFER) or rejected (status is changed to
            CORRECTIONS_REQUIRED).

            If corrections are required, the employee may resubmit the proposal
            again by changing the status back to PROPOSAL.

            If the proposal is accepted (IN_OFFER) it can be put into the
            current offer voting (IN_VOTE), left for future semesters or
            archived (WITHDRAWN).
            """
            if not self.data:
                return [
                    Proposal.ProposalStatus.DRAFT,
                    Proposal.ProposalStatus.PROPOSAL,
                ]
            else:
                current_status = self.data.status
                if current_status == Proposal.ProposalStatus.DRAFT:
                    return [
                        Proposal.ProposalStatus.DRAFT,
                        Proposal.ProposalStatus.PROPOSAL,
                    ]
                elif current_status == Proposal.ProposalStatus.IN_OFFER:
                    return [
                        Proposal.ProposalStatus.IN_OFFER,
                        Proposal.ProposalStatus.IN_VOTE,
                        Proposal.ProposalStatus.WITHDRAWN,
                    ]
                elif current_status == Proposal.ProposalStatus.CORRECTIONS_REQUIRED:
                    return [
                        Proposal.ProposalStatus.PROPOSAL,
                        Proposal.ProposalStatus.CORRECTIONS_REQUIRED,
                    ]
                else:
                    return [current_status]

        return map(choices_pair, limit_choices())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = ProposalFormHelper()

        # Populate placeholders from dictionary.
        for k, v in self.Meta.placeholders.items():
            self.fields[k].widget.attrs['placeholder'] = v

        # Populate initial values from dictionary.
        for k, v in self.Meta.initial_values.items():
            self.fields[k].initial = v

        # Limits status choices available to the user.
        self.fields['status'].choices = self.status_choices()

    class Meta:
        model = Proposal
        fields = [
            'name',
            'name_en',
            'short_name',
            'language',
            'semester',
            'course_type',
            'has_exam',
            'recommended_for_first_year',
            'description',

            'hours_lecture',
            'hours_exercise',
            'hours_lab',
            'hours_exercise_lab',
            'hours_seminar',
            'hours_recap',

            'status',
            'teaching_methods',
            'preconditions',
            'goals',
            'contents',
            'teaching_effects',
            'literature',
            'verification_methods',
            'passing_means',
            'student_labour',
        ]
        help_texts = {
            'name': "Nazwa powinna być w języku wykładowym.",
            'name_en': "Dla przedmiotów po angielsku powinna być taka sama jak nazwa.",
            'language': ("Wszystkie pola należy wypełnić w języku wykładowym. Aby zmienić "
                         "język istniejącego przedmiotu należy stworzyć nową propozycję."),
            'short_name': "np. „JFiZO”, „AiSD” — nazwa do wyświetlania w planie zajęć.",
            'description': "Można formatować tekst używając Markdown.",
            'status': "Szkic można sobie zapisać na później.",
            'teaching_methods': (
                "Wyliczyć lub krótko opisać, np.: wykład · wykład interaktywny · prezentacja · "
                "live coding · dyskusja · analiza tekstu · e-learning · rozwiązywanie zadań z "
                "komentowaniem · indywidualne/grupowe rozwiązywanie zadań · indywidualny/"
                "zespołowy projekt programistyczny · samodzielna praca przy komputerze · "
                "ćwiczenia warsztatowe · zajęcia terenowe · studium przypadku · samodzielne "
                "wykonywanie zadań zawodowych"),
            'literature': (
                "Wyliczyć 1-5 pozycji; jeśli dana pozycja nie jest wymagana w całości - określić "
                "które części/rozdziały."),
            'verification_methods': (
                "Podać sposoby pozwalające sprawdzić osiągnięcie wszystkich efektów kształcenia "
                "podanych powyżej, np. egzamin pisemny · kolokwium · prezentacja projektu · "
                "prezentacja rozwiązania zadania · opracowanie i przedstawienie prezentacji na "
                "zadany temat · napisanie programu komputerowego · realizacja zadań przy "
                "komputerze."),
            'student_labour': (
                "Wyliczyć rodzaje aktywności studenta i przybliżoną liczbę godzin. Suma godzin "
                "powinna wynosić około 25 * liczba <abbr>ECTS</abbr>."),
        }
        # Helps filling the form by providing examples.
        placeholders = {
            'name': "Sztuczna inteligencja",
            'name_en': "Artificial Intelligence",
            'hours_lecture': 30,
            'hours_exercise': 0,
            'hours_lab': 0,
            'hours_exercise_lab': 30,
            'hours_seminar': 0,
            'hours_recap': 0,
            'teaching_methods': (
                "Wykład, prezentacja, rozwiązywanie zadań z komentowaniem, dyskusja, "
                "konsultowanie pomysłów na rozwiązywanie zadań programistycznych, samodzielna "
                "praca przy komputerze, indywidualny projekt programistyczny"),
            'preconditions': ("## Zrealizowane przedmioty:\n"
                              " * Logika dla informatyków\n"
                              " * Wstęp do informatyki lub Algorytmy i struktury danych\n"
                              " * Analiza matematyczna\n"
                              "## Niezbędne kompetencje:\n"
                              " * Umiejętność programowania w języku wyższego poziomu\n"
                              " * Pożądana wstępna znajomość języka Python\n"),
            'goals': ("Podstawowym celem przedmiotu jest zapoznanie studentów z technikami "
                      "stosowanymi do rozwiązywania problemów, które są z jednej strony "
                      "trudne do rozwiązania przy użyciu standardowych technik "
                      "algorytmicznych, a z drugiej są efektywnie rozwiązywane przez ludzi, "
                      "korzystających ze swojej inteligencji. Zajęcia koncentrują się na "
                      "następujących pojęciach: modelowanie świata, przeszukiwanie "
                      "przestrzeni rozwiązań, wnioskowanie i uczenie się z przykładów bądź z "
                      "symulacji."),
            'contents': (
                "1. Modelowanie rzeczywistości za pomocą przestrzeni stanów.\n"
                "2. Przeszukiwanie w przestrzeni stanów: przeszukiwanie wszerz i w głąb, "
                "iteracyjne pogłębianie, przeszukiwanie dwustronne, algorytm A*, właściwości i "
                "tworzenie funkcji heurystycznych wspomagających przeszukiwanie. \n"
                "3. Przeszukiwanie metaheurystyczne: hill climbing, symulowane wyżarzanie, beam "
                "search, algorytmy ewolucyjne.\n"
                "4. Rozwiązywanie więzów: modelowanie za pomocą więzów, spójność więzów i "
                "algorytm AC-3, łączenie propagacji więzów z przeszukiwaniem z nawrotami, "
                "specjalistyczne języki programowania z więzami na przykładzie Prologa z "
                "więzami.\n"
                "5. Strategie w grach: gry dwuosobowe, algorytm minimax, odcięcia alfa-beta, "
                "przykłady heurystycznej oceny sytuacji na planszy w wybranych grach, losowość w "
                "grach, algorytm Monte Carlo Tree Search.\n"
                "6. Elementy teorii gier: strategie czyste i mieszane, rozwiązywanie prostych "
                "gier typu dylemat więźnia.\n"
                "7. Modelowanie za pomocą logiki zdaniowej, wnioskowanie forward-chaining i "
                "backward-chaining, rozwiązywanie problemów spełnialności formuły w CNF (WalkSAT, "
                "DPLL).\n"
                "8. Modelowanie niepewności świata: sieci bayesowskie, procesy decyzyjne Markowa, "
                "algorytmy value iteration oraz policy iteration. Elementy uczenia ze "
                "wzmocnieniem: TD-learning oraz Q-learning.\n"
                "9. Podstawy uczenia maszynowego: idea uczenia się z przykładów, generalizacja, "
                "niebezpieczeństwo przeuczenia. Wybrane metody: regresja liniowa i logistyczna, "
                "wielowarstwowe sieci neuronowe (MLP), algorytm k-NN, drzewa decyzyjne i lasy "
                "losowe."),
            'teaching_effects': (
                "## Wiedza\n"
                " * rozumie, czym zajmuje się Sztuczna inteligencja, rozumie również, na czym "
                "polega specyficzność metod tej dziedziny\n"
                " * posiada przeglądową wiedzę o różnych dziedzinach sztucznej inteligencji\n"
                " * zna różne metody modelowania świata, z uwzględnieniem niepewności\n"
                " * zna algorytmy przeszukiwania przestrzeni stanów oraz przeszukiwania drzew gry\n"
                " * zna podstawowe algorytmy wnioskowania\n"
                " * zna podstawowe metody uczenia maszynowego (z nadzorem oraz ze wzmocnieniem)\n\n"
                "## Umiejętności\n"
                " * umie modelować różne zagadnienia jako zadania przeszukiwania (lub "
                "przeszukiwania z więzami)\n"
                " * umie stosować i modyfikować różne algorytmy przeszukiwania (w tym również "
                "przeszukiwania w grach)\n"
                " * umie modelować niepewność świata za pomocą narzędzi z rachunku "
                "prawdopodobieństwa (ze szczególnym uwzględnieniem metod Monte Carlo)\n"
                " * umie stosować podstawowe metody uczenia maszynowego (w tym również metody "
                "uczenia ze wzmocnieniem)\n"
                "## Kompetencje społeczne\n"
                " * rozumie znaczenie algorytmów sztucznej inteligencji dla funkcjonowania "
                "współczesnego społeczeństwa, rozumie możliwości i niebezpieczeństwa z tym "
                "związane\n"
                " * umie prezentować swoje idee w sposób dostosowany do wiedzy słuchaczy"),
            'literature': (
                " * Stuart Russell and Peter Norvig, Artificial Intelligence: A Modern Approach.\n"
                " * Richard S. Sutton and Andrew G. Barto, Reinforcement Learning: An "
                "Introduction.\n"
                " * Prateek Joshi, Artificial Intelligence with Python."),
            'verification_methods': (
                "egzamin pisemny, prezentacja projektu, prezentacja rozwiązania zadania, "
                "napisanie i prezentacja programu komputerowego"),
            'passing_means': (
                "Do zaliczenia ćwiczenio-pracowni należy zdobyć wymaganą, podaną w regulaminie "
                "przedmiotu liczbę punktów za zadania ćwiczeniowe, pracowniowe i opcjonalny "
                "projekt. Punkty za wszystkie wyżej wymienione aktywności liczą się łącznie. "
                "Egzamin ma formę pisemną, aby go zaliczyć konieczne jest zdobycie wymaganej "
                "liczby punktów. Osoby, które osiągnęły bardzo dobre wyniki na ćwiczeniach i "
                "zdobyły ustaloną liczbę punktów za rozwiązanie dodatkowych, trudniejszych zadań "
                "mogą uzyskać zwolnienie z egzaminu."),
            'student_labour': (
                "## Praca własna studenta:\n"
                " * przygotowywanie się do ćwiczeń (w tym czytanie materiałów dodatkowych) 30\n"
                " * samodzielne rozwiązywanie zadań pracowniowych i projektowych 60\n"
                " * przygotowanie do egzaminu lub rozwiązywanie dodatkowych zadań 20\n"),
        }

        initial_values = {
            'hours_lecture': 30,
            'hours_exercise': 30,
            'hours_lab': 0,
            'hours_exercise_lab': 0,
            'hours_seminar': 0,
            'hours_recap': 0,
            'preconditions': ("## Zrealizowane przedmioty:\n"
                              " *  \n\n"
                              "## Niezbędne kompetencje:\n"
                              " *  \n"),
            'student_labour': (
                "## Zajęcia z udziałem nauczyciela:\n"
                "_dodatkowe względem programowych godzin zajęć, np. udział w egzaminie_\n"
                " * udział w egzaminie **??**\n"
                " * dodatkowe konsultacje w ramach potrzeb **??**\n\n"
                "## Praca własna studenta:\n"
                "_np. rozwiązywanie zadań z list · przygotowanie do kolokwium/egzaminu · czytanie "
                "literatury · rozwiązywanie zadań programistycznych_\n"
                " * przygotowywanie się do ćwiczeń (w tym czytanie materiałów dodatkowych) **??**\n"
                " * samodzielne rozwiązywanie zadań pracowniowych i projektowych **??**\n"
                " * przygotowanie do egzaminu lub rozwiązywanie dodatkowych zadań **??**\n"),
        }

        field_classes = {
            f: TextareaField for f in [
                'description',
                'teaching_methods',
                'preconditions',
                'goals',
                'contents',
                'teaching_effects',
                'literature',
                'verification_methods',
                'passing_means',
                'student_labour',
            ]
        }


class CustomCheckbox(Field):
    """Renders Bootstrap 4 custom checkboxes.

    Inspired by
    https://simpleisbetterthancomplex.com/tutorial/2018/11/28/advanced-form-rendering-with-django-crispy-forms.html.
    """
    template = 'proposal/fields/custom_checkbox.html'


class Markdown(Field):
    """Renders textarea with Markdown preview.

    For the editor to work, the bundle 'proposal-markdown-editor' must be
    included in the template.
    """
    template = 'proposal/fields/markdown.html'


class FormRow(Div):
    """Represents Booststrap 4 form layout row."""
    css_class = 'form-row'


class Column(Column):
    """Represents Bootstrap 4 layout column."""
    css_class = 'col-12 col-sm'


class ProposalFormHelper(FormHelper):
    """Defines layout for the Proposal form.

    Fields here must be the same as in `EditProposalForm`.
    """
    layout = Layout(
        Fieldset(
            "Informacje podstawowe",
            FormRow(
                Column('name', css_class='col-md-8'),
                Column('language', css_class='col-md-4'),
            ),
            FormRow(
                Column('semester', css_class='col-md-4'),
                Column('course_type', css_class='col-md-4'),
                Column(
                    CustomCheckbox('has_exam'),
                    CustomCheckbox('recommended_for_first_year'),
                    css_class='col-md-4 px-4'),
                css_class='align-items-end',
            ),
            Markdown('description'),
            FormRow(
                Column('hours_lecture', css_class='col-md-2'),
                Column('hours_exercise', css_class='col-md-2'),
                Column('hours_lab', css_class='col-md-2'),
                Column('hours_exercise_lab', css_class='col-md-2'),
                Column('hours_seminar', css_class='col-md-2'),
                Column('hours_recap', css_class='col-md-2'),
                css_class='align-items-end',
            ),
            FormRow(
                Column('ects'),
                Column('status'),
            )
        ),
        Fieldset(
            "Informacje szczegółowe"
            '<a class="btn btn-outline-secondary btn-sm ml-3" data-toggle="collapse" '
            'href="#proposal-details-fields" role="button" aria-expanded="false">'
            'Rozwiń/Zwiń</a>',
            Div(
                'name_en',
                Markdown('teaching_methods'),
                Markdown('preconditions'),
                Markdown('goals'),
                Markdown('contents'),
                Markdown('teaching_effects'),
                Markdown('literature'),
                Markdown('verification_methods'),
                Markdown('passing_means'),
                Markdown('student_labour'),
                css_class='collapse',
                css_id='proposal-details-fields',
            )
        ),
        Submit('submit', "Zapisz"),
    )
