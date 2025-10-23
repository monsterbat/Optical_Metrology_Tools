#!/usr/bin/env python3
"""
Correlation/Chromaticity Dialog Module
相關性/色度分析對話框
Author: SC Hsiao
Version: 1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from src.core.correlation_analyzer import CorrelationAnalyzer
import matplotlib.pyplot as plt


class CorrelationDialog:
    """相關性/色度分析對話框"""
    
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
        self.analyzer = CorrelationAnalyzer()
        
        # 當前圖形
        self.current_figure = None
        self.canvas = None
        self.toolbar = None
        
        # 創建對話框視窗
        self.dialog = None
    
    def show(self):
        """顯示對話框"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Correlation / Chromaticity Analysis")
        self.dialog.geometry("1400x900")
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
        control_frame = tk.Frame(self.dialog, width=350, padx=10, pady=10)
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
        title_label = tk.Label(parent, text="Analysis Settings", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # === X 軸變數選擇 ===
        x_frame = tk.LabelFrame(parent, text="Select X-Axis Variable", padx=10, pady=10)
        x_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(x_frame, text="X-Axis Variable:", font=("Arial", 10)).pack(anchor="w", pady=(0, 5))
        
        self.x_var = tk.StringVar()
        self.x_combo = ttk.Combobox(x_frame, textvariable=self.x_var, 
                                   state="readonly", font=("Arial", 10))
        self.x_combo.pack(fill="x", pady=(0, 5))
        
        # === Y 軸變數選擇 ===
        y_frame = tk.LabelFrame(parent, text="Select Y-Axis Variable", padx=10, pady=10)
        y_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(y_frame, text="Y-Axis Variable:", font=("Arial", 10)).pack(anchor="w", pady=(0, 5))
        
        self.y_var = tk.StringVar()
        self.y_combo = ttk.Combobox(y_frame, textvariable=self.y_var, 
                                   state="readonly", font=("Arial", 10))
        self.y_combo.pack(fill="x", pady=(0, 5))
        
        # 填充變數列表
        self._populate_variable_lists()
        
        # === 顯示選項 ===
        options_frame = tk.LabelFrame(parent, text="Display Options", padx=10, pady=10)
        options_frame.pack(fill="x", pady=(0, 10))
        
        # 顯示規格框
        self.show_spec_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="☐ Show Spec Limits", 
                      variable=self.show_spec_var,
                      font=("Arial", 10)).pack(anchor="w", pady=3)
        
        # 顯示趨勢線
        self.show_fit_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="☐ Show Fit Line + R²", 
                      variable=self.show_fit_var,
                      font=("Arial", 10)).pack(anchor="w", pady=3)
        
        # 顯示直方圖
        self.show_histogram_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="☐ Show Histograms", 
                      variable=self.show_histogram_var,
                      font=("Arial", 10)).pack(anchor="w", pady=3)
        
        # 說明文字
        info_text = ("Tip: You can combine display options freely.\n"
                    "Spec limits must be set in Setup Spec first.")
        tk.Label(options_frame, text=info_text, 
                font=("Arial", 9), fg="gray", 
                wraplength=300, justify="left").pack(anchor="w", pady=(5, 0))
        
        # === 統計資訊顯示 ===
        stats_frame = tk.LabelFrame(parent, text="Statistics", padx=10, pady=10)
        stats_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.stats_text = tk.Text(stats_frame, height=10, width=40, 
                                 font=("Consolas", 9), wrap="word")
        self.stats_text.pack(fill="both", expand=True)
        self.stats_text.config(state="disabled")
        
        # === 操作按鈕 ===
        action_frame = tk.Frame(parent)
        action_frame.pack(fill="x", pady=(10, 0))
        
        # 生成按鈕
        self.generate_btn = tk.Button(action_frame, text="Generate Plot", 
                                     command=self._generate_plot,
                                     font=("Arial", 11, "bold"), 
                                     width=28)
        self.generate_btn.pack(pady=(0, 10))
        
        # 儲存按鈕
        self.save_btn = tk.Button(action_frame, text="Save Plot", 
                                 command=self._save_plot,
                                 font=("Arial", 10),
                                 width=28,
                                 state="disabled")
        self.save_btn.pack(pady=(0, 5))
        
        # 關閉按鈕
        tk.Button(action_frame, text="Close", 
                 command=self._on_close,
                 font=("Arial", 10),
                 width=28).pack()
    
    def _create_plot_area(self, parent):
        """創建圖形顯示區域"""
        # 標題
        title_label = tk.Label(parent, text="Visualization", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 圖形容器
        self.plot_container = tk.Frame(parent, bg="white", relief="sunken", bd=2)
        self.plot_container.pack(fill="both", expand=True)
        
        # 初始提示
        self.placeholder_label = tk.Label(self.plot_container, 
                                         text="Please select X and Y axis variables, then click 'Generate Plot'",
                                         font=("Arial", 12),
                                         fg="gray")
        self.placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def _populate_variable_lists(self):
        """填充變數列表"""
        # 獲取所有分析變數
        analysis_vars = self.core.get_analysis_variables()
        
        if not analysis_vars:
            messagebox.showwarning("Warning", "No analysis variables available!")
            return
        
        # 設定下拉選單
        self.x_combo['values'] = analysis_vars
        self.y_combo['values'] = analysis_vars
        
        # 預設選擇前兩個變數（如果有的話）
        if len(analysis_vars) >= 1:
            self.x_var.set(analysis_vars[0])
        if len(analysis_vars) >= 2:
            self.y_var.set(analysis_vars[1])
    
    def _generate_plot(self):
        """生成圖表"""
        # 獲取選擇的變數
        x_var = self.x_var.get()
        y_var = self.y_var.get()
        
        if not x_var or not y_var:
            messagebox.showwarning("Warning", "Please select both X and Y axis variables!")
            return
        
        if x_var == y_var:
            messagebox.showwarning("Warning", "X and Y axis cannot be the same variable!")
            return
        
        # 檢查變數是否存在於數據中
        if x_var not in self.core.processed_data.columns or \
           y_var not in self.core.processed_data.columns:
            messagebox.showerror("Error", "Selected variable not found in data!")
            return
        
        try:
            # 清除之前的圖形
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
            if self.toolbar:
                self.toolbar.destroy()
            if self.placeholder_label:
                self.placeholder_label.destroy()
                self.placeholder_label = None
            
            # 獲取顯示選項
            show_spec = self.show_spec_var.get()
            show_fit = self.show_fit_var.get()
            show_histogram = self.show_histogram_var.get()
            
            # 獲取規格限制
            spec_limits = self._get_spec_limits(x_var, y_var)
            
            # 調試信息
            print(f"\n=== Debug Info ===")
            print(f"X Variable: {x_var}")
            print(f"Y Variable: {y_var}")
            print(f"Show Spec: {show_spec}")
            print(f"Show Fit: {show_fit}")
            print(f"Show Histogram: {show_histogram}")
            print(f"Spec Limits: {spec_limits}")
            print(f"==================\n")
            
            # 如果用戶選擇顯示規格但沒有設定規格，給予提示
            if show_spec and not spec_limits:
                messagebox.showinfo(
                    "Notice",
                    "Spec limits not found for X or Y axis.\n\n"
                    "Plot will be generated without spec limits.\n\n"
                    "To show spec limits, please set them in Setup Spec first."
                )
            
            # 生成統一的分析圖
            self.current_figure = self.analyzer.create_unified_plot(
                self.core.processed_data,
                x_var,
                y_var,
                spec_limits=spec_limits,
                show_spec=show_spec,
                show_fit=show_fit,
                show_histogram=show_histogram,
                figsize=(12, 10) if show_histogram else (10, 8)
            )
            
            # 顯示圖形
            self.canvas = FigureCanvasTkAgg(self.current_figure, master=self.plot_container)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # 添加工具列
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_container)
            self.toolbar.update()
            
            # 更新統計資訊
            self._update_statistics(x_var, y_var)
            
            # 啟用儲存按鈕
            self.save_btn.config(state="normal")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate plot: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _get_spec_limits(self, x_var: str, y_var: str) -> dict:
        """獲取 X 和 Y 軸的規格限制"""
        if self.limits_data is None:
            return None
        
        spec_limits = {}
        
        # 獲取 X 軸規格
        x_spec = self.limits_data[self.limits_data['Variable'] == x_var]
        if len(x_spec) > 0:
            spec_limits['LSL_x'] = x_spec.iloc[0]['LSL']
            spec_limits['USL_x'] = x_spec.iloc[0]['USL']
            spec_limits['Target_x'] = x_spec.iloc[0]['Target']
        else:
            spec_limits['LSL_x'] = None
            spec_limits['USL_x'] = None
            spec_limits['Target_x'] = None
        
        # 獲取 Y 軸規格
        y_spec = self.limits_data[self.limits_data['Variable'] == y_var]
        if len(y_spec) > 0:
            spec_limits['LSL_y'] = y_spec.iloc[0]['LSL']
            spec_limits['USL_y'] = y_spec.iloc[0]['USL']
            spec_limits['Target_y'] = y_spec.iloc[0]['Target']
        else:
            spec_limits['LSL_y'] = None
            spec_limits['USL_y'] = None
            spec_limits['Target_y'] = None
        
        # 如果所有 LSL/USL 都是 None，返回 None
        if all(v is None for v in [spec_limits.get('LSL_x'), spec_limits.get('USL_x'),
                                    spec_limits.get('LSL_y'), spec_limits.get('USL_y')]):
            return None
        
        return spec_limits
    
    def _update_statistics(self, x_var: str, y_var: str):
        """更新統計資訊顯示"""
        try:
            stats = self.analyzer.calculate_statistics(
                self.core.processed_data, x_var, y_var
            )
            
            if not stats:
                return
            
            # 格式化統計資訊
            text = "=== Statistics ===\n\n"
            text += f"Sample size: {stats['n']}\n\n"
            
            text += f"Correlation (r): {stats['correlation']:.4f}\n"
            text += f"R-squared (R²): {stats['r_squared']:.4f}\n\n"
            
            text += f"Regression equation:\n"
            text += f"y = {stats['slope']:.4f}x + {stats['intercept']:.4f}\n\n"
            
            text += f"p-value: {stats['p_value']:.4e}\n"
            text += f"Std error: {stats['std_err']:.4f}\n\n"
            
            text += f"--- {x_var} (X-axis) ---\n"
            text += f"Mean: {stats['x_mean']:.4f}\n"
            text += f"Std dev: {stats['x_std']:.4f}\n\n"
            
            text += f"--- {y_var} (Y-axis) ---\n"
            text += f"Mean: {stats['y_mean']:.4f}\n"
            text += f"Std dev: {stats['y_std']:.4f}\n"
            
            # 更新文字框
            self.stats_text.config(state="normal")
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, text)
            self.stats_text.config(state="disabled")
            
        except Exception as e:
            print(f"Failed to update statistics: {e}")
    
    def _save_plot(self):
        """儲存圖表"""
        if self.current_figure is None:
            messagebox.showwarning("Warning", "No plot available to save")
            return
        
        try:
            # 使用變數名稱作為預設檔名
            x_var = self.x_var.get()
            y_var = self.y_var.get()
            default_name = f"analysis_{x_var}_vs_{y_var}.png" if x_var and y_var else "analysis_plot.png"
            
            file_path = filedialog.asksaveasfilename(
                title="Save Analysis Plot",
                defaultextension=".png",
                initialfile=default_name,
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

