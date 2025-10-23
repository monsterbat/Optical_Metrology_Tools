import tkinter as tk
from tkinter import Label, Button, StringVar, filedialog, messagebox
from tkinter import ttk
import os

class QuickReportWindow:
    def __init__(self, parent=None):
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Quick report")
        self.window.geometry("600x300")
        self.window.resizable(False, False)
        
        # Variables to store selected file paths
        self.data_file_path = StringVar(self.window)
        self.setting_file_path = StringVar(self.window)
        
        # Set default display text
        self.data_file_display = StringVar(self.window, value="No file selected")
        self.setting_file_display = StringVar(self.window, value="No file selected")
        
        self.setup_ui()
        
        # Center the window
        self.center_window()
    
    def setup_ui(self):
        """Set up UI elements"""
        # Main frame
        main_frame = tk.Frame(self.window, relief='raised', bd=2)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="Quick report", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(10, 20))
        
        # File selection area
        file_frame = tk.Frame(main_frame)
        file_frame.pack(pady=10)
        
        # Data File row
        data_row = tk.Frame(file_frame)
        data_row.pack(fill='x', pady=5)
        
        data_btn = tk.Button(
            data_row,
            text="1. Data File",
            width=15,
            font=("Arial", 11),
            command=self.select_data_file
        )
        data_btn.pack(side='left', padx=(0, 20))
        
        self.data_label = tk.Label(
            data_row,
            textvariable=self.data_file_display,
            font=("Arial", 11),
            anchor='w'
        )
        self.data_label.pack(side='left', fill='x', expand=True)
        
        # Setting File row
        setting_row = tk.Frame(file_frame)
        setting_row.pack(fill='x', pady=5)
        
        setting_btn = tk.Button(
            setting_row,
            text="2. Setting File",
            width=15,
            font=("Arial", 11),
            command=self.select_setting_file
        )
        setting_btn.pack(side='left', padx=(0, 20))
        
        self.setting_label = tk.Label(
            setting_row,
            textvariable=self.setting_file_display,
            font=("Arial", 11),
            anchor='w'
        )
        self.setting_label.pack(side='left', fill='x', expand=True)
        
        # Generate button
        generate_btn = tk.Button(
            main_frame,
            text="Generate",
            width=15,
            font=("Arial", 12),
            command=self.generate_report
        )
        generate_btn.pack(pady=(30, 10))
    
    def center_window(self):
        """Center window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def select_data_file(self):
        """Select data file"""
        file_path = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            print(f"Selected data file path: {file_path}")  # Debug info
            self.data_file_path.set(file_path)
            # Only display filename, not path
            filename = os.path.basename(file_path)
            print(f"Extracted filename: {filename}")  # Debug info
            self.data_file_display.set(filename)
            print(f"Display value after setting: {self.data_file_display.get()}")  # Debug info
            # Force UI update
            self.window.update_idletasks()
    
    def select_setting_file(self):
        """Select setting file"""
        file_path = filedialog.askopenfilename(
            title="Select Setting File",
            filetypes=[
                ("JSON files", "*.json"),
                ("XML files", "*.xml"),
                ("Config files", "*.cfg *.ini"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            print(f"Selected setting file path: {file_path}")  # Debug info
            self.setting_file_path.set(file_path)
            # Only display filename, not path
            filename = os.path.basename(file_path)
            print(f"Extracted filename: {filename}")  # Debug info
            self.setting_file_display.set(filename)
            print(f"Display value after setting: {self.setting_file_display.get()}")  # Debug info
            # Force UI update
            self.window.update_idletasks()
    
    def generate_report(self):
        """Generate report (currently placeholder function)"""
        data_file = self.data_file_path.get()
        setting_file = self.setting_file_path.get()
        
        if not data_file:
            messagebox.showwarning("Warning", "Please select data file")
            return
        
        if not setting_file:
            messagebox.showwarning("Warning", "Please select setting file")
            return
        
        # Currently displays selected file info, can be replaced with actual report generation logic later
        messagebox.showinfo(
            "File Information", 
            f"Data file: {data_file}\nSetting file: {setting_file}\n\nGenerate function under development..."
        )

def open_quick_report_window(parent=None):
    """Open Quick report window"""
    quick_report = QuickReportWindow(parent)
    return quick_report 