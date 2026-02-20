"""Entry point for the FSM to DOT File Generator.

Runs in CLI mode when command-line arguments are supplied, or launches
the Tkinter GUI otherwise.

CLI usage::

    makeDotFile <working_directory> <json_file_name> <fsm_name>

Command-line arguments (CLI mode):
    argv[1] (str): Path to the directory containing the JSON input file.
    argv[2] (str): Filename of the JSON input file (within that directory).
    argv[3] (str): Name to assign to the FSM.

Note:
    Docstrings in this file use Google style and are intended to be
    processed by Sphinx with the Napoleon extension (sphinx.ext.napoleon).

Originally written in early 2025, published to GitHub repo 17/02/2026.

To compile to a single executable use PyInstaller::

    pyinstaller makeDotFile.py --onefile --name makeDotFile_v2.0
"""

import sys
from NodeRed_FSM import NodeRed_FSM


VERSION = "Source file: makeDotFile.py Ver 2.0"
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
