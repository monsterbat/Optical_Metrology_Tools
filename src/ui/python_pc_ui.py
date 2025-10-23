#!/usr/bin/env python3
"""
Process Capability Python Only - UI Module
完全使用Python實現的數據處理和過程能力分析用戶界面
Author: SC Hsiao
Version: 1.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
import os
import json
from typing import List, Dict, Any
from src.core.data_processor import PythonPCCore
from src.core.pc_calculator import ProcessCapabilityCalculator

class PythonPCUI:
    """Process Capability Python Only UI Class"""
    
    def __init__(self, parent):
        self.parent = parent
        self.core = PythonPCCore()
        self.calculator = ProcessCapabilityCalculator()
        
        # UI狀態
        self.current_file_path = None
        self.current_sheet_name = None
        self.available_sheets = []
        
        # 配置檔案路徑
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")
        self.presets_file = os.path.join(self.config_dir, "variable_presets.json")
        
        # 載入預設分析變數組合（從 JSON 檔案）
        self.analysis_presets = self.load_presets()
        
        self.create_ui()
    
    def create_ui(self):
        """創建主要UI界面"""
        # 主框架
        main_frame = tk.LabelFrame(self.parent, bd=2, relief="groove", padx=10, pady=10)
        main_frame.pack(fill="x", padx=10, pady=10)
        
        # 標題
        title = tk.Label(main_frame, text="Optical Data Analysis Tools v1.0", 
                        font=("Arial", 18, "bold"), anchor="center")
        title.pack(fill="x", pady=(0, 15))
        
        # Step 1: Open Data
        self.create_open_data_ui(main_frame)
        
        # Step 2: 選擇分析變數組合
        self.create_variable_selection_ui(main_frame)
        
        # Step 3: 數據處理
        self.create_data_process_ui(main_frame)
        
        # Step 4: Process Capability 計算
        self.create_process_capability_ui(main_frame)
        
        # 狀態顯示
        self.create_status_ui(main_frame)
    
    def create_variable_selection_ui(self, parent):
        """創建分析變數選擇UI"""
        frame = tk.LabelFrame(parent, text="Step 2: Quick Data Source You Are Analyzed", padx=5, pady=5)
        frame.pack(fill="x", pady=(0, 10))
        
        # 下拉選單和自訂按鈕
        combo_frame = tk.Frame(frame)
        combo_frame.pack(fill="x", pady=(0, 5))
        
        tk.Label(combo_frame, text="Select Data Source:", 
                font=("Arial", 11)).pack(side="left", padx=(0, 10))
        
        self.preset_var = tk.StringVar(value="Test")
        self.preset_combo = ttk.Combobox(combo_frame, textvariable=self.preset_var, 
                                        values=list(self.analysis_presets.keys()),
                                        state="readonly", width=20)
        self.preset_combo.pack(side="left", padx=(0, 10))
        self.preset_combo.bind("<<ComboboxSelected>>", self.on_preset_change)
        
        # Custom 按鈕
        tk.Button(combo_frame, text="Custom Variables", 
                 command=self.open_custom_variables_dialog,
                 font=("Arial", 11), width=15).pack(side="left", padx=(0, 5))
        
        # Upload Selection 按鈕
        tk.Button(combo_frame, text="Upload Selection", 
                 command=self.upload_selection_file,
                 font=("Arial", 11), width=15).pack(side="left", padx=(0, 5))
        
        # Delete Preset 按鈕
        tk.Button(combo_frame, text="Delete Preset", 
                 command=self.delete_preset_dialog,
                 font=("Arial", 11), width=15).pack(side="left")
        
        # 顯示當前選擇的變數
        self.vars_label = tk.Label(frame, text="", font=("Arial", 10), 
                                  fg="white", wraplength=600, anchor="w")
        self.vars_label.pack(fill="x", pady=(5, 0))
        
        self.update_variables_display()
    
    def create_open_data_ui(self, parent):
        """創建Open Data UI"""
        frame = tk.LabelFrame(parent, text="Step 1: Open Data", padx=5, pady=5)
        frame.pack(fill="x", pady=(0, 10))
        
        # 檔案選擇
        file_frame = tk.Frame(frame)
        file_frame.pack(fill="x", pady=(0, 5))
        
        tk.Button(file_frame, text="Select File", command=self.select_file,
                 font=("Arial", 11), width=12).pack(side="left", padx=(0, 10))
        
        self.file_label = tk.Label(file_frame, text="No file selected", 
                                  font=("Arial", 10), anchor="w")
        self.file_label.pack(side="left", fill="x", expand=True)
        
        # Sheet選擇 (Excel檔案)
        sheet_frame = tk.Frame(frame)
        sheet_frame.pack(fill="x", pady=(0, 5))
        
        tk.Label(sheet_frame, text="Sheet:", font=("Arial", 10)).pack(side="left")
        self.sheet_var = tk.StringVar()
        self.sheet_combo = ttk.Combobox(sheet_frame, textvariable=self.sheet_var, 
                                       state="disabled", width=20)
        self.sheet_combo.pack(side="left", padx=(5, 10))
        
        # 數據開始行
        tk.Label(sheet_frame, text="Data Start Row:", font=("Arial", 10)).pack(side="left")
        self.start_row_var = tk.StringVar(value="2")
        tk.Entry(sheet_frame, textvariable=self.start_row_var, width=5).pack(side="left", padx=(5, 10))
        
        # 載入按鈕
        tk.Button(sheet_frame, text="Load Data", command=self.load_data,
                 font=("Arial", 11), width=12).pack(side="left")
    
    def create_data_process_ui(self, parent):
        """創建數據處理UI"""
        frame = tk.LabelFrame(parent, text="Step 3: Data Processing", padx=5, pady=5)
        frame.pack(fill="x", pady=(0, 10))
        
        # 按鈕框架
        btn_frame = tk.Frame(frame)
        btn_frame.pack()
        
        # 處理按鈕
        self.exclude_dup_btn = tk.Button(btn_frame, text="Exclude Duplicate", 
                                        command=self.exclude_duplicates,
                                        font=("Arial", 11), width=16, state="disabled")
        self.exclude_dup_btn.pack(side="left", padx=5)
        
        self.setup_spec_btn = tk.Button(btn_frame, text="Setup Spec", 
                                       command=self.setup_spec,
                                       font=("Arial", 11), width=16, state="disabled")
        self.setup_spec_btn.pack(side="left", padx=5)
        
        self.exclude_outlier_btn = tk.Button(btn_frame, text="Exclude Outlier", 
                                            command=self.exclude_outliers,
                                            font=("Arial", 11), width=16, state="disabled")
        self.exclude_outlier_btn.pack(side="left", padx=5)
        
        self.export_data_btn = tk.Button(btn_frame, text="Export Processed Data", 
                                        command=self.export_processed_data,
                                        font=("Arial", 11), width=18, state="disabled")
        self.export_data_btn.pack(side="left", padx=5)
    
    def create_process_capability_ui(self, parent):
        """創建Analysis UI"""
        frame = tk.LabelFrame(parent, text="Step 4: Analysis", padx=5, pady=5)
        frame.pack(fill="x", pady=(0, 10))
        
        # 按鈕框架
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        
        # Process Capability 按鈕
        self.pc_btn = tk.Button(btn_frame, text="Process Capability", 
                               command=self.calculate_process_capability,
                               font=("Arial", 12, "bold"), width=20, state="disabled")
        self.pc_btn.pack(side="left", padx=5)
        
        # Box Plot 按鈕
        self.box_plot_btn = tk.Button(btn_frame, text="Box Plot", 
                                      command=self.show_box_plot,
                                      font=("Arial", 12, "bold"), width=20, state="disabled")
        self.box_plot_btn.pack(side="left", padx=5)
        
        # Correlation/Chromaticity 按鈕
        self.correlation_btn = tk.Button(btn_frame, text="Correlation/Chromaticity", 
                                        command=self.show_correlation,
                                        font=("Arial", 12, "bold"), width=25, state="disabled")
        self.correlation_btn.pack(side="left", padx=5)
    
    def create_status_ui(self, parent):
        """創建狀態顯示UI"""
        frame = tk.LabelFrame(parent, text="Status", padx=5, pady=5)
        frame.pack(fill="x", pady=(0, 10))
        
        # 創建容器來放置 Text 和 Scrollbar
        text_container = tk.Frame(frame)
        text_container.pack(fill="both", expand=True)
        
        # 捲軸
        scrollbar = ttk.Scrollbar(text_container, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        # 狀態文字區域（可選取和複製，但不可編輯）
        self.status_text = tk.Text(text_container, height=8, font=("Consolas", 10),
                                   wrap="word", yscrollcommand=scrollbar.set,
                                   cursor="xterm")  # 設置為文字選取游標
        self.status_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.status_text.yview)
        
        # 設置為只讀（但保持可選取）
        self._make_text_readonly(self.status_text)
        
        # 綁定右鍵選單（複製功能）
        self.create_text_context_menu(self.status_text)
        
        # 綁定快捷鍵 Cmd+C (macOS) 或 Ctrl+C (Windows/Linux)
        self.status_text.bind("<Command-c>", lambda e: self.copy_selection(self.status_text))
        self.status_text.bind("<Control-c>", lambda e: self.copy_selection(self.status_text))
        self.status_text.bind("<Command-a>", lambda e: self.select_all(self.status_text))
        self.status_text.bind("<Control-a>", lambda e: self.select_all(self.status_text))
    
    def _make_text_readonly(self, text_widget):
        """讓 Text widget 只讀但可選取"""
        # 綁定事件來阻止所有修改操作，但允許選取
        def block_edit(event):
            # 允許的操作：選取、複製、移動游標、滾動
            allowed_keysyms = [
                'Left', 'Right', 'Up', 'Down',  # 方向鍵
                'Home', 'End', 'Prior', 'Next',  # Home, End, Page Up, Page Down
                'Shift_L', 'Shift_R', 'Control_L', 'Control_R',  # 修飾鍵
                'Command', 'Alt_L', 'Alt_R'  # macOS Command 和 Alt
            ]
            
            # 允許選取相關的快捷鍵
            if event.keysym in allowed_keysyms:
                return None  # 允許這些操作
            
            # 允許 Cmd+C / Ctrl+C (複製)
            if event.keysym in ['c', 'C'] and (event.state & 0x4 or event.state & 0x8):
                return None
            
            # 允許 Cmd+A / Ctrl+A (全選)
            if event.keysym in ['a', 'A'] and (event.state & 0x4 or event.state & 0x8):
                return None
            
            # 阻止其他所有鍵盤輸入
            return "break"
        
        # 綁定鍵盤事件
        text_widget.bind("<Key>", block_edit)
        
        # 允許滑鼠選取但不允許貼上
        text_widget.bind("<Button-1>", lambda e: None)  # 允許點擊
        text_widget.bind("<B1-Motion>", lambda e: None)  # 允許拖曳選取
        text_widget.bind("<Double-Button-1>", lambda e: None)  # 允許雙擊選取
        text_widget.bind("<Triple-Button-1>", lambda e: None)  # 允許三擊選取
    
    def create_text_context_menu(self, text_widget):
        """創建文字區域的右鍵選單"""
        context_menu = tk.Menu(text_widget, tearoff=0)
        context_menu.add_command(label="Copy (Cmd+C)", 
                                command=lambda: self.copy_selection(text_widget))
        context_menu.add_command(label="Select All (Cmd+A)", 
                                command=lambda: self.select_all(text_widget))
        context_menu.add_separator()
        context_menu.add_command(label="Clear", 
                                command=lambda: self.clear_text(text_widget))
        
        def show_context_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        # 綁定右鍵點擊
        text_widget.bind("<Button-2>", show_context_menu)  # macOS (右鍵)
        text_widget.bind("<Button-3>", show_context_menu)  # Windows/Linux (右鍵)
    
    def copy_selection(self, text_widget):
        """複製選取的文字到剪貼簿"""
        try:
            selected_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.parent.clipboard_clear()
            self.parent.clipboard_append(selected_text)
            return "break"  # 防止事件繼續傳播
        except tk.TclError:
            # 沒有選取任何文字
            pass
    
    def select_all(self, text_widget):
        """全選文字"""
        text_widget.tag_add(tk.SEL, "1.0", tk.END)
        text_widget.mark_set(tk.INSERT, "1.0")
        text_widget.see(tk.INSERT)
        return "break"
    
    def clear_text(self, text_widget):
        """清空文字（僅用於 Status）"""
        if text_widget == self.status_text:
            response = messagebox.askyesno("Confirm", "Are you sure you want to clear the status log?")
            if response:
                # 程式內部的刪除操作不受只讀限制（只限制用戶輸入）
                text_widget.delete("1.0", tk.END)
    
    def log_status(self, message: str):
        """添加狀態訊息"""
        # Text widget 設置為只讀模式，但插入時需要暫時解除
        # 由於我們使用事件綁定來實現只讀，直接插入不受影響
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.parent.update()
    
    def on_preset_change(self, event=None):
        """處理預設變數組合改變"""
        self.update_variables_display()
    
    def update_variables_display(self):
        """更新變數顯示"""
        preset = self.preset_var.get()
        variables = self.analysis_presets.get(preset, [])
        self.core.set_analysis_variables(variables)
        
        if variables:
            vars_text = f"Selected variables: {', '.join(variables)}"
        else:
            vars_text = "No variables selected"
        
        self.vars_label.config(text=vars_text)
    
    def load_presets(self) -> Dict[str, List[str]]:
        """從 JSON 檔案載入預設組合"""
        # 預設值
        default_presets = {
            "Example": [],
            "Custom": []
        }
        
        try:
            # 確保 config 目錄存在
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)
                print("📁 已創建 config 目錄")
            
            # 如果檔案存在，載入它
            if os.path.exists(self.presets_file):
                with open(self.presets_file, 'r', encoding='utf-8') as f:
                    presets = json.load(f)
                    # 移除註解欄位（如果存在）
                    presets.pop('_comment', None)
                    print(f"✅ 已從 JSON 載入 {len(presets)} 個預設組合")
                    return presets
            else:
                # 檔案不存在，創建預設配置檔案
                if not os.path.exists(self.config_dir):
                    os.makedirs(self.config_dir)
                
                save_data = default_presets.copy()
                save_data['_comment'] = "此檔案儲存分析變數的預設組合。你可以手動編輯此檔案來新增或修改預設組合。"
                
                with open(self.presets_file, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, ensure_ascii=False, indent=2)
                
                print("📝 已創建預設配置檔案")
                return default_presets
                
        except Exception as e:
            print(f"⚠️ 載入配置檔案失敗，使用預設值: {str(e)}")
            return default_presets
    
    def save_presets(self, presets: Dict[str, List[str]] = None):
        """儲存預設組合到 JSON 檔案"""
        if presets is None:
            presets = self.analysis_presets
        
        try:
            # 確保 config 目錄存在
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)
            
            # 加入註解
            save_data = presets.copy()
            save_data['_comment'] = "此檔案儲存分析變數的預設組合。你可以手動編輯此檔案來新增或修改預設組合。"
            
            # 儲存到 JSON 檔案
            with open(self.presets_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            self.log_status(f"💾 Saved {len(presets)} preset(s) to configuration file")
            return True
            
        except Exception as e:
            self.log_status(f"❌ Failed to save configuration file: {str(e)}")
            return False
    
    def open_custom_variables_dialog(self):
        """打開自訂變數選擇對話框"""
        if self.core.processed_data is None:
            messagebox.showwarning("Warning", "Please load data in Step 1 first!")
            return
        
        # 獲取所有欄位名稱（第一行）
        all_columns = list(self.core.processed_data.columns)
        
        if not all_columns:
            messagebox.showwarning("Warning", "No columns found in data!")
            return
        
        # 打開自訂變數對話框
        dialog = CustomVariableDialog(self.parent, all_columns, 
                                      self.analysis_presets.get("Custom", []))
        
        # 等待對話框關閉
        self.parent.wait_window(dialog.dialog)
        
        # 如果用戶選擇了變數
        if dialog.selected_variables is not None:
            self.analysis_presets["Custom"] = dialog.selected_variables
            self.preset_var.set("Custom")
            self.update_variables_display()
            self.log_status(f"✅ Set {len(dialog.selected_variables)} custom analysis variables")
            
            # 儲存到 JSON 檔案
            self.save_presets()
    
    def delete_preset_dialog(self):
        """打開刪除預設組合對話框"""
        if len(self.analysis_presets) == 0:
            messagebox.showwarning("Warning", "No presets available to delete!")
            return
        
        # 打開刪除對話框
        dialog = DeletePresetDialog(self.parent, list(self.analysis_presets.keys()))
        
        # 等待對話框關閉
        self.parent.wait_window(dialog.dialog)
        
        # 如果用戶選擇了要刪除的預設組合
        if dialog.presets_to_delete:
            try:
                # 刪除選中的預設組合
                for preset_name in dialog.presets_to_delete:
                    if preset_name in self.analysis_presets:
                        del self.analysis_presets[preset_name]
                
                # 儲存到 JSON 檔案
                self.save_presets()
                
                # 更新下拉選單選項
                self.preset_combo.config(values=list(self.analysis_presets.keys()))
                
                # 如果當前選擇的預設組合被刪除了，切換到第一個可用的
                if self.preset_var.get() not in self.analysis_presets:
                    if self.analysis_presets:
                        first_preset = list(self.analysis_presets.keys())[0]
                        self.preset_var.set(first_preset)
                    else:
                        self.preset_var.set("")
                
                self.update_variables_display()
                
                # 顯示成功訊息
                deleted_count = len(dialog.presets_to_delete)
                self.log_status(f"✅ Deleted {deleted_count} preset(s): {', '.join(dialog.presets_to_delete)}")
                messagebox.showinfo("Success", f"Successfully deleted {deleted_count} preset(s)")
                
            except Exception as e:
                error_msg = f"Failed to delete presets: {str(e)}"
                self.log_status(f"❌ {error_msg}")
                messagebox.showerror("Error", error_msg)
    
    def upload_selection_file(self):
        """上傳變數選擇檔案（CSV 或 Excel）"""
        # 選擇檔案
        file_path = filedialog.askopenfilename(
            title="Select Variable List File",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            import pandas as pd
            
            # 讀取檔案
            if file_path.lower().endswith(('.xlsx', '.xls')):
                # Excel 檔案 - 讀取第一欄
                df = pd.read_excel(file_path, header=None)
            elif file_path.lower().endswith('.csv'):
                # CSV 檔案 - 讀取第一欄
                df = pd.read_csv(file_path, header=None)
            else:
                messagebox.showerror("Error", "Unsupported file format! Please select Excel or CSV file.")
                return
            
            # 取得第一欄的所有值（從上到下）
            if df.empty or df.shape[1] == 0:
                messagebox.showerror("Error", "No data found in file!")
                return
            
            # 讀取第一欄（A列）的所有非空值
            first_column = df.iloc[:, 0].dropna()
            
            if first_column.empty:
                messagebox.showerror("Error", "No variable names found in first column!")
                return
            
            # 轉換為字串列表並移除空白
            variables = [str(val).strip() for val in first_column if str(val).strip()]
            
            if not variables:
                messagebox.showerror("Error", "No valid variable names found!")
                return
            
            # 使用檔案名稱（不含副檔名）作為預設組合名稱
            file_name = os.path.basename(file_path)
            preset_name = os.path.splitext(file_name)[0]  # 移除副檔名
            
            # 將上傳的變數加入到新的預設組合
            self.analysis_presets[preset_name] = variables
            
            # 更新下拉選單選項
            self.preset_combo.config(values=list(self.analysis_presets.keys()))
            
            # 切換到上傳的組合
            self.preset_var.set(preset_name)
            self.update_variables_display()
            
            # 儲存到 JSON 檔案
            self.save_presets()
            
            # 顯示成功訊息
            success_msg = f"Successfully loaded {len(variables)} variable(s)"
            self.log_status(f"✅ {success_msg}")
            self.log_status(f"   Preset name: {preset_name}")
            self.log_status(f"   Source file: {file_name}")
            self.log_status(f"   Variables: {', '.join(variables[:10])}{'...' if len(variables) > 10 else ''}")
            
            messagebox.showinfo("Success", f"{success_msg}\nCreated preset: {preset_name}")
            
        except Exception as e:
            error_msg = f"Failed to read file: {str(e)}"
            self.log_status(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
    
    def select_file(self):
        """選擇檔案"""
        file_path = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.current_file_path = file_path
            self.file_label.config(text=os.path.basename(file_path))
            
            # 如果是Excel檔案，取得工作表列表
            if file_path.lower().endswith(('.xlsx', '.xls')):
                self.available_sheets = self.core.get_excel_sheets(file_path)
                if self.available_sheets:
                    self.sheet_combo.config(values=self.available_sheets, state="readonly")
                    self.sheet_combo.set(self.available_sheets[0])
                else:
                    self.sheet_combo.config(state="disabled")
            else:
                self.sheet_combo.config(state="disabled")
                self.sheet_var.set("")
    
    def load_data(self):
        """載入數據"""
        if not self.current_file_path:
            messagebox.showerror("Error", "Please select a file first")
            return
        
        try:
            # 取得參數
            sheet_name = self.sheet_var.get() if self.sheet_var.get() else None
            start_row = int(self.start_row_var.get()) - 1  # 轉換為0-based index
            
            # 載入數據
            success = self.core.load_data_file(self.current_file_path, sheet_name, start_row)
            
            if success:
                self.log_status("✅ Data loaded successfully")
                summary = self.core.get_data_summary()
                self.log_status(f"   Records: {summary['total_records']}")
                self.log_status(f"   Columns: {summary['total_columns']}")
                
                # 啟用處理按鈕
                self.exclude_dup_btn.config(state="normal")
                self.setup_spec_btn.config(state="normal")
                self.exclude_outlier_btn.config(state="normal")
                self.export_data_btn.config(state="normal")
                self.pc_btn.config(state="normal")
                self.box_plot_btn.config(state="normal")
                self.correlation_btn.config(state="normal")
                
                # 檢查必要欄位
                if not self.core.validate_required_columns():
                    self.log_status("⚠️ Warning: Some required columns may be missing")
                    self.log_status("   Required: SerialNumber, OverallResult, StartTime")
            else:
                self.log_status("❌ Failed to load data")
                
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid start row: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
    def exclude_duplicates(self):
        """移除重複值"""
        if self.core.processed_data is None:
            messagebox.showerror("Error", "No data loaded")
            return
        
        success, message = self.core.exclude_duplicates()
        self.log_status(message)
        
        if not success:
            messagebox.showerror("Error", "Failed to exclude duplicates")
    
    def setup_spec(self):
        """設定規格限制"""
        limits_file = filedialog.askopenfilename(
            title="Select Limits File",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*")
            ]
        )
        
        if limits_file:
            success, message = self.core.load_spec_limits(limits_file)
            self.log_status(message)
            
            if not success:
                messagebox.showerror("Error", "Failed to load spec limits")
    
    def exclude_outliers(self):
        """移除異常值"""
        if self.core.processed_data is None:
            messagebox.showerror("Error", "No data loaded")
            return
        
        # 開啟異常值設定對話框
        self.show_outlier_settings_dialog()
    
    def show_outlier_settings_dialog(self):
        """顯示異常值設定對話框"""
        dialog = Toplevel(self.parent)
        dialog.title("Outlier Detection Settings")
        dialog.geometry("600x500")  # 增大視窗大小
        dialog.resizable(True, True)  # 允許調整大小
        
        # 置中顯示
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # 創建主容器和滾動條
        main_container = tk.Frame(dialog)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 創建canvas和scrollbar
        canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        # 配置滾動
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 打包canvas和scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 滑鼠滾輪支援
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux
        
        # 主框架 (現在在scrollable_frame中)
        main_frame = tk.Frame(scrollable_frame, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # 標題
        tk.Label(main_frame, text="Quantile Range Outliers", 
                font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        # 說明
        tk.Label(main_frame, text="Outliers are values Q times the interquantile range past the lower and upper quantiles.",
                wraplength=350, justify="left").pack(pady=(0, 15))
        
        # 參數設定
        params_frame = tk.Frame(main_frame)
        params_frame.pack(pady=(0, 20))
        
        # Tail Quantile
        tk.Label(params_frame, text="Tail Quantile:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        tail_var = tk.StringVar(value=str(self.core.tail_quantile))
        tk.Entry(params_frame, textvariable=tail_var, width=10).grid(row=0, column=1, padx=(0, 20))
        
        # Q
        tk.Label(params_frame, text="Q:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        q_var = tk.StringVar(value=str(self.core.q_value))
        tk.Entry(params_frame, textvariable=q_var, width=10).grid(row=0, column=3)
        
        # 選項
        options_frame = tk.Frame(main_frame)
        options_frame.pack(pady=(0, 20))
        
        restrict_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Restrict search to integers", 
                      variable=restrict_var).pack(anchor="w")
        
        # 預覽
        preview_frame = tk.LabelFrame(main_frame, text="Outliers by Column")
        preview_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(preview_frame, text="Show only columns with outliers").pack(anchor="w")
        
        # 按鈕框架 (在主容器外部，不會滾動)
        btn_container = tk.Frame(dialog)
        btn_container.pack(side="bottom", fill="x", padx=20, pady=10)
        
        btn_frame = tk.Frame(btn_container)
        btn_frame.pack()
        
        def apply_outlier_detection():
            try:
                tail_quantile = float(tail_var.get())
                q_value = float(q_var.get())
                
                success, message = self.core.exclude_outliers(tail_quantile, q_value)
                self.log_status(message)
                
                if not success:
                    messagebox.showerror("Error", "Failed to exclude outliers")
                
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values")
        
        tk.Button(btn_frame, text="Exclude", command=apply_outlier_detection,
                 font=("Arial", 11), width=12).pack(side="left", padx=(0, 10))
        tk.Button(btn_frame, text="Close", command=dialog.destroy,
                 font=("Arial", 11), width=12).pack(side="left")
        
        # 初始聚焦到canvas以支援滾輪
        canvas.focus_set()
    
    def export_processed_data(self):
        """輸出處理後的數據（移除重複值和異常值後）"""
        if self.core.processed_data is None:
            messagebox.showerror("Error", "No processed data available")
            return
        
        try:
            # 詢問保存位置
            from tkinter import filedialog
            save_path = filedialog.asksaveasfilename(
                title="Export Processed Data",
                defaultextension=".csv",
                filetypes=[
                    ("CSV files", "*.csv"),
                    ("Excel files", "*.xlsx"),
                    ("All files", "*.*")
                ]
            )
            
            if save_path:
                # 根據文件擴展名選擇保存格式
                if save_path.lower().endswith('.xlsx'):
                    self.core.processed_data.to_excel(save_path, index=False)
                else:
                    self.core.processed_data.to_csv(save_path, index=False)
                
                # 顯示數據摘要信息
                data_info = f"""
