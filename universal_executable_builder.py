import os
import shutil
import subprocess

from pathlib import Path
from sys import exit

import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, simpledialog, scrolledtext, ttk

BUILD_DIRECTORY = "build"
SPECIFICATION_EXTENSION = ".spec"


class PyInstallerGUI(tk.Tk):
    def __init__(self):
        """
            Initialize the PyInstaller Builder GUI application.
        """
        super().__init__()
        self.title("Universal PyInstaller Builder")
        self.geometry("900x900")

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Increase all default fonts by 5
        for fname in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
            f = tkfont.nametofont(fname)
            f.configure(size=f.cget("size") + 5, weight="bold")

        # Variables for settings
        self.entry_point = tk.StringVar()
        self.executable_name = tk.StringVar()
        self.hidden_imports = tk.StringVar()
        self.icon = tk.StringVar()
        self.output_directory = tk.StringVar(value="dist")
        self.onefile = tk.BooleanVar(value=True)
        self.data_files = []  # List of data file specifications

        self.entry_point_entry = None
        self.data_listbox = None
        self.hidden_imports_entry = None
        self.icon_entry = None
        self.output_directory_entry = None
        self.log_text = None

        # Create GUI components
        self.create_widgets()

    def create_widgets(self):
        """
            Create and layout all the GUI widgets.
        """
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Entry Point section
        entry_frame = ttk.LabelFrame(main_frame, text="Entry Point")
        entry_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        ttk.Label(entry_frame, text="Main Python File:").grid(row=0, column=0, sticky="w")
        self.entry_point_entry = ttk.Entry(entry_frame, textvariable=self.entry_point, width=50)
        self.entry_point_entry.grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(entry_frame, text="Browse", command=self.browse_entry_point, cursor="hand1").grid(row=0, column=2, padx=5)
        entry_frame.columnconfigure(1, weight=1)

        # Executable Name Section
        executable_frame = ttk.LabelFrame(main_frame, text="Executable Name")
        executable_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        ttk.Label(executable_frame, text="Name:").grid(row=0, column=0, sticky="w")
        ex = ttk.Entry(executable_frame, textvariable=self.executable_name, width=50)
        ex.grid(row=0, column=1, sticky="ew", padx=5)
        executable_frame.columnconfigure(1, weight=1)

        # Additional Data Files section
        data_frame = ttk.LabelFrame(main_frame, text="Additional Data Files")
        data_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.data_listbox = tk.Listbox(data_frame, height=5)
        self.data_listbox.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        ttk.Button(data_frame, text="Add File", command=self.add_data_file, cursor="hand1").grid(row=1, column=0, padx=100, pady=5)
        ttk.Button(data_frame, text="Add Folder", command=self.add_data_folder, cursor="hand1").grid(row=1, column=1, padx=70, pady=5)
        ttk.Button(data_frame, text="Remove Selected", command=self.remove_data_file, cursor="hand1").grid(row=1, column=2, padx=5, pady=5)
        data_frame.columnconfigure(0, weight=1)

        # Hidden Imports Section
        hidden_frame = ttk.LabelFrame(main_frame, text="Hidden Imports (comma-separated)")
        hidden_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        self.hidden_imports_entry = ttk.Entry(hidden_frame, textvariable=self.hidden_imports, width=50)
        self.hidden_imports_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        hidden_frame.columnconfigure(0, weight=1)

        # Icon Selection Section
        icon_frame = ttk.LabelFrame(main_frame, text="Icon")
        icon_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        ttk.Label(icon_frame, text="Icon File:").grid(row=0, column=0, sticky="w")
        self.icon_entry = ttk.Entry(icon_frame, textvariable=self.icon, width=50)
        self.icon_entry.grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(icon_frame, text="Browse", command=self.browse_icon, cursor="hand1").grid(row=0, column=2, padx=5)
        icon_frame.columnconfigure(1, weight=1)

        # Output Directory Section
        output_frame = ttk.LabelFrame(main_frame, text="Output Directory")
        output_frame.grid(row=5, column=0, sticky="ew", padx=5, pady=5)
        ttk.Label(output_frame, text="Directory:").grid(row=0, column=0, sticky="w")
        self.output_directory_entry = ttk.Entry(output_frame, textvariable=self.output_directory, width=50)
        self.output_directory_entry.grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(output_frame, text="Browse", command=self.browse_output_directory, cursor="hand1").grid(row=0, column=2, padx=5)
        output_frame.columnconfigure(1, weight=1)

        # Options Section (One-file toggle)
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=6, column=0, sticky="w", padx=5, pady=5)
        ttk.Checkbutton(options_frame, text="Build one-file executable", variable=self.onefile, cursor="hand2").pack(side=tk.LEFT)

        # Build Button
        build_button = ttk.Button(main_frame, text="Build Executable", command=self.build_executable, cursor="hand1")
        build_button.grid(row=7, column=0, pady=10)

        # Build Log Output
        log_frame = ttk.LabelFrame(main_frame, text="Build Log")
        log_frame.grid(row=8, column=0, sticky="nsew", padx=5, pady=5)
        log_text = scrolledtext.ScrolledText(log_frame, height=10, bd=0, highlightthickness=0)
        log_text.pack(fill=tk.BOTH, expand=True)
        log_text.configure(state=tk.DISABLED)
        main_frame.rowconfigure(8, weight=1)
        self.log_text = log_text

    def browse_entry_point(self):
        """
            Browse and select the main Python entry point file.
        """
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            self.entry_point.set(file_path)

    def add_data_file(self):

        """
            Add a data file to include in the build.
        """
        file_path = filedialog.askopenfilename()
        if file_path:
            destination = simpledialog.askstring("Destination",
                                                 f"Enter destination folder for {os.path.basename(file_path)} (relative to executable):",
                                                 initialvalue=".")
            if destination is None:
                destination = "."
            specification = f"{file_path};{destination}"
            self.data_files.append(specification)
            self.data_listbox.insert(tk.END, specification)

    def add_data_folder(self):
        """
            Add a data folder to include in the build.
        """
        folder_path = filedialog.askdirectory()
        if folder_path:
            destination = simpledialog.askstring("Destination",
                                                 f"Enter destination folder for {os.path.basename(folder_path)} (relative to executable):",
                                                 initialvalue=os.path.basename(folder_path))
            if destination is None:
                destination = os.path.basename(folder_path)

            specification = f"{folder_path}{os.sep};{destination}"  # Appending os.sep to indicate folder
            self.data_files.append(specification)
            self.data_listbox.insert(tk.END, specification)

    def remove_data_file(self):
        """
            Remove the selected data file or folder from the list.
        """
        selected = self.data_listbox.curselection()
        if selected:
            index = selected[0]
            self.data_listbox.delete(index)
            del self.data_files[index]

    def browse_icon(self):
        """
            Browse and select an icon file.
        """
        file_path = filedialog.askopenfilename(filetypes=[("Icon Files", "*.ico"), ("All Files", "*.*")])
        if file_path:
            self.icon.set(file_path)

    def browse_output_directory(self):
        """
            Browse and select an output directory.
        """
        directory = filedialog.askdirectory()
        if directory:
            self.output_directory.set(directory)

    def append_log(self, text):
        """
            Insert into the read-only log.
        """
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self.update_idletasks()

    @staticmethod
    def cleanup_build_artifacts():
        """
            Clean previous PyInstaller build artifacts.
        """
        if Path(BUILD_DIRECTORY).is_dir():
            shutil.rmtree(BUILD_DIRECTORY)
        for specification in Path(".").glob(f"*{SPECIFICATION_EXTENSION}"):
            specification.unlink()

    def assemble_commands(self):
        command = ["pyinstaller", self.entry_point, "--onefile" if self.onefile.get() else "--onedir"]
        for data in self.data_files:
            command.extend(["--add-data", data])
        for hidden_import in filter(None, map(str.strip, self.hidden_imports.get().split(","))):
            command.extend(["--hidden-import", hidden_import])

        icon = self.icon.get()
        if icon:
            command.extend(["--icon", icon])

        command.extend(["--distpath", self.output_directory.get()])
        return command

    def build_executable(self):
        """
            Build the executable using PyInstaller with the selected options.
        """
        if not self.entry_point:
            messagebox.showerror("Error", "Please select an entry point file.")
            return

        command = self.assemble_commands()
        self.cleanup_build_artifacts()

        self.log_text.insert(tk.END, "Running command:\n" + " ".join(command) + "\n\n")
        self.log_text.see(tk.END)
        self.update_idletasks()

        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            for line in process.stdout:
                self.log_text.insert(tk.END, line)
                self.log_text.see(tk.END)
                self.update_idletasks()

            return_code = process.wait()
            if return_code == 0:
                self.log_text.insert(tk.END, "\nExecutable built successfully.")
            else:
                self.log_text.insert(tk.END, "\nBuild failed. Check the log above for details.")

        except (OSError, subprocess.SubprocessError) as e:
            self.log_text.insert(tk.END, f"\nBuild failed: {e}")
            messagebox.showerror("Build Error", str(e))

    def on_close(self):
        """
            Called when a window is closed—quits, destroys, and exits.
        """
        self.quit()
        self.destroy()
        exit(0)


if __name__ == "__main__":
    app = PyInstallerGUI()
    app.mainloop()
