from google.oauth2 import service_account
from apiclient import discovery

SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'google-token.json'

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = discovery.build('sheets', 'v4', credentials=credentials)

spreadsheet_id = '1dsdUbH3H73i4nXWs-_kaU5VhK9VTo_hK4lxSPeCoHTY'
range_name = 'Questions!A1:A1'

values = [['test']]
data = { 'values' : values }

#service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, body=data, range=range_name, valueInputOption='USER_ENTERED').execute()

response = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()

print(response)

print(response['values'][0][0])
