import os
import platform
import subprocess
import tkinter as tk
from tkinter import Tk, filedialog, messagebox, ttk, Listbox, MULTIPLE, Scrollbar
import pandas as pd
import numpy as np
import re
import tempfile
from src.utils.paths import resource_path
from src.core.jsl_handler import extract_process_variables, save_jsl_with_vars
from src.utils.constants import (
    FILE_TYPE_JMP, FILE_TYPE_ALL, FILE_EXT_JMP, FILE_EXT_ALL,
    MSG_TITLE_SUCCESS, MSG_TITLE_ERROR, MSG_TITLE_NOTICE, MSG_TITLE_INFO,
    MSG_NO_SCRIPT_TEMPLATE
)

# 全域變數來追蹤當前打開的檔案路徑（Beta功能用）
current_file_path_beta = None

def open_file(filepath):
    """Open file at specified path"""
    system = platform.system()
    if system == "Windows":
        os.startfile(filepath)
    elif system == "Darwin":  # macOS
        subprocess.run(["open", filepath])
    elif system == "Linux":
        subprocess.run(["xdg-open", filepath])
    else:
        print("Unsupported operating system")

def open_with_jmp(filepath):
    """Open file specifically with JMP application"""
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            # 嘗試多種 JMP 應用程式名稱（常見的排在前面）
            jmp_app_names = ["JMP 18", "JMP 19", "JMP 17", "JMP Pro 18", "JMP Pro 19", "JMP Pro 17", "JMP", "JMP Pro"]
            
            jmp_opened = False
            for app_name in jmp_app_names:
                result = subprocess.run(["open", "-a", app_name, filepath], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    jmp_opened = True
                    break
            
            if not jmp_opened:
                # 如果找不到 JMP，回到一般開啟方式
                open_file(filepath)
                    
        elif system == "Windows":
            # Windows 版本 - 可能需要調整 JMP 路徑
            jmp_paths = [
                r"C:\Program Files\SAS\JMP\19\jmp.exe",
                r"C:\Program Files\SAS\JMP\18\jmp.exe",
                r"C:\Program Files\SAS\JMP\17\jmp.exe",
                r"C:\Program Files\SAS\JMP\16\jmp.exe", 
                r"C:\Program Files\SAS\JMP\15\jmp.exe",
                r"C:\Program Files (x86)\SAS\JMP\19\jmp.exe",
                r"C:\Program Files (x86)\SAS\JMP\18\jmp.exe",
                r"C:\Program Files (x86)\SAS\JMP\17\jmp.exe",
                r"C:\Program Files (x86)\SAS\JMP\16\jmp.exe",
                r"C:\Program Files (x86)\SAS\JMP\15\jmp.exe"
            ]
            
            jmp_found = False
            for jmp_path in jmp_paths:
                if os.path.exists(jmp_path):
                    subprocess.run([jmp_path, filepath])
                    jmp_found = True
                    break
            
            if not jmp_found:
                print("JMP not found, using default application")
                open_file(filepath)
                
        else:
            # Linux 或其他系統，回到一般開啟方式
            print("JMP path not configured for this system, using default application")
            open_file(filepath)
            
    except Exception as e:
        print(f"Error opening with JMP: {e}")
        # 如果有錯誤，回到一般開啟方式
        open_file(filepath)

def ask_and_open_file(jmp_file_path=None):
    """Open file selection dialog and open selected file"""
    root = Tk()
    root.withdraw()  # Hide main window
    filepath = filedialog.askopenfilename(
        title="Select File to Open",
        filetypes=[(FILE_TYPE_JMP, FILE_EXT_JMP), (FILE_TYPE_ALL, FILE_EXT_ALL)]
    )
    if filepath:
        print("Selected file:", filepath)
        open_file(filepath)
        if jmp_file_path:
            jmp_file_path.set(filepath)
        return filepath
    else:
        print("No file selected")
        return None

def open_analysis_item(file_path=None):
    """Open analysis item file - 原版 Best Fit 功能，顯示 Report Generate 彈出視窗"""
    try:
        # 彈出 Report Generate 視窗
        create_report_generate_popup()
    except Exception as e:
        messagebox.showerror("錯誤", f"開啟 Best Fit 功能失敗: {str(e)}")

def open_duplicate_process():
    """Open Exclude Duplicate JSL file"""
    jsl_path = resource_path("config/duplicate_process.jsl")
    open_file(jsl_path)

def open_box_plot_tool():
    """Open Box Plot analysis tool UI"""
    # Box Plot UI 已封存，此功能暫時停用
    messagebox.showinfo("功能停用", "Box Plot 功能已暫時停用")

def open_correlation_tool():
    """Open Correlation analysis tool"""
    # Check if configuration file exists
    jsl_path = resource_path("config/correlation_tool.jsl")
    if os.path.exists(jsl_path):
        open_file(jsl_path)
    else:
        messagebox.showinfo(
            MSG_TITLE_INFO, 
            MSG_NO_SCRIPT_TEMPLATE.format("Correlation", "scripts/jsl/correlation_tool.jsl")
        )

def open_user_guide():
    """Open user guide document"""
    guide_path = resource_path("docs/Data Analysis Tools SOP.pdf")
    open_file(guide_path)

def open_box_plot_lite():
    """Open Box Plot Lite analysis tool JSL script"""
    jsl_path = resource_path("config/box_plot_tool.jsl")
    open_file(jsl_path)

def open_quick_report():
    """Open Quick Report function"""
    from src.ui.quick_report_ui import open_quick_report_window
    open_quick_report_window()

def open_exclude_outliers():
    """Open Exclude Outliers JSL file"""
    jsl_path = resource_path("config/explore_outliers.jsl")
    if os.path.exists(jsl_path):
        open_file(jsl_path)
    else:
        messagebox.showinfo(
            MSG_TITLE_INFO, 
            MSG_NO_SCRIPT_TEMPLATE.format("Exclude Outliers", "scripts/jsl/explore_outliers.jsl")
        )

def select_data_file():
    """Select data file but don't open it"""
    root = Tk()
    root.withdraw()  # Hide main window
    filepath = filedialog.askopenfilename(
        title="Select Data File",
        filetypes=[(FILE_TYPE_JMP, FILE_EXT_JMP), (FILE_TYPE_ALL, FILE_EXT_ALL)]
    )
    root.destroy()
    return filepath

def open_data_file_and_update_ui(file_path_var, status_label, process_buttons):
    """Open data file and update UI status"""
    filepath = select_data_file()
    if filepath:
        # Open file
        open_file(filepath)
        # Update UI
        import os
        filename = os.path.basename(filepath)
        file_path_var.set(filepath)
        status_label.config(text=filename)
        # Enable process buttons
        for btn in process_buttons:
            btn.config(state="normal")
        print(f"Selected and opened file: {filepath}")
        return filepath
    else:
        print("No file selected")
        return None

def process_duplicate_with_file(file_path_var):
    """Execute Exclude Duplicate with specified file"""
    filepath = file_path_var.get()
    if not filepath:
        messagebox.showwarning("Warning", "Please select a data file first")
        return
    
    # Here we can pass file path to JSL script
    # Currently just open JSL file for manual operation
    jsl_path = resource_path("config/duplicate_process.jsl")
    open_file(jsl_path)

def process_spec_setup_with_file(file_path_var):
    """Execute Setup Spec with specified file"""
    filepath = file_path_var.get()
    if not filepath:
        messagebox.showwarning("Warning", "Please select a data file first")
        return
    
    # Call spec_setup function
    from src.ui.spec_setup_dialog import open_spec_setup
    open_spec_setup()

def process_outliers_with_file(file_path_var):
    """Execute Exclude Outlier with specified file"""
    filepath = file_path_var.get()
    if not filepath:
        messagebox.showwarning("Warning", "Please select a data file first")
        return
    
    # Open outliers JSL file
    jsl_path = resource_path("config/explore_outliers.jsl")
    if os.path.exists(jsl_path):
        open_file(jsl_path)
    else:
        messagebox.showinfo(
            MSG_TITLE_INFO, 
            MSG_NO_SCRIPT_TEMPLATE.format("Exclude Outliers", "scripts/jsl/explore_outliers.jsl")
        )

def on_extract(text_input):
    """Process JSL code extraction and integrate into JSL file
    Args:
        text_input (tk.Text): Text input box containing JSL code
    """
    input_text = text_input.get("1.0", tk.END)
    extracted = extract_process_variables(input_text)
    
    if extracted.startswith("Process Variables") or extracted.startswith("Unbalanced"):
        messagebox.showerror(MSG_TITLE_ERROR, extracted)
        return
        
    # Save to JSL file (use Beta path if available)
    save_result, file_path = save_jsl_with_vars(extracted, current_file_path_beta)
    
    # Display result message
    if "Successfully saved" in save_result:
        messagebox.showinfo(MSG_TITLE_SUCCESS, save_result)
        # Automatically open newly created file
        if file_path:
            open_file(file_path)
    elif "Save cancelled" in save_result:
        messagebox.showinfo(MSG_TITLE_NOTICE, save_result)
    else:
        messagebox.showerror(MSG_TITLE_ERROR, save_result) 

def open_normal_distribution():
    """Open Normal distribution JSL file"""
    jsl_path = resource_path("config/jmp_pc_report_generate_normal.jsl")
    if os.path.exists(jsl_path):
        open_file(jsl_path)
    else:
        messagebox.showinfo(
            MSG_TITLE_INFO, 
            MSG_NO_SCRIPT_TEMPLATE.format("Normal distribution", "scripts/jsl/jmp_pc_report_generate_normal.jsl")
        ) 

def open_file_jsl():
    """Open file selection JSL script"""
    jsl_path = resource_path("scripts/jsl/open_file.jsl")
    if os.path.exists(jsl_path):
        open_file(jsl_path)
    else:
        messagebox.showinfo(
            MSG_TITLE_INFO, 
            MSG_NO_SCRIPT_TEMPLATE.format("Open File", "scripts/jsl/open_file.jsl")
        )

def open_file_jsl_beta():
    """Open file selection dialog and track file path (Beta)"""
    global current_file_path_beta
    
    root = Tk()
    root.withdraw()  # 隱藏主視窗
    
    # 打開檔案選擇對話框（支援 CSV 和 JMP）
    file_path = filedialog.askopenfilename(
        title="Choose data file (Beta)",
        filetypes=[("CSV Files", "*.csv"), ("JMP Files", "*.jmp"), ("All Files", "*.*")]
    )
    
    if file_path:
        # 保存當前檔案路徑
        current_file_path_beta = file_path
        
        # 根據檔案類型決定開啟方式
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.jmp':
            # .jmp 檔案用系統預設方式開啟（通常已設定為 JMP）
            open_file(file_path)
        else:
            # 其他檔案（如 CSV）強制用 JMP 開啟
            open_with_jmp(file_path)

def open_best_fit_beta():
    """
    🔬 開啟 Best Fit(beta) 功能 - 多欄位 AICc 分布分析主入口
    
    📋 功能說明：
    這是 Best Fit(beta) 按鈕的主要處理函數，負責啟動整個分析流程
    
    🔄 處理流程：
    1. 顯示資料準備指引視窗
    2. 引導使用者處理 JMP 檔案 (如需要)
    3. 選擇 CSV/Excel 檔案進行分析
    4. 進行多欄位的 AICc Best Fit 計算
    5. 開啟 Process Capability 預覽對話框
    
    ✨ 特色功能：
    - 支援 JMP 檔案的無縫轉換流程
    - 多欄位同時分析，提高效率
    - 自動化的 AICc 計算和分布排序
    - 直觀的使用者引導介面
    
    🎯 呼叫時機：
    當使用者點擊主介面的 "Best Fit(beta)" 按鈕時觸發
    
    🔗 主要調用函數：
    - show_jmp_data_preparation_guide(): 顯示資料準備指引
    - continue_best_fit_beta_analysis(): 繼續 CSV/Excel 分析
    
    ⚠️ 錯誤處理：
    捕捉所有異常並顯示使用者友善的錯誤訊息
    """
    try:
        # 步驟 0: 先顯示 JMP 資料準備指引
        # 這個指引會說明整個分析流程，並提供 JMP 檔案轉換選項
        show_jmp_data_preparation_guide()
        
    except Exception as e:
        messagebox.showerror("錯誤", f"開啟 Best Fit(beta) 失敗: {str(e)}")

def show_jmp_data_preparation_guide():
    """
    📋 顯示 JMP 資料準備指引視窗
    
    📋 功能說明：
    為使用者提供完整的資料準備指引，支援 JMP 檔案轉換和 CSV/Excel 直接分析
    
    🎯 主要目的：
    1. 説明整個 Best Fit(beta) 分析流程
    2. 提供 JMP 檔案轉 CSV 的詳細步驟
    3. 讓使用者選擇合適的分析路徑
    4. 確保資料品質符合分析要求
    
    🖥️ UI 元件：
    - 流程說明文字和圖示
    - "開啟 JSL 腳本" 按鈕：啟動 JMP 資料匯出
    - "選擇檔案進行分析" 按鈕：直接分析 CSV/Excel
    - 詳細的步驟指導和注意事項
    
    🔄 使用者流程：
    情境 1 - JMP 檔案：
      1. 點擊 "開啟 JSL 腳本"
      2. 在 JMP 中執行匯出腳本
      3. 獲得不含排除資料的 CSV 檔案
      4. 點擊 "選擇檔案進行分析" 選取 CSV
    
    情境 2 - CSV/Excel 檔案：
      1. 直接點擊 "選擇檔案進行分析"
      2. 選取現有的 CSV 或 Excel 檔案
    
    💡 設計理念：
    採用引導式介面，降低使用門檻，確保不同背景的使用者都能順利完成分析
    
    🔗 調用的函數：
    - open_jsl_script(): 開啟 JSL 匯出腳本
    - continue_best_fit_beta_analysis(): 繼續檔案分析流程
    """
    try:
        # 創建指引視窗
        guide_window = tk.Toplevel()
        guide_window.title("Best Fit(beta) - 資料準備")
        guide_window.geometry("700x600")
        guide_window.grab_set()  # 設為模態視窗
        
        # 標題
        title_label = tk.Label(guide_window, 
                              text="Best Fit(beta) - 資料準備步驟", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=15)
        
        # 說明文字
        info_text = """🎯 Best Fit(beta) 需要使用乾淨的 CSV 資料進行分析

📋 請按照以下步驟準備您的資料：

🔧 步驟 1: 在 JMP 中準備資料
• 確保您已在 JMP 中完成所有資料處理：
  - Exclude Duplicate（排除重複資料）
  - Setup Spec（設定規格）  
  - Exclude Outlier（排除異常值）
• 確認所有不需要的資料列已標記為 excluded（🚫 符號）

📤 步驟 2: 執行 JSL 腳本匯出乾淨資料
• 點擊下方「開啟 JSL 腳本」按鈕
• 在 JMP 中執行該腳本
• 腳本會自動匯出不含 excluded 資料的 CSV 檔案

✅ 步驟 3: 繼續 Best Fit(beta) 分析
• CSV 檔案匯出完成後，點擊「繼續分析」按鈕
• 選擇剛匯出的 CSV 檔案進行 AICc 分析

💡 為什麼需要這樣做？
• 確保分析結果的準確性
• 與 JMP 的資料處理邏輯完全一致
• 避免被排除的資料影響分析結果"""
        
        info_label = tk.Label(guide_window, 
                             text=info_text,
                             font=("Arial", 11),
                             justify="left",
                             anchor="nw")
        info_label.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 按鈕框架
        button_frame = tk.Frame(guide_window)
        button_frame.pack(pady=15)
        
        # 開啟 JSL 腳本按鈕
        def open_jsl_script():
            try:
                jsl_path = resource_path("scripts/jsl/export_non_excluded_data.jsl")
                open_file(jsl_path)
            except Exception as e:
                messagebox.showerror("錯誤", f"開啟 JSL 腳本失敗: {str(e)}")
        
        jsl_btn = tk.Button(button_frame, 
                           text="📄 開啟 JSL 腳本", 
                           font=("Arial", 12, "bold"), 
                           command=open_jsl_script,
                           width=20)
        jsl_btn.pack(side=tk.LEFT, padx=10)
        
        # 繼續分析按鈕
        def continue_analysis():
            guide_window.destroy()
            # 繼續原本的 Best Fit(beta) 流程
            continue_best_fit_beta_analysis()
        
        continue_btn = tk.Button(button_frame, 
                               text="✅ 繼續分析", 
                               font=("Arial", 12, "bold"), 
                               command=continue_analysis,
                               width=20)
        continue_btn.pack(side=tk.LEFT, padx=10)
        
        # 取消按鈕
        cancel_btn = tk.Button(button_frame, 
                             text="取消", 
                             font=("Arial", 12), 
                             command=guide_window.destroy,
                             width=15)
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
    except Exception as e:
        messagebox.showerror("錯誤", f"顯示資料準備指引失敗: {str(e)}")

def continue_best_fit_beta_analysis():
    """繼續 Best Fit(beta) 的原始分析流程"""
    try:
        # 步驟1: 選擇檔案（現在應該是 CSV 檔案）
        file_path = filedialog.askopenfilename(
            title="選擇匯出的 CSV 檔案",
            filetypes=[
                ("CSV 檔案", "*.csv"),
                ("Excel 檔案", "*.xlsx *.xls"),
                ("所有檔案", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        # 原始的 Best Fit(beta) 流程從這裡繼續...
        # [這裡會包含所有原本的檔案載入和分析邏輯]
        process_best_fit_beta_file(file_path)
        
    except Exception as e:
        messagebox.showerror("錯誤", f"繼續 Best Fit(beta) 分析失敗: {str(e)}")

def process_best_fit_beta_file(file_path):
    """處理 Best Fit(beta) 的檔案分析流程"""
    try:
        # 步驟2: 載入檔案
        try:
            if file_path.endswith(('.xlsx', '.xls')):
                data = pd.read_excel(file_path)
            elif file_path.endswith('.csv'):
                data = pd.read_csv(file_path)
            else:
                messagebox.showerror("錯誤", "不支援的檔案格式\n支援格式: Excel (.xlsx, .xls), CSV (.csv)")
                return
        except Exception as e:
            messagebox.showerror("錯誤", f"載入檔案失敗: {str(e)}")
            return
        
        # 步驟3: 獲取數值欄位
        numeric_columns = []
        for col in data.columns:
            if pd.api.types.is_numeric_dtype(data[col]):
                numeric_columns.append(col)
        
        if not numeric_columns:
            messagebox.showerror("錯誤", "檔案中沒有找到數值欄位")
            return
        
        # 步驟4: 創建欄位選擇視窗
        selection_window = tk.Toplevel()
        selection_window.title("選擇要分析的欄位")
        selection_window.geometry("500x400")
        selection_window.grab_set()  # 設為模態視窗
        
        # 標題
        title_label = tk.Label(selection_window, 
                              text="Best Fit(beta) - 多欄位 AICc 分析", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # 檔案資訊
        info_label = tk.Label(selection_window, 
                             text=f"檔案: {os.path.basename(file_path)}\n"
                                  f"資料形狀: {data.shape}\n"
                                  f"可用數值欄位: {len(numeric_columns)} 個",
                             font=("Arial", 10))
        info_label.pack(pady=5)
        
        # 說明
        instruction_label = tk.Label(selection_window, 
                                   text="請選擇要分析的欄位 (可多選):",
                                   font=("Arial", 11, "bold"))
        instruction_label.pack(pady=(10, 2))
        
        # 操作說明
        usage_label = tk.Label(selection_window, 
                             text="📖 操作方式: 滑鼠拖拽選擇 | Shift+點擊範圍選擇 | Ctrl/Cmd+點擊多選",
                             font=("Arial", 9), 
                             fg="gray")
        usage_label.pack(pady=(0, 8))
        
        # 欄位選擇列表框 - 改用 EXTENDED 模式支援 Shift 範圍選擇
        listbox_frame = tk.Frame(selection_window)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        listbox = Listbox(listbox_frame, selectmode=tk.EXTENDED, height=10)
        scrollbar = Scrollbar(listbox_frame)
        
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        
        # 添加欄位到列表框
        for col in numeric_columns:
            listbox.insert(tk.END, col)
        
        # 添加滑鼠拖拽多選功能
        def on_drag_select(event):
            """滑鼠拖拽選擇功能"""
            try:
                # 獲取當前滑鼠位置對應的項目索引
                current_index = listbox.nearest(event.y)
                
                # 如果沒有開始拖拽，記錄起始位置
                if not hasattr(on_drag_select, 'start_index'):
                    on_drag_select.start_index = current_index
                
                # 清除目前選擇
                listbox.selection_clear(0, tk.END)
                
                # 選擇範圍
                start = min(on_drag_select.start_index, current_index)
                end = max(on_drag_select.start_index, current_index)
                
                for i in range(start, end + 1):
                    listbox.selection_set(i)
                    
            except Exception:
                pass
        
        def on_drag_start(event):
            """開始拖拽"""
            on_drag_select.start_index = listbox.nearest(event.y)
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(on_drag_select.start_index)
        
        def on_drag_end(event):
            """結束拖拽"""
            if hasattr(on_drag_select, 'start_index'):
                del on_drag_select.start_index
        
        # 綁定滑鼠事件
        listbox.bind("<Button-1>", on_drag_start)
        listbox.bind("<B1-Motion>", on_drag_select)
        listbox.bind("<ButtonRelease-1>", on_drag_end)
        
        # 按鈕框架
        button_frame = tk.Frame(selection_window)
        button_frame.pack(pady=10)
        
        def calculate_selected_columns():
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showerror("錯誤", "請選擇至少一個欄位")
                return
            
            selected_columns = [numeric_columns[i] for i in selected_indices]
            selection_window.destroy()
            
            # 開始計算
            calculate_multiple_aicc(data, selected_columns, file_path)
        
        def select_all():
            listbox.select_set(0, tk.END)
        
        def clear_selection():
            listbox.selection_clear(0, tk.END)
        
        # 按鈕
        select_all_btn = tk.Button(button_frame, text="全選", command=select_all)
        select_all_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(button_frame, text="清除選擇", command=clear_selection)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        calculate_btn = tk.Button(button_frame, text="開始計算 AICc", 
                                 command=calculate_selected_columns,
                                 font=("Arial", 12, "bold"))
        calculate_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(button_frame, text="取消", 
                              command=selection_window.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
    except Exception as e:
        messagebox.showerror("錯誤", f"處理 Best Fit(beta) 檔案失敗: {str(e)}")

def calculate_multiple_aicc(data, selected_columns, file_path):
    """計算多個欄位的 AICc 值並顯示結果"""
    try:
        # 導入 AICc 計算器
        from src.core.distribution_fitter import AICcCalculator
        
        # 創建結果視窗
        result_window = tk.Toplevel()
        result_window.title("AICc 計算結果")
        result_window.geometry("900x700")
        
        # 標題
        title_label = tk.Label(result_window, 
                              text="Best Fit(beta) - AICc 計算結果", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 檔案資訊
        info_label = tk.Label(result_window, 
                             text=f"檔案: {os.path.basename(file_path)}\n"
                                  f"分析欄位數量: {len(selected_columns)} 個",
                             font=("Arial", 10))
        info_label.pack(pady=5)
        
        # 結果顯示區域
        result_frame = tk.Frame(result_window)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        result_text = tk.Text(result_frame, wrap=tk.WORD, font=("Consolas", 10))
        result_scrollbar = tk.Scrollbar(result_frame)
        
        result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        result_text.config(yscrollcommand=result_scrollbar.set)
        result_scrollbar.config(command=result_text.yview)
        
        # 進度顯示
        progress_label = tk.Label(result_window, text="正在計算...", font=("Arial", 10))
        progress_label.pack(pady=5)
        
        # 計算器初始化
        calculator = AICcCalculator()
        
        result_text.insert(tk.END, "="*80 + "\n")
        result_text.insert(tk.END, "AICc 分布配適計算器 - 多欄位分析結果\n")
        result_text.insert(tk.END, "="*80 + "\n\n")
        result_text.insert(tk.END, f"檔案: {os.path.basename(file_path)}\n")
        result_text.insert(tk.END, f"分析時間: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        all_results = {}
        
        # 對每個選中的欄位計算 AICc
        for i, column_name in enumerate(selected_columns):
            progress_label.config(text=f"正在計算 {column_name} ({i+1}/{len(selected_columns)})...")
            result_window.update()
            
            try:
                # 提取欄位數據
                column_data = data[column_name].dropna()
                
                if len(column_data) < 3:
                    result_text.insert(tk.END, f"[{column_name}] 數據點太少，跳過分析\n\n")
                    continue
                
                result_text.insert(tk.END, f"【欄位: {column_name}】\n")
                result_text.insert(tk.END, f"數據點數量: {len(column_data)}\n")
                result_text.insert(tk.END, f"平均值: {column_data.mean():.6f}\n")
                result_text.insert(tk.END, f"標準差: {column_data.std():.6f}\n")
                result_text.insert(tk.END, f"範圍: {column_data.min():.6f} 到 {column_data.max():.6f}\n")
                result_text.insert(tk.END, "-" * 50 + "\n")
                
                # 計算所有分布的 AICc
                results = calculator.calculate_all_distributions(column_data, column_name)
                
                # 排序結果
                sorted_results = sorted([(name, aicc) for name, aicc in results.items() 
                                       if np.isfinite(aicc)], key=lambda x: x[1])
                
                if sorted_results:
                    all_results[column_name] = sorted_results
                    
                    for j, (dist_name, aicc) in enumerate(sorted_results):
                        rank_symbol = "🥇" if j == 0 else "🥈" if j == 1 else "🥉" if j == 2 else f"{j+1:2d}."
                        result_text.insert(tk.END, f"{rank_symbol} {dist_name:20s}: AICc = {aicc:10.3f}\n")
                    
                    best_name, best_aicc = sorted_results[0]
                    result_text.insert(tk.END, f"\n✅ 最佳分布: {best_name} (AICc = {best_aicc:.3f})\n")
                    
                    # 特殊提示
                    if "GAMMA" in column_name.upper():
                        result_text.insert(tk.END, f"💡 注意: GAMMA 欄位已自動應用 JMP 修正邏輯\n")
                else:
                    result_text.insert(tk.END, f"❌ 無法計算任何分布的 AICc 值\n")
                
                result_text.insert(tk.END, "\n" + "="*50 + "\n\n")
                result_text.update()
                
            except Exception as e:
                result_text.insert(tk.END, f"❌ 計算 {column_name} 時發生錯誤: {str(e)}\n\n")
        
        # 顯示總結
        if all_results:
            result_text.insert(tk.END, "🏆 各欄位最佳分布總結:\n")
            result_text.insert(tk.END, "="*60 + "\n")
            
            for column_name, sorted_results in all_results.items():
                if sorted_results:
                    best_name, best_aicc = sorted_results[0]
                    result_text.insert(tk.END, f"{column_name:25s} → {best_name:15s} (AICc = {best_aicc:8.3f})\n")
            
            result_text.insert(tk.END, "="*60 + "\n")
        
        progress_label.config(text="計算完成！")
        
        # 收集最佳分布資訊用於JSL生成
        best_distributions = {}
        if all_results:
            for column_name, sorted_results in all_results.items():
                if sorted_results:
                    best_name, _ = sorted_results[0]
                    best_distributions[column_name] = best_name
        
        # 儲存按鈕
        def save_results():
            try:
                save_path = filedialog.asksaveasfilename(
                    title="儲存結果",
                    defaultextension=".txt",
                    filetypes=[("文字檔案", "*.txt"), ("所有檔案", "*.*")]
                )
                
                if save_path:
                    with open(save_path, 'w', encoding='utf-8') as f:
                        f.write(result_text.get("1.0", tk.END))
                    messagebox.showinfo("成功", f"結果已儲存到: {save_path}")
            except Exception as e:
                messagebox.showerror("錯誤", f"儲存失敗: {str(e)}")
        
        # 生成JSL檔案
        def generate_jsl():
            try:
                if not best_distributions:
                    messagebox.showerror("錯誤", "沒有找到最佳分布資訊")
                    return
                
                # 顯示即將生成的JSL變數
                jsl_preview = generate_jsl_vars_string(best_distributions)
                
                # 確認對話框
                confirm_msg = f"即將生成JSL檔案到資料檔案同個目錄，變數設定如下：\n\n{jsl_preview}\n\n是否繼續？"
                if messagebox.askyesno("確認生成JSL", confirm_msg):
                    # 生成JSL檔案（傳入原始資料檔案路徑）
                    output_path = update_jsl_file_with_best_distributions(best_distributions, file_path)
                    
                    # 顯示成功訊息
                    result_msg = f"JSL檔案已生成到資料檔案同個目錄：\n{output_path}\n\n是否要開啟該檔案？"
                    if messagebox.askyesno("成功", result_msg):
                        # 開啟JSL檔案
                        open_file(output_path)
                    
            except Exception as e:
                messagebox.showerror("錯誤", f"生成JSL檔案失敗: {str(e)}")
        
        # 按鈕框架
        button_frame = tk.Frame(result_window)
        button_frame.pack(pady=10)
        
        save_btn = tk.Button(button_frame, text="儲存結果", command=save_results,
                            font=("Arial", 12))
        save_btn.pack(side=tk.LEFT, padx=10)
        
        # 只有在有結果時才顯示生成JSL按鈕
        if best_distributions:
            generate_jsl_btn = tk.Button(button_frame, text="生成JSL檔案", 
                                       command=generate_jsl,
                                       font=("Arial", 12, "bold"))
            generate_jsl_btn.pack(side=tk.LEFT, padx=10)
        
        close_btn = tk.Button(button_frame, text="關閉", command=result_window.destroy,
                             font=("Arial", 12))
        close_btn.pack(side=tk.LEFT, padx=10)
        
    except Exception as e:
        messagebox.showerror("錯誤", f"計算過程發生錯誤: {str(e)}")

def load_jmp_file(file_path):
    """嘗試讀取JMP檔案，使用多種方法"""
    
    # 方法1: 嘗試使用JMPReader庫
    try:
        import sys
        import os
        
        # 嘗試導入JMPReader
        try:
            from src.utils import jmptools
            print(f"使用JMPReader讀取JMP檔案: {file_path}")
            
            # 使用JMPReader讀取 (返回: status_code, error_message, dataframe)
            status, message, df = jmptools.readjmp(file_path)
            
            if status == 0 and df is not None:
                print("✅ JMP檔案讀取成功")
                return df
            else:
                print(f"❌ JMP檔案讀取失敗: {message}")
            
        except ImportError:
            print("JMPReader未安裝，嘗試其他方法...")
        except Exception as e:
            print(f"JMPReader讀取失敗: {e}，嘗試其他方法...")
    except Exception as e:
        print(f"JMPReader方法失敗: {e}")
    
    # 方法2: 嘗試使用JMP 18內建Python支援
    try:
        import jmp
        print(f"使用JMP 18內建Python支援讀取: {file_path}")
        
        # 使用JMP內建功能讀取
        dt = jmp.open(file_path)
        
        # 轉換為pandas DataFrame
        df = pd.DataFrame()
        for idx in range(len(dt)):
            col_data = []
            for i in range(dt.nrows):
                col_data.append(dt[idx][i])
            df[dt[idx].name] = col_data
        
        dt.close(save=False)
        return df
        
    except ImportError:
        print("JMP 18內建Python支援不可用...")
    except Exception as e:
        print(f"JMP 18方法失敗: {e}")
    
    # 方法3: 提供手動轉換建議
    messagebox.showwarning(
        "JMP檔案讀取需要協助", 
        "JMP檔案讀取功能有版本限制。建議解決方法：\n\n"
        "📁 最簡單的方法：\n"
        "1. 在JMP軟體中開啟該檔案\n"
        "2. 選擇 檔案 → 匯出 → Excel檔案 或 CSV檔案\n"
        "3. 使用匯出的檔案重新分析\n\n"
        "🔧 技術限制：\n"
        "• JMPReader庫僅支援JMP 11版本\n"
        "• JMP 18 Python整合需要JMP軟體環境\n"
        "• 較新的JMP檔案格式可能不相容\n\n"
        "✅ 完全支援的格式：\n"
        "• Excel (.xlsx, .xls)\n"
        "• CSV (.csv)\n"
        "• JMP 11版本檔案 (.jmp)\n\n"
        "轉換後您就可以享受完整的多欄位AICc分析功能！"
    )
    
    return None

def convert_distribution_to_jsl(dist_name):
    """將分布名稱轉換為JSL格式"""
    conversion_map = {
        "Normal": "Normal",
        "LogNormal": "Lognormal", 
        "Exponential": "Exponential",
        "Gamma": "Gamma",
        "Weibull": "Weibull",
        "Johnson Sb": "Johnson",
        "SHASH": "Normal",  # SHASH在JSL中可能不直接支援，暫用Normal
        "Mixture of 2 Normals": "Normal",  # 混合分布暫用Normal
        "Mixture of 3 Normals": "Normal"   # 混合分布暫用Normal
    }
    return conversion_map.get(dist_name, "Normal")

def generate_jsl_vars_string(best_distributions):
    """生成JSL變數字串"""
    jsl_vars = []
    
    for column_name, dist_name in best_distributions.items():
        jsl_dist = convert_distribution_to_jsl(dist_name)
        jsl_var = f":{column_name} & Dist( {jsl_dist} )"
        jsl_vars.append(jsl_var)
    
    # 組合成JSL格式
    if jsl_vars:
        vars_string = "myVars = {\n\t" + ",\n\t".join(jsl_vars) + "\n};"
    else:
        vars_string = "myVars = {\n\t:Variable_A\n};"
    
    return vars_string

def update_jsl_file_with_best_distributions(best_distributions, data_file_path, output_path=None):
    """更新JSL檔案中的myVars設定"""
    try:
        # 讀取原始JSL檔案
        jsl_template_path = "scripts/jsl/jmp_pc_report_generate_best_fit.jsl"
        
        with open(jsl_template_path, 'r', encoding='utf-8') as f:
            jsl_content = f.read()
        
        # 生成新的變數字串
        new_vars_string = generate_jsl_vars_string(best_distributions)
        
        # 找到並替換myVars部分
        lines = jsl_content.split('\n')
        start_idx = -1
        end_idx = -1
        
        for i, line in enumerate(lines):
            if 'myVars = {' in line:
                start_idx = i
            elif start_idx != -1 and '};' in line:
                end_idx = i
                break
        
        if start_idx != -1 and end_idx != -1:
            # 替換myVars部分
            new_lines = lines[:start_idx] + new_vars_string.split('\n') + lines[end_idx+1:]
            new_content = '\n'.join(new_lines)
            
            # 決定輸出路徑 - 儲存到原始資料檔案的同個目錄
            if output_path is None:
                import datetime
                # 取得原始檔案的目錄
                data_dir = os.path.dirname(data_file_path)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"jmp_pc_report_best_fit_{timestamp}.jsl"
                output_path = os.path.join(data_dir, filename)
            
            # 寫入新檔案
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return output_path
        else:
            raise Exception("無法找到myVars定義區塊")
            
    except Exception as e:
        raise Exception(f"更新JSL檔案失敗: {str(e)}")

# === Google Drive 檔案處理功能 ===

def extract_google_drive_file_id(url):
    """從 Google Drive URL 中提取檔案 ID"""
    patterns = [
        r'/file/d/([a-zA-Z0-9-_]+)',  # https://drive.google.com/file/d/FILE_ID/view
        r'id=([a-zA-Z0-9-_]+)',       # https://drive.google.com/open?id=FILE_ID
        r'/d/([a-zA-Z0-9-_]+)/'       # 其他格式
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def download_google_drive_file(url, target_dir=None):
    """下載 Google Drive 檔案到本地"""
    try:
        import gdown
        
        # 提取檔案 ID
        file_id = extract_google_drive_file_id(url)
        if not file_id:
            raise Exception("無法從 URL 中提取 Google Drive 檔案 ID")
        
        # 設定下載目錄
        if target_dir is None:
            target_dir = tempfile.gettempdir()
        
        # 創建下載 URL
        download_url = f"https://drive.google.com/uc?id={file_id}"
        
        # 指定完整的輸出檔案路徑
        output_filename = f"google_drive_{file_id}.csv"
        output_path = os.path.join(target_dir, output_filename)
        
        # 下載檔案
        print(f"正在下載 Google Drive 檔案 (ID: {file_id})...")
        downloaded_file = gdown.download(download_url, output=output_path, quiet=False)
        
        if downloaded_file and os.path.exists(output_path):
            print(f"✅ 檔案下載成功: {output_path}")
            return output_path
        else:
            raise Exception("檔案下載失敗或檔案不存在")
            
    except ImportError:
        raise Exception("請先安裝 gdown 套件: pip install gdown")
    except Exception as e:
        raise Exception(f"下載 Google Drive 檔案失敗: {str(e)}")

def open_google_drive_file():
    """開啟 Google Drive 檔案的對話框"""
    try:
        # 創建輸入對話框
        input_window = tk.Toplevel()
        input_window.title("開啟 Google Drive 檔案")
        input_window.geometry("600x400")
        input_window.grab_set()  # 設為模態視窗
        
        # 標題
        title_label = tk.Label(input_window, 
                              text="Google Drive 檔案連接器", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 說明
        info_text = """
請輸入 Google Drive 檔案連結：

支援的連結格式：
• https://drive.google.com/file/d/FILE_ID/view?usp=sharing
• https://drive.google.com/file/d/FILE_ID/view?usp=drive_link
• https://drive.google.com/open?id=FILE_ID

注意事項：
• 請確保檔案已設定為「任何人都可以檢視」
• 支援的檔案格式：Excel (.xlsx, .xls), CSV (.csv), JMP (.jmp)
• 檔案將會下載到暫存目錄後開啟
        """
        
        info_label = tk.Label(input_window, text=info_text.strip(), 
                             font=("Arial", 10), justify=tk.LEFT)
        info_label.pack(pady=10, padx=20)
        
        # URL 輸入框
        url_label = tk.Label(input_window, text="Google Drive 檔案連結:", 
                            font=("Arial", 12, "bold"))
        url_label.pack(pady=(10, 5))
        
        url_entry = tk.Entry(input_window, width=80, font=("Arial", 10))
        url_entry.pack(pady=5, padx=20)
        
        # ⛔ 不預填任何真實連結:那會把某個人的雲端檔印在公開的程式碼裡,
        #    而且下一個使用者要的是自己的檔,不是別人的。放格式範例就好。
        url_entry.insert(0, "https://drive.google.com/file/d/FILE_ID/view?usp=sharing")
        
        # 狀態標籤
        status_label = tk.Label(input_window, text="", font=("Arial", 10))
        status_label.pack(pady=5)
        
        # 處理函數
        def process_google_drive_file():
            url = url_entry.get().strip()
            if not url:
                messagebox.showerror("錯誤", "請輸入 Google Drive 檔案連結")
                return
            
            try:
                status_label.config(text="正在下載檔案...", fg="blue")
                input_window.update()
                
                # 下載檔案到專案 temp 目錄
                target_dir = os.path.join(os.getcwd(), 'temp')
                os.makedirs(target_dir, exist_ok=True)  # 確保目錄存在
                downloaded_path = download_google_drive_file(url, target_dir)
                
                status_label.config(text="檔案下載完成，正在開啟...", fg="green")
                input_window.update()
                
                # 判斷檔案類型並開啟
                file_extension = os.path.splitext(downloaded_path)[1].lower()
                
                if file_extension == '.jmp':
                    # JMP 檔案用 JMP 開啟
                    open_with_jmp(downloaded_path)
                else:
                    # 其他檔案用系統預設方式開啟
                    open_file(downloaded_path)
                
                # 顯示成功訊息
                rel_path = os.path.relpath(downloaded_path, os.getcwd())
                success_msg = f"✅ Google Drive 檔案已成功開啟！\n\n"
                success_msg += f"檔案已下載到: {rel_path}\n"
                success_msg += f"完整路徑: {downloaded_path}\n"
                success_msg += f"檔案類型: {file_extension}\n\n"
                success_msg += "您現在可以在 JMP 或其他應用程式中使用這個檔案。"
                
                messagebox.showinfo("成功", success_msg)
                input_window.destroy()
                
            except Exception as e:
                status_label.config(text="下載失敗", fg="red")
                messagebox.showerror("錯誤", f"處理 Google Drive 檔案時發生錯誤:\n{str(e)}")
        
        def analyze_with_best_fit():
            """直接用 Best Fit 分析 Google Drive 檔案"""
            url = url_entry.get().strip()
            if not url:
                messagebox.showerror("錯誤", "請輸入 Google Drive 檔案連結")
                return
            
            try:
                status_label.config(text="正在下載檔案進行分析...", fg="blue")
                input_window.update()
                
                # 下載檔案到專案 temp 目錄
                target_dir = os.path.join(os.getcwd(), 'temp')
                os.makedirs(target_dir, exist_ok=True)  # 確保目錄存在
                downloaded_path = download_google_drive_file(url, target_dir)
                
                # 關閉輸入視窗
                input_window.destroy()
                
                # 直接呼叫 Best Fit 分析，傳入下載的檔案路徑
                status_label.config(text="開始 Best Fit 分析...", fg="green")
                
                # 載入檔案進行分析
                try:
                    if downloaded_path.endswith(('.xlsx', '.xls')):
                        data = pd.read_excel(downloaded_path)
                    elif downloaded_path.endswith('.csv'):
                        data = pd.read_csv(downloaded_path)
                    elif downloaded_path.endswith('.jmp'):
                        data = load_jmp_file(downloaded_path)
                        if data is None:
                            return
                    else:
                        messagebox.showerror("錯誤", "不支援的檔案格式")
                        return
                except Exception as e:
                    messagebox.showerror("錯誤", f"載入檔案失敗: {str(e)}")
                    return
                
                # 獲取數值欄位
                numeric_columns = []
                for col in data.columns:
                    if pd.api.types.is_numeric_dtype(data[col]):
                        numeric_columns.append(col)
                
                if not numeric_columns:
                    messagebox.showerror("錯誤", "檔案中沒有找到數值欄位")
                    return
                
                # 直接進行多欄位選擇和分析
                create_column_selection_window(data, numeric_columns, downloaded_path)
                
            except Exception as e:
                status_label.config(text="處理失敗", fg="red")
                messagebox.showerror("錯誤", f"處理 Google Drive 檔案時發生錯誤:\n{str(e)}")
        
        # 按鈕框架
        button_frame = tk.Frame(input_window)
        button_frame.pack(pady=20)
        
        download_btn = tk.Button(button_frame, text="下載並開啟檔案", 
                               command=process_google_drive_file,
                               font=("Arial", 12, "bold"))
        download_btn.pack(side=tk.LEFT, padx=10)
        
        analyze_btn = tk.Button(button_frame, text="直接進行 Best Fit 分析", 
                              command=analyze_with_best_fit,
                              font=("Arial", 12, "bold"))
        analyze_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(button_frame, text="取消", 
                              command=input_window.destroy,
                              font=("Arial", 12))
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # 設定焦點到輸入框
        url_entry.focus()
        url_entry.select_range(0, tk.END)
        
    except Exception as e:
        messagebox.showerror("錯誤", f"開啟 Google Drive 檔案對話框失敗: {str(e)}")

def create_column_selection_window(data, numeric_columns, file_path):
    """創建欄位選擇視窗（從 open_best_fit_beta 分離出來）"""
    # 創建欄位選擇視窗
    selection_window = tk.Toplevel()
    selection_window.title("選擇要分析的欄位")
    selection_window.geometry("500x400")
    selection_window.grab_set()  # 設為模態視窗
    
    # 標題
    title_label = tk.Label(selection_window, 
                          text="Best Fit - 多欄位 AICc 分析", 
                          font=("Arial", 14, "bold"))
    title_label.pack(pady=10)
    
    # 檔案資訊
    info_label = tk.Label(selection_window, 
                         text=f"檔案: {os.path.basename(file_path)}\n"
                              f"資料形狀: {data.shape}\n"
                              f"可用數值欄位: {len(numeric_columns)} 個",
                         font=("Arial", 10))
    info_label.pack(pady=5)
    
    # 說明
    instruction_label = tk.Label(selection_window, 
                               text="請選擇要分析的欄位 (可多選):",
                               font=("Arial", 11, "bold"))
    instruction_label.pack(pady=(10, 5))
    
    # 欄位選擇列表框
    listbox_frame = tk.Frame(selection_window)
    listbox_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    listbox = Listbox(listbox_frame, selectmode=MULTIPLE, height=10)
    scrollbar = Scrollbar(listbox_frame)
    
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    
    # 添加欄位到列表框
    for col in numeric_columns:
        listbox.insert(tk.END, col)
    
    # 按鈕框架
    button_frame = tk.Frame(selection_window)
    button_frame.pack(pady=10)
    
    def calculate_selected_columns():
        selected_indices = listbox.curselection()
        if not selected_indices:
            messagebox.showerror("錯誤", "請選擇至少一個欄位")
            return
        
        selected_columns = [numeric_columns[i] for i in selected_indices]
        selection_window.destroy()
        
        # 開始計算
        calculate_multiple_aicc(data, selected_columns, file_path)
    
    def select_all():
        listbox.select_set(0, tk.END)
    
    def clear_selection():
        listbox.selection_clear(0, tk.END)
    
    # 按鈕
    select_all_btn = tk.Button(button_frame, text="全選", command=select_all)
    select_all_btn.pack(side=tk.LEFT, padx=5)
    
    clear_btn = tk.Button(button_frame, text="清除選擇", command=clear_selection)
    clear_btn.pack(side=tk.LEFT, padx=5)
    
    calculate_btn = tk.Button(button_frame, text="開始計算 AICc", 
                             command=calculate_selected_columns,
                             font=("Arial", 12, "bold"))
    calculate_btn.pack(side=tk.LEFT, padx=10)
    
    cancel_btn = tk.Button(button_frame, text="取消", 
                          command=selection_window.destroy)
    cancel_btn.pack(side=tk.LEFT, padx=5) 

def create_report_generate_popup():
    """創建 Report Generate 彈出視窗"""
    try:
        # 創建彈出視窗
        popup = tk.Toplevel()
        popup.title("Report Generate - Best Fit")
        popup.geometry("700x500")
        popup.grab_set()  # 設為模態視窗
        
        # 標題
        title_label = tk.Label(popup, 
                              text="Process capability best fit distribution report generator", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=15)
        
        # Step 1: Select analysis items
        step1_frame = tk.Frame(popup)
        step1_frame.pack(pady=10)
        
        def open_original_best_fit():
            try:
                jsl_path = resource_path("scripts/jsl/best_fit_distribution.jsl")
                open_file(jsl_path)
            except Exception as e:
                messagebox.showerror("錯誤", f"打開 Best Fit 功能失敗: {str(e)}")
        
        step1_btn = tk.Button(step1_frame, 
                             text="Step 1. Select analysis items", 
                             font=("Arial", 11), 
                             command=open_original_best_fit,
                             width=25)
        step1_btn.pack()
        
        # Step 2: JSL code input area
        step2_label = tk.Label(popup, 
                              text="Step 2. Copy and paste jsl code below here", 
                              font=("Arial", 12))
        step2_label.pack(pady=(20, 10))
        
        # JSL 文字輸入框 - 簡化設計，移除 LabelFrame
        text_input = tk.Text(popup, height=12, width=70, 
                           font=("Consolas", 11),
                           wrap=tk.WORD,
                           bd=2, 
                           relief="sunken")
        text_input.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))
        
        # Step 3: Generate button
        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10)
        
        # 生成報告按鈕
        def generate_report():
            try:
                # 使用現有的 on_extract 函數
                on_extract(text_input)
            except Exception as e:
                messagebox.showerror("錯誤", f"生成報告失敗: {str(e)}")
        
        generate_btn = tk.Button(button_frame, 
                               text="Generate Best fit result", 
                               font=("Arial", 11), 
                               command=generate_report,
                               width=22)
        generate_btn.pack()
        
        # 讓文字輸入框獲得焦點
        text_input.focus_set()
        
    except Exception as e:
        messagebox.showerror("錯誤", f"創建 Report Generate 視窗失敗: {str(e)}")

def show_jmp_conversion_guide():
    """顯示 JMP 檔案轉換指引"""
    try:
        # 創建指引視窗
        guide_window = tk.Toplevel()
        guide_window.title("JMP 資料轉換指引")
        guide_window.geometry("600x500")
        guide_window.grab_set()  # 設為模態視窗
        
        # 標題
        title_label = tk.Label(guide_window, 
                              text="JMP 資料準備指引", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=15)
        
        # 說明文字
        info_text = """為了確保分析準確性，Best Fit(beta) 需要使用不包含被排除資料的 CSV 檔案。

請按照以下步驟準備您的資料：

🔧 步驟 1: 在 JMP 中執行 JSL 腳本
• 在 JMP 中開啟您的資料檔案
• 確認已正確標記要排除的資料列（🚫 符號）
• 執行下方的 JSL 腳本來匯出乾淨的 CSV 檔案

📁 步驟 2: 重新選擇檔案
• JSL 腳本會自動匯出 CSV 檔案到桌面
• 返回 Best Fit(beta) 重新選擇剛匯出的 CSV 檔案

✅ 優點：
• 只包含未被排除的資料
• 確保分析結果準確性
• 與 JMP 的資料處理邏輯一致"""
        
        info_label = tk.Label(guide_window, 
                             text=info_text,
                             font=("Arial", 11),
                             justify="left",
                             anchor="nw")
        info_label.pack(fill="both", expand=True, padx=20, pady=10)
        
        # JSL 腳本按鈕
        button_frame = tk.Frame(guide_window)
        button_frame.pack(pady=15)
        
        def open_jsl_script():
            try:
                jsl_path = resource_path("scripts/jsl/export_non_excluded_data.jsl")
                open_file(jsl_path)
            except Exception as e:
                messagebox.showerror("錯誤", f"開啟 JSL 腳本失敗: {str(e)}")
        
        jsl_btn = tk.Button(button_frame, 
                           text="開啟 JSL 腳本", 
                           font=("Arial", 12, "bold"), 
                           command=open_jsl_script,
                           width=20)
        jsl_btn.pack(side=tk.LEFT, padx=10)
        
        # 關閉按鈕
        close_btn = tk.Button(button_frame, 
                            text="關閉", 
                            font=("Arial", 12), 
                            command=guide_window.destroy,
                            width=15)
        close_btn.pack(side=tk.LEFT, padx=10)
        
    except Exception as e:
        messagebox.showerror("錯誤", f"顯示轉換指引失敗: {str(e)}")