import os
import shutil
import subprocess

from pathlib import Path
from sys import exit
from threading import Thread

import tkinter as tk
import customtkinter as ctk

from tkinter import filedialog, messagebox, simpledialog
from CTkToolTip import CTkToolTip


BUILD_DIRECTORY = "build"
SPECIFICATION_EXTENSION = ".spec"

# Initialize CustomTkinter appearance (dark mode and theme accent)
ctk.set_appearance_mode("Dark")            # Dark mode for modern look
ctk.set_default_color_theme("blue")        # You can use "dark-blue" or others as needed


def no_operation(self, *args, **kwargs):    # Monkey-patch CTkToolTip so it satisfies the scaling tracker’s calls:

    """
        A no-op handler that matches the expected signature of:
          block_update_dimensions_event(self)
          unblock_update_dimensions_event(self)
    """
    return None

CTkToolTip.block_update_dimensions_event = no_operation
CTkToolTip.unblock_update_dimensions_event = no_operation

class PyInstallerGUI(ctk.CTk):
    def __init__(self):
        """
            Initialize the PyInstaller Builder GUI application.
        """
        super().__init__()
        self.configure(fg_color="#1E1E1E")  # Forces the root window to a near-black
        self.title("Universal PyInstaller Builder")
        self.geometry("900x900")

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Variables for settings
        self.entry_point = tk.StringVar()
        self.executable_name = tk.StringVar()
        self.hidden_imports = tk.StringVar()
        self.icon = tk.StringVar()
        self.output_directory = tk.StringVar(value="dist")
        self.onefile = tk.BooleanVar(value=True)
        self.data_files = []  # List of data file specifications

        self.entry_point_entry = None
        self.executable_name_entry = None
        self.data_listbox = None
        self.hidden_imports_entry = None
        self.icon_entry = None
        self.output_directory_entry = None
        self.onefile_check = None
        self.build_button = None
        self.log_text = None

        # Create GUI components
        self.create_widgets()

    def create_widgets(self):
        """
            Create and layout all the GUI widgets.
        """
        # Main container frame
        main_frame = ctk.CTkFrame(self, fg_color="transparent")  # transparent uses window default dark bg
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_frame.grid_rowconfigure(15, weight=1)  # make the log section expandable (row index 15 below)
        main_frame.grid_columnconfigure(0, weight=1)  # make content stretch horizontally

        # Define fonts for section headers and field labels (for modern, readable text)
        section_font = ("Segoe UI", 16, "bold")
        label_font = ("Segoe UI", 14, "bold")

        # Entry Point section
        ctk.CTkLabel(main_frame, text="Entry Point", font=section_font).grid(row=0, column=0, sticky="w", pady=(5, 0))
        self.place_help(main_frame, row=0, column=1, text="Select the main .py file where your program starts.")
        entry_frame = ctk.CTkFrame(main_frame)
        entry_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        entry_frame.grid_columnconfigure(1, weight=1)  # Make the entry field expand in this frame
        ctk.CTkLabel(entry_frame, text="Main Python File:", font=label_font).grid(row=0, column=0, sticky="w")
        self.entry_point_entry = ctk.CTkEntry(entry_frame, textvariable=self.entry_point)
        self.entry_point_entry.grid(row=0, column=1, sticky="ew", padx=5)
        ctk.CTkButton(entry_frame, text="Browse", command=self.browse_entry_point).grid(row=0, column=2, padx=5)

        # Executable Name Section
        ctk.CTkLabel(main_frame, text="Executable Name", font=section_font).grid(row=2, column=0, sticky="w", pady=(5, 0))
        self.place_help(main_frame, row=2, column=1, text="Specifies the name of the generated .exe.")
        exe_frame = ctk.CTkFrame(main_frame)
        exe_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        exe_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(exe_frame, text="Name:", font=label_font).grid(row=0, column=0, sticky="w")
        self.executable_name_entry = ctk.CTkEntry(exe_frame, textvariable=self.executable_name)
        self.executable_name_entry.grid(row=0, column=1, sticky="ew", padx=5)

        # Additional Data Files section
        ctk.CTkLabel(main_frame, text="Additional Data Files",
                     font=section_font).grid(row=4, column=0, sticky="w", pady=(5, 0))
        self.place_help(main_frame, row=4, column=1, text="Include extra files/folders.")
        data_frame = ctk.CTkFrame(main_frame)
        data_frame.grid(row=5, column=0, sticky="ew", padx=5, pady=5)
        data_frame.grid_columnconfigure((0, 1, 2), weight=1)  # Distribute extra space across three columns
        # Listbox for data files – using a standard tkinter Listbox, but styled to match dark theme
        self.data_listbox = tk.Listbox(data_frame, height=5, selectmode=tk.SINGLE)
        self.data_listbox.configure(background="#2B2B2B", foreground="white",
                                    selectbackground="#3A9FBF", highlightthickness=0)
        self.data_listbox.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        # Buttons for adding/removing data files
        ctk.CTkButton(data_frame, text="Add File", command=self.add_data_file).grid(row=1, column=0, padx=5, pady=5)
        ctk.CTkButton(data_frame, text="Add Folder", command=self.add_data_folder).grid(row=1, column=1, padx=5, pady=5)
        ctk.CTkButton(data_frame, text="Remove Selected",
                      command=self.remove_data_file).grid(row=1, column=2, padx=5, pady=5)

        # Hidden Imports Section
        ctk.CTkLabel(main_frame, text="Hidden Imports (comma-separated)",
                     font=section_font).grid(row=6, column=0, sticky="w", pady=(5, 0))
        self.place_help(main_frame, row=6, column=1, text = "Specify modules not auto-detected.")
        hidden_frame = ctk.CTkFrame(main_frame)
        hidden_frame.grid(row=7, column=0, sticky="ew", padx=5, pady=5)
        hidden_frame.grid_columnconfigure(0, weight=1)
        self.hidden_imports_entry = ctk.CTkEntry(hidden_frame, textvariable=self.hidden_imports)
        self.hidden_imports_entry.grid(row=0, column=0, sticky="ew", padx=5)

        # Icon Selection Section
        ctk.CTkLabel(main_frame, text="Icon", font=section_font).grid(row=8, column=0, sticky="w", pady=(5, 0))
        self.place_help(main_frame, row=8, column=1, text = "Path to a .ico file to embed in your executable.")
        icon_frame = ctk.CTkFrame(main_frame)
        icon_frame.grid(row=9, column=0, sticky="ew", padx=5, pady=5)
        icon_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(icon_frame, text="Icon File:", font=label_font).grid(row=0, column=0, sticky="w")
        self.icon_entry = ctk.CTkEntry(icon_frame, textvariable=self.icon)
        self.icon_entry.grid(row=0, column=1, sticky="ew", padx=5)
        ctk.CTkButton(icon_frame, text="Browse", command=self.browse_icon).grid(row=0, column=2, padx=5)

        # Output Directory Section
        ctk.CTkLabel(main_frame, text="Output Directory",
                     font=section_font).grid(row=10, column=0, sticky="w", pady=(5, 0))
        self.place_help(main_frame, row=10, column=1, text = "Destination folder for build output.")
        out_frame = ctk.CTkFrame(main_frame)
        out_frame.grid(row=11, column=0, sticky="ew", padx=5, pady=5)
        out_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(out_frame, text="Directory:", font=label_font).grid(row=0, column=0, sticky="w")
        self.output_directory_entry = ctk.CTkEntry(out_frame, textvariable=self.output_directory)
        self.output_directory_entry.grid(row=0, column=1, sticky="ew", padx=5)
        ctk.CTkButton(out_frame, text="Browse", command=self.browse_output_directory).grid(row=0, column=2, padx=5)

        # Options Section (One-file toggle)
        self.onefile_check = ctk.CTkCheckBox(main_frame, text="Build one-file executable", variable=self.onefile)
        self.onefile_check.grid(row=12, column=0, sticky="w", padx=5, pady=5)
        self.place_help(main_frame, row=12, column=1, text = "Choose single-file or folder build.")

        # Build Button
        self.build_button = ctk.CTkButton(main_frame, text="Build Executable", command=self.build_executable)
        self.build_button.grid(row=13, column=0, pady=10)
        self.place_help(main_frame, row=14, column=1, text = "Displays real-time output from PyInstaller during build.")

        # Build Log Output
        ctk.CTkLabel(main_frame, text="Build Log", font=section_font).grid(row=14, column=0, sticky="w", pady=(5, 0))
        # Text box for log output. CTkTextbox provides a scrollbar automatically in customtkinter >=5
        self.log_text = ctk.CTkTextbox(main_frame, height=180)
        self.log_text.grid(row=15, column=0, sticky="nsew", padx=5, pady=5)
        self.log_text.configure(state="disabled")  # Start as read-only

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

    def _append_log_async(self, text: str):
        """
            Schedule a log append on the GUI thread.
        """
        self.after_idle(self.append_log, text)

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
        if not self.entry_point.get():
            messagebox.showerror("Error", "Please select an entry point file.")
            return None
        command = ["pyinstaller", self.entry_point.get(),
                   "--onefile" if self.onefile.get() else "--onedir", "--noconsole"]

        executable_name = self.executable_name.get().strip()
        if executable_name:
            command.extend(["--name", executable_name])

        for data in self.data_files:
            command.extend(["--add-data", data])
        for hidden_import in filter(None, map(str.strip, self.hidden_imports.get().split(","))):
            command.extend(["--hidden-import", hidden_import])

        icon = self.icon.get()
        if icon:
            command.extend(["--icon", icon])

        command.extend(["--distpath", self.output_directory.get()])
        return command

    def _run_build(self):
        """
            Runs in a background thread—executes PyInstaller and updates the log.
        """
        command = self.assemble_commands()
        if not command:
            # Re-enable the button if assemble failed
            self.after_idle(self.build_button.configure, {"state": "normal"})
            return

        # Clean artifacts before build
        self.cleanup_build_artifacts()

        # Log the command asynchronously
        self._append_log_async("Running command:\n" + " ".join(command) + "\n\n")

        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            for line in process.stdout: # Send each line back to the GUI thread
                self._append_log_async(line)

            code = process.wait()
            if code == 0:
                self._append_log_async("\nExecutable built successfully.\n")
            else:
                self._append_log_async("\nBuild failed. Check the log above for details.\n")

        except Exception as e:
            self._append_log_async(f"\nBuild failed: {e}\n")
            self.after_idle(messagebox.showerror, "Build Error", str(e))
        finally:
            self.cleanup_build_artifacts()  # Clean up artifacts after build
            self.after_idle(self.build_button.configure, {"state": "normal"})  # Re-enable the build button

    def build_executable(self):
        """
            Build the executable using PyInstaller with the selected options.
        """
        if not self.entry_point:
            messagebox.showerror("Error", "Please select an entry point file.")
            return

        # Disable the build button so user can't start multiple builds
        self.build_button.configure(state="disabled")

        # Start background thread
        thread = Thread(target=self._run_build, daemon=True)
        thread.start()

    @staticmethod
    def place_help(parent, row, column, text):
        """
            Place a small "?" button at (row, col) that shows "text" when clicked.
        """
        # Create a CTkButton with equal width/height and corner_radius to make it a circle
        size = 24
        button = ctk.CTkButton(parent, text="❓", width=size, height=size, corner_radius=size // 2, fg_color="#3A3A3A",
            hover_color="#4A4A4A", text_color="white", font=("", 10, "bold"), border_width=0,
            command=lambda: None)
        button.grid(row=row, column=column, sticky="n", padx=(2, 10))

        # Attach a tooltip that appears on hover
        CTkToolTip(widget=button, message=text, delay=0.3, follow=True,  x_offset=10, y_offset=10, alpha=0.9,
                   bg_color="#2B2B2B", text_color="white", corner_radius=6, border_width=0,  border_color="#4A4A4A",
                   wraplength=200, padding=(8, 4), font=("Segoe UI", 15),justify="left",)

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
