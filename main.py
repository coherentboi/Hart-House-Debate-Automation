from util import connect, read_sheet, check_payment, check_manual

from summersplit2024 import spreadsheet_id

def main():
    
    driveService, sheetsService = connect()

    formResponseData = read_sheet(sheetsService, spreadsheet_id, 'Form Responses 1!A1:ZZ')

    check_payment(sheetsService, spreadsheet_id, driveService, formResponseData)

    failedPaymentData = read_sheet(sheetsService, spreadsheet_id, 'Review Payment!A2:ZZ')

    check_manual(sheetsService, spreadsheet_id, failedPaymentData)

    processed_payments = read_sheet(sheetsService, spreadsheet_id, 'Payment Processed!A1:ZZ')


if __name__ == '__main__':
    main()
