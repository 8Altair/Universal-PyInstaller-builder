import os
import sys
import shutil
import subprocess

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, scrolledtext, ttk


class PyInstallerGUI(tk.Tk):
    def __init__(self):
        """
            Initialize the PyInstaller Builder GUI application.
        """
        super().__init__()
        self.title("Universal PyInstaller Builder")
        self.geometry("800x600")

        # Variables for settings
        self.entry_point_var = tk.StringVar()
        self.hidden_imports_var = tk.StringVar()
        self.icon_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value="dist")
        self.onefile_var = tk.BooleanVar(value=True)
        self.data_files = []  # List of data file specifications

        # Create GUI components
        self.create_widgets()

    def create_widgets(self):
        """
            Create and layout all the GUI widgets.
        """
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Entry Point Section
        entry_frame = ttk.LabelFrame(main_frame, text="Entry Point")
        entry_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        ttk.Label(entry_frame, text="Main Python File:").grid(row=0, column=0, sticky="w")
        self.entry_point_entry = ttk.Entry(entry_frame, textvariable=self.entry_point_var, width=50)
        self.entry_point_entry.grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(entry_frame, text="Browse", command=self.browse_entry_point).grid(row=0, column=2, padx=5)
        entry_frame.columnconfigure(1, weight=1)

        # Additional Data Files Section
        data_frame = ttk.LabelFrame(main_frame, text="Additional Data Files")
        data_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.data_listbox = tk.Listbox(data_frame, height=5)
        self.data_listbox.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        ttk.Button(data_frame, text="Add File", command=self.add_data_file).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(data_frame, text="Add Folder", command=self.add_data_folder).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(data_frame, text="Remove Selected", command=self.remove_data_file).grid(row=1, column=2, padx=5,
                                                                                           pady=5)
        data_frame.columnconfigure(0, weight=1)

        # Hidden Imports Section
        hidden_frame = ttk.LabelFrame(main_frame, text="Hidden Imports (comma-separated)")
        hidden_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.hidden_imports_entry = ttk.Entry(hidden_frame, textvariable=self.hidden_imports_var, width=50)
        self.hidden_imports_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        hidden_frame.columnconfigure(0, weight=1)

        # Icon Selection Section
        icon_frame = ttk.LabelFrame(main_frame, text="Icon")
        icon_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        ttk.Label(icon_frame, text="Icon File:").grid(row=0, column=0, sticky="w")
        self.icon_entry = ttk.Entry(icon_frame, textvariable=self.icon_var, width=50)
        self.icon_entry.grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(icon_frame, text="Browse", command=self.browse_icon).grid(row=0, column=2, padx=5)
        icon_frame.columnconfigure(1, weight=1)

        # Output Directory Section
        output_frame = ttk.LabelFrame(main_frame, text="Output Directory")
        output_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        ttk.Label(output_frame, text="Directory:").grid(row=0, column=0, sticky="w")
        self.output_dir_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, width=50)
        self.output_dir_entry.grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(output_frame, text="Browse", command=self.browse_output_dir).grid(row=0, column=2, padx=5)
        output_frame.columnconfigure(1, weight=1)

        # Options Section (One-file toggle)
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=5, column=0, sticky="w", padx=5, pady=5)
        ttk.Checkbutton(options_frame, text="Build one-file executable", variable=self.onefile_var).pack(side=tk.LEFT)

        # Build Button
        build_button = ttk.Button(main_frame, text="Build Executable", command=self.build_executable)
        build_button.grid(row=6, column=0, pady=10)

        # Build Log Output
        log_frame = ttk.LabelFrame(main_frame, text="Build Log")
        log_frame.grid(row=7, column=0, sticky="nsew", padx=5, pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        main_frame.rowconfigure(7, weight=1)

    def browse_entry_point(self):
        """
            Browse and select the main Python entry point file.
        """
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            self.entry_point_var.set(file_path)

    def add_data_file(self):
        """
            Add a data file to include in the build.
        """
        file_path = filedialog.askopenfilename()
        if file_path:
            dest = simpledialog.askstring("Destination",
                                          f"Enter destination folder for {os.path.basename(file_path)} (relative to executable):",
                                          initialvalue=".")
            if dest is None:
                dest = "."
            spec = f"{file_path};{dest}"
            self.data_files.append(spec)
            self.data_listbox.insert(tk.END, spec)

    def add_data_folder(self):
        """
            Add a data folder to include in the build.
        """
        folder_path = filedialog.askdirectory()
        if folder_path:
            dest = simpledialog.askstring("Destination",
                                          f"Enter destination folder for {os.path.basename(folder_path)} (relative to executable):",
                                          initialvalue=os.path.basename(folder_path))
            if dest is None:
                dest = os.path.basename(folder_path)
            # Note: appending os.sep to indicate folder
            spec = f"{folder_path}{os.sep};{dest}"
            self.data_files.append(spec)
            self.data_listbox.insert(tk.END, spec)

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
            self.icon_var.set(file_path)

    def browse_output_dir(self):
        """
            Browse and select an output directory.
        """
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_var.set(directory)

    @staticmethod
    def cleanup_build_artifacts():
        """
            Clean previous PyInstaller build artifacts.
        """
        if os.path.isdir("build"):
            shutil.rmtree("build")
        for f in os.listdir("."):
            if f.endswith(".spec"):
                os.remove(f)

    def build_executable(self):
        """
            Build the executable using PyInstaller with the selected options.
        """
        entry_point = self.entry_point_var.get()
        if not entry_point:
            messagebox.showerror("Error", "Please select an entry point file.")
            return

        # Build the PyInstaller command
        cmd = ["pyinstaller", entry_point, "--onefile" if self.onefile_var.get() else "--onedir"]
        for data in self.data_files:
            cmd.extend(["--add-data", data])
        hidden_imports = [imp.strip() for imp in self.hidden_imports_var.get().split(",") if imp.strip()]
        for imp in hidden_imports:
            cmd.extend(["--hidden-import", imp])
        icon = self.icon_var.get()
        if icon:
            cmd.extend(["--icon", icon])
        output_dir = self.output_dir_var.get()
        cmd.extend(["--distpath", output_dir])

        self.cleanup_build_artifacts()

        self.log_text.insert(tk.END, "Running command:\n" + " ".join(cmd) + "\n\n")
        self.log_text.see(tk.END)
        self.update_idletasks()

        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    universal_newlines=True)
            for line in proc.stdout:
                self.log_text.insert(tk.END, line)
                self.log_text.see(tk.END)
                self.update_idletasks()
            proc.wait()
            if proc.returncode == 0:
                self.log_text.insert(tk.END, "\nExecutable built successfully!")
            else:
                self.log_text.insert(tk.END, "\nBuild failed. Check the log above for details.")
        except Exception as e:
            self.log_text.insert(tk.END, f"\nError: {e}")
            messagebox.showerror("Build Error", str(e))


if __name__ == "__main__":
    app = PyInstallerGUI()
    app.mainloop()
