# - pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
# - pip install --upgrade oauth2client
# - pip install gspread

# https://developers.google.com/sheets/api/reference/rest
# https://developers.google.com/sheets/api/quickstart/python
# https://github.com/googleapis/google-api-python-client

# https://developers.google.com/sheets/api/guides/create
# https://spreadsheetpoint.com/get-sheet-name-google-sheets/

from Google import Create_Service
import json

## list Google Sheets
def _list_sheets(gds):
    """파일 or 폴더 목록
    """
    results = gds.files().list(
        q = "mimeType='application/vnd.google-apps.spreadsheet'",
        fields="nextPageToken, files(id, name)"
    ).execute()

    return {item['name']: item['id'] for item in results.get('files', [])}


def _spreadsheetId_by_title(title, gds):
    return gds.files().list(
        q = f"name = '{title}'",
        fields="nextPageToken, files(id, name)"
    ).execute()['files'][0]['id']


def _spreadsheet_by_title(title, gss):
    return gss.spreadsheets().get(spreadsheetId=_spreadsheetId_by_title(title))


def _worksheet_by_title(title='sheet1', spreadsheet=None, gss=None):
    return gss.spreadsheets().get(spreadsheetId=_spreadsheetId_by_title(title))


def create_file(title, gss):
    spreadsheet = {
        'properties': {
            'title': title
        }
    }
    spreadsheet = gss.spreadsheets().create(
        body=spreadsheet,
        fields='spreadsheetId'
    ).execute()

    return {title: spreadsheet.get('spreadsheetId')}


if __name__ == "__main__":
    ## NOTE: service
    gds = Create_Service("drive")  # Google Drive Service
    gss = Create_Service("sheets")  # Google Sheets Service

    title = 'test_google_sheets'

    ## NOTE:
    data = _list_sheets(gds)
    print(data)

    json.dump(data, open("list.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)


