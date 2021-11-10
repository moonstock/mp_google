import pickle
import os
import json
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request


PATH_CLIENT_SECRET = "configs/client_secret.json"
PATH_PICKLE = "configs/token.pickle"
PATH_API_SPEC = "configs/api_spec.json"


def Create_Service(api_name):
    api_spec = json.load(open(PATH_API_SPEC, "r", encoding="utf-8"))[api_name]
    cred = None
    if os.path.exists(PATH_PICKLE):
        with open(PATH_PICKLE, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(PATH_CLIENT_SECRET, api_spec['scopes'])
            cred = flow.run_local_server(port = 34905)

        with open(PATH_PICKLE, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(api_name, api_spec['version'], credentials=cred)
        print(api_name, 'service created successfully')
        return service
    except Exception as e:
        print(f'Unable to connect\n{e}')
        return None

if __name__ == "__main__":
    pass
    service = Create_Service(api_name="sheets")

    ## NOTE: Google Sheets
    worksheet_id = '144wxY9kdNAm68hySqE9-1pUvuKSzZiaYHdqT0-wEdWk'

    input_values_list = [
        [1, 2, 3],
        ['a','b','c'],
        ['ㄱ','ㄴ','ㄷ'],
        # [1.1, 2.2, 3.3]
    ]
    write_requests = [{
        "range": "Sheet1!B7:D9",
        "majorDimension": "ROWS",
        "values": input_values_list
    }]

    Body = {"valueInputOption": "RAW", "data": write_requests}
    result = service.spreadsheets().values().batchUpdate(spreadsheetId=worksheet_id, body=Body).execute()
