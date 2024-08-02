import os
import io
from google.cloud import vision
from google.cloud.vision_v1 import types
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import PyPDF2

# If modifying these scopes, delete the file ../token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/cloud-platform']

def connect():
    """Shows basic usage of the Sheets API."""
    creds = None
    # The file ../token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('./token.json'):
        creds = Credentials.from_authorized_user_file('./token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                './credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('./token.json', 'w') as token:
            token.write(creds.to_json())

    visionClient = vision.ImageAnnotatorClient(credentials=creds)
    
    return build('drive', 'v3', credentials=creds), build('sheets', 'v4', credentials=creds), visionClient

def read_sheet(service, spreadsheet_id, range_name):
    # Call the Sheets API to fetch the data
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
        return []
    else:
        return values

def download_pdf(driveService, url, filename):

    if(os.path.exists(filename)):
        os.remove(filename)

    file_id = url.split("id=")[1]
    request = driveService.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))

    # Save the PDF locally
    with open(filename, 'wb') as f:
        fh.seek(0)
        f.write(fh.read())

def download_image(driveService, url, filename):

    if(os.path.exists(filename)):
        os.remove(filename)

    file_id = url.split("id=")[1]

    request = driveService.files().get_media(fileId=file_id)

    fh = io.BytesIO()

    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    
    with open(filename, 'wb') as f:
        fh.seek(0)
        f.write(fh.read())
        
    print(f"File {filename} downloaded successfully.")

def read_image(file_path, visionClient):

    with open(file_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = visionClient.text_detection(image=image)

    texts = response.text_annotations

    if texts:
        # Compile all detected texts into a single string
        compiled_text = " ".join([text.description for text in texts])
    else:
        print('No text detected.')

    return compiled_text

def read_pdf(file_path):
    # Open the PDF file
    with open(file_path, "rb") as file:
        # Create PDF reader object
        pdf_reader = PyPDF2.PdfReader(file)
        
        data = ""

        # Iterate over each page
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            data += page.extract_text()
        
        return data
    
def process_files(driveService, link_col, row, config):
    
    filename = f"./tournaments/{config['tournament_name']}/output.pdf"
    download_pdf(driveService, row[link_col], filename)
    return read_pdf(filename)

def process_image(visionClient, driveService, link_col, row, config):
    
    filename = f"./tournaments/{config['tournament_name']}/output.png"
    download_image(driveService, row[link_col], filename)
    return read_image(filename, visionClient)

def fetch_existing_data(service, spreadsheet_id, sheet_name):
    range_name = f"{sheet_name}!A1:ZZ"  # Adjust range as needed
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])
    return values

def check_duplicates(new_data, existing_data):
    return new_data in existing_data

def append_data_to_sheet(service, spreadsheet_id, sheet_name, data):
    existing_data = fetch_existing_data(service, spreadsheet_id, sheet_name)
    if not check_duplicates(data, existing_data):
        range_name = f"{sheet_name}!A1"  # Starting point for the append
        value_input_option = 'USER_ENTERED'
        insert_data_option = 'INSERT_ROWS'
        value_range_body = {
            "majorDimension": "ROWS",
            "values": [data]
        }
        request = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            insertDataOption=insert_data_option,
            body=value_range_body
        )
        response = request.execute()
    else:
        print("Duplicate entry. Not adding to sheet.")

def check_payment(sheetsService, driveService, visionClient, config, data):
    link_col = data[0].index(config["Payment_Check_Message"])
    for index, row in enumerate(data[1:]):
        print(f"Processing row {index + 1}")

        paymentData = ""

        try:
            pdfData = process_files(driveService, link_col, row, config).lower().replace(" ", "").replace("\n", "")
            paymentData += pdfData

        except:
            
            try:
                print("PDF Processing Failed, Attempting To Process Image")
                imageData = process_image(visionClient, driveService, link_col, row, config).lower().replace(" ", "").replace("\n", "")
                paymentData += imageData


            except:
                print("Image Processing Failed, Manual Inspection Required")
                append_data_to_sheet(sheetsService, config['registration_spreadsheet_id'], config["Review_Payment_Sheet"], row)
                continue
        
        valid = False

        with open(f"./tournaments/{config['tournament_name']}/paymentInformation/orders.txt", 'r') as orderNumbers, open(f"./tournaments/{config['tournament_name']}/paymentInformation/firstnames.txt", 'r') as firstNames, open(f"./tournaments/{config['tournament_name']}/paymentInformation/lastnames.txt", 'r') as lastNames:
            for number, first, last in zip(orderNumbers, firstNames, lastNames):
                if number.strip().lower().replace(" ", "") in paymentData and first.strip().lower().replace(" ", "") in paymentData and last.strip().lower().replace(" ", "") in paymentData:
                    valid = True
                    break
            

        if(valid):
            print("Proof of Payment Valid, Adding To Sheet")
            append_data_to_sheet(sheetsService, config['registration_spreadsheet_id'], config["Processed_Payment_Sheet"], row)
        else:
            print("Proof of Payment Invalid, Manual Inspection Required")
            append_data_to_sheet(sheetsService, config['registration_spreadsheet_id'], config["Review_Payment_Sheet"], row)

        

