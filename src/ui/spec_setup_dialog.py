import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import re
import struct
from datetime import datetime
from src.utils.paths import resource_path

def open_spec_setup():
    """Open Spec Setup function"""
    try:
        # Select limits file
        file_path = select_limits_file()
        if file_path:
            # Read file
            limits_data = read_limits_file(file_path)
            if limits_data is not None:
                # Generate JSL code
                generate_jsl_file(limits_data, file_path)
            else:
                messagebox.showerror("Error", "Unable to read Limits file")
        else:
            print("User cancelled file selection")
            
    except Exception as e:
        messagebox.showerror("Error", f"Spec Setup execution failed: {str(e)}")
        print(f"❌ Error: {str(e)}")

def select_limits_file():
    """Select Limits file"""
    # Create file selection dialog
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    try:
        # Open file selection dialog (simplified version to avoid macOS compatibility issues)
        file_path = filedialog.askopenfilename(
            title="Select Limits file (supports .csv, .xlsx, .xls)",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx"),
                ("Excel 97-2003", "*.xls"),
                ("All files", "*.*")
            ],
            initialdir=os.getcwd()
        )
        
        root.destroy()  # Close tkinter window
        
        return file_path if file_path else None
        
    except Exception as e:
        root.destroy()  # Ensure window is closed
        print(f"❌ File selection dialog error: {str(e)}")
        return None

def read_limits_file(file_path):
    """Read Limits file"""
    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.csv':
            # Read CSV file
            df = pd.read_csv(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            # Read Excel file
            df = pd.read_excel(file_path)
        elif file_ext == '.jmp':
            # JMP files are binary format, need special handling
            try:
                # Try different encoding methods
                encodings = ['latin-1', 'cp1252', 'iso-8859-1', 'utf-16', 'utf-32']
                df = None
                
                for encoding in encodings:
                    try:
                        print(f"🔍 Trying to read JMP file with {encoding} encoding...")
                        temp_df = pd.read_csv(file_path, sep='\t', encoding=encoding)
                        
                        # Check if the read data is valid
                        if temp_df.empty or not any(col in temp_df.columns for col in ['Variable', 'LSL', 'USL', 'Target', 'Show Limits']):
                            print(f"❌ Data format read with {encoding} encoding is incorrect")
                            continue
                        
                        df = temp_df
                        print(f"✅ Successfully read with {encoding} encoding")
                        break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        print(f"❌ {encoding} encoding failed: {str(e)}")
                        continue
                
                if df is None:
                    raise ValueError("Unable to read JMP file format. JMP files are binary format, recommend exporting data as CSV or Excel format.")
                    
            except Exception as e:
                raise ValueError(f"Unable to read JMP file: {str(e)}. Recommend exporting JMP file as CSV or Excel format.")
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        # Check required columns
        required_columns = ['Variable', 'LSL', 'USL', 'Target', 'Show Limits']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"⚠️  Missing columns: {missing_columns}")
            print(f"Available columns: {list(df.columns)}")
        
        # Keep only the columns we need (if they exist)
        available_columns = [col for col in required_columns if col in df.columns]
        if available_columns:
            df = df[available_columns]
        
        return df
        
    except Exception as e:
        print(f"❌ File reading failed: {str(e)}")
        return None

