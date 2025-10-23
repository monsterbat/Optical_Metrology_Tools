import tkinter as tk
from tkinter import StringVar
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.io.file_operations import ask_and_open_file, open_analysis_item, on_extract
from src.ui.jmp_ui import create_main_window, create_header_ui, create_open_data_ui, create_data_process_ui, create_process_capability_ui, create_analysis_tools_ui, create_app_info_ui, create_quick_analysis_ui, create_process_capability_python_only_ui

def main():
    # Initialize the main window
    root = create_main_window()

    # Create header UI with description and instruction link
    create_header_ui(root)

    # Create Open Data UI at the top
    create_open_data_ui(root)
    
    # Future work : Create Quick analysis UI at the top
    # create_quick_analysis_ui(root)

    """Create_data_process_ui"""
    create_data_process_ui(root)  
    
    # Create the Process Capability UI
    create_process_capability_ui(root, open_analysis_item)
    
    # Create the Process Capability Python Only UI (NEW)
    create_process_capability_python_only_ui(root)
    
    # Create the Analysis Tools UI
    create_analysis_tools_ui(root)
    
    # Create the application info UI at the bottom
    create_app_info_ui(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()