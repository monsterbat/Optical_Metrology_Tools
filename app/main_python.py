#!/usr/bin/env python3
"""
Data Analysis Tools - Python Only Version
專門處理 Process Capability Python Only 的主程式
直接打開 Python PC 分析介面
"""

import tkinter as tk
import sys
import os

# 添加專案路徑到系統路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ui.python_pc_ui import create_python_pc_ui

def main():
    """Python Only 版本主程式 - 直接打開 Process Capability Python Only 介面"""
    # 創建主視窗
    root = tk.Tk()
    root.title("Optical Data Analysis Tools v1.0")
    root.geometry("1000x750")
    root.resizable(True, True)
    
    # 設置視窗最小大小
    root.minsize(900, 650)
    
    # 置中顯示視窗
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # 創建 Python PC UI（直接在主視窗中）
    python_pc_ui = create_python_pc_ui(root)
    
    # 啟動主循環
    root.mainloop()

if __name__ == "__main__":
    main()


