#!/usr/bin/env python3
"""
Data Analysis Tools - JMP Version
專門處理 JMP 相關功能的主程式
不包含 Process Capability Python Only
"""

import tkinter as tk
from tkinter import StringVar
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.io.file_operations import ask_and_open_file, open_analysis_item, on_extract
from src.ui.jmp_ui import (
    create_main_window, 
    create_header_ui, 
    create_open_data_ui, 
    create_data_process_ui, 
    create_process_capability_ui, 
    create_analysis_tools_ui, 
    create_app_info_ui
)

def main():
    """JMP 版本主程式 - 只包含 JMP 相關功能"""
    # Initialize the main window
    root = create_main_window()
    
    # Modify window title to indicate JMP version
    root.title("Data Analysis Tools v1.3 - JMP Edition")

    # Create header UI with description and instruction link
    create_header_ui(root)

    # Create Open Data UI at the top
    create_open_data_ui(root)

    # Create data process UI
    create_data_process_ui(root)  
    
    # Create the Process Capability UI (JMP related)
    create_process_capability_ui(root, open_analysis_item)
    
    # ========================================
    # Process Capability Python Only 已移除
    # 請使用 main_python.py 來啟動 Python Only 版本
    # ========================================
    
    # Create the Analysis Tools UI
    create_analysis_tools_ui(root)
    
    # Create the application info UI at the bottom
    create_app_info_ui(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()


