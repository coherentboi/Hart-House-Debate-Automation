from googleUtil import connect, read_sheet, check_payment, check_manual, organize_debaters
from tabbycatUtil import create_teams, get_break_categories, get_institutions, get_speaker_categories, get_teams

from util import intInput, clear, enter

from loadTournament import load_json_data

tournaments = ["hhss2024", "Exit"]
options = ["Check Payment", "Transfer Manually Reviewed Payment", "Organize Debaters", "Get TabbyCat Information", "Create Teams","Exit"]

def main():
    
    while(True):
        print("Welcome to the Hart House Debate Club Tournament Automation Software!\n")
        print("---------------------------------------------------")
        for index, option in enumerate(tournaments):
                print(f"{index + 1} - {option}")
        print("---------------------------------------------------")
        userChoice = intInput("\nPlease Select the Tournament You'd Like To Access: ", 1, len(tournaments))
        clear()
        if(userChoice == len(tournaments)):
            break
        
        selectedTournament = tournaments[userChoice - 1]
    
        driveService, sheetsService, visionClient = connect()

        config = load_json_data(selectedTournament)

        tabby_headers = {'Content-Type': 'application/json', "Authorization": f"Token {config['tabs_token']}"}

        while(True):
            print("Welcome to the Hart House Debate Club Tournament Automation Software!\n")
            print("---------------------------------------------------")
            for index, option in enumerate(options):
                print(f"{index + 1} - {option}")
            print("---------------------------------------------------")
            userChoice = intInput("\nPlease Select an Option: ", 1, len(options))
            clear()
            if(userChoice == 1):
                formResponseData = read_sheet(sheetsService, config['registration_spreadsheet_id'], f"{config['Form_Responses_Sheet']}!A1:ZZ")
                check_payment(sheetsService, driveService, visionClient, config, formResponseData)
                print("Checking Payment Completed")
                enter()
            elif(userChoice == 2):
                failedPaymentData = read_sheet(sheetsService, config['registration_spreadsheet_id'], f"{config['Review_Payment_Sheet']}!A2:ZZ")
                check_manual(sheetsService, config, failedPaymentData)
                print("Transfered Manually Reviewed Payments")
                enter()
            elif(userChoice == 3):
                processed_payments = read_sheet(sheetsService, config['registration_spreadsheet_id'], f"{config['Processed_Payment_Sheet']}!A1:ZZ")
                organize_debaters(sheetsService, config, processed_payments)
                print("Compiled Debater Information")
                enter()
            elif(userChoice == 4):
                get_institutions(config, tabby_headers)
                get_break_categories(config, tabby_headers)
                get_speaker_categories(config, tabby_headers)
                get_teams(config, tabby_headers)
                print("Tabbycat Information Extracted")
                enter()
            elif(userChoice == 5):
                debater_information = read_sheet(sheetsService, config['registration_spreadsheet_id'], f"{config['Debater_Information_Sheet']}!A1:ZZ")
                team_names = read_sheet(sheetsService, config['registration_spreadsheet_id'], f"{config['Team_Names_Sheet']}!A1:ZZ")
                create_teams(config, tabby_headers, debater_information, team_names)
                enter()
            else:
                break

if __name__ == '__main__':
    main()
