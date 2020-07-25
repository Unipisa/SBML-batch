import os
from pathlib import Path

# to create a directory and close the program if a failure occur
def createDirectoryExit(path):
    if not Path(path).is_dir():
        try:
            os.mkdir(path)
        except:
            exit("An error occurred during creation of directory")

# to create a directory. If a failure occurs it returns 1 else 0
def createDirectory(path):
    if not Path(path).is_dir():
        try:
            os.mkdir(path)
        except:
            print("An error occurred during creation of directory")
            return 1
    return 0

# to remove a file. If a failure occurs it returns 1 else 0
def removeFile(path):
    if Path(path).is_file():
        try:
            os.remove(path)
        except:
            print("An error occurred while removing of file")
            return 1
    return 0

# to ask to user a integer number. Allow values can be specified 
# using a list. It returns the user's value
def numericalInput(outputString, allowValues):
    try:
        choice=int(input(outputString))
    except ValueError:
        exit("Error: insert a number")
    if allowValues!=[] and choice not in allowValues:
        exit("Error: invalid choice")
    return choice