#!/usr/bin/env python3
"""
Process Capability Calculator - Python Only
使用Python實現完整的過程能力計算，包括Best Fit分析和PPK計算
Author: SC Hsiao
Version: 1.0
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.optimize import minimize
import warnings
from typing import Dict, List, Tuple, Optional, Any
import os
from datetime import datetime

warnings.filterwarnings('ignore')

class ProcessCapabilityCalculator:
    """過程能力計算器"""
    
    def __init__(self):
        self.aicc_calculator = None
        self._initialize_aicc_calculator()
    
    def _initialize_aicc_calculator(self):
        """初始化AICc計算器 - 重用現有的AICcCalculator"""
        try:
            from src.core.aicc_calculator import AICcCalculator
            self.aicc_calculator = AICcCalculator()
        except ImportError:
            print("⚠️ 無法載入AICcCalculator，將使用簡化版本")
            self.aicc_calculator = self._create_simple_aicc_calculator()
    
    def _create_simple_aicc_calculator(self):
        """創建簡化版AICc計算器"""
        class SimpleAICcCalculator:
            def calculate_aicc(self, log_likelihood, n_params, n_data):
                aic = -2 * log_likelihood + 2 * n_params
                aicc = aic + (2 * n_params * (n_params + 1)) / (n_data - n_params - 1)
                return aicc
            
            def fit_normal(self, data):
                try:
                    clean_data = data.dropna()
                    if len(clean_data) < 3:
                        return None, np.inf
                    mu, sigma = stats.norm.fit(clean_data)
                    log_likelihood = np.sum(stats.norm.logpdf(clean_data, mu, sigma))
                    aicc = self.calculate_aicc(log_likelihood, 2, len(clean_data))
                    return {"mu": mu, "sigma": sigma}, aicc
                except:
                    return None, np.inf
            
            def calculate_all_distributions(self, data, column_name=""):
                # 簡化版只計算Normal分布
                params, aicc = self.fit_normal(data)
                if params is not None:
                    return {"Normal": aicc}
                return {"Normal": np.inf}
        
        return SimpleAICcCalculator()
    
    def perform_best_fit_analysis(self, data: pd.DataFrame, variables: List[str]) -> Dict[str, Any]:
        """
        執行Best Fit分析
        
        Args:
            data: 處理後的數據
            variables: 要分析的變數列表
            
        Returns:
            Dict[str, Any]: Best Fit分析結果
        """
        results = {}
        
        print("🔍 開始Best Fit分析...")
        
        for variable in variables:
            if variable not in data.columns:
                print(f"⚠️ 變數 {variable} 不存在於數據中")
                continue
            
            var_data = data[variable].dropna()
            if len(var_data) < 10:
                print(f"⚠️ 變數 {variable} 數據量不足 ({len(var_data)} < 10)")
                continue
            
            print(f"\n分析變數: {variable}")
            print(f"數據量: {len(var_data)}")
            
            # 使用AICc計算器進行分布擬合
            distribution_results = self.aicc_calculator.calculate_all_distributions(var_data, variable)
            
            # 找出最佳分布
            best_distribution = min(distribution_results.keys(), 
                                  key=lambda x: distribution_results[x])
            best_aicc = distribution_results[best_distribution]
            
            print(f"最佳分布: {best_distribution} (AICc: {best_aicc:.3f})")
            
            # 儲存結果
            results[variable] = {
                'best_distribution': best_distribution,
                'best_aicc': best_aicc,
                'all_distributions': distribution_results,
                'data_count': len(var_data),
                'data_mean': float(var_data.mean()),
                'data_std': float(var_data.std()),
                'data_min': float(var_data.min()),
                'data_max': float(var_data.max())
            }
        
        print(f"\n✅ Best Fit分析完成，共分析 {len(results)} 個變數")
        return results
    
    def calculate_process_capability(self, data: pd.DataFrame, variables: List[str], 
                                   limits_data: pd.DataFrame = None) -> Dict[str, Any]:
        """
        計算過程能力指標
        
        Args:
            data: 處理後的數據
            variables: 要分析的變數列表
            limits_data: 規格限制數據
            
        Returns:
            Dict[str, Any]: 過程能力計算結果
        """
        results = {}
        
        print("📊 開始過程能力計算...")
        
        # 先執行Best Fit分析
        best_fit_results = self.perform_best_fit_analysis(data, variables)
        
        for variable in variables:
            if variable not in best_fit_results:
                continue
            
            var_data = data[variable].dropna()
            best_fit_info = best_fit_results[variable]
            
            print(f"\n計算變數: {variable}")
            
            # 取得規格限制
            lsl, usl, target = self._get_spec_limits(variable, limits_data)
            
            # 根據最佳分布計算PPK和失效率
            capability_metrics = self._calculate_capability_metrics(
                var_data, best_fit_info['best_distribution'], lsl, usl, target
            )
            
            # 合併結果
            results[variable] = {
                **best_fit_info,
                **capability_metrics,
                'lsl': lsl,
                'usl': usl,
                'target': target
            }
            
            print(f"PPK: {capability_metrics.get('ppk', 'N/A')}")
            print(f"失效率: {capability_metrics.get('fail_rate_percent', 'N/A')}%")
        
        print(f"\n✅ 過程能力計算完成")
        return results
    
    def _get_spec_limits(self, variable: str, limits_data: pd.DataFrame) -> Tuple[float, float, float]:
        """取得變數的規格限制"""
        lsl = usl = target = None
        
        if limits_data is not None:
            var_limits = limits_data[limits_data['Variable'] == variable]
            if len(var_limits) > 0:
                row = var_limits.iloc[0]
                lsl = row.get('LSL', None)
                usl = row.get('USL', None)
                target = row.get('Target', None)
                
                # 轉換為float，處理NaN值
                lsl = float(lsl) if pd.notna(lsl) else None
                usl = float(usl) if pd.notna(usl) else None
                target = float(target) if pd.notna(target) else None
        
        return lsl, usl, target
    
    def _calculate_capability_metrics(self, data: pd.Series, distribution: str, 
                                    lsl: float, usl: float, target: float) -> Dict[str, Any]:
        """計算過程能力指標"""
        metrics = {}
        
        try:
            data_mean = float(data.mean())
            data_std = float(data.std())
            
            # 計算基本統計量
            metrics['sample_mean'] = data_mean
            metrics['sample_std'] = data_std
            metrics['sample_count'] = len(data)
            
            # 計算PPK
            if lsl is not None and usl is not None:
                # 雙邊規格
                ppu = (usl - data_mean) / (3 * data_std)
                ppl = (data_mean - lsl) / (3 * data_std)
                ppk = min(ppu, ppl)
                pp = (usl - lsl) / (6 * data_std)
                
                metrics['ppu'] = float(ppu)
                metrics['ppl'] = float(ppl)
                metrics['ppk'] = float(ppk)
                metrics['pp'] = float(pp)
                
            elif usl is not None:
                # 只有上限
                ppu = (usl - data_mean) / (3 * data_std)
                metrics['ppu'] = float(ppu)
                metrics['ppk'] = float(ppu)
                
            elif lsl is not None:
                # 只有下限
                ppl = (data_mean - lsl) / (3 * data_std)
                metrics['ppl'] = float(ppl)
                metrics['ppk'] = float(ppl)
            
            # 計算失效率 (基於Normal分布近似)
            fail_rate = self._calculate_fail_rate(data, distribution, lsl, usl)
            metrics['fail_rate_percent'] = fail_rate
            
            # 計算期望失效率 (基於Normal分布)
            if lsl is not None or usl is not None:
                expected_fail_rate = self._calculate_expected_fail_rate(data_mean, data_std, lsl, usl)
                metrics['expected_fail_rate_percent'] = expected_fail_rate
            
        except Exception as e:
            print(f"⚠️ 計算過程能力指標時發生錯誤: {str(e)}")
        
        return metrics
    
    def _calculate_fail_rate(self, data: pd.Series, distribution: str, 
                           lsl: float, usl: float) -> float:
        """計算實際失效率"""
        try:
            total_count = len(data)
            fail_count = 0
            
            for value in data:
                if lsl is not None and value < lsl:
                    fail_count += 1
                elif usl is not None and value > usl:
                    fail_count += 1
            
            fail_rate = (fail_count / total_count) * 100 if total_count > 0 else 0
            return float(fail_rate)
            
        except Exception:
            return 0.0
    
    def _calculate_expected_fail_rate(self, mean: float, std: float, 
                                    lsl: float, usl: float) -> float:
        """計算期望失效率 (基於Normal分布)"""
        try:
            fail_prob = 0.0
            
            if lsl is not None:
                # 低於下限的機率
                fail_prob += stats.norm.cdf(lsl, mean, std)
            
            if usl is not None:
                # 高於上限的機率
                fail_prob += 1 - stats.norm.cdf(usl, mean, std)
            
            return float(fail_prob * 100)
            
        except Exception:
            return 0.0
    
    def generate_excel_report(self, results: Dict[str, Any], output_path: str = None) -> str:
        """
        生成Excel報告
        
        Args:
            results: 過程能力計算結果
            output_path: 輸出路徑 (可選)
            
        Returns:
            str: 生成的檔案路徑
        """
        try:
            # 準備報告數據
            report_data = []
            
            for variable, result in results.items():
                row = {
                    'Variable': variable,
                    'Sample_Count': result.get('sample_count', 0),
                    'Sample_Mean': result.get('sample_mean', 0),
                    'Sample_Std': result.get('sample_std', 0),
                    'Best_Distribution': result.get('best_distribution', 'Unknown'),
                    'Best_AICc': result.get('best_aicc', np.inf),
                    'LSL': result.get('lsl', ''),
                    'USL': result.get('usl', ''),
                    'Target': result.get('target', ''),
                    'PPL': result.get('ppl', ''),
                    'PPU': result.get('ppu', ''),
                    'PPK': result.get('ppk', ''),
                    'PP': result.get('pp', ''),
                    'Actual_Fail_Rate_%': result.get('fail_rate_percent', ''),
                    'Expected_Fail_Rate_%': result.get('expected_fail_rate_percent', ''),
                    'Data_Min': result.get('data_min', ''),
                    'Data_Max': result.get('data_max', '')
                }
                report_data.append(row)
            
            # 創建DataFrame
            df = pd.DataFrame(report_data)
            
            # 設定輸出路徑
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"ProcessCapability_Report_{timestamp}.xlsx"
            
            # 寫入Excel檔案
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 主要報告
                df.to_excel(writer, sheet_name='Process_Capability', index=False)
                
                # 分布AICc比較表
                if results:
                    aicc_data = []
                    for variable, result in results.items():
                        all_dist = result.get('all_distributions', {})
                        for dist_name, aicc_value in all_dist.items():
                            aicc_data.append({
                                'Variable': variable,
                                'Distribution': dist_name,
                                'AICc': aicc_value,
                                'Is_Best': dist_name == result.get('best_distribution', '')
                            })
                    
                    if aicc_data:
                        aicc_df = pd.DataFrame(aicc_data)
                        aicc_df.to_excel(writer, sheet_name='AICc_Comparison', index=False)
                
                # 格式化工作表
                self._format_excel_sheets(writer, df)
            
            print(f"📊 Excel報告已生成: {output_path}")
            return output_path
            
        except Exception as e:
            error_msg = f"❌ 生成Excel報告失敗: {str(e)}"
            print(error_msg)
            return ""
    
    def generate_excel_report_from_results(self, pc_results: Dict[str, Any], 
                                         file_name: str = None, file_path: str = None) -> str:
        """
        從 PC Preview Dialog 的結果生成Excel報告
        
        Args:
            pc_results: PC Preview Dialog 的計算結果
            file_name: 原始檔案名稱
            file_path: 原始檔案路徑
            
        Returns:
            str: 生成的檔案路徑
        """
        try:
            # 轉換數據格式為 generate_excel_report 期望的格式
            converted_results = {}
            
            for variable, result in pc_results.items():
                converted_results[variable] = {
                    'sample_count': result.get('n_samples', 0),
                    'sample_mean': result.get('sample_mean', 0),
                    'sample_std': result.get('sample_std', 0),
                    'best_distribution': result.get('distribution', 'Unknown'),
                    'best_aicc': 0,  # PC Preview中沒有這個資訊
                    'lsl': result.get('lsl'),
                    'usl': result.get('usl'),
                    'target': result.get('target'),
                    'ppl': 0,  # 暫時設為0，如需要可以後續計算
                    'ppu': 0,  # 暫時設為0，如需要可以後續計算
                    'ppk': result.get('ppk_academic', 0),
                    'pp': 0,   # 暫時設為0，如需要可以後續計算
                    'fail_rate_percent': result.get('observed_outside', 0),
                    'expected_fail_rate_percent': result.get('expected_outside', 0),
                    'data_min': '',  # PC Preview中沒有這個資訊
                    'data_max': ''   # PC Preview中沒有這個資訊
                }
            
            # 設定輸出路徑
            if file_name:
                base_name = os.path.splitext(file_name)[0]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"PC_Report_{base_name}_{timestamp}.xlsx"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"ProcessCapability_Report_{timestamp}.xlsx"
            
            # 如果有檔案路徑，在同一目錄下生成報告
            if file_path:
                output_dir = os.path.dirname(file_path)
                output_path = os.path.join(output_dir, output_path)
            
            # 調用原有的Excel生成方法
            return self.generate_excel_report(converted_results, output_path)
            
        except Exception as e:
            error_msg = f"❌ 從PC結果生成Excel報告失敗: {str(e)}"
            print(error_msg)
            return ""
    
    def _format_excel_sheets(self, writer, main_df):
        """格式化Excel工作表"""
        try:
            from openpyxl.styles import Font, Alignment, PatternFill
            from openpyxl.utils.dataframe import dataframe_to_rows
            
            # 取得工作表
            ws = writer.sheets['Process_Capability']
            
            # 設定標題格式
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            
            for cell in ws[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center")
            
            # 調整欄寬
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 20)
                ws.column_dimensions[column_letter].width = adjusted_width
            
        except Exception as e:
            print(f"⚠️ Excel格式化失敗: {str(e)}")
    
    def get_summary_statistics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """取得摘要統計"""
        if not results:
            return {}
        
        summary = {
            'total_variables': len(results),
            'variables_with_specs': 0,
            'average_ppk': 0,
            'min_ppk': float('inf'),
            'max_ppk': float('-inf'),
            'distribution_summary': {}
        }
        
        ppk_values = []
        
        for variable, result in results.items():
            # 統計有規格的變數
            if result.get('lsl') is not None or result.get('usl') is not None:
                summary['variables_with_specs'] += 1
            
            # 收集PPK值
            ppk = result.get('ppk')
            if ppk is not None and not np.isnan(ppk):
                ppk_values.append(ppk)
                summary['min_ppk'] = min(summary['min_ppk'], ppk)
                summary['max_ppk'] = max(summary['max_ppk'], ppk)
            
            # 統計分布類型
            dist = result.get('best_distribution', 'Unknown')
            if dist in summary['distribution_summary']:
                summary['distribution_summary'][dist] += 1
            else:
                summary['distribution_summary'][dist] = 1
        
        # 計算平均PPK
        if ppk_values:
            summary['average_ppk'] = float(np.mean(ppk_values))
        else:
            summary['min_ppk'] = 0
            summary['max_ppk'] = 0
        
        return summary
