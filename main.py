from googleUtil import connect, read_sheet, check_payment, check_manual, organize_debaters

from util import intInput, clear, enter

from summersplit2024 import spreadsheet_id

options = ["Check Payment", "Transfer Manually Reviewed Payment", "Organize Debaters", "Get TabbyCat Information", "Exit"]

def main():
    
    driveService, sheetsService = connect()

    while(True):
        print("Welcome to the Hart House Debate Club Tournament Automation Software!\n")
        print("---------------------------------------------------")
        for index, option in enumerate(options):
            print(f"{index + 1} - {option}")
        print("---------------------------------------------------")
        userChoice = intInput("\nPlease Select an Option: ", 1, len(options))
        clear()
        if(userChoice == 1):
            formResponseData = read_sheet(sheetsService, spreadsheet_id, 'Form Responses 1!A1:ZZ')
            check_payment(sheetsService, spreadsheet_id, driveService, formResponseData)
            print("Checking Payment Completed")
            enter()
        elif(userChoice == 2):
            failedPaymentData = read_sheet(sheetsService, spreadsheet_id, 'Review Payment!A2:ZZ')
            check_manual(sheetsService, spreadsheet_id, failedPaymentData)
            print("Transfered Manually Reviewed Payments")
            enter()
        elif(userChoice == 3):
            processed_payments = read_sheet(sheetsService, spreadsheet_id, 'Payment Processed!A1:ZZ')
            organize_debaters(sheetsService, spreadsheet_id, processed_payments)
            print("Compiled Debater Information")
            enter()
        else:
            break
      

    

    

    

    debater_information = read_sheet(sheetsService, spreadsheet_id, 'Debater Information!A1:ZZ')

if __name__ == '__main__':
    main()
