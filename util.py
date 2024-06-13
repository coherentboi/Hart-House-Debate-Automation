import os

def intInput(message, lowerBound = 0, upperBound = 999999999999):
    while(True):
        #User Inputs Value
        userInput = input(message)
        try:
            #Try To Convert To Integer
            userInteger = int(userInput)
            #Checks That Integer Is Within Bounds
            if(userInteger >= lowerBound and userInteger <= upperBound):
                return userInteger
        except:
            pass
        #Prompts User To Try Again
        print("Invalid Input. Please Try Again")

def clear():
    os.system("clear")

def enter():
    input("Press Enter To Continue")
    clear()