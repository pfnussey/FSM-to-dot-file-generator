
import sys
from NodeRed_FSM import NodeRed_FSM


# To compile this program to a single .exe file use the following command (with the version number updated appropriately
# C:\Users\pfnus\PycharmProjects\PFN Testing>pyinstaller makeDotFile.py --onefile --name makeDotFile_v1.0


VERSION = "Source file: makeDotFile.py Ver 1.0"
USAGE = "Usage: makeDotFile \"working_directory\" \"JSON file name\" \"FSM name\""

#command line paramaters: argv[1] = JSON file path; argv[2] = JSON file name

print(VERSION)
print(USAGE)
print("argv[0]: ", sys.argv[0]) #program name
print("argv[1]: ", sys.argv[1]) #file path to working directory
print("argv[2]: ", sys.argv[2]) #file name of JSON file (in the working directory)
print("argv[3]: ", sys.argv[3]) #the name of the FSM

inputFilePath = sys.argv[1]
inputfileName = sys.argv[2]
FSM_Name = sys.argv[3]
FSM = NodeRed_FSM(FSM_Name, inputFilePath, inputfileName)
FSM.load_FSM_Definition()
FSM.buildDotFile()
