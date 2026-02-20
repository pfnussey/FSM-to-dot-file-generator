"""Tkinter GUI for the FSM to DOT File Generator.

Provides the :class:`FSMGeneratorGUI` class, which builds the main application
window and handles user interaction for selecting input/output files, entering
an FSM name and optional notes, and triggering ``.dot`` file generation.

Note:
    Docstrings in this file use Google style and are intended to be
    processed by Sphinx with the Napoleon extension (sphinx.ext.napoleon).

Originally written in early 2025, published to GitHub repo 17/02/2026.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
from NodeRed_FSM import NodeRed_FSM

VERSION = "Author: Peter Nussey\nver2.0, 20/02/2026"

ABOUT_TEXT = (
    "This utility program has been written to assist the user in developing "
    "Finite State Machine (FSM) definitions for Node-Red by providing a "
    "conversion between the raw JSON format used by Node-Red and a graphical "
    "state diagram representation generated from Graphviz. The FSM to DOT "
    "File Generator takes as input a JSON file which defines the FSM and "
    "converts it to a .dot file which can be used by Graphviz to draw a "
    "state diagram of the FSM.\n\n"
    "A typical workflow incorporating this tool is shown below:\n\n"
    "1. Write a JSON file to describe the desired FSM.\n"
    "2. Use the FSM to DOT File Generator to convert this file to a Graphviz "
    ".dot file.\n"
    "3. Run the dot command from Graphviz with the generated .dot file as "
    "input to generate a PDF representation of the FSM state diagram.\n"
    "4. Test the FSM and refer to the state diagram to assist with further "
    "development and debugging of the FSM.\n"
    "5. Update the JSON file as required.\n"
    "6. Repeat steps 2 - 5 until a satisfactory FSM has been developed."
)

class FSMGeneratorGUI:
  """Main application window for the FSM to DOT File Generator.

  Builds and manages the Tkinter GUI, including file selection widgets,
  an FSM name entry, a user notes area, a Generate button, and read-only
  output fields showing the derived PDF path and Graphviz dot command.

  Attributes:
      root (tk.Tk): The root Tkinter window.
      input_var (tk.StringVar): Holds the path to the input JSON file.
      name_var (tk.StringVar): Holds the FSM name.
      output_var (tk.StringVar): Holds the path for the output ``.dot`` file.
      pdf_var (tk.StringVar): Derived PDF output path (auto-updated from
          ``output_var``).
      dot_command_var (tk.StringVar): Graphviz dot command string
          (auto-updated from ``output_var`` and ``pdf_var``).
      notes_text (tk.Text): Multi-line text widget for optional user notes.
      status_var (tk.StringVar): Status bar message.
  """

  def __init__(self, root):
    """Initialise the GUI and build all widgets.

    Args:
        root (tk.Tk): The root Tkinter window to build the GUI into.
    """
    self.root = root
    self.root.title("FSM to DOT File Generator")
    self.root.resizable(False, False)

    # Title bar
    title_frame = tk.Frame(root)
    title_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
    tk.Label(title_frame, text="FSM to DOT File Generator", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT)
    tk.Label(title_frame, text=VERSION, font=("Helvetica", 10), justify=tk.RIGHT).pack(side=tk.RIGHT)
    tk.Button(title_frame, text="About", command=self.show_about).pack(side=tk.RIGHT, padx=(0, 10))

    # Input JSON File
    tk.Label(root, text="Input JSON File:", anchor=tk.W).pack(fill=tk.X, padx=10, pady=(10, 0))
    input_frame = tk.Frame(root)
    input_frame.pack(fill=tk.X, padx=10, pady=2)
    self.input_var = tk.StringVar()
    self.input_var.trace_add("write", self._on_input_changed)
    tk.Entry(input_frame, textvariable=self.input_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
    tk.Button(input_frame, text="Browse...", command=self.browse_input_file).pack(side=tk.RIGHT, padx=(5, 0))

    # FSM Name
    tk.Label(root, text="FSM Name:", anchor=tk.W).pack(fill=tk.X, padx=10, pady=(10, 0))
    self.name_var = tk.StringVar()
    self.name_var.trace_add("write", self._on_name_changed)
    tk.Entry(root, textvariable=self.name_var, width=50).pack(fill=tk.X, padx=10, pady=2)

    # Output DOT File
    tk.Label(root, text="Output DOT File:", anchor=tk.W).pack(fill=tk.X, padx=10, pady=(10, 0))
    output_frame = tk.Frame(root)
    output_frame.pack(fill=tk.X, padx=10, pady=2)
    self.output_var = tk.StringVar()
    self.pdf_var = tk.StringVar()
    self.dot_command_var = tk.StringVar()
    self.output_var.trace_add("write", self._on_output_dot_changed)
    self.pdf_var.trace_add("write", self._on_pdf_changed)
    tk.Entry(output_frame, textvariable=self.output_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
    tk.Button(output_frame, text="Browse...", command=self.browse_output_file).pack(side=tk.RIGHT, padx=(5, 0))

    # User Notes
    tk.Label(root, text="Notes:", anchor=tk.W).pack(fill=tk.X, padx=10, pady=(10, 0))
    notes_frame = tk.Frame(root)
    notes_frame.pack(fill=tk.X, padx=10, pady=2)
    notes_scrollbar = tk.Scrollbar(notes_frame, orient=tk.VERTICAL)
    self.notes_text = tk.Text(notes_frame, height=4, wrap=tk.WORD, yscrollcommand=notes_scrollbar.set)
    notes_scrollbar.config(command=self.notes_text.yview)
    self.notes_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
    notes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Generate button
    tk.Button(root, text="Generate", command=self.generate, width=15).pack(pady=15)

    # Output PDF File
    tk.Label(root, text="Output PDF File:", anchor=tk.W).pack(fill=tk.X, padx=10, pady=(0, 0))
    tk.Entry(root, textvariable=self.pdf_var, width=50).pack(fill=tk.X, padx=10, pady=2)

    # Dot Command
    tk.Label(root, text="Dot Command:", anchor=tk.W).pack(fill=tk.X, padx=10, pady=(5, 0))
    cmd_frame = tk.Frame(root)
    cmd_frame.pack(fill=tk.X, padx=10, pady=2)
    tk.Entry(cmd_frame, textvariable=self.dot_command_var, state="readonly", width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
    tk.Button(cmd_frame, text="Copy", command=self.copy_dot_command).pack(side=tk.RIGHT, padx=(5, 0))

    # Status label
    self.status_var = tk.StringVar(value="Ready")
    tk.Label(root, textvariable=self.status_var, anchor=tk.W, relief=tk.SUNKEN).pack(fill=tk.X, padx=10, pady=(10, 10))

    self._auto_update_output = True

  def show_about(self):
    """Display the About dialog as a modal window centred over the main window."""
    win = tk.Toplevel(self.root)
    win.title("About FSM to DOT File Generator")
    win.resizable(False, False)
    win.grab_set()  # modal

    text = tk.Text(win, wrap=tk.WORD, width=60, height=18, padx=10, pady=10,
                   relief=tk.FLAT)
    text.insert(tk.END, ABOUT_TEXT)
    text.config(state=tk.DISABLED)
    text.pack(padx=10, pady=(10, 0))

    tk.Button(win, text="OK", command=win.destroy, width=10).pack(pady=10)

    # Centre the dialog over the parent window
    win.update_idletasks()
    x = self.root.winfo_x() + (self.root.winfo_width()  - win.winfo_width())  // 2
    y = self.root.winfo_y() + (self.root.winfo_height() - win.winfo_height()) // 2
    win.geometry(f"+{x}+{y}")

  def _build_output_path(self):
    """Build an auto-suggested output ``.dot`` path from the input directory and FSM name.

    Returns:
        str: The suggested output path, or an empty string if either the
        input file path or FSM name is not yet set.
    """
    input_path = self.input_var.get()
    fsm_name = self.name_var.get()
    if input_path and fsm_name:
      input_dir = os.path.dirname(input_path)
      date = datetime.now().strftime("%Y%m%d")
      return os.path.join(input_dir, fsm_name + "_" + date + ".dot")
    return ""

  def _on_input_changed(self, *args):
    """Trace callback: when the input file path changes, auto-fill the FSM name.

    If the new path points to an existing file, the FSM name field is
    populated with the filename stem (i.e. the basename without extension).

    Args:
        *args: Positional arguments supplied by the Tkinter trace mechanism
            (name, index, mode); not used directly.
    """
    input_path = self.input_var.get()
    if input_path and os.path.isfile(input_path):
      stem = os.path.splitext(os.path.basename(input_path))[0]
      self.name_var.set(stem)

  def _on_name_changed(self, *args):
    """Trace callback: when the FSM name changes, update the auto-suggested output path.

    Only updates the output path while :attr:`_auto_update_output` is
    ``True``; auto-update is disabled once the user manually selects an
    output file via the Browse dialog.

    Args:
        *args: Positional arguments supplied by the Tkinter trace mechanism;
            not used directly.
    """
    if self._auto_update_output:
      self.output_var.set(self._build_output_path())

  def browse_input_file(self):
    """Open a file-chooser dialog to select the input JSON file.

    On confirmation, sets :attr:`input_var` to the chosen path, which in
    turn triggers :meth:`_on_input_changed` to auto-fill the FSM name.
    """
    filepath = filedialog.askopenfilename(
      title="Select Input JSON File",
      filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    if filepath:
      self.input_var.set(filepath)

  def browse_output_file(self):
    """Open a save-as dialog to choose the output ``.dot`` file path.

    Pre-populates the dialog with the current output path if one is already
    set. On confirmation, disables auto-update of the output path and sets
    :attr:`output_var` to the chosen path.
    """
    initial_dir = ""
    initial_file = ""
    current_output = self.output_var.get()
    if current_output:
      initial_dir = os.path.dirname(current_output)
      initial_file = os.path.basename(current_output)

    filepath = filedialog.asksaveasfilename(
      title="Save DOT File As",
      initialdir=initial_dir,
      initialfile=initial_file,
      defaultextension=".dot",
      filetypes=[("DOT files", "*.dot"), ("All files", "*.*")]
    )
    if filepath:
      self._auto_update_output = False
      self.output_var.set(filepath)

  def _on_output_dot_changed(self, *args):
    """Trace callback: when the ``.dot`` output path changes, update the PDF path.

    Sets :attr:`pdf_var` to the same path with the extension replaced by
    ``.pdf``, or clears it if the dot path is empty.

    Args:
        *args: Positional arguments supplied by the Tkinter trace mechanism;
            not used directly.
    """
    dot_path = self.output_var.get()
    if dot_path:
      self.pdf_var.set(os.path.splitext(dot_path)[0] + ".pdf")
    else:
      self.pdf_var.set("")

  def _on_pdf_changed(self, *args):
    """Trace callback: when the PDF path changes, rebuild the dot command string.

    Sets :attr:`dot_command_var` to the ready-to-run Graphviz command, or
    clears it if either path is empty.

    Args:
        *args: Positional arguments supplied by the Tkinter trace mechanism;
            not used directly.
    """
    dot_path = self.output_var.get()
    pdf_path = self.pdf_var.get()
    if dot_path and pdf_path:
      self.dot_command_var.set('dot -Tpdf "' + dot_path + '" -o "' + pdf_path + '"')
    else:
      self.dot_command_var.set("")

  def copy_dot_command(self):
    """Copy the current dot command string to the system clipboard."""
    cmd = self.dot_command_var.get()
    if cmd:
      self.root.clipboard_clear()
      self.root.clipboard_append(cmd)

  def generate(self):
    """Validate inputs and generate the ``.dot`` file.

    Reads the input file path, FSM name, output path, and optional notes
    from the GUI widgets. Performs basic field validation, then delegates
    to :class:`~NodeRed_FSM.NodeRed_FSM` to load, validate, and write the
    ``.dot`` file. Updates :attr:`status_var` with the outcome.

    On success, the status bar shows the output file path.
    On validation failure, a modal error dialog lists the validation errors
    and the status bar shows the error count.
    On any other exception, the status bar shows the exception message.
    """
    input_path = self.input_var.get().strip()
    fsm_name = self.name_var.get().strip()
    output_path = self.output_var.get().strip()

    if not input_path:
      self.status_var.set("Error: No input file specified.")
      return
    if not os.path.isfile(input_path):
      self.status_var.set("Error: Input file not found.")
      return
    if not fsm_name:
      self.status_var.set("Error: FSM name is empty.")
      return
    if not output_path:
      self.status_var.set("Error: No output file specified.")
      return

    user_notes = self.notes_text.get("1.0", tk.END).strip()

    try:
      fsm = NodeRed_FSM(fsm_name, input_path, output_path)
      fsm.load_FSM_Definition()
      errors = fsm.validate()
      if errors:
        error_text = "\n".join(errors)
        messagebox.showerror("Validation Failed", error_text)
        self.status_var.set("Validation failed: " + str(len(errors)) + " error(s)")
        return
      fsm.buildDotFile(user_notes)
      self.status_var.set("Success: " + output_path)
    except Exception as e:
      self.status_var.set("Error: " + str(e))
