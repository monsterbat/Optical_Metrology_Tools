#!/usr/bin/env python3
"""
Process Capability Preview Dialog
用於預覽和調整分布選擇的對話框
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from src.core.pc_calculator import ProcessCapabilityCalculator
import threading

class PCPreviewDialog:
    """Process Capability預覽對話框"""
    
    def __init__(self, parent, core, limits_data=None):
        self.parent = parent
        self.core = core
        self.limits_data = limits_data
        self.dialog = None
        self.tree = None
        self.calculator = ProcessCapabilityCalculator()
        
        # 計算模式：JMP 或 Academic（學術）
        self.calculation_mode = None  # 於UI建立時初始化為Tk變數
        
        # 儲存計算結果和分布選擇
        self.pc_results = {}
        self.aicc_results = {}
        self.current_selections = {}  # 儲存當前選擇的分布
        
        # 分布名稱對應 (參考JMP的完整分布列表)
        self.distribution_names = {
            'normal': 'Normal',
            'lognormal': 'Lognormal', 
            'weibull': 'Weibull',
            'exponential': 'Exponential',
            'gamma': 'Gamma',
            'beta': 'Beta',
            'johnson_su': 'Johnson Su',
            'johnson_sb': 'Johnson Sb',
            'mixture_2_normals': 'Mixture of 2 Normals',
            'mixture_3_normals': 'Mixture of 3 Normals',
            'shash': 'SHASH',
            'chi2': 'Chi-Square',
            'f': 'F-Distribution',
            't': 't-Distribution',
            'uniform': 'Uniform',
            'triangular': 'Triangular',
            'logistic': 'Logistic',
            'laplace': 'Laplace',
            'gumbel': 'Gumbel',
            # Notebook 版本的分佈
            'normal_notebook': 'Normal (Notebook)',
            'lognormal_notebook': 'LogNormal (Notebook)',
            'weibull_notebook': 'Weibull (Notebook)',
            'exponential_notebook': 'Exponential (Notebook)',
            'gamma_notebook': 'Gamma (Notebook)'
        }
        
        # Notebook 版本分佈映射回基礎分佈類型（用於 PC 計算）
        self.notebook_to_base_distribution = {
            'normal_notebook': 'normal',
            'lognormal_notebook': 'lognormal',
            'weibull_notebook': 'weibull',
            'exponential_notebook': 'exponential',
            'gamma_notebook': 'gamma'
        }
        
    def show(self):
        """顯示預覽對話框"""
        self._create_dialog()
        self._calculate_initial_results()
        self._populate_tree()
        
    def _create_dialog(self):
        """創建對話框界面"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Process Capability Preview")
        self.dialog.geometry("1200x600")
        self.dialog.grab_set()
        
        # 主框架
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 標題
        title_label = tk.Label(main_frame, text="Process Capability Analysis Preview", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 說明文字
        desc_label = tk.Label(main_frame, 
                             text="Preview calculation results. You can adjust distribution types and recalculate. Click 'Confirm' to generate Excel report.",
                             font=("Arial", 10))
        desc_label.pack(pady=(0, 10))
        
        # 移除 Calculation Mode 選項，統一使用 Academic 方法

        # 創建表格框架
        table_frame = tk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True)
        
        # 創建Treeview
        columns = (
            'Variable', 'Distribution', 'LSL', 'Target', 'USL', 'Sample_Mean', 'Sample_StdDev',
            'Ppk_Academic', 'Expected_Outside', 'Observed_Outside'
        )
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # 設定欄位標題和寬度
        column_configs = {
            'Variable': ('Process', 120),
            'Distribution': ('Distribution', 120),
            'LSL': ('LSL', 80),
            'Target': ('Target', 80),  
            'USL': ('USL', 80),
            'Sample_Mean': ('Sample Mean', 100),
            'Sample_StdDev': ('Sample StdDev', 100),
            'Ppk_Academic': ('Ppk (Academic)', 110),
            'Expected_Outside': ('Expected % Outside', 120),
            'Observed_Outside': ('Observed % Outside', 120)
        }
        
        for col, (heading, width) in column_configs.items():
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor='center')
        
        # 添加滾動條
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # 放置組件
        self.tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # 綁定雙擊事件
        self.tree.bind('<Double-1>', self._on_item_double_click)
        
        # 添加右鍵選單功能（複製表格數據）
        self._create_tree_context_menu()
        
        # 按鈕框架
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        # 重新計算按鈕
        refresh_btn = tk.Button(button_frame, text="Recalculate", 
                               command=self._refresh_calculations,
                               font=("Arial", 11), width=12)
        refresh_btn.pack(side="left", padx=(0, 10))
        
        # 顯示分布圖按鈕
        plot_btn = tk.Button(button_frame, text="Show Distribution", 
                            command=self._show_distribution_plots,
                            font=("Arial", 11), width=15)
        plot_btn.pack(side="left", padx=(0, 10))
        
        # 確認按鈕
        confirm_btn = tk.Button(button_frame, text="Confirm & Generate", 
                               command=self._confirm_and_generate,
                               font=("Arial", 11, "bold"), width=18)
        confirm_btn.pack(side="right", padx=(10, 0))
        
        # 取消按鈕
        cancel_btn = tk.Button(button_frame, text="Cancel", 
                              command=self.dialog.destroy,
                              font=("Arial", 11), width=12)
        cancel_btn.pack(side="right")
        
    def _calculate_initial_results(self):
        """計算初始結果"""
        if self.core.processed_data is None:
            messagebox.showerror("Error", "No data available for processing")
            return
            
        analysis_variables = self.core.get_analysis_variables()
        
        print("🔄 計算Process Capability預覽...")
        
        for variable in analysis_variables:
            if variable in self.core.processed_data.columns:
                print(f"   處理變數: {variable}")
                
                # 獲取數據
                data = self.core.processed_data[variable].dropna()
                
                if len(data) < 3:
                    continue
                
                # 計算AICC for all distributions
                aicc_results = self._calculate_aicc_for_variable(data)
                self.aicc_results[variable] = aicc_results
                
                # 選擇最佳分布 (AICC最小)
                best_dist = min(aicc_results.keys(), key=lambda k: aicc_results[k]['aicc'])
                self.current_selections[variable] = best_dist
                
                # 計算PC結果
                pc_result = self._calculate_pc_for_variable(variable, data, best_dist)
                self.pc_results[variable] = pc_result
                
        print("✅ 預覽計算完成")
        
    def _calculate_aicc_for_variable(self, data) -> Dict[str, Dict]:
        """為變數計算所有分布的AICC - 只使用我們的標準方法（JMP標準）"""
        results = {}
        
        # 使用新的標準化 AICc 計算器
        from src.core.distribution_fitter import AICcCalculator
        aicc_calc = AICcCalculator()
        
        # 定義要計算的分佈（只包含5個主要分佈 - JMP標準方法）
        distributions_config = [
            # 我們的方法（JMP標準）
            ('normal', aicc_calc.fit_normal, 'Normal'),
            ('lognormal', aicc_calc.fit_lognormal, 'LogNormal'),
            ('weibull', aicc_calc.fit_weibull, 'Weibull'),
            ('exponential', aicc_calc.fit_exponential, 'Exponential'),
            ('gamma', aicc_calc.fit_gamma, 'Gamma'),
            
            # Notebook 方法 - 暫時屏蔽，保留代碼供未來使用
            # ('normal_notebook', aicc_calc.fit_normal_notebook, 'Normal (Notebook)'),
            # ('lognormal_notebook', aicc_calc.fit_lognormal_notebook, 'LogNormal (Notebook)'),
            # ('weibull_notebook', aicc_calc.fit_weibull_notebook, 'Weibull (Notebook)'),
            # ('exponential_notebook', aicc_calc.fit_exponential_notebook, 'Exponential (Notebook)'),
            # ('gamma_notebook', aicc_calc.fit_gamma_notebook, 'Gamma (Notebook)'),
        ]
        
        for dist_key, fit_func, display_name in distributions_config:
            try:
                params, aicc = fit_func(data)
                
                if params is not None and not np.isinf(aicc):
                    results[dist_key] = {
                        'params': params,
                        'aicc': aicc,
                        'display_name': display_name
                    }
                    print(f"   ✅ {display_name}: AICC={aicc:.2f}")
                else:
                    print(f"   ⚠️ {display_name}: 擬合失敗")
                    
            except Exception as e:
                print(f"   ⚠️ {display_name} fitting failed: {str(e)}")
                continue
        
        return results
        
    def _calculate_pc_for_variable(self, variable: str, data: pd.Series, distribution: str) -> Dict:
        """計算特定變數和分布的PC結果"""
        result = {
            'variable': variable,
            'distribution': self.distribution_names.get(distribution, distribution),
            'sample_mean': float(data.mean()),
            'sample_std': float(data.std()),
            'n_samples': len(data)
        }
        
        # 獲取規格限制
        lsl, target, usl = self._get_spec_limits(variable)
        result.update({
            'lsl': lsl,
            'target': target, 
            'usl': usl
        })
        
        # 獲取該分佈的擬合參數（如果有的話）
        fitted_params = None
        if variable in self.aicc_results and distribution in self.aicc_results[variable]:
            fitted_params = self.aicc_results[variable][distribution].get('params')
            print(f"      📦 使用已擬合的參數: {fitted_params}")
        
        # 計算 PPK（僅使用 Academic 方法）
        if lsl is not None or usl is not None:
            print(f"      🔢 計算 PPK: LSL={lsl}, USL={usl}, 分布={distribution}")
            
            ppk_acad, exp_acad = self._calculate_capability_metrics_mode(
                data, distribution, lsl, usl, fitted_params, mode="Academic"
            )
            
            print(f"      ✅ PPK 計算完成: Academic={ppk_acad:.3f}, Expected={exp_acad:.2f}")
            
            observed_outside = self._calculate_observed_outside(data, lsl, usl)

            result.update({
                'ppk_academic': ppk_acad,
                'expected_outside': exp_acad,
                'observed_outside': observed_outside
            })
            
            # 除錯訊息：確認資料有正確儲存
            print(f"      📊 儲存結果: ppk_academic={result.get('ppk_academic', 'None')}")
        else:
            print(f"      ⚠️ 無規格限制，PPK 設為 0")
            result.update({
                'ppk_academic': 0.0,
                'expected_outside': 0.0,
                'observed_outside': 0.0
            })
            
        return result
        
    def _get_spec_limits(self, variable: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """獲取規格限制"""
        if self.limits_data is None:
            return None, None, None
            
        # 尋找對應的規格
        matching_rows = self.limits_data[self.limits_data['Variable'] == variable]
        
        if len(matching_rows) == 0:
            return None, None, None
            
        row = matching_rows.iloc[0]
        
        lsl = row.get('LSL')
        target = row.get('Target') 
        usl = row.get('USL')
        
        # 處理空值
        lsl = None if pd.isna(lsl) else float(lsl)
        target = None if pd.isna(target) else float(target)
        usl = None if pd.isna(usl) else float(usl)
        
        return lsl, target, usl
        
    def _calculate_capability_metrics_mode(self, data: pd.Series, distribution: str,
                                           lsl: Optional[float], usl: Optional[float], 
                                           fitted_params: Optional[Dict] = None,
                                           mode: str = "Academic") -> Tuple[float, float]:
        """依模式計算 Ppk 與 expected outside（使用原本的 Academic 方法）"""
        try:
            # 如果是 Notebook 版本，映射回基礎分佈類型（但保留原始distribution用於參數判斷）
            is_notebook = distribution in self.notebook_to_base_distribution
            base_distribution = self.notebook_to_base_distribution.get(distribution, distribution)
            
            # 使用原本有效的計算方法 - Academic 分位數方法
            if base_distribution == 'normal':
                mean = data.mean()
                std = data.std(ddof=1)  # 樣本標準差
                ppk = self._calculate_ppk_normal(mean, std, lsl, usl)
                expected_outside = self._calculate_expected_outside_normal(mean, std, lsl, usl)
                print(f"        Normal PPK (Academic): μ={mean:.3f}, σ={std:.3f}, PPK={ppk:.3f}")
                return ppk, expected_outside
            
            elif base_distribution == 'lognormal':
                # JMP 方法：LogNormal 分布使用分位數方法，不是對數空間方法
                ppk = self._calculate_ppk_lognormal_jmp(data, lsl, usl, fitted_params, is_notebook)
                expected_outside = self._calculate_expected_outside_lognormal_jmp(data, lsl, usl, fitted_params, is_notebook)
                method_type = "Notebook" if is_notebook else "JMP標準"
                print(f"        Lognormal PPK ({method_type}方法): PPK={ppk:.3f}")
                return ppk, expected_outside
            
            else:
                # 根據分布類型選擇相應的 Academic 計算方法
                distribution_lower = base_distribution.lower()
                
                if distribution_lower == 'gamma':
                    ppk = self._calculate_ppk_gamma(data, lsl, usl)
                elif distribution_lower == 'weibull':
                    ppk = self._calculate_ppk_weibull(data, lsl, usl)
                elif distribution_lower == 'exponential':
                    ppk = self._calculate_ppk_exponential(data, lsl, usl)
                else:
                    print(f"        ⚠️ 不支援的分布: {base_distribution}")
                    ppk = 0.0
                
                expected_outside = self._calculate_expected_outside_general(data, base_distribution, lsl, usl)
                print(f"        {base_distribution.title()} PPK (Academic 專用方法): PPK={ppk:.3f}")
                return ppk, expected_outside
                
        except Exception as e:
            print(f"⚠️ 計算能力指標失敗: {str(e)}")
            return 0.0, 0.0

    def _on_mode_changed(self):
        """模式切換函數已移除，因為統一使用 Academic 方法"""
        # 此函數已不再使用，因為移除了 Calculation Mode 選項
        pass
            
    def _calculate_expected_outside_general(self, data: pd.Series, distribution: str,
                                          lsl: Optional[float], usl: Optional[float]) -> float:
        """計算其他分布的expected outside %"""
        try:
            from scipy import stats
            
            # 如果是 Notebook 版本，映射回基礎分佈類型
            base_distribution = self.notebook_to_base_distribution.get(distribution, distribution)
            
            # 根據分布類型選擇scipy分布
            if base_distribution == 'weibull':
                dist_params = stats.weibull_min.fit(data)
                dist_obj = stats.weibull_min
            elif base_distribution == 'gamma':
                dist_params = stats.gamma.fit(data)
                dist_obj = stats.gamma
            elif base_distribution == 'exponential':
                dist_params = stats.expon.fit(data)
                dist_obj = stats.expon
            elif base_distribution == 'beta':
                # Beta分布需要先標準化到[0,1]
                data_min, data_max = data.min(), data.max()
                normalized_data = (data - data_min) / (data_max - data_min)
                dist_params = stats.beta.fit(normalized_data)
                dist_obj = stats.beta
                # 對規格限制也進行同樣的標準化
                if lsl is not None:
                    lsl = (lsl - data_min) / (data_max - data_min)
                if usl is not None:
                    usl = (usl - data_min) / (data_max - data_min)
            else:
                return 0.0
            
            outside_prob = 0.0
            
            if lsl is not None:
                outside_prob += dist_obj.cdf(lsl, *dist_params)
                
            if usl is not None:
                outside_prob += 1 - dist_obj.cdf(usl, *dist_params)
                
            return outside_prob * 100
            
        except Exception as e:
            print(f"⚠️ 計算expected outside失敗: {str(e)}")
            return 0.0
        
    def _calculate_observed_outside(self, data: pd.Series, 
                                  lsl: Optional[float], usl: Optional[float]) -> float:
        """計算觀測到的outside %"""
        total = len(data)
        if total == 0:
            return 0.0
            
        outside_count = 0
        
        if lsl is not None:
            outside_count += (data < lsl).sum()
            
        if usl is not None:
            outside_count += (data > usl).sum()
            
        return (outside_count / total) * 100
        
    def _create_tree_context_menu(self):
        """創建表格的右鍵選單"""
        self.tree_context_menu = tk.Menu(self.tree, tearoff=0)
        self.tree_context_menu.add_command(label="Copy Selected Row", command=self._copy_selected_row)
        self.tree_context_menu.add_command(label="Copy All Data", command=self._copy_all_data)
        self.tree_context_menu.add_separator()
        self.tree_context_menu.add_command(label="Export to CSV", command=self._export_to_csv)
        
        def show_context_menu(event):
            try:
                self.tree_context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.tree_context_menu.grab_release()
        
        # 綁定右鍵點擊
        self.tree.bind("<Button-2>", show_context_menu)  # macOS
        self.tree.bind("<Button-3>", show_context_menu)  # Windows/Linux
    
    def _copy_selected_row(self):
        """複製選中的行到剪貼簿"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Notice", "Please select rows to copy first")
            return
        
        # 獲取欄位名稱
        columns = self.tree['columns']
        
        # 複製選中的行
        copied_text = []
        for item in selected_items:
            values = self.tree.item(item)['values']
            row_text = '\t'.join(str(v) for v in values)
            copied_text.append(row_text)
        
        # 複製到剪貼簿
        self.dialog.clipboard_clear()
        self.dialog.clipboard_append('\n'.join(copied_text))
        
        messagebox.showinfo("Success", f"Copied {len(selected_items)} row(s)")
    
    def _copy_all_data(self):
        """複製所有數據到剪貼簿（包含標題）"""
        # 獲取欄位名稱
        columns = self.tree['columns']
        headers = [self.tree.heading(col)['text'] for col in columns]
        
        # 添加標題行
        copied_text = ['\t'.join(headers)]
        
        # 添加所有數據行
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            row_text = '\t'.join(str(v) for v in values)
            copied_text.append(row_text)
        
        # 複製到剪貼簿
        self.dialog.clipboard_clear()
        self.dialog.clipboard_append('\n'.join(copied_text))
        
        messagebox.showinfo("Success", f"Copied all table data ({len(copied_text)-1} row(s))")
    
    def _export_to_csv(self):
        """匯出表格數據為CSV文件"""
        from tkinter import filedialog
        import csv
        from datetime import datetime
        
        # 選擇儲存位置
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"PC_Results_{timestamp}.csv"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=default_filename
        )
        
        if not file_path:
            return
        
        try:
            # 獲取欄位名稱
            columns = self.tree['columns']
            headers = [self.tree.heading(col)['text'] for col in columns]
            
            # 寫入CSV
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                
                for item in self.tree.get_children():
                    values = self.tree.item(item)['values']
                    writer.writerow(values)
            
            messagebox.showinfo("Success", f"Data exported to:\n{file_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def _populate_tree(self):
        """填充表格數據 (僅顯示 Academic PPK)"""
        # 清空現有數據
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 添加數據行 - 僅包含必要欄位
        for variable, result in self.pc_results.items():
            # 只需要 Academic PPK 欄位
            ppk_academic = result.get('ppk_academic', 0.0)
            
            values = (
                result['variable'],
                result['distribution'],
                f"{result['lsl']:.3f}" if result['lsl'] is not None else "-",
                f"{result['target']:.3f}" if result['target'] is not None else "-",
                f"{result['usl']:.3f}" if result['usl'] is not None else "-",
                f"{result['sample_mean']:.3f}",
                f"{result.get('sample_std', 0.0):.3f}",
                f"{ppk_academic:.2f}" if ppk_academic is not None else "0.00", 
                f"{result.get('expected_outside', 0.0):.2f}",
                f"{result.get('observed_outside', 0.0):.2f}"
            )
            
            item_id = self.tree.insert('', 'end', values=values)
            # 儲存變數名稱以便後續識別
            self.tree.set(item_id, '#1', variable)  # 使用第一列儲存變數名
            
    def _on_item_double_click(self, event):
        """處理項目雙擊事件"""
        selected_item = self.tree.selection()[0] if self.tree.selection() else None
        if not selected_item:
            return
            
        # 獲取變數名稱
        variable = self.tree.item(selected_item)['values'][0]
        
        # 顯示分布選擇對話框
        self._show_distribution_selection_dialog(variable)
        
    def _show_distribution_selection_dialog(self, variable: str):
        """顯示分布選擇對話框"""
        if variable not in self.aicc_results:
            messagebox.showwarning("Warning", f"AICC results not found for variable {variable}")
            return
            
        # 創建新對話框
        selection_dialog = tk.Toplevel(self.dialog)
        selection_dialog.title(f"Select Distribution - {variable}")
        selection_dialog.geometry("600x500")  # 增大視窗尺寸
        selection_dialog.grab_set()
        
        # 標題
        title_label = tk.Label(selection_dialog, text=f"Select Distribution for {variable}", 
                              font=("Arial", 12, "bold"))
        title_label.pack(pady=10)
        
        # 說明
        desc_label = tk.Label(selection_dialog, text="Distributions sorted by AICC (lower is better):")
        desc_label.pack(pady=(0, 10))
        
        # 創建分布列表
        aicc_data = self.aicc_results[variable]
        sorted_distributions = sorted(aicc_data.items(), key=lambda x: x[1]['aicc'])
        
        # 選擇變數
        selected_dist = tk.StringVar(value=self.current_selections[variable])
        
        # 分布選項
        for dist_name, dist_data in sorted_distributions:
            text = f"{dist_data['display_name']} (AICC: {dist_data['aicc']:.2f})"
            rb = tk.Radiobutton(selection_dialog, text=text, variable=selected_dist, 
                               value=dist_name, font=("Arial", 10))
            rb.pack(anchor='w', padx=20, pady=2)
            
        # 按鈕框架
        btn_frame = tk.Frame(selection_dialog)
        btn_frame.pack(fill="x", pady=20, padx=20)
        
        def apply_selection():
            old_dist = self.current_selections[variable]
            new_dist = selected_dist.get()
            
            if old_dist != new_dist:
                # 更新選擇
                self.current_selections[variable] = new_dist
                
                # 重新計算該變數的PC結果
                data = self.core.processed_data[variable].dropna()
                new_result = self._calculate_pc_for_variable(variable, data, new_dist)
                self.pc_results[variable] = new_result
                
                # 更新表格
                self._populate_tree()
                
                messagebox.showinfo("Success", f"Distribution for {variable} updated to {self.distribution_names.get(new_dist, new_dist)}")
                
            selection_dialog.destroy()
            
        # 確認按鈕
        apply_btn = tk.Button(btn_frame, text="Apply", command=apply_selection,
                             font=("Arial", 11, "bold"), width=10)
        apply_btn.pack(side="right", padx=(10, 0))
        
        # 取消按鈕  
        cancel_btn = tk.Button(btn_frame, text="Cancel", command=selection_dialog.destroy,
                              font=("Arial", 11), width=10)
        cancel_btn.pack(side="right")
        
    def _refresh_calculations(self):
        """重新計算所有結果"""
        # 重新計算所有變數
        for variable in self.current_selections.keys():
            if variable in self.core.processed_data.columns:
                data = self.core.processed_data[variable].dropna()
                dist = self.current_selections[variable]
                new_result = self._calculate_pc_for_variable(variable, data, dist)
                self.pc_results[variable] = new_result
                
        # 更新表格
        self._populate_tree()
        messagebox.showinfo("Complete", "All calculations updated")
        
    def _confirm_and_generate(self):
        """確認並生成Excel報告"""
        try:
            # 使用當前的結果生成報告
            output_path = self.calculator.generate_excel_report_from_results(
                self.pc_results, 
                self.core.file_name,
                self.core.file_path
            )
            
            if output_path:
                messagebox.showinfo("Success", f"Excel report generated:\n{output_path}")
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to generate Excel report")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error occurred while generating report:\n{str(e)}")
    
    def _show_distribution_plots(self):
        """顯示分布比較圖"""
        selected_item = self.tree.selection()[0] if self.tree.selection() else None
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a variable first")
            return
            
        variable = self.tree.item(selected_item)['values'][0]
        if variable not in self.core.processed_data.columns:
            messagebox.showerror("Error", f"Variable {variable} not found")
            return
            
        data = self.core.processed_data[variable].dropna()
        if len(data) < 3:
            messagebox.showerror("Error", "Insufficient data")
            return
            
        # 創建分布比較對話框
        self._create_distribution_plot_dialog(variable, data)
    
    def _create_distribution_plot_dialog(self, variable: str, data: pd.Series):
        """創建分布比較圖對話框"""
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import matplotlib.patches as patches
        except ImportError:
            messagebox.showerror("Error", "matplotlib is required to display charts")
            return
            
        # 創建新對話框
        plot_dialog = tk.Toplevel(self.dialog)
        plot_dialog.title(f"Distribution Comparison - {variable}")
        plot_dialog.geometry("1400x900")  # 進一步增大視窗
        plot_dialog.grab_set()
        
        # 創建 matplotlib 圖形
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 畫直方圖
        n_bins = min(50, max(10, len(data) // 10))
        counts, bins, patches_hist = ax.hist(data, bins=n_bins, density=True, alpha=0.6, 
                                           color='lightblue', edgecolor='black', label='Data Histogram')
        
        # 獲取AICC結果並排序
        if variable in self.aicc_results:
            aicc_data = self.aicc_results[variable]
            sorted_distributions = sorted(aicc_data.items(), key=lambda x: x[1]['aicc'])
            
            # 準備分布曲線顏色
            colors = ['red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan', 'magenta']
            x_range = np.linspace(data.min(), data.max(), 1000)
            
            # 獲取規格限制線
            lsl, target, usl = self._get_spec_limits(variable)
            
            # 畫規格限制線
            if lsl is not None:
                ax.axvline(lsl, color='red', linestyle='--', linewidth=2, label=f'LSL={lsl:.3f}')
            if target is not None:
                ax.axvline(target, color='green', linestyle='--', linewidth=2, label=f'Target={target:.3f}')
            if usl is not None:
                ax.axvline(usl, color='red', linestyle='--', linewidth=2, label=f'USL={usl:.3f}')
            
            # 畫分布曲線
            for i, (dist_name, dist_data) in enumerate(sorted_distributions[:8]):  # 最多顯示8條曲線
                if i < len(colors):
                    color = colors[i]
                    try:
                        y_values = self._calculate_distribution_pdf(dist_name, dist_data['params'], x_range)
                        if y_values is not None:
                            label = f"{dist_data['display_name']} (AICc: {dist_data['aicc']:.2f})"
                            ax.plot(x_range, y_values, color=color, linewidth=2, label=label)
                    except Exception as e:
                        print(f"⚠️ 無法畫 {dist_name} 曲線: {str(e)}")
        
        # 設定圖表
        ax.set_xlabel(f'{variable}', fontsize=12)
        ax.set_ylabel('Density', fontsize=12)
        ax.set_title(f'Distribution Comparison - {variable}', fontsize=14, fontweight='bold')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # 調整佈局
        plt.tight_layout()
        
        # 嵌入到 tkinter
        canvas = FigureCanvasTkAgg(fig, plot_dialog)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # 關閉按鈕
        btn_frame = tk.Frame(plot_dialog)
        btn_frame.pack(fill="x", pady=10)
        tk.Button(btn_frame, text="Close", command=plot_dialog.destroy,
                 font=("Arial", 11), width=12).pack()
    
    def _calculate_distribution_pdf(self, dist_name: str, params: dict, x_values: np.ndarray) -> Optional[np.ndarray]:
        """計算分布的概率密度函數值"""
        try:
            if dist_name == 'normal':
                from scipy import stats
                return stats.norm.pdf(x_values, loc=params['mu'], scale=params['sigma'])
                
            elif dist_name == 'lognormal':
                from scipy import stats
                # 我們的參數名稱是 mu_log 和 sigma_log
                return stats.lognorm.pdf(x_values, s=params['sigma_log'], scale=np.exp(params['mu_log']))
                
            elif dist_name == 'gamma':
                from scipy import stats
                # 我們的參數名稱是 alpha 和 sigma (不是 shape 和 scale)
                return stats.gamma.pdf(x_values, a=params['alpha'], scale=params['sigma'])
                
            elif dist_name == 'weibull':
                from scipy import stats
                # 我們的參數名稱是 beta 和 alpha (不是 c 和 scale)
                return stats.weibull_min.pdf(x_values, c=params['beta'], scale=params['alpha'])
                
            elif dist_name == 'exponential':
                from scipy import stats
                # 我們的參數名稱是 sigma (不是 scale)
                return stats.expon.pdf(x_values, scale=params['sigma'])
                
            elif dist_name == 'beta':
                from scipy import stats
                return stats.beta.pdf(x_values, a=params['a'], b=params['b'], 
                                    loc=params['loc'], scale=params['scale'])
                
            elif dist_name == 'johnson_su':
                from scipy import stats
                return stats.johnsonsu.pdf(x_values, a=params['gamma'], b=params['delta'],
                                         loc=params['loc'], scale=params['scale'])
                
            elif dist_name == 'johnson_sb':
                from scipy import stats
                return stats.johnsonsb.pdf(x_values, a=params['gamma'], b=params['delta'],
                                         loc=params['loc'], scale=params['scale'])
                
            elif dist_name == 'mixture_2_normals':
                # 混合正態分布
                weights = params['weights']
                means = params['means']
                stds = np.sqrt(params['covariances'])
                
                pdf_vals = np.zeros_like(x_values)
                for i in range(2):
                    from scipy import stats
                    pdf_vals += weights[i] * stats.norm.pdf(x_values, loc=means[i], scale=stds[i])
                return pdf_vals
                
            elif dist_name == 'mixture_3_normals':
                # 混合正態分布
                weights = params['weights']
                means = params['means']
                stds = np.sqrt(params['covariances'])
                
                pdf_vals = np.zeros_like(x_values)
                for i in range(3):
                    from scipy import stats
                    pdf_vals += weights[i] * stats.norm.pdf(x_values, loc=means[i], scale=stds[i])
                return pdf_vals
                
            elif dist_name == 'shash':
                # SHASH 分布
                mu, sigma, epsilon, delta = params['mu'], params['sigma'], params['epsilon'], params['delta']
                z = (x_values - mu) / sigma
                sinh_term = np.sinh(delta * np.arcsinh(z) - epsilon)
                jacobian = delta / (sigma * np.sqrt(1 + z**2))
                return jacobian * np.exp(-0.5 * sinh_term**2) / np.sqrt(2 * np.pi)
            
            return None
            
        except Exception as e:
            print(f"⚠️ 計算 {dist_name} PDF 失敗: {str(e)}")
            return None

    # ========================================
    # PPK 計算函數 (JMP 兼容方法)
    # ========================================
    
    def _calculate_ppk_normal(self, mean: float, std: float, lsl: Optional[float], usl: Optional[float]) -> float:
        """正態分布 PPK 計算 (AIAG 標準)"""
        if std <= 0:
            return 0.0
        
        cpu = float('inf') if usl is None else (usl - mean) / (3 * std)
        cpl = float('inf') if lsl is None else (mean - lsl) / (3 * std)
        
        if cpu == float('inf') and cpl == float('inf'):
            return 0.0
        elif cpu == float('inf'):
            return max(0, cpl)
        elif cpl == float('inf'):
            return max(0, cpu)
        else:
            return max(0, min(cpu, cpl))
    
    def _calculate_ppk_lognormal_jmp(self, data: pd.Series, lsl: Optional[float], usl: Optional[float],
                                      fitted_params: Optional[Dict] = None, is_notebook: bool = False) -> float:
        """
        LogNormal PPK 計算 (JMP 方法 - 分位數方法)
        
        JMP 對 LogNormal 分布使用分位數方法，不是對數空間方法：
        1. 使用傳入的擬合參數（或重新擬合）
        2. 計算 0.135%, 50%, 99.865% 分位數
        3. 使用公式：CPU = (USL - P50) / (P99.865 - P50)
        
        參考：JMP Statistical Discovery (LogNormal Distribution Process Capability)
        """
        try:
            from scipy import stats
            
            # 移除非正數值
            clean_data = data[data > 0].dropna()
            if len(clean_data) < 3:
                return 0.0
            
            # 使用傳入的參數或重新擬合
            if fitted_params is not None:
                # 使用已擬合的參數
                if is_notebook and 'parameters' in fitted_params:
                    # Notebook 版本：參數格式是 (s, loc, scale)
                    params = fitted_params['parameters']
                    s, loc, scale = params
                    print(f"          使用 Notebook 擬合參數: s={s:.6f}, loc={loc:.6f}, scale={scale:.6f}")
                else:
                    # 我們的版本：從對數空間參數轉換
                    mu_log = fitted_params.get('mu_log')
                    sigma_log = fitted_params.get('sigma_log')
                    if mu_log is not None and sigma_log is not None:
                        s = sigma_log
                        loc = 0
                        scale = np.exp(mu_log)
                        print(f"          使用 JMP標準 擬合參數: s={s:.6f}, scale={scale:.6f} (固定loc=0)")
                    else:
                        # 降級：重新擬合
                        params = stats.lognorm.fit(clean_data, floc=0)
                        s, loc, scale = params
                        print(f"          警告：參數格式不符，重新擬合")
            else:
                # 沒有傳入參數，重新擬合（固定 loc=0）
                params = stats.lognorm.fit(clean_data, floc=0)
                s, loc, scale = params
                print(f"          重新擬合參數: s={s:.6f}, loc={loc:.6f}, scale={scale:.6f}")
            
            # 計算關鍵分位數 (等效於正態分布的 ±3σ)
            median = stats.lognorm.ppf(0.5, s, loc, scale)          # 50%
            p_0135 = stats.lognorm.ppf(0.00135, s, loc, scale)     # 0.135% (-3σ)
            p_99865 = stats.lognorm.ppf(0.99865, s, loc, scale)    # 99.865% (+3σ)
            
            print(f"          LogNormal 參數: s={s:.6f}, scale={scale:.6f}")
            print(f"          分位數: P0.135={p_0135:.6f}, P50={median:.6f}, P99.865={p_99865:.6f}")
            
            # 計算 PPK (JMP 分位數方法)
            cpu = float('inf') if usl is None else (usl - median) / (p_99865 - median) if p_99865 > median else 0
            cpl = float('inf') if lsl is None else (median - lsl) / (median - p_0135) if median > p_0135 else 0
            
            if cpu == float('inf') and cpl == float('inf'):
                return 0.0
            elif cpu == float('inf'):
                return max(0, cpl)
            elif cpl == float('inf'):
                return max(0, cpu)
            else:
                return max(0, min(cpu, cpl))
                
        except Exception as e:
            print(f"          ❌ LogNormal PPK 計算失敗: {e}")
            return 0.0
    
    def _calculate_ppk_gamma(self, data: pd.Series, lsl: Optional[float], usl: Optional[float]) -> float:
        """Gamma 分布 PPK 計算 (JMP 分位數方法)"""
        try:
            from scipy import stats
            
            clean_data = data.dropna()
            if len(clean_data) < 3:
                return 0.0
            
            # 擬合三參數 Gamma 分布 (JMP 方法：自由擬合所有參數)
            params = stats.gamma.fit(clean_data)  # 不固定 floc，允許三參數擬合
            a, loc, scale = params
            
            print(f"          Gamma 參數: α={a:.6f}, θ={loc:.6f}, β={scale:.6f}")
            
            # 計算分位數
            median = stats.gamma.ppf(0.5, a, loc, scale)
            p_0135 = stats.gamma.ppf(0.00135, a, loc, scale)
            p_99865 = stats.gamma.ppf(0.99865, a, loc, scale)
            
            print(f"          分位數: P0.135={p_0135:.6f}, P50={median:.6f}, P99.865={p_99865:.6f}")
            
            # 計算 PPK
            cpu = float('inf') if usl is None else (usl - median) / (p_99865 - median) if p_99865 > median else 0
            cpl = float('inf') if lsl is None else (median - lsl) / (median - p_0135) if median > p_0135 else 0
            
            if cpu == float('inf') and cpl == float('inf'):
                return 0.0
            elif cpu == float('inf'):
                return max(0, cpl)
            elif cpl == float('inf'):
                return max(0, cpu)
            else:
                return max(0, min(cpu, cpl))
                
        except Exception as e:
            print(f"          ❌ Gamma PPK 計算失敗: {e}")
            return 0.0
    
    def _calculate_ppk_weibull(self, data: pd.Series, lsl: Optional[float], usl: Optional[float]) -> float:
        """Weibull 分布 PPK 計算 (JMP 分位數方法)"""
        try:
            from scipy import stats
            
            clean_data = data.dropna()
            if len(clean_data) < 3:
                return 0.0
            
            # 擬合 Weibull 分布 (floc=0 固定位置參數)
            params = stats.weibull_min.fit(clean_data, floc=0)
            c, loc, scale = params
            
            # 計算分位數
            median = stats.weibull_min.ppf(0.5, c, loc, scale)
            p_0135 = stats.weibull_min.ppf(0.00135, c, loc, scale)
            p_99865 = stats.weibull_min.ppf(0.99865, c, loc, scale)
            
            # 計算 PPK
            cpu = float('inf') if usl is None else (usl - median) / (p_99865 - median) if p_99865 > median else 0
            cpl = float('inf') if lsl is None else (median - lsl) / (median - p_0135) if median > p_0135 else 0
            
            if cpu == float('inf') and cpl == float('inf'):
                return 0.0
            elif cpu == float('inf'):
                return max(0, cpl)
            elif cpl == float('inf'):
                return max(0, cpu)
            else:
                return max(0, min(cpu, cpl))
                
        except Exception as e:
            print(f"          ❌ Weibull PPK 計算失敗: {e}")
            return 0.0
    
    def _calculate_ppk_exponential(self, data: pd.Series, lsl: Optional[float], usl: Optional[float]) -> float:
        """Exponential 分布 PPK 計算 (JMP 分位數方法)"""
        try:
            from scipy import stats
            
            clean_data = data.dropna()
            if len(clean_data) < 3:
                return 0.0
            
            # 擬合 Exponential 分布 (floc=0 固定位置參數)
            params = stats.expon.fit(clean_data, floc=0)
            loc, scale = params
            
            # 計算分位數
            median = stats.expon.ppf(0.5, loc, scale)
            p_0135 = stats.expon.ppf(0.00135, loc, scale)
            p_99865 = stats.expon.ppf(0.99865, loc, scale)
            
            # 計算 PPK
            cpu = float('inf') if usl is None else (usl - median) / (p_99865 - median) if p_99865 > median else 0
            cpl = float('inf') if lsl is None else (median - lsl) / (median - p_0135) if median > p_0135 else 0
            
            if cpu == float('inf') and cpl == float('inf'):
                return 0.0
            elif cpu == float('inf'):
                return max(0, cpl)
            elif cpl == float('inf'):
                return max(0, cpu)
            else:
                return max(0, min(cpu, cpl))
                
        except Exception as e:
            print(f"          ❌ Exponential PPK 計算失敗: {e}")
            return 0.0
    
    # ========================================
    # Expected Outside 計算函數 (JMP 兼容版本)
    # ========================================
    
    def _calculate_expected_outside_normal(self, mean: float, std: float, lsl: Optional[float], usl: Optional[float]) -> float:
        """Normal 分布 Expected Outside 計算 (JMP 兼容)"""
        try:
            from scipy import stats
            
            if std <= 0:
                return 0.0
            
            outside_prob = 0.0
            
            # 計算低於LSL的機率
            if lsl is not None:
                prob_below_lsl = stats.norm.cdf(lsl, loc=mean, scale=std)
                outside_prob += prob_below_lsl
                
            # 計算高於USL的機率
            if usl is not None:
                prob_above_usl = 1 - stats.norm.cdf(usl, loc=mean, scale=std)
                outside_prob += prob_above_usl
                
            return outside_prob * 100
            
        except Exception as e:
            print(f"⚠️ 計算Normal Expected Outside失敗: {str(e)}")
            return 0.0
    
    def _calculate_expected_outside_lognormal_jmp(self, data: pd.Series, lsl: Optional[float], usl: Optional[float],
                                                   fitted_params: Optional[Dict] = None, is_notebook: bool = False) -> float:
        """LogNormal 分布 Expected Outside 計算 (JMP 方法)"""
        try:
            from scipy import stats
            
            # 移除非正數值
            clean_data = data[data > 0].dropna()
            if len(clean_data) < 3:
                return 0.0
            
            # 使用傳入的參數或重新擬合（與 PPK 計算保持一致）
            if fitted_params is not None:
                if is_notebook and 'parameters' in fitted_params:
                    params = fitted_params['parameters']
                    s, loc, scale = params
                else:
                    mu_log = fitted_params.get('mu_log')
                    sigma_log = fitted_params.get('sigma_log')
                    if mu_log is not None and sigma_log is not None:
                        s = sigma_log
                        loc = 0
                        scale = np.exp(mu_log)
                    else:
                        params = stats.lognorm.fit(clean_data, floc=0)
                        s, loc, scale = params
            else:
                params = stats.lognorm.fit(clean_data, floc=0)
                s, loc, scale = params
            
            outside_prob = 0.0
            
            # 計算低於LSL的機率
            if lsl is not None and lsl > 0:
                prob_below_lsl = stats.lognorm.cdf(lsl, s, loc, scale)
                outside_prob += prob_below_lsl
                
            # 計算高於USL的機率
            if usl is not None and usl > 0:
                prob_above_usl = 1 - stats.lognorm.cdf(usl, s, loc, scale)
                outside_prob += prob_above_usl
                
            return outside_prob * 100
            
        except Exception as e:
            print(f"⚠️ 計算LogNormal Expected Outside失敗: {str(e)}")
            return 0.0
