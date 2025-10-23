#!/usr/bin/env python3
"""
Box Plot Analyzer Module
用於繪製箱型圖和小提琴圖分析
Author: SC Hsiao
Version: 1.0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Dict, List, Optional, Tuple
import matplotlib
matplotlib.use('TkAgg')

# 嘗試導入 seaborn 以獲得更好的視覺效果
try:
    import seaborn as sns
    sns.set_style("whitegrid")
    sns.set_context("notebook", font_scale=1.1)
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False

class BoxPlotAnalyzer:
    """箱型圖分析器"""
    
    def __init__(self):
        """初始化"""
        # 設置中文字體
        try:
            plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Microsoft JhengHei', 'SimHei']
            plt.rcParams['axes.unicode_minus'] = False
        except:
            pass
    
    def create_box_plot(self, 
                       data: pd.DataFrame, 
                       variable: str,
                       spec_limits: Dict[str, float],
                       figsize: Tuple[float, float] = (8, 6),
                       orientation: str = 'vertical') -> plt.Figure:
        """
        創建箱型圖 + 小提琴圖
        
        Args:
            data: 數據 DataFrame
            variable: 要分析的變數名稱
            spec_limits: 規格限制字典 {'LSL': value, 'USL': value, 'Target': value}
            figsize: 圖形大小
            orientation: 方向 ('vertical' 或 'horizontal')
            
        Returns:
            matplotlib Figure 對象
        """
        if variable not in data.columns:
            raise ValueError(f"變數 '{variable}' 不存在於數據中")
        
        # 取得數據（移除 NaN）
        plot_data = data[variable].dropna()
        
        if len(plot_data) == 0:
            raise ValueError(f"變數 '{variable}' 沒有有效數據")
        
        # 創建圖形
        fig, ax = plt.subplots(1, 1, figsize=figsize)
        
        # 取得規格限制
        LSL = spec_limits.get('LSL', None)
        USL = spec_limits.get('USL', None)
        Target = spec_limits.get('Target', None)
        
        # 判斷方向
        is_vertical = (orientation.lower() == 'vertical')
        
        # 繪製小提琴圖
        parts = ax.violinplot([plot_data], 
                              widths=0.7, 
                              vert=is_vertical,
                              showmeans=False,
                              showmedians=False,
                              showextrema=False)
        
        # 設置小提琴圖顏色
        for pc in parts['bodies']:
            pc.set_facecolor('lightblue')
            pc.set_alpha(0.4)
            pc.set_edgecolor('blue')
            pc.set_linewidth(1)
        
        # 繪製箱型圖（覆蓋在小提琴圖上）
        bp = ax.boxplot([plot_data],
                        widths=0.5,
                        notch=True,
                        showmeans=True,
                        meanline=True,
                        vert=is_vertical,
                        patch_artist=True,
                        labels=[variable])
        
        # 設置箱型圖顏色
        for patch in bp['boxes']:
            patch.set_facecolor('white')
            patch.set_alpha(0.8)
            patch.set_edgecolor('black')
            patch.set_linewidth(1.5)
        
        # 設置中位數線顏色
        for median in bp['medians']:
            median.set_color('red')
            median.set_linewidth(2)
        
        # 設置平均值線顏色
        for mean in bp['means']:
            mean.set_color('green')
            mean.set_linewidth(2)
        
        # 計算 Y 軸範圍
        y_min, y_max = self._calculate_axis_limits(plot_data, LSL, USL)
        
        # 繪製規格限制線（調整文字位置避免被線遮擋）
        if is_vertical:
            # 垂直方向
            if LSL is not None and not np.isnan(LSL):
                ax.axhline(LSL, 0, 1, linestyle='--', linewidth=2, color='red', label='LSL', alpha=0.7)
                # 文字放在圖表右側外面，避免遮擋
                ax.text(1.02, LSL, f'LSL: {LSL:.4f}', 
                       transform=ax.get_yaxis_transform(),
                       verticalalignment='center', fontsize=9, color='red', weight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='red'))
            
            if USL is not None and not np.isnan(USL):
                ax.axhline(USL, 0, 1, linestyle='--', linewidth=2, color='red', label='USL', alpha=0.7)
                ax.text(1.02, USL, f'USL: {USL:.4f}', 
                       transform=ax.get_yaxis_transform(),
                       verticalalignment='center', fontsize=9, color='red', weight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='red'))
            
            if Target is not None and not np.isnan(Target):
                ax.axhline(Target, 0, 1, linestyle='--', linewidth=2, color='orange', label='Target', alpha=0.7)
                ax.text(1.02, Target, f'Target: {Target:.4f}', 
                       transform=ax.get_yaxis_transform(),
                       verticalalignment='center', fontsize=9, color='orange', weight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='orange'))
            
            ax.set_ylim(y_min, y_max)
            ax.set_ylabel(variable, weight='bold', fontsize=12)
            ax.set_xlabel('')
        else:
            # 水平方向
            if LSL is not None and not np.isnan(LSL):
                ax.axvline(LSL, 0, 1, linestyle='--', linewidth=2, color='red', label='LSL', alpha=0.7)
                # 文字放在圖表上方，避免遮擋
                ax.text(LSL, 1.02, f'LSL: {LSL:.4f}', 
                       transform=ax.get_xaxis_transform(),
                       horizontalalignment='center', fontsize=9, color='red', weight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='red'))
            
            if USL is not None and not np.isnan(USL):
                ax.axvline(USL, 0, 1, linestyle='--', linewidth=2, color='red', label='USL', alpha=0.7)
                ax.text(USL, 1.02, f'USL: {USL:.4f}', 
                       transform=ax.get_xaxis_transform(),
                       horizontalalignment='center', fontsize=9, color='red', weight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='red'))
            
            if Target is not None and not np.isnan(Target):
                ax.axvline(Target, 0, 1, linestyle='--', linewidth=2, color='orange', label='Target', alpha=0.7)
                ax.text(Target, 1.02, f'Target: {Target:.4f}', 
                       transform=ax.get_xaxis_transform(),
                       horizontalalignment='center', fontsize=9, color='orange', weight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='orange'))
            
            ax.set_xlim(y_min, y_max)
            ax.set_xlabel(variable, weight='bold', fontsize=12)
            ax.set_ylabel('')
        
        # 添加網格
        ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
        
        # 設置標題
        title = f'Box Plot Analysis: {variable}'
        ax.set_title(title, weight='bold', fontsize=14, pad=15)
        
        # 添加統計信息
        stats_text = self._get_statistics_text(plot_data, spec_limits)
        ax.text(0.02, 0.98, stats_text,
               transform=ax.transAxes,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
               fontsize=9,
               family='monospace')
        
        # 調整佈局
        plt.tight_layout()
        
        return fig
    
    def _calculate_axis_limits(self, 
                               data: pd.Series, 
                               LSL: Optional[float], 
                               USL: Optional[float]) -> Tuple[float, float]:
        """
        計算軸的範圍
        優先使用 LSL/USL 作為基準，但如果數據超出範圍則擴展
        """
        data_min = data.min()
        data_max = data.max()
        
        # 計算數據範圍的 margin（5%）
        data_range = data_max - data_min
        data_margin = data_range * 0.05 if data_range > 0 else 0.1
        
        # 初始化範圍
        if LSL is not None and not np.isnan(LSL):
            min_value = LSL
        else:
            min_value = data_min
        
        if USL is not None and not np.isnan(USL):
            max_value = USL
        else:
            max_value = data_max
        
        # 如果數據超出規格限，擴展範圍
        if data_min < min_value:
            min_value = data_min - data_margin
        
        if data_max > max_value:
            max_value = data_max + data_margin
        
        # 計算規格範圍的 margin（10%）
        spec_range = max_value - min_value
        spec_margin = spec_range * 0.1 if spec_range > 0 else 0.1
        
        # 添加 margin 使圖形更美觀
        min_value -= spec_margin
        max_value += spec_margin
        
        return min_value, max_value
    
    def _get_statistics_text(self, 
                            data: pd.Series, 
                            spec_limits: Dict[str, float]) -> str:
        """生成統計信息文本"""
        stats = {
            'Count': len(data),
            'Mean': data.mean(),
            'Median': data.median(),
            'Std': data.std(),
            'Min': data.min(),
            'Max': data.max()
        }
        
        # 計算異常值比例
        LSL = spec_limits.get('LSL', None)
        USL = spec_limits.get('USL', None)
        
        outliers = 0
        if LSL is not None and not np.isnan(LSL):
            outliers += (data < LSL).sum()
        if USL is not None and not np.isnan(USL):
            outliers += (data > USL).sum()
        
        outlier_rate = (outliers / len(data)) * 100 if len(data) > 0 else 0
        
        # 格式化文本
        text = f"Statistics:\n"
        text += f"N     : {stats['Count']}\n"
        text += f"Mean  : {stats['Mean']:.6f}\n"
        text += f"Median: {stats['Median']:.6f}\n"
        text += f"Std   : {stats['Std']:.6f}\n"
        text += f"Min   : {stats['Min']:.6f}\n"
        text += f"Max   : {stats['Max']:.6f}\n"
        text += f"Out%  : {outlier_rate:.2f}%"
        
        return text
    
    def create_multi_box_plots(self,
                               data: pd.DataFrame,
                               variables: List[str],
                               limits_data: pd.DataFrame,
                               figsize: Tuple[float, float] = None) -> plt.Figure:
        """創建多個變數的箱型圖組合"""
        n_vars = len(variables)
        
        if n_vars == 0:
            raise ValueError("請至少選擇一個變數")
        
        # 計算子圖佈局
        n_cols = min(3, n_vars)
        n_rows = (n_vars + n_cols - 1) // n_cols
        
        # 自動計算圖形大小
        if figsize is None:
            figsize = (6 * n_cols, 5 * n_rows)
        
        # 創建圖形
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        
        # 確保 axes 是 2D 陣列
        if n_rows == 1 and n_cols == 1:
            axes = np.array([[axes]])
        elif n_rows == 1:
            axes = axes.reshape(1, -1)
        elif n_cols == 1:
            axes = axes.reshape(-1, 1)
        
        # 繪製每個變數
        for idx, variable in enumerate(variables):
            row = idx // n_cols
            col = idx % n_cols
            ax = axes[row, col]
            
            # 取得規格限制
            spec_row = limits_data[limits_data['Variable'] == variable]
            if len(spec_row) > 0:
                spec_limits = {
                    'LSL': spec_row.iloc[0]['LSL'],
                    'USL': spec_row.iloc[0]['USL'],
                    'Target': spec_row.iloc[0]['Target']
                }
            else:
                spec_limits = {'LSL': None, 'USL': None, 'Target': None}
            
            # 繪製單個箱型圖
            self._plot_single_box_on_axis(ax, data, variable, spec_limits, True)
        
        # 隱藏多餘的子圖
        for idx in range(n_vars, n_rows * n_cols):
            row = idx // n_cols
            col = idx % n_cols
            axes[row, col].set_visible(False)
        
        # 調整佈局
        plt.tight_layout()
        
        return fig
    
    def _plot_single_box_on_axis(self,
                                 ax: plt.Axes,
                                 data: pd.DataFrame,
                                 variable: str,
                                 spec_limits: Dict[str, float],
                                 is_vertical: bool = True):
        """在指定的 Axes 上繪製單個箱型圖"""
        
        # 取得數據
        plot_data = data[variable].dropna()
        
        if len(plot_data) == 0:
            ax.text(0.5, 0.5, f'No data for\n{variable}',
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        # 繪製小提琴圖
        parts = ax.violinplot([plot_data], 
                             widths=0.7, 
                             vert=is_vertical,
                             showmeans=False,
                             showmedians=False,
                             showextrema=False)
        
        for pc in parts['bodies']:
            pc.set_facecolor('lightblue')
            pc.set_alpha(0.4)
            pc.set_edgecolor('blue')
            pc.set_linewidth(1)
        
        # 繪製箱型圖
        bp = ax.boxplot([plot_data],
                       widths=0.5,
                       notch=True,
                       showmeans=True,
                       meanline=True,
                       vert=is_vertical,
                       patch_artist=True)
        
        for patch in bp['boxes']:
            patch.set_facecolor('white')
            patch.set_alpha(0.8)
            patch.set_edgecolor('black')
            patch.set_linewidth(1.5)
        
        for median in bp['medians']:
            median.set_color('red')
            median.set_linewidth(2)
        
        for mean in bp['means']:
            mean.set_color('green')
            mean.set_linewidth(2)
        
        # 取得規格限制
        LSL = spec_limits.get('LSL', None)
        USL = spec_limits.get('USL', None)
        Target = spec_limits.get('Target', None)
        
        # 計算軸範圍
        y_min, y_max = self._calculate_axis_limits(plot_data, LSL, USL)
        
        # 繪製規格限制線
        if is_vertical:
            if LSL is not None and not np.isnan(LSL):
                ax.axhline(LSL, 0, 1, linestyle='--', linewidth=1.5, color='red')
            if USL is not None and not np.isnan(USL):
                ax.axhline(USL, 0, 1, linestyle='--', linewidth=1.5, color='red')
            if Target is not None and not np.isnan(Target):
                ax.axhline(Target, 0, 1, linestyle='--', linewidth=1.5, color='orange')
            ax.set_ylim(y_min, y_max)
            ax.set_ylabel(variable, weight='bold', fontsize=10)
        else:
            if LSL is not None and not np.isnan(LSL):
                ax.axvline(LSL, 0, 1, linestyle='--', linewidth=1.5, color='red')
            if USL is not None and not np.isnan(USL):
                ax.axvline(USL, 0, 1, linestyle='--', linewidth=1.5, color='red')
            if Target is not None and not np.isnan(Target):
                ax.axvline(Target, 0, 1, linestyle='--', linewidth=1.5, color='orange')
            ax.set_xlim(y_min, y_max)
            ax.set_xlabel(variable, weight='bold', fontsize=10)
        
        # 添加網格
        ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
        
        # 設置標題
        ax.set_title(variable, weight='bold', fontsize=11)

