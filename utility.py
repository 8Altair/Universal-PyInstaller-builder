import customtkinter as ctk

from pathlib import Path
from shutil import rmtree

from tkinter import Misc
from CTkToolTip import CTkToolTip


BUILD_DIRECTORY = "build"
SPECIFICATION_EXTENSION = ".spec"

def place_help(parent: Misc, row: int, column: int, text: str) -> None:
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

def cleanup_build_artifacts():
    """
        Clean previous PyInstaller build artifacts.
    """
    if Path(BUILD_DIRECTORY).is_dir():
        rmtree(BUILD_DIRECTORY)
    for specification in Path(".").glob(f"*{SPECIFICATION_EXTENSION}"):
        specification.unlink()

def no_operation(self, *args, **kwargs):    # Monkey-patch CTkToolTip so it satisfies the scaling tracker’s calls:

    """
        A no-op handler that matches the expected signature of:
          block_update_dimensions_event(self)
          unblock_update_dimensions_event(self)
    """
    return None


CTkToolTip.block_update_dimensions_event = no_operation
CTkToolTip.unblock_update_dimensions_event = no_operation
