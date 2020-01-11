import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from apps.offer.vote.models.system_state import SystemState

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def create_sheets_service(sheet_id):
    credentials = ServiceAccountCredentials.from_json_keyfile_name('apps/offer/plan/Credentials.json', SCOPES)
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key(sheet_id)
    return sh


##################################################
# BEGIN VOTING RESULT SHEET LOGIC
##################################################


def votes_to_sheets_format(votes):
    values = create_voting_results_sheet_layout(votes)

    for value in votes.values():
        latest_year = list(value.values())[0]
        row = []
        years = []
        year = 365
        current_year_str = SystemState.get_current_state().year
        current_year = datetime.datetime.strptime(current_year_str, '%Y/%y')
        val = list(value.values())

        for key in value.keys():
            years.append(datetime.datetime.strptime(key, '%Y/%y'))

        if len(years) == 3:
            for val in value.values():
                voting_sheet_create_annual_part_of_row(row, val)
        elif len(years) == 2:
            if current_year == years[0]:
                if (current_year - years[1]).days > year:
                    voting_sheet_create_annual_part_of_row(row, val[0])
                    voting_sheet_create_annual_part_of_row(row)
                    voting_sheet_create_annual_part_of_row(row, val[1])
                else:
                    voting_sheet_create_annual_part_of_row(row, val[0])
                    voting_sheet_create_annual_part_of_row(row, val[1])
                    voting_sheet_create_annual_part_of_row(row)
            else:
                voting_sheet_create_annual_part_of_row(row)
                voting_sheet_create_annual_part_of_row(row, val[0])
                voting_sheet_create_annual_part_of_row(row, val[1])
        elif len(years) == 1:
            if current_year == years[0]:
                voting_sheet_create_annual_part_of_row(row, val[0])
                voting_sheet_create_annual_part_of_row(row)
                voting_sheet_create_annual_part_of_row(row)
            elif (current_year - years[0]).days > year:
                voting_sheet_create_annual_part_of_row(row)
                voting_sheet_create_annual_part_of_row(row)
                voting_sheet_create_annual_part_of_row(row, val[0])
            else:
                voting_sheet_create_annual_part_of_row(row)
                voting_sheet_create_annual_part_of_row(row, val[0])
                voting_sheet_create_annual_part_of_row(row)

        row.insert(0, latest_year['semester'])
        row.insert(0, latest_year['type'])
        row.insert(0, latest_year['name'])
        values.append(row)

    return values


# Argument does_exist tells if this annual position exists
# if does_exist is False then fill with blanks -> ''
def voting_sheet_create_annual_part_of_row(row, value={}):
    if len(value) > 0:
        took_place = True if value['enrolled'] else False
        number_of_enrolled_students = value['enrolled'] if value['enrolled'] else ''

        row.insert(0, number_of_enrolled_students)
        row.insert(0, took_place)
        row.insert(0, value['count_max'])
        row.insert(0, value['votes'])
        row.insert(0, value['total'])
    else:
        for i in range(5):
            row.insert(0, '')


def create_voting_results_sheet_layout(votes):
    years = list(list(votes.values())[0].keys())
    values = [
        [],
        [
            'Nazwa',
            'Typ kursu',
            'Semestr',
        ]
    ]

    for i in range(3):
        if i == 0:
            for j in range(3):
                values[0].append('')
        else:
            for j in range(4):
                values[0].append('')
        values[0].append(years[2 - i])

    block = [
        'Głosów',
        'Głosujących',
        'Za 3pkt',
        'Był prowadzony',
        'Zapisanych',
    ]

    for i in range(3):
        for j in range(5):
            values[1].append(block[j])

    return values


def update_voting_results_sheet(sheet, votes):
    data = votes_to_sheets_format(votes)

    sheet.sheet1.clear()
    sheet.values_update(
        range='A:R',
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


def proposal_to_sheets_format(proposal):
    data = [
        [
            'Lp',
            'Przedmiot',
            'Forma zajęć',
            'Semestr',
            'h/semestr',
            'Przydział',
            'Kod prowadzącego',
        ]
    ]

    lp = 0
    prev_name = ''
    for value in proposal:
        if value[0][1] != prev_name:
            lp += 1
        prev_name = value[0][1]

        row = [
            lp,
            value[0][1],  # course
            value[4][1],  # type
            value[1][1],  # semester
            value[5][1],  # hours
            value[2][1],  # teacher
            value[3][1],  # code
        ]

        data.append(row)
    return data


def update_plan_proposal_sheet(sheet, proposal):
    data = proposal_to_sheets_format(proposal)
    sheet.sheet1.clear()
    sheet.values_update(
        range='A:G',
        params={
            'valueInputOption': 'USER_ENTERED'
        },
        body={
            'values': data
        }
    )

##################################################
# END PLAN PROPOSAL SHEET LOGIC
##################################################

##################################################
# START READING ASSIGNMENTS SHEET LOGIC
##################################################


def read_entire_sheet(sheet):
    return sheet.sheet1.get_all_values()

##################################################
# END READING ASSIGNMENTS SHEET LOGIC
##################################################
