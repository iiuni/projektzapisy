import os
from typing import List, Optional, Set

from django.conf import settings
import environ
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from apps.offer.plan.utils import (
    EmployeeData,
    EmployeesSummary,
    ProposalSummary,
    ProposalVoteSummary,
    SingleAssignmentData,
    SingleYearVoteSummary,
    VotingSummaryPerYear,
)

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
    row1 = [""]*9 + sum(([y, "", "", "", ""] for y in years), [])
    row2 = [
        "Proposal ID",
        "Nazwa",
        "Typ kursu",
        "Semestr",
        "Obowiązkowy",
        "Rekomendowany dla I roku",
        "Punktów pow. średniej",
        "Utrzymana popularność",
        "Heurystyka",
    ] + [
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


def prepare_proposal_row(pvs: ProposalVoteSummary, years: List[str], row: int) -> List[List[str]]:
    """Creates a single spreadsheet row summarising voting for the proposal."""
    proposal = pvs.proposal
    beg: List[str] = [
        proposal.id,
        proposal.name,
        proposal.course_type.name,
        proposal.semester,
        proposal.course_type.obligatory,
        proposal.recommended_for_first_year,
        f'=J{row}>AVERAGE(J$3:J)',
        f'=IFERROR(J{row}>0.8*AVERAGEIF($2:$2; "Głosów";K{row}:{row}))',
        f'=OR(E{row}; F{row}; G{row}; H{row})',
    ]
    per_year = (prepare_annual_voting_part_of_row(
        pvs.voting.get(y, None)) for y in years)
    return [beg + sum(per_year, [])]


def votes_to_sheets_format(votes: VotingSummaryPerYear, years: List[str]) -> List[List[str]]:
    legend_rows = prepare_legend_rows(years)
    proposal_rows = (prepare_proposal_row(pvs, years, i+3)
                     for i, pvs in enumerate(votes.values()))
    return legend_rows + sum(proposal_rows, [])


def update_voting_results_sheet(sheet: gspread.models.Spreadsheet, votes: VotingSummaryPerYear,
                                years: List[str]):
    data = votes_to_sheets_format(votes, years)
    sheet.sheet1.clear()
    sheet.values_update(
        range='A:' + gspread.utils.rowcol_to_a1(1, 9 + 5 * len(years))[:-1],
        params={
            'valueInputOption': 'USER_ENTERED'
        },
        body={
            'values': data
        }
    )


def read_opening_recommendations(sheet: gspread.models.Spreadsheet) -> Set[int]:
    """Reads recommendations (whether to open course) from the voting sheet."""
    worksheet = sheet.sheet1
    try:
        data = worksheet.batch_get(['A3:A', 'I3:I'], major_dimension='COLUMNS')
    except KeyError:
        return set()
    ids = data[0][0]
    rec = data[1][0]
    pick = set()
    for proposal_id, recommendation in zip(ids, rec):
        if recommendation == 'TRUE':
            pick.add(int(proposal_id))
    return pick


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
    data = [
        [
            'Proposal ID',
            'Przedmiot',
            'Forma zajęć',
            'Skrót f.z.',
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

    for i, group in enumerate(groups):
        row = [
            group.proposal_id,  # A. proposal_id
            group.name,  # B. course name
            group.group_type,  # C. group type
            group.group_type_short,  # D. abbr. group type (as in Scheduler)
            group.hours_weekly or f'=QUOTIENT(G{i+2};15)',  # E. h/week
            group.equivalent,  # F. hours equivalent (towards pensum)
            group.hours_semester,  # G. h/semester
            f'=G{i+2}*$F{i+2}/N{i+2}',  # H. formula counting the hours into pensum.
            group.semester,  # I. semester
            group.teacher,  # J. assigned teacher
            group.teacher_username,  # K. assigned teacher username
            group.confirmed,  # L. confirmed
            group.multiple_teachers_id,  # M. multiple teachers
            f'=IF(ISBLANK(M{i+2}); 1; COUNTIFS(B:B; B{i+2}; M:M; M{i+2}))',
            # N. formula computing the denominator per
            # multiple teachers
        ]

        data.append(row)
    return data


def update_plan_proposal_sheet(sheet: gspread.models.Spreadsheet, proposal: ProposalSummary):
    data = proposal_to_sheets_format(proposal)
    worksheet = sheet.get_worksheet(0)
    worksheet.clear()
    worksheet.update_title("Przydziały")
    worksheet.update('A:O', data, raw=False)


def read_assignments_sheet(sheet: gspread.models.Spreadsheet) -> List[SingleAssignmentData]:
    """Reads confirmed assignments from the spreadsheet."""
    try:
        worksheet = sheet.worksheet("Przydziały")
    except gspread.WorksheetNotFound:
        return []
    data = read_entire_sheet(worksheet)
    assignments = []
    for row in data:
        try:
            sad = SingleAssignmentData(
                proposal_id=int(row[0]),
                name=row[1],
                group_type=row[2].lower(),
                group_type_short=row[3],
                hours_weekly=int(row[4]),
                equivalent=float(row[5]),
                hours_semester=float(row[6]),
                semester=row[8],
                teacher=row[9],
                teacher_username=row[10],
                confirmed=row[11] == 'TRUE',
                multiple_teachers_id=row[12],
                multiple_teachers=int(row[13]),
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


def update_employees_sheet(sheet: gspread.models.Spreadsheet, teachers: List[EmployeeData]):
    data = [[
        'Imię', 'Nazwisko', 'Username', 'Status', 'Pensum', 'Godziny (z)', 'Godziny (l)',
        'Godziny razem', 'Bilans'
    ]]

    for i, t in enumerate(teachers):
        data.append([
            t['first_name'],
            t['last_name'],
            t['username'],
            t['status'],
            str(t['pensum']),
            # Formulas computing winter and summer hours.
            f'=SUMIFS(Przydziały!$H:$H; Przydziały!$I:$I; "z"; Przydziały!$K:$K; $C{i+2}; Przydziały!$L:$L;True)',
            f'=SUMIFS(Przydziały!$H:$H; Przydziały!$I:$I; "l"; Przydziały!$K:$K; $C{i+2}; Przydziały!$L:$L;True)',
            # Total hours.
            f'=$F{i+2}+$G{i+2}',
            # Balance.
            f'=$H{i+2}-$E{i+2}',
        ])

    worksheet: gspread.models.Worksheet = sheet.get_worksheet(1)
    if worksheet is None:
        worksheet = sheet.add_worksheet("Arkusz1", 2, 10)
    worksheet.clear()
    worksheet.update_title("Pracownicy")
    worksheet.update('A:I', data, raw=False)


def read_employees_sheet(sheet: gspread.models.Spreadsheet) -> EmployeesSummary:
    """Reads Employee data from the Spreadsheet."""
    emp_sum: EmployeesSummary = {}
    try:
        worksheet = sheet.worksheet("Pracownicy")
    except gspread.WorksheetNotFound:
        return emp_sum
    data = read_entire_sheet(worksheet)
    for row in data:
        try:
            ed = EmployeeData(
                first_name=row[0],
                last_name=row[1],
                username=row[2],
                status=row[3].lower(),
                pensum=int(row[4]),
                hours_winter=float(row[5]),
                hours_summer=float(row[6]),
                balance=float(row[8]),
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


def read_entire_sheet(worksheet: gspread.models.Worksheet):
    try:
        sh = worksheet.get_all_values()
    except gspread.exceptions.APIError:
        return []
    return sh

##################################################
# END READING ASSIGNMENTS SHEET LOGIC
##################################################
