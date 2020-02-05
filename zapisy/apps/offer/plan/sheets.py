import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from apps.offer.vote.models.system_state import SystemState
import environ
import json
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def create_sheets_service(sheet_id):
    env = environ.Env()
    environ.Env.read_env()
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

# votes is return type of function get_votes
# this functions prepare data to be in a sheet format
# this function returns list with voting data for every course List[List]
# and sheet header
def votes_to_sheets_format(votes, years):
    values = create_voting_results_sheet_layout(votes, years)

    for name, value in votes.items():
        row = []
        years = []
        year = 365
        current_year_str = SystemState.get_current_state().year
        current_year = datetime.datetime.strptime(current_year_str, '%Y/%y')
        val = list(value.voting.values())

        for key in value.voting.keys():
            years.append(datetime.datetime.strptime(key, '%Y/%y'))

        if len(years) == 3:
            for val in value.voting.values():
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

        row.insert(0, value.semester)
        row.insert(0, value.course_type)
        row.insert(0, name)
        values.append(row)

    return values


# arg row is a one year voting data for one course
# arg value is dict of values that should be filled
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


# votes is return type of function get_votes
def create_voting_results_sheet_layout(votes, years):
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


# votes is return type of function get_votes
# arg sheet is sheet object returns by function create_sheets_service
def update_voting_results_sheet(sheet, votes, years):
    data = votes_to_sheets_format(votes, years)
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

# proposal is return type of function get_subjects_data
# function returns a list of lists
# each inner list is a row in sheet
def proposal_to_sheets_format(proposal):
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
        if value[0][1] != prev_name:
            lp += 1
        prev_name = value[0][1]

        row = [
            lp,
            value[0][1],                        # nazwa kursu
            value[4][1],                        # typ kursu
            get_short_type_name(value[4][1]),   # skrót typu
            '',                                 # niestangardowa liczba godzin/semestr
            '',                                 # h/tydzień
            '',                                 # przelicznik
            value[5][1],                        # h/semestr
            '',                                 # do pensum
            value[1][1],                        # semestr
            value[2][1],                        # przydział
            value[3][1],                        # kod prowadzącego
            'FALSE',                            # potwierdzony
            ''                                  # wielu prowadzących
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
        return 'ćw+prac'
    elif type_name.lower() == 'seminarium':
        return 'sem'
    elif type_name.lower() == 'admin':
        return 'admin'


# proposal is return type of function get_subjects_data
# arg sheet is sheet object returns by function create_sheets_service
def update_plan_proposal_sheet(sheet, proposal):
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

##################################################
# END PLAN PROPOSAL SHEET LOGIC
##################################################

##################################################
# START READING ASSIGNMENTS SHEET LOGIC
##################################################


# arg sheet is sheet object returns by function create_sheets_service
def read_entire_sheet(sheet):
    try:
        sh = sheet.sheet1.get_all_values()
    except gspread.exceptions.APIError:
        return []
    return sh
##################################################
# END READING ASSIGNMENTS SHEET LOGIC
##################################################
