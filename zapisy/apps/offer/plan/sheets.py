import gspread
from oauth2client.service_account import ServiceAccountCredentials

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def create_sheets_service(id):
    credentials = ServiceAccountCredentials.from_json_keyfile_name('apps/offer/plan/Credentials.json', SCOPES)
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key(id)
    return sh


def votes_to_sheets_format(votes):
    values = [
        [
            'name',
            'votes',
            'total',
            'count max',
            'type',
            'teacher',
            'proposal',
            'semester',
            'enrolled'
        ]
    ]

    for key, value in votes.items():
        for ke, val in value.items():
            row = [val['name'], val['votes']]
            for k, v in val.items():
                if k != 'name' and k != 'votes':
                    row.append(v)
            values.append(row)

    return values


def update_voting_results_sheet(sheet, votes):
    data = votes_to_sheets_format(votes)
    sheet.values_update(
        range='A:I',
        params={
            'valueInputOption': 'USER_ENTERED'
        },
        body={
            'values': data
        }
    )
