#!/usr/bin/env python3
"""
Box Plot Dialog Module
箱型圖分析對話框
Author: SC Hsiao
Version: 1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from src.core.box_plot_analyzer import BoxPlotAnalyzer
import matplotlib.pyplot as plt

class BoxPlotDialog:
    """箱型圖分析對話框"""
    
    def __init__(self, parent, core, limits_data):
        """
        初始化對話框
        
        Args:
            parent: 父視窗
            core: PythonPCCore 實例
            limits_data: 規格限制數據 DataFrame
        """
        self.parent = parent
        self.core = core
        self.limits_data = limits_data
        self.analyzer = BoxPlotAnalyzer()
        
        # 當前圖形
        self.current_figure = None
        self.canvas = None
        self.toolbar = None
        
        # 創建對話框視窗
        self.dialog = None
    
    def show(self):
        """顯示對話框"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Box Plot Analysis")
        self.dialog.geometry("1200x800")
        self.dialog.resizable(True, True)
        
        # 創建主要佈局
        self._create_layout()
        
        # 置中顯示
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # 綁定關閉事件
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_layout(self):
        """創建對話框佈局"""
        # 左側控制面板
        control_frame = tk.Frame(self.dialog, width=300, padx=10, pady=10)
        control_frame.pack(side="left", fill="y")
        control_frame.pack_propagate(False)
        
        # 右側圖形顯示區域
        plot_frame = tk.Frame(self.dialog, padx=10, pady=10)
        plot_frame.pack(side="right", fill="both", expand=True)
        
        # 創建控制面板內容
        self._create_control_panel(control_frame)
        
        # 創建圖形顯示區域
        self._create_plot_area(plot_frame)
    
    def _create_control_panel(self, parent):
        """創建控制面板"""
        # 標題
        title_label = tk.Label(parent, text="Box Plot Settings", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 變數選擇區域
        var_frame = tk.LabelFrame(parent, text="Select Variables", padx=10, pady=10)
        var_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # 說明文字
        info_label = tk.Label(var_frame, 
                             text="Select variables to analyze:",
                             font=("Arial", 10))
        info_label.pack(anchor="w", pady=(0, 5))
        
        # 搜尋框
        search_frame = tk.Frame(var_frame)
        search_frame.pack(fill="x", pady=(0, 5))
        
        tk.Label(search_frame, text="Search:", font=("Arial", 9)).pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._filter_variables())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True)
        
        # 快速按鈕
        btn_frame = tk.Frame(var_frame)
        btn_frame.pack(fill="x", pady=(0, 5))
        
        tk.Button(btn_frame, text="Select All", command=self._select_all,
                 font=("Arial", 9), width=10).pack(side="left", padx=(0, 5))
        tk.Button(btn_frame, text="Deselect All", command=self._deselect_all,
                 font=("Arial", 9), width=10).pack(side="left")
        
        # 顯示選擇數量
        self.count_label = tk.Label(var_frame, text="Selected: 0", 
                                   font=("Arial", 9), fg="blue")
        self.count_label.pack(anchor="w", pady=(0, 5))
        
        # 變數列表（含滾輪）
        list_frame = tk.Frame(var_frame)
        list_frame.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        self.var_listbox = tk.Listbox(list_frame, 
                                       selectmode="extended",
                                       font=("Consolas", 9),
                                       yscrollcommand=scrollbar.set)
        self.var_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.var_listbox.yview)
        
        # 綁定選擇變更事件
        self.var_listbox.bind("<<ListboxSelect>>", self._update_count)
        
        # 填充變數列表
        self._populate_variable_list()
        
        # 恢復之前的選擇（從 core 中獲取）
        self._restore_selection()
        
        # 顯示選項區域
        option_frame = tk.LabelFrame(parent, text="Display Options", padx=10, pady=10)
        option_frame.pack(fill="x", pady=(0, 10))
        
        # 方向選擇
        tk.Label(option_frame, text="Orientation:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.orientation_var = tk.StringVar(value="vertical")
        tk.Radiobutton(option_frame, text="Vertical", variable=self.orientation_var, 
                      value="vertical", font=("Arial", 9)).grid(row=0, column=1, sticky="w")
        tk.Radiobutton(option_frame, text="Horizontal", variable=self.orientation_var, 
                      value="horizontal", font=("Arial", 9)).grid(row=0, column=2, sticky="w")
        
        # 顯示模式選擇
        tk.Label(option_frame, text="Display Mode:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.display_mode_var = tk.StringVar(value="single")
        tk.Radiobutton(option_frame, text="Single Variable", variable=self.display_mode_var, 
                      value="single", font=("Arial", 9)).grid(row=1, column=1, sticky="w")
        tk.Radiobutton(option_frame, text="Multiple Variables", variable=self.display_mode_var, 
                      value="multiple", font=("Arial", 9)).grid(row=1, column=2, sticky="w")
        
        # 操作按鈕區域
        action_frame = tk.Frame(parent)
        action_frame.pack(fill="x", pady=(10, 0))
        
        # 生成按鈕
        self.generate_btn = tk.Button(action_frame, text="Generate Plot", 
                                     command=self._generate_plot,
                                     font=("Arial", 11, "bold"), 
                                     width=25)
        self.generate_btn.pack(pady=(0, 10))
        
        # 儲存按鈕
        self.save_btn = tk.Button(action_frame, text="Save Plot", 
                                 command=self._save_plot,
                                 font=("Arial", 10),
                                 width=25,
                                 state="disabled")
        self.save_btn.pack(pady=(0, 5))
        
        # 關閉按鈕
        tk.Button(action_frame, text="Close", 
                 command=self._on_close,
                 font=("Arial", 10),
                 width=25).pack()
    
    def _create_plot_area(self, parent):
        """創建圖形顯示區域"""
        # 標題
        title_label = tk.Label(parent, text="Box Plot Visualization", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 圖形容器
        self.plot_container = tk.Frame(parent, bg="white", relief="sunken", bd=2)
        self.plot_container.pack(fill="both", expand=True)
        
        # 初始提示
        self.placeholder_label = tk.Label(self.plot_container, 
                                         text="Please select variables on the left and click 'Generate Plot'",
                                         font=("Arial", 12),
                                         fg="gray")
        self.placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def _populate_variable_list(self):
        """填充變數列表"""
        # 獲取已選擇的分析變數
        analysis_vars = self.core.get_analysis_variables()
        
        # 顯示所有分析變數（無論有沒有 spec）
        # 因為 Box Plot 現在支援無 spec 繪圖
        self.all_variables = analysis_vars
        
        self._update_listbox()
    
    def _update_listbox(self):
        """更新 Listbox 內容"""
        self.var_listbox.delete(0, tk.END)
        search_text = self.search_var.get().lower()
        
        for var in self.all_variables:
            if not search_text or search_text in var.lower():
                self.var_listbox.insert(tk.END, var)
    
    def _filter_variables(self):
        """根據搜尋文字過濾變數"""
        # 儲存當前選擇
        current_selected = [self.var_listbox.get(i) for i in self.var_listbox.curselection()]
        
        # 重新填充
        self._update_listbox()
        
        # 恢復選擇
        for i in range(self.var_listbox.size()):
            if self.var_listbox.get(i) in current_selected:
                self.var_listbox.selection_set(i)
    
    def _restore_selection(self):
        """恢復先前的選擇"""
        # 預設選擇前3個變數
        for i in range(min(3, self.var_listbox.size())):
            self.var_listbox.selection_set(i)
        self._update_count()
    
    def _select_all(self):
        """全選"""
        self.var_listbox.selection_set(0, tk.END)
        self._update_count()
    
    def _deselect_all(self):
        """全不選"""
        self.var_listbox.selection_clear(0, tk.END)
        self._update_count()
    
    def _update_count(self, event=None):
        """更新選擇數量顯示"""
        count = len(self.var_listbox.curselection())
        self.count_label.config(text=f"Selected: {count}")
    
    def _generate_plot(self):
        """生成箱型圖"""
        # 獲取選擇的變數
        selected_indices = self.var_listbox.curselection()
        
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select at least one variable!")
            return
        
        selected_vars = [self.var_listbox.get(i) for i in selected_indices]
        
        try:
            # 清除之前的圖形
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
            if self.toolbar:
                self.toolbar.destroy()
            if self.placeholder_label:
                self.placeholder_label.destroy()
                self.placeholder_label = None
            
            # 獲取顯示模式
            display_mode = self.display_mode_var.get()
            orientation = self.orientation_var.get()
            
            if display_mode == "single" and len(selected_vars) > 1:
                # 單一變數模式但選了多個，只用第一個
                messagebox.showinfo("Notice", f"Single variable mode: showing only first variable: {selected_vars[0]}")
                selected_vars = [selected_vars[0]]
            
            # 生成圖形
            if display_mode == "single":
                # 單一變數模式
                variable = selected_vars[0]
                
                # 取得規格限制（如果沒有 spec 則使用 None）
                spec_limits = {'LSL': None, 'USL': None, 'Target': None}
                
                if self.limits_data is not None:
                    spec_row = self.limits_data[self.limits_data['Variable'] == variable]
                    if len(spec_row) > 0:
                        spec_limits = {
                            'LSL': spec_row.iloc[0]['LSL'],
                            'USL': spec_row.iloc[0]['USL'],
                            'Target': spec_row.iloc[0]['Target']
                        }
                
                # 創建圖形（即使沒有 spec 也能繪製）
                self.current_figure = self.analyzer.create_box_plot(
                    self.core.processed_data,
                    variable,
                    spec_limits,
                    figsize=(10, 8),
                    orientation=orientation
                )
            else:
                # 多個變數模式
                self.current_figure = self.analyzer.create_multi_box_plots(
                    self.core.processed_data,
                    selected_vars,
                    self.limits_data,
                    figsize=None  # 自動計算
                )
            
            # 顯示圖形
            self.canvas = FigureCanvasTkAgg(self.current_figure, master=self.plot_container)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # 添加工具列
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_container)
            self.toolbar.update()
            
            # 啟用儲存按鈕
            self.save_btn.config(state="normal")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate plot: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _save_plot(self):
        """儲存圖表"""
        if self.current_figure is None:
            messagebox.showwarning("Warning", "No plot available to save")
            return
        
        try:
            # 詢問保存位置
            file_path = filedialog.asksaveasfilename(
                title="Save Box Plot",
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("PDF files", "*.pdf"),
                    ("SVG files", "*.svg"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                # 儲存圖形
                self.current_figure.savefig(file_path, 
                                          bbox_inches='tight', 
                                          dpi=300,
                                          facecolor='white')
                messagebox.showinfo("Success", f"Plot saved to:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save plot: {str(e)}")
    
    def _on_close(self):
        """關閉對話框"""
        # 清理資源
        if self.current_figure:
            plt.close(self.current_figure)
        
        self.dialog.destroy()

