import customtkinter as ctk

from pathlib import Path
from shutil import rmtree

from tkinter import Misc
from CTkToolTip import CTkToolTip


BUILD_DIRECTORY = "build"
SPECIFICATION_EXTENSION = ".spec"

def no_operation(self, *args, **kwargs):    # Monkey-patch CTkToolTip so it satisfies the scaling tracker’s calls:

    """
        A no-op handler that matches the expected signature of:
          block_update_dimensions_event(self)
          unblock_update_dimensions_event(self)
    """
    return None

CTkToolTip.block_update_dimensions_event = no_operation
CTkToolTip.unblock_update_dimensions_event = no_operation
