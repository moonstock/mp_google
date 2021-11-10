# - pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
# - pip install --upgrade oauth2client
# - pip install gspread

import os, sys
import json

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials  ## googledrive 인증

PATH_ACCOUNT = "configs/account.json"
PATH_API_SPEC = "configs/api_spec.json"


def Create_Service(api_name="sheets"):
    api_spec = json.load(open(PATH_API_SPEC, "r", encoding="utf-8"))[api_name]

    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        json.load(open(PATH_ACCOUNT, "r", encoding="utf-8")), 
        api_spec['scopes']
    )

    api_name = api_name.lower()

    if 'gspread' in api_name:  ## gspread는 별도(3rd party) package
        return credentials
    else:
        return build(api_name, api_spec['version'], credentials=credentials)


if __name__ == "__main__":
    service = Create_Service(api_name="sheets")

    # ## NOTE: Google Sheets
    # worksheet_id = '144wxY9kdNAm68hySqE9-1pUvuKSzZiaYHdqT0-wEdWk'

    # input_values_list = [
    #     [1, 2, 3],
    #     ['a','b','c'],
    #     ['ㄱ','ㄴ','ㄷ'],
    # ]
    # write_requests = [{
    #     "range": "Sheet1!B7:D9",
    #     "majorDimension": "ROWS",
    #     "values": input_values_list
    # }]

    # Body = {"valueInputOption": "RAW", "data": write_requests}
    # result = service.spreadsheets().values().batchUpdate(spreadsheetId=worksheet_id, body=Body).execute()
