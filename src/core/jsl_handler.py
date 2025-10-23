import os
from tkinter import filedialog, Tk
from src.utils.paths import resource_path

def extract_process_variables(jsl_text):
    """從JSL文本中提取Process Variables部分"""
    keyword = "Process Variables("
    start_idx = jsl_text.find(keyword)
    if start_idx == -1:
        return "Process Variables(...) not found"

    # 開始位置是在 "(" 之後
    start_idx += len(keyword)
    depth = 1
    end_idx = start_idx

    while end_idx < len(jsl_text):
        char = jsl_text[end_idx]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                break
        end_idx += 1

    if depth == 0:
        return jsl_text[start_idx:end_idx].strip()
    else:
        return "Unbalanced parentheses, cannot extract correctly"

def read_jsl_template():
    """讀取JSL模板檔案"""
    try:
        with open(resource_path("config/jmp_pc_report_generate_best_fit.jsl"), "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def save_jsl_with_vars(vars_text, source_file_path=None):
    """將變數儲存到JSL檔案中
    Args:
        vars_text: JSL變數文字
        source_file_path: 來源檔案路徑（用於決定存檔位置）
    """
    try:
        # 讀取原始檔案
        template = read_jsl_template()
        
        # 找到 myVars 的位置
        start_idx = template.find("myVars = {")
        if start_idx == -1:
            return "myVars definition not found", None
            
        # 找到 myVars 的結束位置
        end_idx = template.find("};", start_idx)
        if end_idx == -1:
            return "Cannot find end of myVars", None
            
        # 構建新的檔案內容
        new_content = template[:start_idx + 10] + vars_text + template[end_idx:]
        
        # 決定存檔位置：與打開檔案同目錄，或桌面作為備選
        import datetime
        
        # 產生時間戳記
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 預設檔案名稱（包含時間戳記）
        default_filename = f"jmp_pc_report_generate_best_fit_{timestamp}.jsl"
        
        if source_file_path and os.path.exists(source_file_path):
            # 如果有來源檔案路徑，存到同一個資料夾
            save_dir = os.path.dirname(source_file_path)
            file_path = os.path.join(save_dir, default_filename)
        else:
            # 沒有來源檔案路徑，存到桌面
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            file_path = os.path.join(desktop_path, default_filename)
            
        # 儲存新檔案
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
            
        return f"Successfully saved to {os.path.basename(file_path)}", file_path
    except Exception as e:
        return f"Error saving file: {str(e)}", None 