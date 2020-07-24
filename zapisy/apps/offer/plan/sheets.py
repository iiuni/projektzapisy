import os
from typing import Iterable, List, Optional

from django.conf import settings
from django.contrib.auth.models import User
import environ
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from apps.enrollment.courses.models.group import GroupType
from apps.offer.plan.utils import (
    EmployeeData,
    EmployeesSummary,
    ProposalSummary,
    ProposalVoteSummary,
    SingleAssignmentData,
    SingleYearVoteSummary,
    VotingSummaryPerYear,
)
from apps.schedulersync.management.commands.scheduler_data import GROUP_TYPES
from apps.users.models import Employee

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def create_sheets_service(sheet_id: str) -> gspread.models.Spreadsheet:
    """Creates a Google Sheets connection.

    Loads up data from environment, creates credentials and connects to
    appropriate spreadsheet.
    """
    env = environ.Env()
    environ.Env.read_env(os.path.join(settings.BASE_DIR, os.pardir, 'env', '.env'))
    creds = {
        "type": env('SERVICE_TYPE'),
        "project_id": env('PROJECT_ID'),
        "private_key_id": env('PRIVATE_KEY_ID'),
        "private_key": env('PRIVATE_KEY').replace('\\n', '\n'),
        "client_email": env('CLIENT_EMAIL'),
        "client_id": env('CLIENT_ID'),
        "auth_uri": env('AUTH_URI'),
        "token_uri": env('TOKEN_URI'),
        "auth_provider_x509_cert_url": env('AUTH_PROVIDER'),
        "client_x509_cert_url": env('CLIENT_CERT_URL')
    }
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        creds, SCOPES)
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key(sheet_id)
    return sh


##################################################
# BEGIN VOTING RESULT SHEET LOGIC
##################################################


def prepare_legend_rows(years: List[str]) -> List[List[str]]:
    """Creates two top rows with a legend.

    The length of a single row is 3+4*len(years).
    """
    row1 = ["", "", ""] + sum(([y, "", "", "", ""] for y in years), [])
    row2 = ["Nazwa", "Typ kursu", "Semestr"] + [
        "Głosów",
        "Głosujących",
        "Za 3pkt",
        "Był prowadzony",
        "Zapisanych",
    ] * len(years)
    return [row1, row2]


def prepare_annual_voting_part_of_row(sy: Optional[SingleYearVoteSummary]) -> List[str]:
    """Dumps voting summary to five spreadsheet cells.

    If sy is None, empty cells will be produced.
    """
    if sy is None:
        return [""] * 5
    return [
        str(sy['total']),
        str(sy['votes']),
        str(sy['count_max']),
        str(sy['enrolled'] is not None),
        str(sy['enrolled']),
    ]


def prepare_proposal_row(pvs: ProposalVoteSummary, years: List[str]) -> List[List[str]]:
    """Creates a single spreadsheet row summarising voting for the proposal."""
    proposal = pvs.proposal
    beg: List[str] = [
        proposal.name,
        proposal.course_type.name,
        proposal.semester,
    ]
    per_year = (prepare_annual_voting_part_of_row(
        pvs.voting.get(y, None)) for y in years)
    return [beg + sum(per_year, [])]


def votes_to_sheets_format(votes: VotingSummaryPerYear, years: List[str]) -> List[List[str]]:
    legend_rows = prepare_legend_rows(years)
    proposal_rows = (prepare_proposal_row(pvs, years)
                     for pvs in votes.values())
    return legend_rows + sum(proposal_rows, [])


def update_voting_results_sheet(sheet: gspread.models.Spreadsheet, votes: VotingSummaryPerYear,
                                years: List[str]):
    data = votes_to_sheets_format(votes, years)
    sheet.sheet1.clear()
    sheet.values_update(
        range='A:' + gspread.utils.rowcol_to_a1(1, 3 + 5 * len(years))[:-1],
        params={
            'valueInputOption': 'USER_ENTERED'
        },
        body={
            'values': data
        }
    )


##################################################
# END VOTING RESULT SHEET LOGIC
##################################################

##################################################
# BEGIN PLAN PROPOSAL SHEET LOGIC
##################################################


def proposal_to_sheets_format(groups: ProposalSummary):
    """Function prepares data for Assignments spreadsheet.

    Returns:
        List of lists, where each inner list represents a single row in spreadsheet.
    """
    REVERSE_GROUP_TYPES = {v: k for k, v in GROUP_TYPES.items()}

    data = [
        [
            'Lp',
            'Przedmiot',
            'Forma zajęć',
            'Skrót f.z.',
            'Niestandardowa liczba godzin/semestr',
            'h/tydzień',
            'Przelicznik',
            'h/semestr',
            'Do pensum',
            'Semestr',
            'Przydział',
            'Kod prowadzącego',
            'Potwierdzone',
            'Wielu prowadzących',
            'Dzielnik (wielu prow.)',
        ]
    ]

    lp = 0
    prev_name = ''
    for i, group in enumerate(groups):
        if group['name'] != prev_name:
            lp += 1
        prev_name = group['name']
        human_readable_type = GroupType(group['group_type']).label

        row = [
            lp,
            group['name'],                              # B. course name
            human_readable_type,                        # C. group type
            REVERSE_GROUP_TYPES[group['group_type']],   # D. abbr. group type (as in Scheduler)
            '',                                         # E. non-standard hours
            '',                                         # F. h/week
            '',                                         # G. przelicznik
            group['hours'],                             # H. h/semester
            f'=H{i+2}*IF(ISBLANK($G{i+2});1;$G{i+2})/O{i+2}',  # I. formula counting the hours into pensum.
            group['semester'],                          # J. semester
            group['teacher'],                           # K. assigned teacher
            group['teacher_username'],                  # L. assigned teacher username
            'FALSE',                                    # M. confirmed
            '',                                         # N. multiple teachers
            f'=IF(ISBLANK(N{i+2}); 1; COUNTIFS(B:B; B{i+2}; N:N; N{i+2}))',
                                                        # O. formula computing the denominator per
                                                        # multiple teachers
        ]

        data.append(row)
    return data


