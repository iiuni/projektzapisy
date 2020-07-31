import os
from typing import List, Optional, Set

from django.conf import settings
import environ
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from .utils import (
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


def voting_legend_rows(years: List[str]) -> List[List[str]]:
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


def voting_annual_part_of_row(sy: Optional[SingleYearVoteSummary]) -> List[str]:
    """Dumps voting summary to five spreadsheet cells.

    If sy is None, empty cells will be produced.
    """
    if sy is None:
        return [""] * 5
    return [
        str(sy.total),
        str(sy.votes),
        str(sy.count_max),
        str(sy.enrolled is not None),
        str(sy.enrolled or ''),
    ]


def voting_proposal_row(pvs: ProposalVoteSummary, years: List[str], row: int) -> List[List[str]]:
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
    per_year = (voting_annual_part_of_row(
        pvs.voting.get(y, None)) for y in years)
    return [beg + sum(per_year, [])]


def votes_to_sheets_format(votes: VotingSummaryPerYear, years: List[str]) -> List[List[str]]:
    legend_rows = voting_legend_rows(years)
    proposal_rows = (voting_proposal_row(pvs, years, i)
                     for i, pvs in enumerate(votes.values(), start=3))
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
    sheet.sheet1.freeze(rows=2)


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
            'Kod prowadzącego',
            'Potwierdzone',
            'Wielu prowadzących',
            'Dzielnik (wielu prow.)',
            'Nadpisano h/tydzień',
        ]
    ]

    for i, group in enumerate(groups, start=2):
        row = [
            group.proposal_id,  # A. proposal_id
            group.name,  # B. course name
            group.group_type,  # C. group type
            group.group_type_short,  # D. abbr. group type (as in Scheduler)
            group.hours_weekly or f'=QUOTIENT(G{i};15)',  # E. h/week
            group.equivalent,  # F. hours equivalent (towards pensum)
            group.hours_semester,  # G. h/semester
            f'=G{i}*$F{i}/M{i}',  # H. formula counting the hours into pensum.
            group.semester,  # I. semester
            group.teacher_username,  # J. assigned teacher username
            group.confirmed,  # K. confirmed
            group.multiple_teachers_id,  # L. multiple teachers
            f'=IF(ISBLANK(L{i}); 1; COUNTIFS(B:B; B{i}; L:L; L{i}))',
            # M. formula computing the denominator per multiple teachers
            f'=NOT(ISFORMULA(E{i}))',  # N. Has the h/semester be overridden.
        ]

        data.append(row)
    return data


def update_assignments_sheet(sheet: gspread.models.Spreadsheet, proposal: ProposalSummary):
    data = proposal_to_sheets_format(proposal)
    worksheet = sheet.get_worksheet(0)
    worksheet.clear()
    worksheet.update_title("Przydziały")
    worksheet.update('A:N', data, raw=False)
    worksheet.format('M:N', {'textFormat': {'italic': True}})
    worksheet.freeze(rows=1)


def read_assignments_sheet(sheet: gspread.models.Spreadsheet) -> List[SingleAssignmentData]:
    """Reads confirmed assignments from the spreadsheet.

    Raises:
        KeyError: When a value is missing in the spreadsheet.
        ValueError: When a value is incorrectly formatted.
    """
    try:
        worksheet = sheet.worksheet("Przydziały")
    except gspread.WorksheetNotFound:
        return []
    data = worksheet.get_all_records()
    assignments = []
    for i, row in enumerate(data, start=2):
        try:
            hours_w_overridden = row['Nadpisano h/tydzień'] == 'TRUE'
            sad = SingleAssignmentData(
                proposal_id=int(row['Proposal ID']),
                name=row['Przedmiot'],
                group_type=row['Forma zajęć'].lower(),
                group_type_short=row['Skrót f.z.'],
                hours_weekly=int(row['h/tydzień']) if hours_w_overridden else None,
                equivalent=float(row['Przelicznik']),
                hours_semester=float(row['h/semestr']),
                semester=row['Semestr'],
                teacher_username=row['Kod prowadzącego'],
                confirmed=row['Potwierdzone'] == 'TRUE',
                multiple_teachers_id=row['Wielu prowadzących'],
                multiple_teachers=int(row['Dzielnik (wielu prow.)']),
            )
        except KeyError as e:
            raise KeyError(f"Błąd czytania arkusza przydziałów. Brakuje wartości w kolumnie {e}.")
        except ValueError as e:
            raise ValueError(
                f"Błąd czytania arkusza przydziałów (wiersz {i}): {str(e).capitalize()}.")
        assignments.append(sad)
    return assignments


def update_employees_sheet(sheet: gspread.models.Spreadsheet, teachers: List[EmployeeData]):
    data = [[
        'Username', 'Imię', 'Nazwisko', 'Status', 'Pensum', 'Godziny (z)', 'Godziny (l)',
        'Godziny razem', 'Bilans'
    ]]

    for i, t in enumerate(teachers):
        data.append([
            t.username,
            t.first_name,
            t.last_name,
            t.status,
            str(t.pensum),
            # Formulas computing winter and summer hours.
            f'=SUMIFS(Przydziały!$H:$H; Przydziały!$I:$I; "z"; Przydziały!$J:$J; $A{i+2}; Przydziały!$K:$K;True)',
            f'=SUMIFS(Przydziały!$H:$H; Przydziały!$I:$I; "l"; Przydziały!$J:$J; $A{i+2}; Przydziały!$K:$K;True)',
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
    worksheet.format('F:I', {'textFormat': {'italic': True}})
    worksheet.freeze(rows=1)


def read_employees_sheet(sheet: gspread.models.Spreadsheet) -> EmployeesSummary:
    """Reads Employee data from the Spreadsheet.

    Raises:
        KeyError: When a value is missing in the spreadsheet.
        ValueError: When a value is incorrectly formatted.
    """
    emp_sum: EmployeesSummary = {}
    try:
        worksheet = sheet.worksheet("Pracownicy")
    except gspread.WorksheetNotFound:
        return emp_sum
    data = worksheet.get_all_records()
    for i, row in enumerate(data, start=2):
        try:
            ed = EmployeeData(
                username=row['Username'],
                first_name=row['Imię'],
                last_name=row['Nazwisko'],
                status=row['Status'].lower(),
                pensum=int(row['Pensum']),
                hours_winter=float(row['Godziny (z)']),
                hours_summer=float(row['Godziny (l)']),
                balance=float(row['Bilans']),
                courses_winter=[],
                courses_summer=[],
            )
        except KeyError as e:
            raise KeyError(f"Błąd czytania arkusza pracowników. Brakuje wartości w kolumnie {e}.")
        except ValueError as e:
            raise ValueError(
                f"Błąd czytania arkusza pracowników (wiersz {i}): {str(e).capitalize()}.")
        emp_sum[ed.username] = ed
    return emp_sum