def generate_jsl_file(limits_data, source_file_path=None):
    """Generate JSL code and save to file"""
    
    jsl_lines = []
    success_count = 0
    fail_count = 0
    
    for index, row in limits_data.iterrows():
        variable = row.get('Variable', 'Unknown')
        lsl = row.get('LSL', '')
        usl = row.get('USL', '')
        target = row.get('Target', '')
        show_limits = row.get('Show Limits', '')
        
        # Check if values are valid and format them
        def format_value(value):
            if pd.isna(value) or value == '':
                return None
            try:
                return float(value)
            except:
                return None
        
        lsl_val = format_value(lsl)
        usl_val = format_value(usl)
        target_val = format_value(target)
        show_limits_val = format_value(show_limits)
        
        # Build spec limits parameters
        spec_params = []
        
        if lsl_val is not None:
            spec_params.append(f"LSL({lsl_val})")
        
        if usl_val is not None:
            spec_params.append(f"USL({usl_val})")
        
        if target_val is not None:
            spec_params.append(f"Target({target_val})")
        
        if show_limits_val is not None:
            spec_params.append(f"Show Limits({int(show_limits_val)})")
        
        # Only generate code when there are parameters
        if spec_params:
            jsl_code = f'Column("{variable}") << Set Property("Spec Limits", {{{", ".join(spec_params)}}});'
            print(jsl_code)
            jsl_lines.append(jsl_code)
            success_count += 1
        else:
            fail_count += 1
            print(f"❌ Skip variable {variable}: No valid spec limits")
    
    # Save to file
    if jsl_lines:
        save_jsl_to_file(jsl_lines, success_count, fail_count, source_file_path)
    else:
        print("❌ No JSL code generated")
        messagebox.showwarning("Warning", "No valid spec limits data found")

def save_jsl_to_file(jsl_lines, success_count, fail_count, source_file_path=None):
    """Save JSL code to file"""
    try:
        # Read JSL template file
        # Use actual file path directly
        template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "scripts", "jsl", "spec_setup.jsl")
        
        if not os.path.exists(template_path):
            print(f"❌ Template file not found: {template_path}")
            # If template not found, use old method
            return save_jsl_to_file_simple(jsl_lines, source_file_path)
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Replace spec limits content
        spec_limits_content = "\n".join(jsl_lines)
        template_content = template_content.replace("// [SPEC_LIMITS_PLACEHOLDER]", spec_limits_content)
        
        # Replace success count
        success_count_line = f"success_count = {success_count};\nfail_count = {fail_count};"
        template_content = template_content.replace("// [SUCCESS_COUNT_PLACEHOLDER]", success_count_line)
        
        # Determine save path
        if source_file_path:
            # Use same folder as limits file
            output_dir = os.path.dirname(source_file_path)
        else:
            # Default to output folder
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
        
        # Generate filename (with timestamp)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"spec_setup_{timestamp}.jsl"
        file_path = os.path.join(output_dir, filename)
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        print(f"✅ JSL file saved: {file_path}")
        print(f"   Successfully processed: {success_count} variables")
        if fail_count > 0:
            print(f"   Failed: {fail_count} variables")
        
        # Automatically open JSL file
        open_jsl_file(file_path)
        
        return file_path
        
    except Exception as e:
        print(f"❌ JSL file save failed: {str(e)}")
        return None

def save_jsl_to_file_simple(jsl_lines, source_file_path=None):
    """Simple version of JSL file save (backup method)"""
    try:
        # Determine save path
        if source_file_path:
            output_dir = os.path.dirname(source_file_path)
        else:
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"spec_limits_{timestamp}.jsl"
        file_path = os.path.join(output_dir, filename)
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            for jsl_line in jsl_lines:
                f.write(jsl_line + "\n")
        
        print(f"✅ JSL file saved: {file_path}")
        open_jsl_file(file_path)
        
        return file_path
        
    except Exception as e:
        print(f"❌ JSL file save failed: {str(e)}")
        return None

def open_jsl_file(file_path):
    """Open JSL file"""
    try:
        import subprocess
        import platform
        
        system = platform.system()
        
        if system == "Darwin":  # macOS
            subprocess.run(["open", file_path], check=True)
        elif system == "Windows":
            subprocess.run(["start", file_path], shell=True, check=True)
        elif system == "Linux":
            subprocess.run(["xdg-open", file_path], check=True)
        else:
            print(f"⚠️  Unsupported operating system: {system}")
            return False
            
        print(f"✅ JSL file opened: {file_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ File open failed: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error occurred while opening file: {str(e)}")
        return False

