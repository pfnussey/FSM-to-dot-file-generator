"""Core FSM data model for the FSM to DOT File Generator.

Provides the :class:`NodeRed_FSM` class, which loads a Node-Red FSM
definition from a JSON file, validates it, and converts it to a
Graphviz ``.dot`` file.

Note:
    Docstrings in this file use Google style and are intended to be
    processed by Sphinx with the Napoleon extension (sphinx.ext.napoleon).

Originally written in early 2025, published to GitHub repo 17/02/2026.
"""

import json
import os
from datetime import datetime

PROGRAM_NAME = "makeDotFile"


class NodeRed_FSM:
    """Encapsulates a Node-Red FSM definition loaded from a JSON file.

    Provides methods to load and validate the FSM definition and to
    generate a Graphviz ``.dot`` file representing the state diagram.

    Attributes:
        name (str): The name assigned to the FSM.
        data (file): The raw file handle returned by ``open()``.
        FSM_as_Dict (dict): The FSM definition parsed from JSON.
        input_file_path (str): Path to the source JSON file.
        output_file_path (str or None): Desired output ``.dot`` file path,
            or ``None`` to auto-generate from the input directory and FSM name.
        dotFileName (str): Resolved path of the generated ``.dot`` file,
            populated after :meth:`buildDotFile` is called.
    """

    def __init__(self, name, input_file_path, output_file_path=None):
        """Initialise the FSM object.

        Args:
            name (str): The name to assign to the FSM.
            input_file_path (str): Path to the JSON file containing the
                FSM definition.
            output_file_path (str, optional): Path for the output ``.dot``
                file. If omitted, a path is auto-generated from the input
                directory and the FSM name. Defaults to ``None``.
        """
        self.name = name
        self.data = ""
        self.FSM_as_Dict: dict = ""
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.dotFileName = ""

    def load_FSM_Definition(self):
        """Load and parse the FSM definition from the JSON input file.

        Reads :attr:`input_file_path` and stores the parsed result in
        :attr:`FSM_as_Dict`.

        Raises:
            FileNotFoundError: If :attr:`input_file_path` does not exist.
            json.JSONDecodeError: If the file content is not valid JSON.
        """
        self.data = open(self.input_file_path, "r")
        self.FSM_as_Dict = json.loads(self.data.read())

    def validate(self):
        """Validate the loaded FSM definition.

        Checks that the required top-level keys are present, that the
        state structure is well-formed, and that all transition target
        states are defined.

        Returns:
            list[str]: A list of error message strings. An empty list
            indicates that the definition is valid.
        """
        errors = []

        # Check top-level keys
        if "state" not in self.FSM_as_Dict:
            errors.append("Missing top-level key: 'state'")
        if "transitions" not in self.FSM_as_Dict:
            errors.append("Missing top-level key: 'transitions'")
        if errors:
            return errors  # Can't continue without these

        # Check state structure
        state = self.FSM_as_Dict["state"]
        if "status" not in state:
            errors.append("'state' object is missing 'status' key")

        # Check transitions is non-empty dict
        transitions = self.FSM_as_Dict["transitions"]
        if not isinstance(transitions, dict) or len(transitions) == 0:
            errors.append("'transitions' must be a non-empty object")
            return errors  # Can't continue

        # Check each transition entry has "status"
        for source_state, triggers in transitions.items():
            if not isinstance(triggers, dict):
                errors.append(f"Transitions for state '{source_state}' must be an object")
                continue
            for trigger_name, trigger_data in triggers.items():
                if not isinstance(trigger_data, dict) or "status" not in trigger_data:
                    errors.append(f"Transition '{source_state}' -> '{trigger_name}' is missing 'status' key")

        # Check initial state exists in transitions
        if "status" in state:
            initial_state = state["status"]
            if initial_state not in transitions:
                errors.append(f"Initial state '{initial_state}' not found in transitions")

        # Check all target states exist as source states
        defined_states = set(transitions.keys())
        for source_state, triggers in transitions.items():
            if not isinstance(triggers, dict):
                continue
            for trigger_name, trigger_data in triggers.items():
                if isinstance(trigger_data, dict) and "status" in trigger_data:
                    target = trigger_data["status"]
                    if target not in defined_states:
                        errors.append(f"Target state '{target}' (from '{source_state}' via '{trigger_name}') is not defined in transitions")

        return errors

    def getFSM_as_dict(self):
        """Return the FSM definition as a Python dictionary.

        Returns:
            dict: The parsed FSM definition, as populated by
            :meth:`load_FSM_Definition`.
        """
        return self.FSM_as_Dict

    def printFSM(self):
        """Print a formatted JSON representation of the FSM to stdout.

        Outputs the FSM name and the full JSON definition with 4-space
        indentation.
        """
        print("JSON formatted print of :", os.path.basename(self.input_file_path), "\n", json.dumps(self.FSM_as_Dict, indent=4))

    def getDotFileName(self):
        """Return the path of the most recently generated ``.dot`` file.

        Returns:
            str: The resolved ``.dot`` file path, or an empty string if
            :meth:`buildDotFile` has not yet been called.
        """
        return(self.dotFileName)

    def buildDotFile(self, user_notes=""):
        """Generate a Graphviz ``.dot`` file from the loaded FSM definition.

        Writes the ``.dot`` file to :attr:`output_file_path` if set,
        otherwise auto-generates the output path in the same directory as
        the input file. The file includes a header comment block with
        metadata (author, timestamp, state/transition counts, initial state)
        and an optional user-supplied notes section.

        Args:
            user_notes (str, optional): Free-text notes to append to the
                diagram label below a ``---`` separator. Double-quote
                characters are escaped automatically. Defaults to ``""``.

        Side effects:
            Sets :attr:`dotFileName` to the resolved output path and writes
            the ``.dot`` file to disk.
        """
        #build the file name
        now = datetime.now()
        date = now.strftime("%Y%m%d")
        time = now.strftime("%H%M%S")

        if self.output_file_path:
            self.dotFileName = self.output_file_path
        else:
            #auto-generate output path in same directory as input file
            input_dir = os.path.dirname(self.input_file_path)
            dot_name = self.name + "_" + date + ".dot"
            self.dotFileName = os.path.join(input_dir, dot_name)

        #extract and format the transitions
        transitions  = ""
        for k1, v1 in self.FSM_as_Dict["transitions"].items():
            for k2, v2 in v1.items():
                transitions = transitions + "\n" + k1 + " -> " + v2["status"] + " [label = \"" + k2 + "\"];"

        #Build the header info for the .dot file
        date = now.strftime("%d/%m/%Y")
        time = now.strftime("%H:%M:%S")
        title = self.name + ": script for rendering FSM diagram in Graphviz (.dot format)"
        newline = "\n"
        author = "Peter Nussey"
        programName = PROGRAM_NAME

        versionInfo = "Generated by " + programName + " " + time + " on " + date

        #Compute auto-generated stats
        transitions_dict = self.FSM_as_Dict["transitions"]
        state_count = len(transitions_dict)
        transition_count = sum(len(v) for v in transitions_dict.values() if isinstance(v, dict))
        initial_state = self.FSM_as_Dict["state"].get("status", "unknown")
        source_file = os.path.basename(self.input_file_path)
        pdf_file_path = os.path.splitext(self.dotFileName)[0] + ".pdf"
        dotCommand = 'dot -Tpdf \\"' + self.dotFileName + '\\" -o \\"' + pdf_file_path + '\\"'

        fileHeader = (newline + title + newline +
                      "Author: " + author + newline +
                      versionInfo + newline +
                      "Source: " + source_file + newline +
                      "States: " + str(state_count) +
                      "  |  Transitions: " + str(transition_count) + newline +
                      "Initial state: " + initial_state + newline)

        #Build diagram label content: auto-generated notes + optional user notes
        label_content = fileHeader + dotCommand + newline
        if user_notes:
            escaped_notes = user_notes.replace('"', '\\"')
            label_content = label_content + "---" + newline + escaped_notes + newline

        layoutInfo = """digraph finite_state_machine {
	node [fontname="Helvetica,Arial,sans-serif", fontcolor=blue, fontsize=7]
	edge [fontname="Times-Italic", fontcolor=red, fontstyle=italic, fontsize=7, arrowsize=0.5]
	rankdir=LR;"""

        diagramFooterComment = "fontsize=8\nlabel = \"" + label_content + "\""

        #Write the .dot file
        f = open(self.dotFileName, "w")
        f.write("/*" + fileHeader + "*/" + newline + layoutInfo + newline + transitions + newline + diagramFooterComment + "\n}")
        f.close()
        print("Wrote to file: ", self.dotFileName)
