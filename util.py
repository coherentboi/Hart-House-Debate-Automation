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


