# - pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
# - pip install --upgrade oauth2client
# - pip install gspread

# https://developers.google.com/sheets/api/reference/rest
# https://developers.google.com/sheets/api/quickstart/python
# https://github.com/googleapis/google-api-python-client

# https://developers.google.com/sheets/api/guides/create

# https://spreadsheetpoint.com/get-sheet-name-google-sheets/

import os, sys
import os.path
import yaml
import csv
import pandas as pd
# import pickle
import json


# from googleapiclient.discovery import build
# from oauth2client.service_account import ServiceAccountCredentials  ## googledrive 인증

##------------------------------------------------------------
## User 모듈
##------------------------------------------------------------
from _session import (session)

# sys.path.append(os.path.join(os.path.dirname(__file__), '../_public/_utils')) ## Note: 현재 디렉토리 기준 상대 경로 설정
# from utils_basic import (flatten_list, file_to_dict)

## 보조 함수(file, sheet)
##=========================================================
def api(path="settings/google_account_mats.yml"):
    """google sheets api

    Args:
        path (list, optional): [description]. Defaults to ["settings/api_google_mats.yml", "settings/account_google_mats.yml"].

    Returns:
        [type]: [description]
    """
    return session(path=path, api="sheets")


def drive(path="settings/google_account_mats.yml"):
    """google sheets api

    Args:
        path (list, optional): [description]. Defaults to ["settings/api_google_mats.yml", "settings/account_google_mats.yml"].

    Returns:
        [type]: [description]
    """
    return session(path=path, api="drive")


## CRUD
##=========================================================
def spreadsheet_list(drive=None, path="settings/google_account_mats.yml"):
    """파일 or 폴더 목록

    Args:
        path (obj): google drive service (<googleapiclient.discovery.Resource object>)

    Returns:
        [dict]: {<file_title>: <file_id>, ....}
    """
    drive = session(path=path, api="drive") if drive==None else drive

    results = drive.files().list(
        q = "mimeType='application/vnd.google-apps.spreadsheet'",
        fields="nextPageToken, files(id, name)"
    ).execute()

    return {item['name']: item['id'] for item in results.get('files', [])}


def _id_by_title(title, drive=None, path="settings/google_account_mats.yml"):
    drive = session(path=path, api="drive") if drive==None else drive
    print(f"drive: {dir(drive)}")

    return drive.files().list(
        q = f"name = '{title}'",
        fields="nextPageToken, files(id, name)"
    ).execute()['files'][0]['id']


def _spreadsheet_by_title(title, drive=None, path="settings/google_account_mats.yml", api=None):
    drive = session(path=path, api="drive") if drive==None else drive   
    return api.spreadsheets().get(spreadsheetId=_id_by_title(title, drive=drive))


def _worksheet_by_title(title='sheet1', spreadsheet=None):
    drive = session(path=path, api="drive") if drive==None else drive   
    return api.spreadsheets().get(spreadsheetId=_id_by_title(title, drive=drive))

# sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
# sheets = sheet_metadata.get('sheets', '')
# title = sheets[0].get("properties", {}).get("title", "Sheet1")
# sheet_id = sheets[0].get("properties", {}).get("sheetId", 0)


def create_file(title, api):
    spreadsheet = {
        'properties': {
            'title': title
        }
    }
    spreadsheet = api.spreadsheets().create(
        body=spreadsheet,
        fields='spreadsheetId'
    ).execute()
    
    return {title: spreadsheet.get('spreadsheetId')}

    # print('Spreadsheet ID: {0}'.format(spreadsheet.get('spreadsheetId')))



if __name__ == "__main__":
    api = api(path="settings/google_account_mats.yml")

    title = 'test_google_sheets'
    # 'test_google_sheets'
    # create_file(title, api)
    # ls = spreadsheet_list(path="settings/google_account_mats.yml")
    # print(ls)

    # print(_id_by_title(title))

    print(_spreadsheet_by_title(title, api=api))