def get_cell_background_color(service, spreadsheet_id, sheet_name, range, rgb):
    # Fetch rows from the specified range in the sheet
    result = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        ranges=f"{sheet_name}!{range}",
        includeGridData=True
    ).execute()

    color_rows = []
    # Define the RGB values for the green color you're looking for

    try:
        rows = result['sheets'][0]['data'][0]['rowData']
        for index, row in enumerate(rows):
            if 'values' in row:
                cell = row['values'][0]
                bg_color = cell.get('effectiveFormat', {}).get('backgroundColor', {})
                # Normalize the RGB values
                cell_color = {k: v for k, v in bg_color.items() if v is not None}
                
                # Check if the cell color matches the green color
                if cell_color == rgb:
                    color_rows.append(True)
                else:
                    color_rows.append(False)
    except KeyError as e:
        # Handle cases where some information might be missing
        print("Error processing the data:", e)

    return color_rows

def check_manual(sheetsService, config, data):
    green_rows = get_cell_background_color(sheetsService, config['registration_spreadsheet_id'], config["Review_Payment_Sheet"], f"A2:A{len(data) + 1}", {'green': 1} )
    for index, green in enumerate(green_rows):
        if(green):
            print(f"Adding row {index} to processed payments")
            append_data_to_sheet(sheetsService, config['registration_spreadsheet_id'], config["Processed_Payment_Sheet"], data[index])
            
    red_rows = get_cell_background_color(sheetsService, config['registration_spreadsheet_id'], config["Review_Payment_Sheet"], f"A2:A{len(data) + 1}", {'red': 1} )
    for index, red in enumerate(red_rows):
        if(red):
            print(f"Adding row {index} to failed payments")
            append_data_to_sheet(sheetsService, config['registration_spreadsheet_id'], config["Payment_Failed_Sheet"], data[index])
            
def organize_debaters(sheetsService, config, data):
    institutionIndex = data[0].index(config["institution_format"])
    ANameList = []
    AEmailList = []
    ALevelList = []
    BNameList = []
    BEmailList = []
    BLevelList = []
    AccessibilityList  = []
    for i in range(1, 10):
        for index, cell in enumerate(data[0]):
            if(cell.strip() == config["debater_a_name_format"].format(i).strip()):
                ANameList.append(index)
            elif(cell.strip() == config["debater_a_email_format"].format(i).strip()):
                AEmailList.append(index)
            elif(cell.strip() == config["debater_a_level_format"].format(i).strip()):
                ALevelList.append(index)
            elif(cell.strip() == config["debater_b_name_format"].format(i).strip()):
                BNameList.append(index)
            elif(cell.strip() == config["debater_b_email_format"].format(i).strip()):
                BEmailList.append(index)
            elif(cell.strip() == config["debater_b_level_format"].format(i).strip()):
                BLevelList.append(index)
            elif(cell.strip() == config["accessibility_requirements"].format(i).strip()):
                AccessibilityList.append(index)
    for row in data[1:]:
        for index in range(len(ANameList)):
            inputRow = [row[institutionIndex].strip()]
            accessibilityRow = []

            if(row[ANameList[index]] == ""):
                continue

            inputRow.append(row[ANameList[index]])
            inputRow.append(row[AEmailList[index]])
            inputRow.append(row[ALevelList[index]])
            inputRow.append(row[BNameList[index]])
            inputRow.append(row[BEmailList[index]])
            inputRow.append(row[BLevelList[index]])

            accessibilityRow.append(row[ANameList[index]].strip() + ", " + row[BNameList[index]].strip())
            accessibilityRow.append(row[AccessibilityList[index]])

            print(f"Adding {row[ANameList[index]]} and {row[BNameList[index]]} to Debater Information")
            
            append_data_to_sheet(sheetsService, config['registration_spreadsheet_id'], config["Debater_Information_Sheet"], inputRow)
            if row[AccessibilityList[index]] != "" and row[AccessibilityList[index]].lower().strip() != "none" and row[AccessibilityList[index]].lower().strip() != "n/a":
                print(f"Adding {row[ANameList[index]]} and {row[BNameList[index]]} to Debater Information to Accessibility Requirements")
                append_data_to_sheet(sheetsService, config['registration_spreadsheet_id'], config["Accessibility_Requirements_Sheet"], accessibilityRow)

            

        