## https://learndataanalysis.org/export-excel-data-to-google-sheets-in-python/

from Google import Create_Service
import pandas as pd
# import win32com.client as win32

# xlApp = win32.Dispatch('Excel.Application')
# wb = xlApp.Workbooks.Open(r"./test.xlsx")
# ws = wb.Worksheets('Sheet1')
# rngData = ws.Range('A1').CurrentRegion()


# Google Sheet Id
worksheet_id = '144wxY9kdNAm68hySqE9-1pUvuKSzZiaYHdqT0-wEdWk'
CLIENT_SECRET_FILE = 'client_secret.json'
# API_SERVICE_NAME = 'sheets'
# API_VERSION = 'v4'
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

API_NAME = 'sheets'
API_VERSION = 'v4'
SCOPES = ['https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/script.external_request']

# service = Create_Service(CLIENT_SECRET_FILE, API_SERVICE_NAME, API_VERSION, SCOPES)
service = Create_Service(API_NAME, API_VERSION, SCOPES)

## NOTE: data
input_values_list = [
    ['a','b','c'],
    ['a','b','c'],
    ['a','b','c']
]
write_requests = [{
    "range": "Sheet1!B7:D9",
    "majorDimension": "ROWS",
    "values": input_values_list
}]

Body = {"valueInputOption": "RAW", "data": write_requests}
result = service.spreadsheets().values().batchUpdate(spreadsheetId=worksheet_id, body=Body).execute()

# response = service.spreadsheets().values().append(
#     spreadsheetId=gsheet_id,
#     valueInputOption='RAW',
#     range='WorksheetName!A1',
#     body=dict(
#         majorDimension='ROWS',
#         values=rngData
#     )
# ).execute()