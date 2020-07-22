import os
from typing import List, Optional

import environ
import gspread
from django.conf import settings
from django.contrib.auth.models import User
from oauth2client.service_account import ServiceAccountCredentials

from apps.offer.plan.utils import (EmployeeData, EmployeesSummary, ProposalSummary, ProposalVoteSummary, SingleAssignmentData, SingleYearVoteSummary,
                                   VotingSummaryPerYear)
from apps.users.models import Employee

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def create_sheets_service(sheet_id: str) -> gspread.models.Spreadsheet:
    """Creates a Google Sheets connection.

    Loads up data from enviorement, creates credentials and connects to
    appropriate spreadsheet.
    """
    env = environ.Env()
    environ.Env.read_env(os.path.join(settings.BASE_DIR, os.pardir, 'env', '.env'))
    creds = {"type": env('SERVICE_TYPE'),
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
        sy['total'],
        sy['votes'],
        sy['count_max'],
        sy['enrolled'] is not None,
        sy['enrolled'],
    ]


def prepare_proposal_row(pvs: ProposalVoteSummary, years: List[str]) -> List[str]:
    """Creates a single spreadsheet row summarising voting for the proposal."""
    proposal = pvs.proposal
    beg = [
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


def update_voting_results_sheet(sheet: gspread.models.Spreadsheet, votes: VotingSummaryPerYear, years: List[str]):
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


def proposal_to_sheets_format(proposal: ProposalSummary):
    """Function prepares data for Assignments spreadsheet.

    Returns:
        List of lists, where each inner list represents a single row in spreadsheet.
    """
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
            'Wielu prowadzących'
        ]
    ]

    lp = 0
    prev_name = ''
    for value in proposal:
        if value['name'] != prev_name:
            lp += 1
        prev_name = value['name']

        row = [
            lp,
            value['name'],                              # nazwa kursu
            value['group_type'],                        # typ grupy
            get_short_type_name(value['group_type']),   # skrót typu
            '',                                         # niestangardowa liczba godzin/semestr
            '',                                         # h/tydzień
            '',                                         # przelicznik
            value['hours'],                             # h/semestr
            '',                                         # do pensum
            value['semester'],                          # semestr
            value['teacher'],                           # przydział
            value['teacher_code'],                      # kod prowadzącego
            'FALSE',                                    # potwierdzony
            ''                                          # wielu prowadzących
        ]

        data.append(row)
    return data


def get_short_type_name(type_name: str):
    if type_name.lower() == 'wykład':
        return 'w'
    elif type_name.lower() == 'repetytorium':
        return 'rep'
    elif type_name.lower() == 'ćwiczenia':
        return 'ćw'
    elif type_name.lower() == 'pracownia':
        return 'prac'
    elif type_name.lower() == 'ćwiczenio-pracownia':
        return 'ćw_prac'
    elif type_name.lower() == 'seminarium':
        return 'sem'
    elif type_name.lower() == 'admin':
        return 'admin'


def update_plan_proposal_sheet(sheet: gspread.models.Spreadsheet, proposal: ProposalSummary):
    data = proposal_to_sheets_format(proposal)
    sheet.sheet1.clear()
    sheet.values_update(
        range='A:N',
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
        assignment_confirmed = row[12] == 'TRUE'
        # Continue to next assignment if this assignment not confirmed.
        if not assignment_confirmed:
            continue

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
            multiple_teachers=row[13] if row[13] else None,
        )
        assignments.append(sad)
    return assignments

##################################################
# END PLAN PROPOSAL SHEET LOGIC
##################################################

##################################################
# BEGIN PLAN EMPLOYEES SHEET LOGIC
##################################################


def employee_row(employee: EmployeeData) -> List[str]:
    return [
        employee['status'],
        employee['first_name'],
        employee['last_name'],
        employee['username'],
        str(employee['pensum']),
    ]


def update_employees_sheet(sheet: gspread.models.Spreadsheet, proposal: ProposalSummary):
    usernames = set(p['teacher_username'] for p in proposal)
    employees = Employee.objects.filter(user__username__in=usernames)
    all_contractors = set(
        User.objects.filter(groups='external_contractors').values_list('username', flat=True))
    all_phd_students = set(
        User.objects.filter(groups='phd_students').values_list('username', flat=True))
    data = [['Status', 'Imię', 'Nazwisko', 'Username', 'Pensum']]
    for e in employees:
        username = e.user.username
        if username in all_contractors:
            status = 'inny'
        elif username in all_phd_students:
            status = 'doktorant'
        else:
            status = 'pracownik'
        summary = EmployeeData(
            status=status,
            username=username,
            first_name=e.user.first_name,
            last_name=e.user.last_name,
            pensum=0,
            balance=0.0,
            weekly_winter=0,
            weekly_summer=0,
            courses_winter=[],
            courses_summer=[],
        )
        data.append(employee_row(summary))
    sheet.sheet1.clear()
    sheet.values_update(
        range='A:E',
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