📊 Exported processed data:
📁 File: {save_path}
📏 Data shape: {self.core.processed_data.shape} (rows × columns)
📋 Total records: {len(self.core.processed_data)}
🔢 Total columns: {len(self.core.processed_data.columns)}

📈 Analysis variables: {', '.join(self.core.get_analysis_variables()) if self.core.get_analysis_variables() else 'Not set'}
                """
                
                messagebox.showinfo("Export Complete", data_info.strip())
                self.log_status(f"✅ Data exported: {save_path}")
                self.log_status(f"   Shape: {self.core.processed_data.shape}")
                
        except Exception as e:
            error_msg = f"Failed to export data: {str(e)}"
            messagebox.showerror("Error", error_msg)
            self.log_status(f"❌ {error_msg}")
    
    def calculate_process_capability(self):
        """計算過程能力 - 使用預覽對話框"""
        if self.core.processed_data is None:
            messagebox.showerror("Error", "No data loaded")
            return
        
        if self.core.limits_data is None:
            messagebox.showerror("Error", "No spec limits loaded")
            return
        
        try:
            self.log_status("🔄 Opening Process Capability preview...")
            
            # 開啟預覽對話框
            from src.ui.pc_preview_dialog import PCPreviewDialog
            preview_dialog = PCPreviewDialog(self.parent, self.core, self.core.limits_data)
            preview_dialog.show()
            
        except Exception as e:
            error_msg = f"❌ Failed to open Process Capability preview: {str(e)}"
            self.log_status(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def show_box_plot(self):
        """顯示箱型圖分析"""
        if self.core.processed_data is None:
            messagebox.showerror("Error", "Please load data first!")
            return
        
        # 如果沒有 spec 限制，給予提示但仍允許繼續
        if self.core.limits_data is None:
            response = messagebox.askyesno(
                "Notice", 
                "Spec limits not set (Setup Spec).\n\n"
                "Without spec limits, Box Plot will not display LSL/USL/Target lines.\n\n"
                "Continue anyway?",
                icon='warning'
            )
            if not response:
                return
        
        try:
            self.log_status("🔄 Opening Box Plot analysis...")
            
            # 開啟箱型圖對話框
            from src.ui.box_plot_dialog import BoxPlotDialog
            box_plot_dialog = BoxPlotDialog(self.parent, self.core, self.core.limits_data)
            box_plot_dialog.show()
            
            self.log_status("✅ Box Plot analysis window opened")
            
        except Exception as e:
            error_msg = f"❌ Failed to open Box Plot analysis: {str(e)}"
            self.log_status(error_msg)
            messagebox.showerror("Error", error_msg)
            import traceback
            traceback.print_exc()
    
    def show_correlation(self):
        """顯示相關性/色度分析"""
        if self.core.processed_data is None:
            messagebox.showerror("Error", "Please load data first!")
            return
        
        # 檢查至少有兩個變數
        analysis_vars = self.core.get_analysis_variables()
        if len(analysis_vars) < 2:
            messagebox.showerror("Error", "At least two analysis variables are required for correlation analysis!")
            return
        
        try:
            self.log_status("🔄 Opening Correlation/Chromaticity analysis...")
            
            # 開啟相關性/色度分析對話框
            from src.ui.correlation_dialog import CorrelationDialog
            correlation_dialog = CorrelationDialog(self.parent, self.core, self.core.limits_data)
            correlation_dialog.show()
            
            self.log_status("✅ Correlation/Chromaticity analysis window opened")
            
        except Exception as e:
            error_msg = f"❌ Failed to open Correlation/Chromaticity analysis: {str(e)}"
            self.log_status(error_msg)
            messagebox.showerror("Error", error_msg)
            import traceback
            traceback.print_exc()

class DeletePresetDialog:
    """刪除預設組合對話框"""
    
    def __init__(self, parent, available_presets):
        """
        初始化對話框
        
        Args:
            parent: 父視窗
            available_presets: 所有可用的預設組合名稱列表
        """
        self.presets_to_delete = []
        
        # 創建對話框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Delete Presets")
        self.dialog.geometry("500x400")
        self.dialog.resizable(True, True)
        
        # 主框架
        main_frame = tk.Frame(self.dialog, padx=15, pady=15)
        main_frame.pack(fill="both", expand=True)
        
        # 說明文字
        info_label = tk.Label(main_frame, 
                             text="Select presets to delete (multiple selection allowed):",
                             font=("Arial", 11, "bold"), fg="red")
        info_label.pack(anchor="w", pady=(0, 10))
        
        # 警告訊息
        warning_label = tk.Label(main_frame, 
                                text="⚠️ This action cannot be undone. Please proceed with caution!",
                                font=("Arial", 10), fg="orange")
        warning_label.pack(anchor="w", pady=(0, 10))
        
        # 顯示選擇數量
        self.count_label = tk.Label(main_frame, text="Selected: 0", 
                                   font=("Arial", 10), fg="blue")
        self.count_label.pack(anchor="w", pady=(0, 5))
        
        # Listbox 框架（含滾輪）
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # 垂直滾輪
        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        # Listbox - 使用 extended 模式支援多選
        self.listbox = tk.Listbox(list_frame, 
                                  selectmode="extended",  # 支援 Shift/Ctrl 多選
                                  font=("Arial", 11),
                                  yscrollcommand=scrollbar.set,
                                  height=12)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # 綁定選擇變更事件
        self.listbox.bind("<<ListboxSelect>>", self.update_count)
        
        # 填充預設組合列表
        for preset in available_presets:
            self.listbox.insert(tk.END, preset)
        
        # 按鈕框架
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        tk.Button(button_frame, text="Delete", command=self.confirm_delete,
                 font=("Arial", 11, "bold"), width=12, fg="red").pack(side="left", padx=(0, 10))
        tk.Button(button_frame, text="Cancel", command=self.cancel,
                 font=("Arial", 11), width=12).pack(side="left")
        
        # 居中顯示
        self.dialog.transient(parent)
        self.dialog.grab_set()
    
    def update_count(self, event=None):
        """更新選擇數量顯示"""
        count = len(self.listbox.curselection())
        self.count_label.config(text=f"Selected: {count}")
    
    def confirm_delete(self):
        """確認刪除"""
        selected_indices = self.listbox.curselection()
        
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select at least one preset!")
            return
        
        # 取得選中的預設組合名稱
        selected_presets = [self.listbox.get(i) for i in selected_indices]
        
        # 再次確認
        confirm_msg = f"Are you sure you want to delete the following {len(selected_presets)} preset(s)?\n\n"
        confirm_msg += "\n".join(f"• {name}" for name in selected_presets)
        confirm_msg += "\n\nThis action cannot be undone!"
        
        response = messagebox.askyesno("Confirm Delete", confirm_msg, icon='warning')
        
        if response:
            self.presets_to_delete = selected_presets
            self.dialog.destroy()
    
    def cancel(self):
        """取消刪除"""
        self.presets_to_delete = []
        self.dialog.destroy()


class CustomVariableDialog:
    """自訂變數選擇對話框"""
    
    def __init__(self, parent, available_columns, current_selection):
        """
        初始化對話框
        
        Args:
            parent: 父視窗
            available_columns: 所有可用的欄位列表
            current_selection: 目前已選擇的欄位列表
        """
        self.selected_variables = None
        
        # 創建對話框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Custom Analysis Variables Selection")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        
        # 主框架
        main_frame = tk.Frame(self.dialog, padx=15, pady=15)
        main_frame.pack(fill="both", expand=True)
        
        # 說明文字
        info_label = tk.Label(main_frame, 
                             text="Select variables to analyze (use Shift/Ctrl for multiple selection):",
                             font=("Arial", 11))
        info_label.pack(anchor="w", pady=(0, 10))
        
        # 搜尋框
        search_frame = tk.Frame(main_frame)
        search_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(search_frame, text="Search:", font=("Arial", 10)).pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.filter_columns())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", fill="x", expand=True)
        
        # 快速按鈕框架
        btn_top_frame = tk.Frame(main_frame)
        btn_top_frame.pack(fill="x", pady=(0, 5))
        
        tk.Button(btn_top_frame, text="Select All", command=self.select_all,
                 font=("Arial", 10), width=10).pack(side="left", padx=(0, 5))
        tk.Button(btn_top_frame, text="Deselect All", command=self.deselect_all,
                 font=("Arial", 10), width=10).pack(side="left", padx=(0, 5))
        tk.Button(btn_top_frame, text="Invert", command=self.invert_selection,
                 font=("Arial", 10), width=10).pack(side="left")
        
        # 顯示選擇數量
        self.count_label = tk.Label(btn_top_frame, text="Selected: 0", 
                                   font=("Arial", 10), fg="blue")
        self.count_label.pack(side="right")
        
        # Listbox 框架（含滾輪）
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # 垂直滾輪
        v_scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        v_scrollbar.pack(side="right", fill="y")
        
        # 水平滾輪
        h_scrollbar = tk.Scrollbar(list_frame, orient="horizontal")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Listbox - 使用 extended 模式支援多選
        self.listbox = tk.Listbox(list_frame, 
                                  selectmode="extended",  # 支援 Shift/Ctrl 多選
                                  font=("Consolas", 10),
                                  yscrollcommand=v_scrollbar.set,
                                  xscrollcommand=h_scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        
        v_scrollbar.config(command=self.listbox.yview)
        h_scrollbar.config(command=self.listbox.xview)
        
        # 綁定選擇變更事件
        self.listbox.bind("<<ListboxSelect>>", self.update_count)
        
        # 儲存所有欄位
        self.all_columns = available_columns
        self.current_selection = current_selection
        
        # 填充欄位列表
        self.populate_listbox()
        
        # 恢復先前的選擇
        self.restore_selection()
        
        # 按鈕框架
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        tk.Button(button_frame, text="OK", command=self.confirm,
                 font=("Arial", 11, "bold"), width=12).pack(side="left", padx=(0, 10))
        tk.Button(button_frame, text="Cancel", command=self.cancel,
                 font=("Arial", 11), width=12).pack(side="left")
        
        # 居中顯示
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 更新選擇數量
        self.update_count()
    
    def populate_listbox(self):
        """填充 Listbox"""
        self.listbox.delete(0, tk.END)
        search_text = self.search_var.get().lower()
        
        for col in self.all_columns:
            if not search_text or search_text in col.lower():
                self.listbox.insert(tk.END, col)
    
    def filter_columns(self):
        """根據搜尋文字過濾欄位"""
        # 儲存當前選擇
        current_selected = [self.listbox.get(i) for i in self.listbox.curselection()]
        
        # 重新填充
        self.populate_listbox()
        
        # 恢復選擇
        for i in range(self.listbox.size()):
            if self.listbox.get(i) in current_selected:
                self.listbox.selection_set(i)
    
    def restore_selection(self):
        """恢復先前的選擇"""
        for i in range(self.listbox.size()):
            if self.listbox.get(i) in self.current_selection:
                self.listbox.selection_set(i)
    
    def select_all(self):
        """全選"""
        self.listbox.selection_set(0, tk.END)
        self.update_count()
    
    def deselect_all(self):
        """全不選"""
        self.listbox.selection_clear(0, tk.END)
        self.update_count()
    
    def invert_selection(self):
        """反選"""
        for i in range(self.listbox.size()):
            if self.listbox.selection_includes(i):
                self.listbox.selection_clear(i)
            else:
                self.listbox.selection_set(i)
        self.update_count()
    
    def update_count(self, event=None):
        """更新選擇數量顯示"""
        count = len(self.listbox.curselection())
        self.count_label.config(text=f"Selected: {count}")
    
    def confirm(self):
        """確認選擇"""
        selected_indices = self.listbox.curselection()
        
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select at least one variable!")
            return
        
        self.selected_variables = [self.listbox.get(i) for i in selected_indices]
        self.dialog.destroy()
    
    def cancel(self):
        """取消選擇"""
        self.selected_variables = None
        self.dialog.destroy()


def create_python_pc_ui(parent):
    """創建Process Capability Python Only UI的函數接口"""
    return PythonPCUI(parent)
