#!/usr/bin/env python3
"""
Process Capability Python Only - Core Module
完全使用Python實現的數據處理和過程能力分析
Author: SC Hsiao
Version: 1.0
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class PythonPCCore:
    """Pure Python Process Capability Analysis Core Class"""
    
    def __init__(self):
        self.raw_data = None
        self.processed_data = None
        self.limits_data = None
        self.selected_variables = []  # 使用者在介面上自己選
        self.file_path = None
        self.file_name = None
        
        # 預設column names (based on JSL script)
        self.sn_col_name = "SerialNumber"
        self.judge_col_name = "OverallResult"
        self.date_col_name = "StartTime"
        self.pass_values = ["PASS"]
        self.fail_values = ["FAIL"]
        
        # Outlier detection parameters
        self.tail_quantile = 0.1
        self.q_value = 3
        
    def load_data_file(self, file_path: str, sheet_name: str = None, data_start_row: int = 1) -> bool:
        """
        載入CSV或Excel檔案
        
        Args:
            file_path: 檔案路徑
            sheet_name: Excel工作表名稱 (CSV檔案時為None)
            data_start_row: 數據開始行號 (0-based, 預設為1即第二行)
        
        Returns:
            bool: 載入成功返回True
        """
        try:
            self.file_path = file_path
            self.file_name = os.path.splitext(os.path.basename(file_path))[0]
            
            if file_path.lower().endswith('.csv'):
                # 讀取CSV檔案
                if data_start_row > 0:
                    # data_start_row是1-based，轉換為0-based，然後跳過從第1行到data_start_row-1行
                    skip_rows = list(range(1, data_start_row)) if data_start_row > 1 else None
                    self.raw_data = pd.read_csv(file_path, header=0, skiprows=skip_rows)
                else:
                    self.raw_data = pd.read_csv(file_path)
            elif file_path.lower().endswith(('.xlsx', '.xls')):
                # 讀取Excel檔案
                if data_start_row > 0:
                    # data_start_row是1-based，轉換為0-based，然後跳過從第1行到data_start_row-1行
                    skip_rows = list(range(1, data_start_row)) if data_start_row > 1 else None
                    if sheet_name:
                        self.raw_data = pd.read_excel(file_path, sheet_name=sheet_name, header=0, skiprows=skip_rows)
                    else:
                        self.raw_data = pd.read_excel(file_path, header=0, skiprows=skip_rows)
                else:
                    if sheet_name:
                        self.raw_data = pd.read_excel(file_path, sheet_name=sheet_name)
                    else:
                        self.raw_data = pd.read_excel(file_path)
            else:
                raise ValueError("不支援的檔案格式，請使用CSV或Excel檔案")
            
            # 初始化processed_data
            self.processed_data = self.raw_data.copy()
            
            print(f"✅ 成功載入檔案: {os.path.basename(file_path)}")
            print(f"   數據形狀: {self.raw_data.shape}")
            print(f"   欄位: {list(self.raw_data.columns)}")
            
            return True
            
        except Exception as e:
            print(f"❌ 載入檔案失敗: {str(e)}")
            return False
    
    def get_excel_sheets(self, file_path: str) -> List[str]:
        """取得Excel檔案的所有工作表名稱"""
        try:
            if file_path.lower().endswith(('.xlsx', '.xls')):
                excel_file = pd.ExcelFile(file_path)
                return excel_file.sheet_names
            else:
                return []
        except Exception:
            return []
    
    def get_columns(self) -> List[str]:
        """取得當前數據的所有欄位名稱"""
        if self.raw_data is not None:
            return list(self.raw_data.columns)
        return []
    
    def validate_required_columns(self) -> bool:
        """驗證必要欄位是否存在"""
        if self.processed_data is None:
            return False
        
        columns = list(self.processed_data.columns)
        missing_cols = []
        
        print(f"🔍 檢查必要欄位...")
        print(f"   尋找欄位: {self.sn_col_name}, {self.judge_col_name}, {self.date_col_name}")
        print(f"   可用欄位前10個: {columns[:10]}")
        
        if self.sn_col_name not in columns:
            missing_cols.append(self.sn_col_name)
        else:
            print(f"   ✅ 找到 {self.sn_col_name}")
            
        if self.judge_col_name not in columns:
            missing_cols.append(self.judge_col_name)
        else:
            print(f"   ✅ 找到 {self.judge_col_name}")
            
        if self.date_col_name not in columns:
            missing_cols.append(self.date_col_name)
        else:
            print(f"   ✅ 找到 {self.date_col_name}")
        
        if missing_cols:
            print(f"❌ 缺少必要欄位: {missing_cols}")
            # 嘗試尋找類似的欄位名稱
            for missing_col in missing_cols:
                similar_cols = []
                for col in columns:
                    # 確保col是字串類型
                    col_str = str(col)
                    missing_col_str = str(missing_col)
                    if (missing_col_str.lower() in col_str.lower() or 
                        col_str.lower() in missing_col_str.lower()):
                        similar_cols.append(col_str)
                        
                if similar_cols:
                    print(f"   可能的相似欄位 ({missing_col}): {similar_cols}")
            return False
        
        print(f"✅ 所有必要欄位都存在")
        return True
    
    def exclude_duplicates(self) -> Tuple[bool, str]:
        """
        移除重複值 - 實現完整的AAB規則
        按照JSL邏輯: 先按出現順序分組，再按時間排序，最後應用AAB規則
        
        Returns:
            Tuple[bool, str]: (成功/失敗, 訊息)
        """
        if not self.validate_required_columns():
            return False, "Missing required columns"
        
        try:
            # 記錄原始數據量
            original_count = len(self.processed_data)
            
            print(f"🔄 開始AAB重複值移除處理...")
            print(f"   原始數據: {original_count} 筆")
            
            # 步驟1: 添加原始索引以保持出現順序
            self.processed_data = self.processed_data.reset_index(drop=True)
            self.processed_data['Original_Index'] = self.processed_data.index
            
            # 步驟2: 解析和處理時間欄位
            print(f"📅 處理時間欄位...")
            self.processed_data['Parsed_DateTime'] = None
            
            for idx, row in self.processed_data.iterrows():
                time_str = str(row[self.date_col_name])
                parsed_time = self._parse_datetime_string(time_str)
                self.processed_data.at[idx, 'Parsed_DateTime'] = parsed_time
            
            # 步驟3: 自定義排序邏輯
            print(f"🔄 執行自定義排序...")
            self._custom_sort_for_aab()
            
            # 步驟4: 計算重複次數
            print(f"📊 計算重複次數...")
            self._calculate_duplicate_numbers()
            
            # 步驟5: 應用AAB邏輯
            print(f"⚖️ 應用AAB判斷邏輯...")
            self._apply_aab_logic()
            
            # 步驟6: 移除被排除的數據
            excluded_rows = self.processed_data[self.processed_data['Duplicate_G'] == "Excluded"]
            excluded_count = len(excluded_rows)
            
            # 儲存被排除的重複值
            if excluded_count > 0:
                self._save_excluded_data(excluded_rows, "duplicate")
            
            # 從主數據中移除被排除的行
            self.processed_data = self.processed_data[self.processed_data['Duplicate_G'] != "Excluded"]
            
            # 清理臨時欄位
            cols_to_drop = ['Original_Index', 'Parsed_DateTime', 'Duplicate', 'Duplicate_G']
            existing_cols = [col for col in cols_to_drop if col in self.processed_data.columns]
            if existing_cols:
                self.processed_data = self.processed_data.drop(existing_cols, axis=1)
            
            final_count = len(self.processed_data)
            
            message = f"✅ AAB duplicate removal completed\n"
            message += f"   Original data: {original_count} records\n"
            message += f"   Removed duplicates: {excluded_count} records\n"
            message += f"   Remaining data: {final_count} records"
            
            print(message)
            return True, message
            
        except Exception as e:
            error_msg = f"❌ AAB duplicate removal failed: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return False, error_msg
    
    def _parse_datetime_string(self, time_str: str):
        """解析時間字串，格式: 20250118-174934"""
        try:
            if pd.isna(time_str) or time_str == 'nan' or time_str.strip() == '':
                return None
            
            # 移除可能的時間部分，只保留日期時間格式
            time_str = str(time_str).strip()
            
            # 檢查格式: YYYYMMDD-HHMMSS
            if len(time_str) >= 15 and '-' in time_str:
                date_part, time_part = time_str.split('-', 1)
                if len(date_part) == 8 and len(time_part) >= 6:
                    # 解析為datetime
                    year = int(date_part[:4])
                    month = int(date_part[4:6])
                    day = int(date_part[6:8])
                    hour = int(time_part[:2])
                    minute = int(time_part[2:4])
                    second = int(time_part[4:6])
                    
                    return pd.Timestamp(year, month, day, hour, minute, second)
            
            return None
            
        except Exception:
            return None
    
    def _custom_sort_for_aab(self):
        """自定義排序: 先按SN出現順序分組，再按時間排序"""
        
        # 為每個SN分配首次出現的索引
        sn_first_appearance = {}
        for idx, row in self.processed_data.iterrows():
            sn = row[self.sn_col_name]
            if sn not in sn_first_appearance:
                sn_first_appearance[sn] = row['Original_Index']
        
        self.processed_data['SN_First_Appearance'] = self.processed_data[self.sn_col_name].map(sn_first_appearance)
        
        # 創建排序鍵
        def create_sort_key(row):
            sn_order = row['SN_First_Appearance']  # SN出現順序
            parsed_time = row['Parsed_DateTime']   # 解析的時間
            original_idx = row['Original_Index']   # 原始檔案順序
            
            # 如果有時間，用時間排序；否則用原始順序
            if pd.notna(parsed_time):
                time_key = parsed_time
            else:
                # 對於沒有時間的記錄，用一個很大的數字確保排在後面
                time_key = pd.Timestamp('2999-12-31') + pd.Timedelta(seconds=original_idx)
            
            return (sn_order, time_key, original_idx)
        
        # 應用排序
        sort_keys = self.processed_data.apply(create_sort_key, axis=1)
        sort_indices = sorted(range(len(sort_keys)), key=lambda i: sort_keys.iloc[i])
        
        self.processed_data = self.processed_data.iloc[sort_indices].reset_index(drop=True)
        
        # 清理臨時欄位
        self.processed_data = self.processed_data.drop('SN_First_Appearance', axis=1)
    
    def _calculate_duplicate_numbers(self):
        """計算每個SN的重複次數"""
        duplicate_numbers = []
        sn_counts = {}
        
        for idx, row in self.processed_data.iterrows():
            sn = row[self.sn_col_name]
            if sn in sn_counts:
                sn_counts[sn] += 1
            else:
                sn_counts[sn] = 1
            duplicate_numbers.append(sn_counts[sn])
        
        self.processed_data['Duplicate'] = duplicate_numbers
    
    def _apply_aab_logic(self):
        """應用AAB邏輯判斷哪些數據要被移除"""
        
        # 初始化Duplicate_G欄位
        self.processed_data['Duplicate_G'] = ""
        
        # 取得所有唯一的SN
        unique_sns = self.processed_data[self.sn_col_name].unique()
        
        for sn in unique_sns:
            # 取得該SN的所有記錄
            sn_data = self.processed_data[self.processed_data[self.sn_col_name] == sn].copy()
            sn_indices = sn_data.index.tolist()
            
            # 取得該SN的重複數量
            max_duplicate = sn_data['Duplicate'].max()
            
            if max_duplicate == 1:
                # 只有一筆記錄，直接保留
                judge_val = str(sn_data.iloc[0][self.judge_col_name])
                if judge_val in self.pass_values:
                    self.processed_data.loc[sn_indices[0], 'Duplicate_G'] = "Done"
                else:
                    self.processed_data.loc[sn_indices[0], 'Duplicate_G'] = "Unclear"
                    
            elif max_duplicate <= 3:
                # 2-3筆記錄，應用AAB邏輯
                self._apply_aab_for_group(sn_data, sn_indices)
                
            else:
                # 超過3筆，移除第4筆以後的所有記錄
                for i, idx in enumerate(sn_indices):
                    duplicate_num = self.processed_data.loc[idx, 'Duplicate']
                    if duplicate_num <= 3:
                        # 前3筆應用AAB邏輯
                        if i == 0:  # 暫時設定，稍後會被AAB邏輯覆蓋
                            judge_val = str(self.processed_data.loc[idx, self.judge_col_name])
                            if judge_val in self.pass_values:
                                self.processed_data.loc[idx, 'Duplicate_G'] = "Done"
                            else:
                                self.processed_data.loc[idx, 'Duplicate_G'] = "Unclear"
                    else:
                        # 第4筆以後全部移除
                        self.processed_data.loc[idx, 'Duplicate_G'] = "Excluded"
                
                # 對前3筆應用AAB邏輯
                first_three = sn_data[sn_data['Duplicate'] <= 3]
                first_three_indices = first_three.index.tolist()
                self._apply_aab_for_group(first_three, first_three_indices)
    
    def _apply_aab_for_group(self, group_data, indices):
        """對一組數據(同一個SN的2-3筆記錄)應用AAB邏輯"""
        
        max_duplicate = group_data['Duplicate'].max()
        
        if max_duplicate == 2:
            # 處理2筆記錄的情況
            first_record = group_data[group_data['Duplicate'] == 1].iloc[0]
            second_record = group_data[group_data['Duplicate'] == 2].iloc[0]
            
            first_idx = first_record.name
            second_idx = second_record.name
            
            first_judge = str(self.processed_data.loc[first_idx, self.judge_col_name])
            second_judge = str(self.processed_data.loc[second_idx, self.judge_col_name])
            
            first_is_pass = first_judge in self.pass_values
            second_is_pass = second_judge in self.pass_values
            
            # AAB邏輯：優先保留PASS，如果都是PASS則保留最新的
            if first_is_pass and second_is_pass:
                # 兩筆都是PASS，保留第2筆(最新)，移除第1筆
                self.processed_data.loc[second_idx, 'Duplicate_G'] = "Done"
                self.processed_data.loc[first_idx, 'Duplicate_G'] = "Excluded"
            elif second_is_pass:
                # 第2筆是PASS，第1筆是FAIL，保留第2筆，移除第1筆
                self.processed_data.loc[second_idx, 'Duplicate_G'] = "Done"
                self.processed_data.loc[first_idx, 'Duplicate_G'] = "Excluded"
            elif first_is_pass:
                # 第1筆是PASS，第2筆是FAIL，保留第1筆，移除第2筆
                self.processed_data.loc[first_idx, 'Duplicate_G'] = "Done"
                self.processed_data.loc[second_idx, 'Duplicate_G'] = "Excluded"
            else:
                # 兩筆都是FAIL，保留第2筆(最新)，移除第1筆
                self.processed_data.loc[second_idx, 'Duplicate_G'] = "Unclear"
                self.processed_data.loc[first_idx, 'Duplicate_G'] = "Excluded"
                
        elif max_duplicate == 3:
            # 處理3筆記錄的情況
            first_record = group_data[group_data['Duplicate'] == 1].iloc[0]
            second_record = group_data[group_data['Duplicate'] == 2].iloc[0]
            third_record = group_data[group_data['Duplicate'] == 3].iloc[0]
            
            first_idx = first_record.name
            second_idx = second_record.name
            third_idx = third_record.name
            
            first_judge = str(self.processed_data.loc[first_idx, self.judge_col_name])
            second_judge = str(self.processed_data.loc[second_idx, self.judge_col_name])
            third_judge = str(self.processed_data.loc[third_idx, self.judge_col_name])
            
            first_is_pass = first_judge in self.pass_values
            second_is_pass = second_judge in self.pass_values
            third_is_pass = third_judge in self.pass_values
            
            # AAB邏輯：優先保留PASS，如果有多個PASS則保留最新的
            if third_is_pass:
                # 第3筆是PASS，保留第3筆(最新)，移除其他
                self.processed_data.loc[third_idx, 'Duplicate_G'] = "Done"
                self.processed_data.loc[first_idx, 'Duplicate_G'] = "Excluded"
                self.processed_data.loc[second_idx, 'Duplicate_G'] = "Excluded"
            elif second_is_pass:
                # 第3筆是FAIL，第2筆是PASS，保留第2筆，移除其他
                self.processed_data.loc[second_idx, 'Duplicate_G'] = "Done"
                self.processed_data.loc[first_idx, 'Duplicate_G'] = "Excluded"
                self.processed_data.loc[third_idx, 'Duplicate_G'] = "Excluded"
            elif first_is_pass:
                # 第3筆、第2筆都是FAIL，第1筆是PASS，保留第1筆，移除其他
                self.processed_data.loc[first_idx, 'Duplicate_G'] = "Done"
                self.processed_data.loc[second_idx, 'Duplicate_G'] = "Excluded"
                self.processed_data.loc[third_idx, 'Duplicate_G'] = "Excluded"
            else:
                # 三筆都是FAIL，保留第3筆(最新)，移除其他
                self.processed_data.loc[third_idx, 'Duplicate_G'] = "Unclear"
                self.processed_data.loc[first_idx, 'Duplicate_G'] = "Excluded"
                self.processed_data.loc[second_idx, 'Duplicate_G'] = "Excluded"
    
    def load_spec_limits(self, limits_file_path: str) -> Tuple[bool, str]:
        """
        載入規格限制檔案
        
        Args:
            limits_file_path: limits檔案路徑
            
        Returns:
            Tuple[bool, str]: (成功/失敗, 訊息)
        """
        try:
            if limits_file_path.lower().endswith('.csv'):
                limits_df = pd.read_csv(limits_file_path)
            elif limits_file_path.lower().endswith(('.xlsx', '.xls')):
                limits_df = pd.read_excel(limits_file_path)
            else:
                return False, "Unsupported file format"
            
            # 驗證limits檔案格式
            required_cols = ['Variable', 'LSL', 'USL', 'Target']
            if not all(col in limits_df.columns for col in required_cols):
                return False, f"Limits file must contain columns: {required_cols}"
            
            self.limits_data = limits_df
            
            message = f"✅ Successfully loaded spec limits file\n"
            message += f"   Number of variables: {len(limits_df)}\n"
            message += f"   Variables: {list(limits_df['Variable'].values)}"
            
            print(message)
            return True, message
            
        except Exception as e:
            error_msg = f"❌ Failed to load spec limits file: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    def exclude_outliers(self, tail_quantile: float = None, q_value: float = None) -> Tuple[bool, str]:
        """
        移除異常值 - 使用quantile-based方法
        
        Args:
            tail_quantile: 尾部分位數 (預設0.1)
            q_value: Q值 (預設3)
            
        Returns:
            Tuple[bool, str]: (成功/失敗, 訊息)
        """
        if self.processed_data is None:
            return False, "沒有可處理的數據"
        
        # 使用傳入的參數或預設值
        if tail_quantile is not None:
            self.tail_quantile = tail_quantile
        if q_value is not None:
            self.q_value = q_value
        
        try:
            original_count = len(self.processed_data)
            outlier_indices = set()
            
            # 只對選定的分析變數進行異常值檢測，而不是所有數值型欄位
            analysis_variables = self.get_analysis_variables()
            
            print(f"🔍 對以下變數進行異常值檢測: {analysis_variables}")
            
            for col in analysis_variables:
                if col in self.processed_data.columns:
                    data = self.processed_data[col].dropna()
                    
                    if len(data) > 0:
                        # 計算分位數
                        lower_quantile = self.tail_quantile
                        upper_quantile = 1 - self.tail_quantile
                        
                        q_low = data.quantile(lower_quantile)
                        q_high = data.quantile(upper_quantile)
                        
                        # 計算IQR和outlier閾值
                        iqr = q_high - q_low
                        lower_bound = q_low - self.q_value * iqr
                        upper_bound = q_high + self.q_value * iqr
                        
                        # 找出outliers
                        col_outliers = self.processed_data[
                            (self.processed_data[col] < lower_bound) | 
                            (self.processed_data[col] > upper_bound)
                        ].index
                        
                        outlier_indices.update(col_outliers)
                        
                        if len(col_outliers) > 0:
                            print(f"   變數 {col}: 發現 {len(col_outliers)} 個異常值 (界限: {lower_bound:.6f} ~ {upper_bound:.6f})")
                        else:
                            print(f"   變數 {col}: 無異常值")
                else:
                    print(f"   ⚠️ 變數 {col} 不存在於數據中")
            
            # 提取outlier數據
            if outlier_indices:
                outlier_data = self.processed_data.loc[list(outlier_indices)]
                self._save_excluded_data(outlier_data, "outlier")
                
                # 從主數據中移除outliers
                self.processed_data = self.processed_data.drop(list(outlier_indices))
            
            outlier_count = len(outlier_indices)
            final_count = len(self.processed_data)
            
            message = f"✅ Outlier removal completed\n"
            message += f"   Original data: {original_count} records\n"
            message += f"   Removed outliers: {outlier_count} records\n"
            message += f"   Remaining data: {final_count} records\n"
            message += f"   Parameters: Tail Quantile={self.tail_quantile}, Q={self.q_value}"
            
            print(message)
            return True, message
            
        except Exception as e:
            error_msg = f"❌ Outlier removal failed: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    def _save_excluded_data(self, excluded_data: pd.DataFrame, data_type: str):
        """儲存被排除的數據"""
        try:
            if self.file_path and len(excluded_data) > 0:
                # 生成檔案名稱
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_name = f"{self.file_name}_{timestamp}_{data_type}_data.csv"
                output_path = os.path.join(os.path.dirname(self.file_path), output_name)
                
                # 儲存CSV檔案
                excluded_data.to_csv(output_path, index=False)
                print(f"📁 已儲存{data_type}數據: {output_name}")
                
        except Exception as e:
            print(f"⚠️ 儲存{data_type}數據失敗: {str(e)}")
    
    def set_analysis_variables(self, variables: List[str]):
        """設定要分析的變數"""
        if self.processed_data is not None:
            available_vars = list(self.processed_data.columns)
            valid_vars = [var for var in variables if var in available_vars]
            
            if valid_vars:
                self.selected_variables = valid_vars
                print(f"✅ 已設定分析變數: {self.selected_variables}")
            else:
                print(f"❌ 沒有找到有效的分析變數")
        else:
            self.selected_variables = variables
    
    def get_analysis_variables(self) -> List[str]:
        """取得目前設定的分析變數"""
        return self.selected_variables.copy()
    
    def get_available_variables(self) -> List[str]:
        """取得所有可用的數值型變數"""
        if self.processed_data is not None:
            numeric_columns = self.processed_data.select_dtypes(include=[np.number]).columns
            # 排除系統欄位
            system_cols = [self.sn_col_name, self.judge_col_name, self.date_col_name]
            return [col for col in numeric_columns if col not in system_cols]
        return []
    
    def get_data_summary(self) -> Dict[str, Any]:
        """取得數據摘要資訊"""
        if self.processed_data is None:
            return {}
        
        summary = {
            'total_records': len(self.processed_data),
            'total_columns': len(self.processed_data.columns),
            'numeric_columns': len(self.get_available_variables()),
            'selected_variables': self.selected_variables.copy(),
            'has_limits': self.limits_data is not None
        }
        
        if self.limits_data is not None:
            summary['limits_variables'] = list(self.limits_data['Variable'].values)
        
        return summary
