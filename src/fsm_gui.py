import os
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
from NodeRed_FSM import NodeRed_FSM

VERSION = "v1.0"

class FSMGeneratorGUI:
  def __init__(self, root):
    self.root = root
    self.root.title("FSM to DOT File Generator")
    self.root.resizable(False, False)

    # Title bar
    title_frame = tk.Frame(root)
    title_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
    tk.Label(title_frame, text="FSM to DOT File Generator", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT)
    tk.Label(title_frame, text=VERSION, font=("Helvetica", 10)).pack(side=tk.RIGHT)

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
    tk.Entry(output_frame, textvariable=self.output_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
    tk.Button(output_frame, text="Browse...", command=self.browse_output_file).pack(side=tk.RIGHT, padx=(5, 0))

    # Generate button
    tk.Button(root, text="Generate", command=self.generate, width=15).pack(pady=15)

    # Status label
    self.status_var = tk.StringVar(value="Ready")
    tk.Label(root, textvariable=self.status_var, anchor=tk.W, relief=tk.SUNKEN).pack(fill=tk.X, padx=10, pady=(0, 10))

    self._auto_update_output = True

  def _build_output_path(self):
    """Build auto-suggested output path from input dir and FSM name."""
    input_path = self.input_var.get()
    fsm_name = self.name_var.get()
    if input_path and fsm_name:
      input_dir = os.path.dirname(input_path)
      date = datetime.now().strftime("%Y%m%d")
      return os.path.join(input_dir, fsm_name + "_" + date + ".dot")
    return ""

  def _on_input_changed(self, *args):
    """When input file changes, auto-fill FSM name from filename stem."""
    input_path = self.input_var.get()
    if input_path and os.path.isfile(input_path):
      stem = os.path.splitext(os.path.basename(input_path))[0]
      self.name_var.set(stem)

  def _on_name_changed(self, *args):
    """When FSM name changes, update the auto-suggested output path."""
    if self._auto_update_output:
      self.output_var.set(self._build_output_path())

  def browse_input_file(self):
    filepath = filedialog.askopenfilename(
      title="Select Input JSON File",
      filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    if filepath:
      self.input_var.set(filepath)

  def browse_output_file(self):
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

  def generate(self):
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

    try:
      fsm = NodeRed_FSM(fsm_name, input_path, output_path)
      fsm.load_FSM_Definition()
      errors = fsm.validate()
      if errors:
        error_text = "\n".join(errors)
        messagebox.showerror("Validation Failed", error_text)
        self.status_var.set("Validation failed: " + str(len(errors)) + " error(s)")
        return
      fsm.buildDotFile()
      self.status_var.set("Success: " + output_path)
    except Exception as e:
      self.status_var.set("Error: " + str(e))
