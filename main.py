import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

from summersplit2024 import check_files

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive.readonly']

# Load the environment variables from .env file
load_dotenv()



def read_sheet(service, spreadsheet_id, range_name):
    # Call the Sheets API to fetch the data
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        return values


def connect():
    """Shows basic usage of the Sheets API."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    
    return build('drive', 'v3', credentials=creds), build('sheets', 'v4', credentials=creds)

    # Call the Sheets API

def main():
    
    driveService, sheetsService = connect()

    spreadsheet_id = os.getenv('HH_SUMMER_SPLIT_SPREADSHEET_ID')

    data = read_sheet(sheetsService, spreadsheet_id, 'Form Responses 1!A1:ZZ')

    check_files(driveService, data)

if __name__ == '__main__':
    main()
