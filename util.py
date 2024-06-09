import os
import io
from googleapiclient.http import MediaIoBaseDownload
import PyPDF2

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
    with open('output.pdf', 'wb') as f:
        fh.seek(0)
        f.write(fh.read())


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

def process_files(driveService, link_col, row):
    
    filename = 'output.pdf'
    download_pdf(driveService, row[link_col], filename)
    return read_pdf(filename)

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