def update_plan_proposal_sheet(sheet: gspread.models.Spreadsheet, proposal: ProposalSummary):
    data = proposal_to_sheets_format(proposal)
    sheet.sheet1.clear()
    sheet.sheet1.update_title("Przydziały")
    sheet.values_update(
        range='A:O',
        params={
            'valueInputOption': 'USER_ENTERED'
        },
        body={
            'values': data
        }
    )


def read_assignments_sheet(sheet: gspread.models.Spreadsheet) -> List[SingleAssignmentData]:
    """Reads confirmed assignments from the spreadsheet."""
    data = read_entire_sheet(sheet)
    assignments = []
    for row in data:
        try:
            sad = SingleAssignmentData(
                index=int(row[0]),
                name=row[1],
                group_type=row[2].lower(),
                group_type_short=row[3],
                semester=row[9],
                teacher=row[10],
                teacher_username=row[11],
                hours_weekly=float(row[5]) if row[5] else 0,
                hours_semester=float(row[7]) if row[7] else 0,
                confirmed=row[12] == 'TRUE',
                multiple_teachers=row[13] if row[13] else None,
            )
            assignments.append(sad)
        except ValueError:
            # Skip header row and incorrectly formatted rows.
            continue
    return assignments

##################################################
# END PLAN PROPOSAL SHEET LOGIC
##################################################

##################################################
# BEGIN PLAN EMPLOYEES SHEET LOGIC
##################################################


def update_employees_sheet(sheet: gspread.models.Spreadsheet, usernames: Iterable[str]):
    employees = Employee.objects.filter(user__username__in=usernames).select_related('user')
    all_contractors = set(
        User.objects.filter(groups__name='external_contractors').values_list('username', flat=True))
    all_phd_students = set(
        User.objects.filter(groups__name='phd_students').values_list('username', flat=True))
    data = [[
        'Imię', 'Nazwisko', 'Username', 'Status', 'Pensum', 'Godziny (z)', 'Godziny (l)',
        'Godziny razem', 'Bilans'
    ]]

    for i, e in enumerate(employees):
        username = e.user.username
        if username in all_contractors:
            status = 'inny'
        elif username in all_phd_students:
            status = 'doktorant'
        else:
            status = 'pracownik'
        data.append([
            e.user.first_name,
            e.user.last_name,
            e.user.username,
            status,
            str(0),
            # Formulas computing winter and summer hours.
            f'=SUMIFS(Przydziały!$I:$I; Przydziały!$J:$J; "z"; Przydziały!$L:$L; $C{i+2}; Przydziały!$M:$M;True)',
            f'=SUMIFS(Przydziały!$I:$I; Przydziały!$J:$J; "l"; Przydziały!$L:$L; $C{i+2}; Przydziały!$M:$M;True)',
            # Total hours.
            f'=$F{i+2}+$G{i+2}',
            # Balance.
            f'=$H{i+2}-$E{i+2}',
        ])
    worksheet = sheet.get_worksheet(1)
    worksheet.clear()
    worksheet.update_title("Pracownicy")
    sheet.values_update(
        range='Pracownicy!A:I',
        params={
            'valueInputOption': 'USER_ENTERED'
        },
        body={
            'values': data
        }
    )


def read_employees_sheet(sheet: gspread.models.Spreadsheet) -> EmployeesSummary:
    """Reads Employee data from the Spreadsheet."""
    emp_sum = EmployeesSummary()
    data = read_entire_sheet(sheet)
    for row in data:
        try:
            ed = EmployeeData(
                status=row[0].lower(),
                username=row[3],
                first_name=row[1],
                last_name=row[2],
                pensum=float(row[4]),
                balance=0,
                weekly_winter=0,
                weekly_summer=0,
                courses_winter=[],
                courses_summer=[],
            )
            emp_sum[ed['username']] = ed
        except ValueError:
            # Skip incorrectly formatted rows (header included).
            continue
    return emp_sum

##################################################
# END PLAN EMPLOYEES SHEET LOGIC
##################################################

##################################################
# BEGIN READING ASSIGNMENTS SHEET LOGIC
##################################################


def read_entire_sheet(sheet: gspread.models.Spreadsheet):
    try:
        sh = sheet.sheet1.get_all_values()
    except gspread.exceptions.APIError:
        return []
    return sh
##################################################
# END READING ASSIGNMENTS SHEET LOGIC
##################################################
