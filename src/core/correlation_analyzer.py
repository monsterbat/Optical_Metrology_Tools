#!/usr/bin/env python3
"""
Correlation and Chromaticity Analyzer Module
相關性與色度分析模組
Author: SC Hsiao
Version: 1.0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from typing import Dict, Optional, Tuple, List


class CorrelationAnalyzer:
    """相關性與色度分析器"""
    
    def __init__(self):
        """初始化分析器"""
        # 設定繪圖風格
        sns.set_style("whitegrid")
        sns.set_context("notebook", font_scale=1.1)
    
    def create_correlation_plot(
        self,
        data: pd.DataFrame,
        x_var: str,
        y_var: str,
        show_fit: bool = True,
        show_r2: bool = True,
        figsize: Tuple[int, int] = (10, 8)
    ) -> plt.Figure:
        """
        創建相關性散點圖（含趨勢線和R²）
        
        Args:
            data: 數據 DataFrame
            x_var: X 軸變數名稱
            y_var: Y 軸變數名稱
            show_fit: 是否顯示趨勢線
            show_r2: 是否顯示 R² 值
            figsize: 圖形大小
            
        Returns:
            matplotlib Figure 對象
        """
        # 準備數據（移除 NaN）
        plot_data = data[[x_var, y_var]].dropna()
        
        if len(plot_data) == 0:
            raise ValueError("沒有有效的數據點")
        
        # 創建圖形
        fig, ax = plt.subplots(figsize=figsize)
        
        # 繪製散點圖
        ax.scatter(plot_data[x_var], plot_data[y_var], 
                  alpha=0.6, s=50, edgecolors='black', linewidth=0.5,
                  color='steelblue', label='Data Points')
        
        # 計算相關係數
        correlation = plot_data[x_var].corr(plot_data[y_var])
        
        # 繪製趨勢線和計算 R²
        if show_fit:
            # 線性回歸
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                plot_data[x_var], plot_data[y_var]
            )
            
            # 生成趨勢線
            x_line = np.array([plot_data[x_var].min(), plot_data[x_var].max()])
            y_line = slope * x_line + intercept
            
            ax.plot(x_line, y_line, 'r-', linewidth=2, label='Fit Line')
            
            # 顯示統計資訊
            if show_r2:
                r2 = r_value ** 2
                text = f'y = {slope:.4f}x + {intercept:.4f}\n'
                text += f'R² = {r2:.4f}\n'
                text += f'Correlation = {correlation:.4f}\n'
                text += f'p-value = {p_value:.4e}'
                
                # 添加文字框
                ax.text(0.05, 0.95, text, 
                       transform=ax.transAxes,
                       fontsize=11,
                       verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='white', 
                               alpha=0.8, edgecolor='gray'))
        
        # 設定標籤和標題
        ax.set_xlabel(x_var, fontsize=14, fontweight='bold')
        ax.set_ylabel(y_var, fontsize=14, fontweight='bold')
        ax.set_title(f'Correlation Plot: {x_var} vs {y_var}', 
                    fontsize=16, fontweight='bold', pad=20)
        
        # 添加網格
        ax.grid(True, alpha=0.3)
        
        # 添加圖例
        ax.legend(loc='best', fontsize=11)
        
        plt.tight_layout()
        
        return fig
    
    def create_chromaticity_plot(
        self,
        data: pd.DataFrame,
        x_var: str,
        y_var: str,
        spec_limits: Optional[Dict[str, float]] = None,
        show_spec: bool = True,
        figsize: Tuple[int, int] = (12, 10)
    ) -> plt.Figure:
        """
        創建色度圖（含直方圖和規格框）
        
        Args:
            data: 數據 DataFrame
            x_var: X 軸變數名稱
            y_var: Y 軸變數名稱
            spec_limits: 規格限制字典 {'LSL_x': val, 'USL_x': val, 'LSL_y': val, 'USL_y': val}
            show_spec: 是否顯示規格框（即使有 spec_limits）
            figsize: 圖形大小
            
        Returns:
            matplotlib Figure 對象
        """
        # 準備數據（移除 NaN）
        plot_data = data[[x_var, y_var]].dropna()
        
        if len(plot_data) == 0:
            raise ValueError("沒有有效的數據點")
        
        # 創建 2x2 子圖佈局
        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(2, 2, height_ratios=[2, 8], width_ratios=[8, 2],
                             hspace=0.02, wspace=0.02)
        
        # 主散點圖 [1,0]
        ax_scatter = fig.add_subplot(gs[1, 0])
        
        # X 軸直方圖 [0,0]
        ax_hist_x = fig.add_subplot(gs[0, 0], sharex=ax_scatter)
        
        # Y 軸直方圖 [1,1]
        ax_hist_y = fig.add_subplot(gs[1, 1], sharey=ax_scatter)
        
        # === 繪製散點圖 ===
        ax_scatter.scatter(plot_data[x_var], plot_data[y_var],
                          alpha=0.6, s=30, edgecolors='black', linewidth=0.5,
                          color='steelblue', label='Data Points')
        
        # 輔助函數：檢查值是否有效
        def is_valid_value(v):
            """檢查值是否有效（不是 None 且不是 NaN）"""
            if v is None:
                return False
            if isinstance(v, (int, float)):
                return not np.isnan(v) and not np.isinf(v)
            return False
        
        # 提取規格值
        lsl_x = spec_limits.get('LSL_x') if spec_limits else None
        usl_x = spec_limits.get('USL_x') if spec_limits else None
        lsl_y = spec_limits.get('LSL_y') if spec_limits else None
        usl_y = spec_limits.get('USL_y') if spec_limits else None
        target_x = spec_limits.get('Target_x') if spec_limits else None
        target_y = spec_limits.get('Target_y') if spec_limits else None
        
        # 調試信息
        print(f"\n=== Analyzer Debug ===")
        print(f"show_spec: {show_spec}")
        print(f"spec_limits: {spec_limits}")
        print(f"LSL_X: {lsl_x}, valid: {is_valid_value(lsl_x)}")
        print(f"USL_X: {usl_x}, valid: {is_valid_value(usl_x)}")
        print(f"LSL_Y: {lsl_y}, valid: {is_valid_value(lsl_y)}")
        print(f"USL_Y: {usl_y}, valid: {is_valid_value(usl_y)}")
        print(f"Target_X: {target_x}, valid: {is_valid_value(target_x)}")
        print(f"Target_Y: {target_y}, valid: {is_valid_value(target_y)}")
        
        # 檢查各個規格線是否有效
        has_lsl_x = is_valid_value(lsl_x)
        has_usl_x = is_valid_value(usl_x)
        has_lsl_y = is_valid_value(lsl_y)
        has_usl_y = is_valid_value(usl_y)
        has_target = is_valid_value(target_x) and is_valid_value(target_y)
        
        # 只要有任一條規格線就顯示（更靈活的邏輯）
        has_any_spec = show_spec and (has_lsl_x or has_usl_x or has_lsl_y or has_usl_y)
        
        print(f"has_lsl_x: {has_lsl_x}, has_usl_x: {has_usl_x}")
        print(f"has_lsl_y: {has_lsl_y}, has_usl_y: {has_usl_y}")
        print(f"has_target: {has_target}")
        print(f"has_any_spec: {has_any_spec}")
        print(f"======================\n")
        
        # 繪製規格線（只要有任一條規格線就顯示）
        if has_any_spec:
            # 用於設定軸範圍的變數
            x_min_spec = x_max_spec = y_min_spec = y_max_spec = None
            
            # 繪製水平規格線（Y 軸的 LSL 和 USL）
            if has_usl_y and (has_lsl_x or has_usl_x):
                # 需要知道 X 的範圍來畫水平線
                x_start = lsl_x if has_lsl_x else plot_data[x_var].min()
                x_end = usl_x if has_usl_x else plot_data[x_var].max()
                ax_scatter.hlines(usl_y, x_start, x_end, colors='red', 
                                linestyles='--', linewidth=2.5, label='Spec Limits', alpha=0.8)
                y_max_spec = usl_y
            
            if has_lsl_y and (has_lsl_x or has_usl_x):
                x_start = lsl_x if has_lsl_x else plot_data[x_var].min()
                x_end = usl_x if has_usl_x else plot_data[x_var].max()
                ax_scatter.hlines(lsl_y, x_start, x_end, colors='red', 
                                linestyles='--', linewidth=2.5, alpha=0.8)
                y_min_spec = lsl_y
            
            # 繪製垂直規格線（X 軸的 LSL 和 USL）
            if has_lsl_x and (has_lsl_y or has_usl_y):
                y_start = lsl_y if has_lsl_y else plot_data[y_var].min()
                y_end = usl_y if has_usl_y else plot_data[y_var].max()
                ax_scatter.vlines(lsl_x, y_start, y_end, colors='red', 
                                linestyles='--', linewidth=2.5, alpha=0.8)
                x_min_spec = lsl_x
            
            if has_usl_x and (has_lsl_y or has_usl_y):
                y_start = lsl_y if has_lsl_y else plot_data[y_var].min()
                y_end = usl_y if has_usl_y else plot_data[y_var].max()
                ax_scatter.vlines(usl_x, y_start, y_end, colors='red', 
                                linestyles='--', linewidth=2.5, alpha=0.8)
                x_max_spec = usl_x
            
            # 繪製 Target 紅點（如果有 Target 值）
            if has_target:
                ax_scatter.scatter(target_x, target_y, 
                                 color='red', s=150, marker='o', 
                                 edgecolors='darkred', linewidth=2,
                                 label='Target', zorder=10, alpha=0.9)
            
            # 設定範圍（基於有效的規格值和數據範圍）
            # X 軸範圍
            if has_lsl_x and has_usl_x:
                margin_x = (usl_x - lsl_x) * 0.1
                ax_scatter.set_xlim(lsl_x - margin_x, usl_x + margin_x)
            elif has_lsl_x:
                x_max_data = plot_data[x_var].max()
                x_range = x_max_data - lsl_x
                ax_scatter.set_xlim(lsl_x - x_range * 0.1, x_max_data + x_range * 0.1)
            elif has_usl_x:
                x_min_data = plot_data[x_var].min()
                x_range = usl_x - x_min_data
                ax_scatter.set_xlim(x_min_data - x_range * 0.1, usl_x + x_range * 0.1)
            else:
                # 使用數據範圍
                x_min, x_max = plot_data[x_var].min(), plot_data[x_var].max()
                x_range = x_max - x_min
                ax_scatter.set_xlim(x_min - x_range * 0.1, x_max + x_range * 0.1)
            
            # Y 軸範圍
            if has_lsl_y and has_usl_y:
                margin_y = (usl_y - lsl_y) * 0.1
                ax_scatter.set_ylim(lsl_y - margin_y, usl_y + margin_y)
            elif has_lsl_y:
                y_max_data = plot_data[y_var].max()
                y_range = y_max_data - lsl_y
                ax_scatter.set_ylim(lsl_y - y_range * 0.1, y_max_data + y_range * 0.1)
            elif has_usl_y:
                y_min_data = plot_data[y_var].min()
                y_range = usl_y - y_min_data
                ax_scatter.set_ylim(y_min_data - y_range * 0.1, usl_y + y_range * 0.1)
            else:
                # 使用數據範圍
                y_min, y_max = plot_data[y_var].min(), plot_data[y_var].max()
                y_range = y_max - y_min
                ax_scatter.set_ylim(y_min - y_range * 0.1, y_max + y_range * 0.1)
            
            # 添加規格標註
            spec_text = ""
            if has_lsl_x:
                spec_text += f'LSL_X: {lsl_x:.4f}  '
            if has_usl_x:
                spec_text += f'USL_X: {usl_x:.4f}'
            if spec_text:
                spec_text += '\n'
            if has_lsl_y:
                spec_text += f'LSL_Y: {lsl_y:.4f}  '
            if has_usl_y:
                spec_text += f'USL_Y: {usl_y:.4f}'
            if has_target:
                spec_text += f'\nTarget: ({target_x:.4f}, {target_y:.4f})'
            
            if spec_text.strip():
                ax_scatter.text(0.02, 0.98, spec_text.strip(),
                              transform=ax_scatter.transAxes,
                              fontsize=9, verticalalignment='top',
                              bbox=dict(boxstyle='round', facecolor='white', 
                                      alpha=0.9, edgecolor='red', linewidth=1.5))
        else:
            # 沒有規格時，使用數據範圍（加 10% margin）
            x_min, x_max = plot_data[x_var].min(), plot_data[x_var].max()
            y_min, y_max = plot_data[y_var].min(), plot_data[y_var].max()
            x_range = x_max - x_min
            y_range = y_max - y_min
            
            ax_scatter.set_xlim(x_min - x_range * 0.1, x_max + x_range * 0.1)
            ax_scatter.set_ylim(y_min - y_range * 0.1, y_max + y_range * 0.1)
        
        ax_scatter.set_xlabel(x_var, fontsize=14, fontweight='bold')
        ax_scatter.set_ylabel(y_var, fontsize=14, fontweight='bold')
        ax_scatter.grid(True, alpha=0.3)
        ax_scatter.legend(loc='best', fontsize=10, framealpha=0.9)
        
        # === 繪製 X 軸直方圖 ===
        ax_hist_x.hist(plot_data[x_var], bins=30, color='steelblue', 
                      alpha=0.6, edgecolor='black', density=True)
        
        # 添加正態分佈曲線
        mu_x = plot_data[x_var].mean()
        std_x = plot_data[x_var].std()
        x_range = np.linspace(plot_data[x_var].min(), plot_data[x_var].max(), 100)
        from scipy.stats import norm
        ax_hist_x.plot(x_range, norm.pdf(x_range, mu_x, std_x), 
                      'r--', linewidth=2, label='Normal Fit')
        
        # 添加規格線（只在有對應規格時）
        if has_lsl_x:
            ax_hist_x.axvline(lsl_x, color='red', 
                            linestyle='--', linewidth=1.5, alpha=0.7)
        if has_usl_x:
            ax_hist_x.axvline(usl_x, color='red', 
                            linestyle='--', linewidth=1.5, alpha=0.7)
        
        ax_hist_x.tick_params(axis='x', labelbottom=False)
        ax_hist_x.grid(True, alpha=0.3)
        ax_hist_x.set_ylabel('Density', fontsize=11)
        
        # === 繪製 Y 軸直方圖 ===
        ax_hist_y.hist(plot_data[y_var], bins=30, color='steelblue', 
                      alpha=0.6, edgecolor='black', orientation='horizontal', 
                      density=True)
        
        # 添加正態分佈曲線
        mu_y = plot_data[y_var].mean()
        std_y = plot_data[y_var].std()
        y_range = np.linspace(plot_data[y_var].min(), plot_data[y_var].max(), 100)
        ax_hist_y.plot(norm.pdf(y_range, mu_y, std_y), y_range, 
                      'r--', linewidth=2)
        
        # 添加規格線（只在有對應規格時）
        if has_lsl_y:
            ax_hist_y.axhline(lsl_y, color='red', 
                            linestyle='--', linewidth=1.5, alpha=0.7)
        if has_usl_y:
            ax_hist_y.axhline(usl_y, color='red', 
                            linestyle='--', linewidth=1.5, alpha=0.7)
        
        ax_hist_y.tick_params(axis='y', labelleft=False)
        ax_hist_y.grid(True, alpha=0.3)
        ax_hist_y.set_xlabel('Density', fontsize=11)
        
        # 總標題
        fig.suptitle(f'Chromaticity Plot: {x_var} vs {y_var}', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        return fig
    
    def create_unified_plot(
        self,
        data: pd.DataFrame,
        x_var: str,
        y_var: str,
        spec_limits: Optional[Dict[str, float]] = None,
        show_spec: bool = True,
        show_fit: bool = True,
        show_histogram: bool = True,
        figsize: Tuple[int, int] = (12, 10)
    ) -> plt.Figure:
        """
        創建統一的分析圖（整合 correlation 和 chromaticity 功能）
        
        Args:
            data: 數據 DataFrame
            x_var: X 軸變數名稱
            y_var: Y 軸變數名稱
            spec_limits: 規格限制字典
            show_spec: 是否顯示規格框
            show_fit: 是否顯示趨勢線和 R²
            show_histogram: 是否顯示直方圖
            figsize: 圖形大小
            
        Returns:
            matplotlib Figure 對象
        """
        # 如果顯示直方圖，使用 create_chromaticity_plot 的邏輯
        # 否則使用單一散點圖佈局
        if show_histogram:
            # 使用現有的 chromaticity_plot，但添加 show_fit 功能
            return self._create_plot_with_histogram(
                data, x_var, y_var, spec_limits, show_spec, show_fit, figsize
            )
        else:
            # 使用單一散點圖
            return self._create_plot_simple(
                data, x_var, y_var, spec_limits, show_spec, show_fit, figsize
            )
    
    def _create_plot_with_histogram(
        self,
        data: pd.DataFrame,
        x_var: str,
        y_var: str,
        spec_limits: Optional[Dict[str, float]],
        show_spec: bool,
        show_fit: bool,
        figsize: Tuple[int, int]
    ) -> plt.Figure:
        """創建帶直方圖的 2x2 佈局圖"""
        # 這裡直接調用並擴展 create_chromaticity_plot 的邏輯
        # 大部分代碼與 create_chromaticity_plot 相同，但添加 show_fit 功能
        
        plot_data = data[[x_var, y_var]].dropna()
        
        if len(plot_data) == 0:
            raise ValueError("沒有有效的數據點")
        
        # 創建 2x2 子圖佈局
        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(2, 2, height_ratios=[2, 8], width_ratios=[8, 2],
                             hspace=0.02, wspace=0.02)
        
        # 主散點圖 [1,0]
        ax_scatter = fig.add_subplot(gs[1, 0])
        
        # X 軸直方圖 [0,0]
        ax_hist_x = fig.add_subplot(gs[0, 0], sharex=ax_scatter)
        
        # Y 軸直方圖 [1,1]
        ax_hist_y = fig.add_subplot(gs[1, 1], sharey=ax_scatter)
        
        # 繪製散點圖
        ax_scatter.scatter(plot_data[x_var], plot_data[y_var],
                          alpha=0.6, s=30, edgecolors='black', linewidth=0.5,
                          color='steelblue', label='Data Points')
        
        # 輔助函數：檢查值是否有效
        def is_valid_value(v):
            if v is None:
                return False
            if isinstance(v, (int, float)):
                return not np.isnan(v) and not np.isinf(v)
            return False
        
        # 提取規格值
        lsl_x = spec_limits.get('LSL_x') if spec_limits else None
        usl_x = spec_limits.get('USL_x') if spec_limits else None
        lsl_y = spec_limits.get('LSL_y') if spec_limits else None
        usl_y = spec_limits.get('USL_y') if spec_limits else None
        target_x = spec_limits.get('Target_x') if spec_limits else None
        target_y = spec_limits.get('Target_y') if spec_limits else None
        
        has_lsl_x = is_valid_value(lsl_x)
        has_usl_x = is_valid_value(usl_x)
        has_lsl_y = is_valid_value(lsl_y)
        has_usl_y = is_valid_value(usl_y)
        has_target = is_valid_value(target_x) and is_valid_value(target_y)
        has_any_spec = show_spec and (has_lsl_x or has_usl_x or has_lsl_y or has_usl_y)
        
        # 繪製趨勢線（如果需要）
        if show_fit:
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                plot_data[x_var], plot_data[y_var]
            )
            x_line = np.array([plot_data[x_var].min(), plot_data[x_var].max()])
            y_line = slope * x_line + intercept
            ax_scatter.plot(x_line, y_line, 'g-', linewidth=2, label='Fit Line', alpha=0.7)
            
            # 添加 R² 資訊
            r2 = r_value ** 2
            fit_text = f'y = {slope:.4f}x + {intercept:.4f}\nR² = {r2:.4f}'
            ax_scatter.text(0.98, 0.02, fit_text,
                          transform=ax_scatter.transAxes,
                          fontsize=9, verticalalignment='bottom',
                          horizontalalignment='right',
                          bbox=dict(boxstyle='round', facecolor='white', 
                                  alpha=0.9, edgecolor='green', linewidth=1.5))
        
        # 繪製規格線
        if has_any_spec:
            # （這裡使用之前的規格線繪製邏輯）
            if has_usl_y and (has_lsl_x or has_usl_x):
                x_start = lsl_x if has_lsl_x else plot_data[x_var].min()
                x_end = usl_x if has_usl_x else plot_data[x_var].max()
                ax_scatter.hlines(usl_y, x_start, x_end, colors='red', 
                                linestyles='--', linewidth=2.5, label='Spec Limits', alpha=0.8)
            
            if has_lsl_y and (has_lsl_x or has_usl_x):
                x_start = lsl_x if has_lsl_x else plot_data[x_var].min()
                x_end = usl_x if has_usl_x else plot_data[x_var].max()
                ax_scatter.hlines(lsl_y, x_start, x_end, colors='red', 
                                linestyles='--', linewidth=2.5, alpha=0.8)
            
            if has_lsl_x and (has_lsl_y or has_usl_y):
                y_start = lsl_y if has_lsl_y else plot_data[y_var].min()
                y_end = usl_y if has_usl_y else plot_data[y_var].max()
                ax_scatter.vlines(lsl_x, y_start, y_end, colors='red', 
                                linestyles='--', linewidth=2.5, alpha=0.8)
            
            if has_usl_x and (has_lsl_y or has_usl_y):
                y_start = lsl_y if has_lsl_y else plot_data[y_var].min()
                y_end = usl_y if has_usl_y else plot_data[y_var].max()
                ax_scatter.vlines(usl_x, y_start, y_end, colors='red', 
                                linestyles='--', linewidth=2.5, alpha=0.8)
            
            if has_target:
                ax_scatter.scatter(target_x, target_y, 
                                 color='red', s=150, marker='o', 
                                 edgecolors='darkred', linewidth=2,
                                 label='Target', zorder=10, alpha=0.9)
            
            # 添加規格標註（左上角）
            spec_text = ""
            if has_lsl_x:
                spec_text += f'LSL_X: {lsl_x:.4f}  '
            if has_usl_x:
                spec_text += f'USL_X: {usl_x:.4f}'
            if spec_text:
                spec_text += '\n'
            if has_lsl_y:
                spec_text += f'LSL_Y: {lsl_y:.4f}  '
            if has_usl_y:
                spec_text += f'USL_Y: {usl_y:.4f}'
            if has_target:
                spec_text += f'\nTarget: ({target_x:.4f}, {target_y:.4f})'
            
            if spec_text.strip():
                ax_scatter.text(0.02, 0.98, spec_text.strip(),
                              transform=ax_scatter.transAxes,
                              fontsize=9, verticalalignment='top',
                              bbox=dict(boxstyle='round', facecolor='white', 
                                      alpha=0.9, edgecolor='red', linewidth=1.5))
        
        # 設定軸範圍（智能調整）
        self._set_axis_limits(ax_scatter, plot_data, x_var, y_var, 
                             has_lsl_x, has_usl_x, has_lsl_y, has_usl_y,
                             lsl_x, usl_x, lsl_y, usl_y)
        
        ax_scatter.set_xlabel(x_var, fontsize=14, fontweight='bold')
        ax_scatter.set_ylabel(y_var, fontsize=14, fontweight='bold')
        ax_scatter.grid(True, alpha=0.3)
        ax_scatter.legend(loc='best', fontsize=10, framealpha=0.9)
        
        # 繪製 X 軸直方圖
        ax_hist_x.hist(plot_data[x_var], bins=30, color='steelblue', 
                      alpha=0.6, edgecolor='black', density=True)
        
        mu_x = plot_data[x_var].mean()
        std_x = plot_data[x_var].std()
        x_range = np.linspace(plot_data[x_var].min(), plot_data[x_var].max(), 100)
        from scipy.stats import norm
        ax_hist_x.plot(x_range, norm.pdf(x_range, mu_x, std_x), 
                      'r--', linewidth=2, label='Normal Fit')
        
        if has_lsl_x:
            ax_hist_x.axvline(lsl_x, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
        if has_usl_x:
            ax_hist_x.axvline(usl_x, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
        
        ax_hist_x.tick_params(axis='x', labelbottom=False)
        ax_hist_x.grid(True, alpha=0.3)
        ax_hist_x.set_ylabel('Density', fontsize=11)
        
        # 繪製 Y 軸直方圖
        ax_hist_y.hist(plot_data[y_var], bins=30, color='steelblue', 
                      alpha=0.6, edgecolor='black', orientation='horizontal', density=True)
        
        mu_y = plot_data[y_var].mean()
        std_y = plot_data[y_var].std()
        y_range = np.linspace(plot_data[y_var].min(), plot_data[y_var].max(), 100)
        ax_hist_y.plot(norm.pdf(y_range, mu_y, std_y), y_range, 
                      'r--', linewidth=2)
        
        if has_lsl_y:
            ax_hist_y.axhline(lsl_y, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
        if has_usl_y:
            ax_hist_y.axhline(usl_y, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
        
        ax_hist_y.tick_params(axis='y', labelleft=False)
        ax_hist_y.grid(True, alpha=0.3)
        ax_hist_y.set_xlabel('Density', fontsize=11)
        
        # 總標題
        fig.suptitle(f'Analysis: {x_var} vs {y_var}', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        return fig
    
    def _create_plot_simple(
        self,
        data: pd.DataFrame,
        x_var: str,
        y_var: str,
        spec_limits: Optional[Dict[str, float]],
        show_spec: bool,
        show_fit: bool,
        figsize: Tuple[int, int]
    ) -> plt.Figure:
        """創建簡單的單一散點圖"""
        plot_data = data[[x_var, y_var]].dropna()
        
        if len(plot_data) == 0:
            raise ValueError("沒有有效的數據點")
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 繪製散點圖
        ax.scatter(plot_data[x_var], plot_data[y_var],
                  alpha=0.6, s=50, edgecolors='black', linewidth=0.5,
                  color='steelblue', label='Data Points')
        
        # 輔助函數
        def is_valid_value(v):
            if v is None:
                return False
            if isinstance(v, (int, float)):
                return not np.isnan(v) and not np.isinf(v)
            return False
        
        # 提取規格值
        lsl_x = spec_limits.get('LSL_x') if spec_limits else None
        usl_x = spec_limits.get('USL_x') if spec_limits else None
        lsl_y = spec_limits.get('LSL_y') if spec_limits else None
        usl_y = spec_limits.get('USL_y') if spec_limits else None
        target_x = spec_limits.get('Target_x') if spec_limits else None
        target_y = spec_limits.get('Target_y') if spec_limits else None
        
        has_lsl_x = is_valid_value(lsl_x)
        has_usl_x = is_valid_value(usl_x)
        has_lsl_y = is_valid_value(lsl_y)
        has_usl_y = is_valid_value(usl_y)
        has_target = is_valid_value(target_x) and is_valid_value(target_y)
        has_any_spec = show_spec and (has_lsl_x or has_usl_x or has_lsl_y or has_usl_y)
        
        # 繪製趨勢線
        if show_fit:
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                plot_data[x_var], plot_data[y_var]
            )
            x_line = np.array([plot_data[x_var].min(), plot_data[x_var].max()])
            y_line = slope * x_line + intercept
            ax.plot(x_line, y_line, 'r-', linewidth=2, label='Fit Line')
            
            r2 = r_value ** 2
            correlation = plot_data[x_var].corr(plot_data[y_var])
            text = f'y = {slope:.4f}x + {intercept:.4f}\n'
            text += f'R² = {r2:.4f}\n'
            text += f'Correlation = {correlation:.4f}\n'
            text += f'p-value = {p_value:.4e}'
            
            ax.text(0.05, 0.95, text, 
                   transform=ax.transAxes,
                   fontsize=11,
                   verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='white', 
                           alpha=0.8, edgecolor='gray'))
        
        # 繪製規格線
        if has_any_spec:
            if has_usl_y:
                ax.axhline(usl_y, color='red', linestyle='--', linewidth=2.5, 
                          label='Spec Limits', alpha=0.8)
            if has_lsl_y:
                ax.axhline(lsl_y, color='red', linestyle='--', linewidth=2.5, alpha=0.8)
            if has_lsl_x:
                ax.axvline(lsl_x, color='red', linestyle='--', linewidth=2.5, alpha=0.8)
            if has_usl_x:
                ax.axvline(usl_x, color='red', linestyle='--', linewidth=2.5, alpha=0.8)
            
            if has_target:
                ax.scatter(target_x, target_y, 
                         color='red', s=150, marker='o', 
                         edgecolors='darkred', linewidth=2,
                         label='Target', zorder=10, alpha=0.9)
        
        ax.set_xlabel(x_var, fontsize=14, fontweight='bold')
        ax.set_ylabel(y_var, fontsize=14, fontweight='bold')
        ax.set_title(f'Analysis: {x_var} vs {y_var}', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=11)
        
        plt.tight_layout()
        
        return fig
    
    def _set_axis_limits(self, ax, plot_data, x_var, y_var, 
                        has_lsl_x, has_usl_x, has_lsl_y, has_usl_y,
                        lsl_x, usl_x, lsl_y, usl_y):
        """智能設定軸範圍"""
        # X 軸範圍
        if has_lsl_x and has_usl_x:
            margin_x = (usl_x - lsl_x) * 0.1
            ax.set_xlim(lsl_x - margin_x, usl_x + margin_x)
        elif has_lsl_x:
            x_max_data = plot_data[x_var].max()
            x_range = x_max_data - lsl_x
            ax.set_xlim(lsl_x - x_range * 0.1, x_max_data + x_range * 0.1)
        elif has_usl_x:
            x_min_data = plot_data[x_var].min()
            x_range = usl_x - x_min_data
            ax.set_xlim(x_min_data - x_range * 0.1, usl_x + x_range * 0.1)
        else:
            x_min, x_max = plot_data[x_var].min(), plot_data[x_var].max()
            x_range = x_max - x_min
            ax.set_xlim(x_min - x_range * 0.1, x_max + x_range * 0.1)
        
        # Y 軸範圍
        if has_lsl_y and has_usl_y:
            margin_y = (usl_y - lsl_y) * 0.1
            ax.set_ylim(lsl_y - margin_y, usl_y + margin_y)
        elif has_lsl_y:
            y_max_data = plot_data[y_var].max()
            y_range = y_max_data - lsl_y
            ax.set_ylim(lsl_y - y_range * 0.1, y_max_data + y_range * 0.1)
        elif has_usl_y:
            y_min_data = plot_data[y_var].min()
            y_range = usl_y - y_min_data
            ax.set_ylim(y_min_data - y_range * 0.1, usl_y + y_range * 0.1)
        else:
            y_min, y_max = plot_data[y_var].min(), plot_data[y_var].max()
            y_range = y_max - y_min
            ax.set_ylim(y_min - y_range * 0.1, y_max + y_range * 0.1)
    
    def calculate_statistics(
        self,
        data: pd.DataFrame,
        x_var: str,
        y_var: str
    ) -> Dict[str, float]:
        """
        計算統計資訊
        
        Args:
            data: 數據 DataFrame
            x_var: X 軸變數名稱
            y_var: Y 軸變數名稱
            
        Returns:
            統計資訊字典
        """
        plot_data = data[[x_var, y_var]].dropna()
        
        if len(plot_data) == 0:
            return {}
        
        # 計算相關係數
        correlation = plot_data[x_var].corr(plot_data[y_var])
        
        # 線性回歸
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            plot_data[x_var], plot_data[y_var]
        )
        
        return {
            'n': len(plot_data),
            'correlation': correlation,
            'r_squared': r_value ** 2,
            'slope': slope,
            'intercept': intercept,
            'p_value': p_value,
            'std_err': std_err,
            'x_mean': plot_data[x_var].mean(),
            'x_std': plot_data[x_var].std(),
            'y_mean': plot_data[y_var].mean(),
            'y_std': plot_data[y_var].std()
        }

