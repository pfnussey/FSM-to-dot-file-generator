
import sys
from NodeRed_FSM import NodeRed_FSM


# To compile this program to a single .exe file use the following command (with the version number updated appropriately
# C:\Users\pfnus\PycharmProjects\PFN Testing>pyinstaller makeDotFile.py --onefile --name makeDotFile_v1.0
# Originally written in early 2025 but published to GitHub repo 17/02/2026


VERSION = "Source file: makeDotFile.py Ver 1.1"
USAGE = "Usage: makeDotFile \"working_directory\" \"JSON file name\" \"FSM name\""

if len(sys.argv) > 1:
    # CLI mode
    print(VERSION)
    print(USAGE)
    print("argv[0]: ", sys.argv[0]) #program name
    print("argv[1]: ", sys.argv[1]) #file path to working directory
    print("argv[2]: ", sys.argv[2]) #file name of JSON file (in the working directory)
    print("argv[3]: ", sys.argv[3]) #the name of the FSM

    inputFilePath = sys.argv[1]
    inputfileName = sys.argv[2]
    FSM_Name = sys.argv[3]
    input_file_path = inputFilePath + inputfileName
    FSM = NodeRed_FSM(FSM_Name, input_file_path)
    FSM.load_FSM_Definition()
    errors = FSM.validate()
    if errors:
        print("Validation failed:")
        for e in errors:
            print("  - " + e)
        sys.exit(1)
    FSM.buildDotFile()
else:
    # GUI mode
    import tkinter as tk
    from fsm_gui import FSMGeneratorGUI
    root = tk.Tk()
    app = FSMGeneratorGUI(root)
    root.mainloop()
