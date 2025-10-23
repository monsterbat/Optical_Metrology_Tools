#!/usr/bin/env python3
"""
標準化 AICc 計算器
嚴格遵循學術標準和 AIAG/ISO 規範
"""

import numpy as np
from scipy import stats
from scipy.optimize import minimize
from scipy.special import gammaln
from typing import Tuple, Optional, Dict, Any
import warnings
warnings.filterwarnings('ignore')

class AICcCalculator:
    """
    標準化 AICc 計算器
    - 嚴格遵循 AICc = -2*ln(L) + 2k + (2k(k+1))/(n-k-1)
    - 無任何人為調整
    - 支援多種分布的標準 MLE 擬合
    """
    
    def __init__(self):
        self.results = {}
        
    def calculate_aicc(self, log_likelihood: float, n_params: int, n_samples: int) -> float:
        """
        標準 AICc 公式 (Akaike, 1974; Burnham & Anderson, 2002)
        AICc = -2*ln(L) + 2k + (2k(k+1))/(n-k-1)
        """
        if n_samples <= n_params + 1:
            return np.inf
        
        aic = -2 * log_likelihood + 2 * n_params
        correction = (2 * n_params * (n_params + 1)) / (n_samples - n_params - 1)
        return aic + correction
    
    def fit_normal(self, data) -> Tuple[Optional[Dict], float]:
        """標準正態分布擬合 (μ, σ)"""
        try:
            clean_data = data.dropna()
            if len(clean_data) < 3:
                return None, np.inf
            
            # 使用 scipy.stats.norm.fit (MLE)
            mu, sigma = stats.norm.fit(clean_data)
            log_likelihood = np.sum(stats.norm.logpdf(clean_data, mu, sigma))
            aicc = self.calculate_aicc(log_likelihood, 2, len(clean_data))  # k=2 (μ, σ)
            
            return {"mu": mu, "sigma": sigma}, aicc
        except Exception:
            return None, np.inf
    
    def fit_lognormal(self, data) -> Tuple[Optional[Dict], float]:
        """標準對數正態分布擬合"""
        try:
            clean_data = data.dropna()
            if len(clean_data) < 3 or np.any(clean_data <= 0):
                return None, np.inf
            
            # 方法1: 對數空間 MLE (JMP 標準方法)
            log_data = np.log(clean_data)
            mu_log = np.mean(log_data)
            sigma_log = np.std(log_data, ddof=1)  # 樣本標準差
            
            log_likelihood = np.sum(stats.lognorm.logpdf(clean_data, s=sigma_log, scale=np.exp(mu_log)))
            aicc = self.calculate_aicc(log_likelihood, 2, len(clean_data))  # k=2 (μ_log, σ_log)
            
            return {"mu_log": mu_log, "sigma_log": sigma_log}, aicc
        except Exception:
            return None, np.inf
    
    def fit_gamma(self, data) -> Tuple[Optional[Dict], float]:
        """JMP 完全相容的 Gamma 分布擬合"""
        try:
            clean_data = data.dropna()
            if len(clean_data) < 3 or np.any(clean_data <= 0):
                return None, np.inf
            
            # JMP Gamma 參數化: f(x; α, σ) = (1/(Γ(α)*σ^α)) * x^(α-1) * exp(-x/σ)
            # 這裡 α=shape, σ=scale
            # E(X) = α*σ, Var(X) = α*σ²
            
            # 使用 MLE（與 JMP 一致）
            # scipy.stats.gamma 使用參數化: f(x; a, scale) = x^(a-1) * exp(-x/scale) / (scale^a * Γ(a))
            # 這與 JMP 的參數化完全一致：a=α, scale=σ
            
            alpha_mle, loc, sigma_mle = stats.gamma.fit(clean_data, floc=0)
            
            # 驗證參數合理性
            if alpha_mle <= 0 or sigma_mle <= 0:
                return None, np.inf
            
            # 使用 JMP 的 PDF 公式計算 log-likelihood
            # log(f(x)) = (α-1)*log(x) - x/σ - α*log(σ) - log(Γ(α))
            log_likelihood = 0
            for x in clean_data:
                if x <= 0:
                    return None, np.inf
                log_likelihood += ((alpha_mle - 1) * np.log(x) 
                                 - x / sigma_mle 
                                 - alpha_mle * np.log(sigma_mle) 
                                 - gammaln(alpha_mle))
            
            # 檢查 log-likelihood 有效性
            if not np.isfinite(log_likelihood):
                return None, np.inf
                
            aicc = self.calculate_aicc(log_likelihood, 2, len(clean_data))
            
            return {"alpha": alpha_mle, "sigma": sigma_mle}, aicc
            
        except Exception:
            return None, np.inf
    
    def fit_weibull(self, data) -> Tuple[Optional[Dict], float]:
        """JMP 完全相容的 Weibull 分布擬合"""
        try:
            clean_data = data.dropna()
            if len(clean_data) < 3 or np.any(clean_data <= 0):
                return None, np.inf
            
            # JMP Weibull 參數化: f(x; α, β) = (β/α^β) * x^(β-1) * exp(-(x/α)^β)
            # 其中 α=scale, β=shape
            # E(X) = α * Γ(1 + 1/β), Var(X) = α² * [Γ(1 + 2/β) - (Γ(1 + 1/β))²]
            
            # 使用 MLE（與 JMP 一致）
            # scipy.stats.weibull_min 的參數化與 JMP 一致
            beta_mle, loc, alpha_mle = stats.weibull_min.fit(clean_data, floc=0)
            
            # 驗證參數合理性
            if beta_mle <= 0 or alpha_mle <= 0:
                return None, np.inf
            
            # 使用 JMP 的 PDF 公式計算 log-likelihood
            # log(f(x)) = log(β) - β*log(α) + (β-1)*log(x) - (x/α)^β
            log_likelihood = 0
            for x in clean_data:
                if x <= 0:
                    return None, np.inf
                log_likelihood += (np.log(beta_mle) 
                                 - beta_mle * np.log(alpha_mle) 
                                 + (beta_mle - 1) * np.log(x) 
                                 - np.power(x / alpha_mle, beta_mle))
            
            # 檢查 log-likelihood 有效性
            if not np.isfinite(log_likelihood):
                return None, np.inf
                
            aicc = self.calculate_aicc(log_likelihood, 2, len(clean_data))
            
            return {"alpha": alpha_mle, "beta": beta_mle}, aicc
            
        except Exception:
            return None, np.inf
    
    def fit_exponential(self, data) -> Tuple[Optional[Dict], float]:
        """JMP 完全相容的指數分布擬合"""
        try:
            clean_data = data.dropna()
            if len(clean_data) < 2 or np.any(clean_data <= 0):
                return None, np.inf
            
            # JMP Exponential 參數化: f(x; σ) = (1/σ) * exp(-x/σ)
            # 其中 σ=scale, E(X) = σ, Var(X) = σ²
            
            # MLE 估計: σ_mle = sample_mean
            sigma_mle = np.mean(clean_data)
            
            if sigma_mle <= 0:
                return None, np.inf
            
            # 使用 JMP 的 PDF 公式計算 log-likelihood
            # log(f(x)) = -log(σ) - x/σ
            log_likelihood = 0
            for x in clean_data:
                if x <= 0:
                    return None, np.inf
                log_likelihood += (-np.log(sigma_mle) - x / sigma_mle)
            
            # 檢查 log-likelihood 有效性
            if not np.isfinite(log_likelihood):
                return None, np.inf
                
            aicc = self.calculate_aicc(log_likelihood, 1, len(clean_data))  # k=1 (只有 σ)
            
            return {"sigma": sigma_mle}, aicc
            
        except Exception:
            return None, np.inf
    
# ========================================
# Notebook 版本的分佈擬合方法
# 使用 scipy 的直接 fit() 和 logpdf() 方法
# 用於比較與我們方法的差異
# ========================================
    
    def fit_normal_notebook(self, data) -> Tuple[Optional[Dict], float]:
        """Notebook 版本：Normal 分布擬合"""
        try:
            clean_data = data.dropna()
            if len(clean_data) < 3:
                return None, np.inf
            
            # 使用 scipy.stats.norm.fit() - 與 Notebook 完全相同
            parameter = stats.norm.fit(clean_data)
            log_likelihood = np.sum(stats.norm.logpdf(clean_data, *parameter))
            
            # 計算參數數量
            n_params = len(parameter)  # 通常是 2 (loc, scale)
            aicc = self.calculate_aicc(log_likelihood, n_params, len(clean_data))
            
            return {"parameters": parameter}, aicc
        except Exception:
            return None, np.inf
    
    def fit_lognormal_notebook(self, data) -> Tuple[Optional[Dict], float]:
        """Notebook 版本：Lognormal 分布擬合"""
        try:
            clean_data = data.dropna()
            if len(clean_data) < 3 or np.any(clean_data <= 0):
                return None, np.inf
            
            # 使用 scipy.stats.lognorm.fit() - 與 Notebook 完全相同
            parameter = stats.lognorm.fit(clean_data)
            log_likelihood = np.sum(stats.lognorm.logpdf(clean_data, *parameter))
            
            # 計算參數數量
            n_params = len(parameter)  # 通常是 3 (s, loc, scale)
            aicc = self.calculate_aicc(log_likelihood, n_params, len(clean_data))
            
            return {"parameters": parameter}, aicc
        except Exception:
            return None, np.inf
    
    def fit_gamma_notebook(self, data) -> Tuple[Optional[Dict], float]:
        """Notebook 版本：Gamma 分布擬合"""
        try:
            clean_data = data.dropna()
            if len(clean_data) < 3 or np.any(clean_data <= 0):
                return None, np.inf
            
            # 使用 scipy.stats.gamma.fit() - 與 Notebook 完全相同
            parameter = stats.gamma.fit(clean_data)
            log_likelihood = np.sum(stats.gamma.logpdf(clean_data, *parameter))
            
            # 計算參數數量
            n_params = len(parameter)  # 通常是 3 (a, loc, scale)
            aicc = self.calculate_aicc(log_likelihood, n_params, len(clean_data))
            
            return {"parameters": parameter}, aicc
        except Exception:
            return None, np.inf
    
    def fit_weibull_notebook(self, data) -> Tuple[Optional[Dict], float]:
        """Notebook 版本：Weibull 分布擬合"""
        try:
            clean_data = data.dropna()
            if len(clean_data) < 3 or np.any(clean_data <= 0):
                return None, np.inf
            
            # 使用 scipy.stats.weibull_min.fit() - 與 Notebook 完全相同
            parameter = stats.weibull_min.fit(clean_data)
            log_likelihood = np.sum(stats.weibull_min.logpdf(clean_data, *parameter))
            
            # 計算參數數量
            n_params = len(parameter)  # 通常是 3 (c, loc, scale)
            aicc = self.calculate_aicc(log_likelihood, n_params, len(clean_data))
            
            return {"parameters": parameter}, aicc
        except Exception:
            return None, np.inf
    
    def fit_exponential_notebook(self, data) -> Tuple[Optional[Dict], float]:
        """Notebook 版本：Exponential 分布擬合"""
        try:
            clean_data = data.dropna()
            if len(clean_data) < 2 or np.any(clean_data <= 0):
                return None, np.inf
            
            # 使用 scipy.stats.expon.fit() - 與 Notebook 完全相同
            parameter = stats.expon.fit(clean_data)
            log_likelihood = np.sum(stats.expon.logpdf(clean_data, *parameter))
            
            # 計算參數數量
            n_params = len(parameter)  # 通常是 2 (loc, scale)
            aicc = self.calculate_aicc(log_likelihood, n_params, len(clean_data))
            
            return {"parameters": parameter}, aicc
        except Exception:
            return None, np.inf

# ========================================
# 以上支援的分布：
# 1. 我們的方法（JMP 標準）: Normal, LogNormal, Gamma, Weibull, Exponential
# 2. Notebook 方法: Normal, LogNormal, Gamma, Weibull, Exponential
# 總共 10 個分布可供比較
# ========================================

    def calculate_all_distributions(self, data, column_name=""):
        """
        計算所有分布的AICc值
        包含我們的方法（JMP標準）和 Notebook 方法，用於比較
        """
        distributions = {
            # 我們的方法（JMP 標準 - 固定 loc=0，手動計算 log-likelihood）
            "Normal": self.fit_normal,
            "LogNormal": self.fit_lognormal, 
            "Gamma": self.fit_gamma,
            "Weibull": self.fit_weibull,
            "Exponential": self.fit_exponential,
            
            # Notebook 方法（使用 scipy 的 fit() 和 logpdf()）
            "Normal (Notebook)": self.fit_normal_notebook,
            "LogNormal (Notebook)": self.fit_lognormal_notebook,
            "Gamma (Notebook)": self.fit_gamma_notebook,
            "Weibull (Notebook)": self.fit_weibull_notebook,
            "Exponential (Notebook)": self.fit_exponential_notebook,
        }
        
        results = {}
        
        print(f"\n{'='*60}")
        print(f"開始比較分析：{column_name if column_name else '數據'}")
        print(f"{'='*60}")
        
        for name, fit_func in distributions.items():
            try:
                method_type = "Notebook方法" if "(Notebook)" in name else "JMP標準方法"
                print(f"\n🔧 計算 {name} [{method_type}]...")
                params, aicc = fit_func(data)
                
                if params is not None and np.isfinite(aicc):
                    results[name] = aicc
                    print(f"✅ {name} AICc: {aicc:.3f}")
                    if len(str(params)) < 200:  # 避免輸出太長
                        print(f"   參數: {params}")
                else:
                    results[name] = np.inf
                    print(f"❌ {name} 計算失敗")
                    
            except Exception as e:
                print(f"⚠️ {name} 發生錯誤: {e}")
                results[name] = np.inf
        
        # 輸出比較結果
        print(f"\n{'='*60}")
        print("📊 AICc 比較結果（越小越好）")
        print(f"{'='*60}")
        
        # 排序結果
        sorted_results = sorted(results.items(), key=lambda x: x[1])
        
        for rank, (name, aicc_value) in enumerate(sorted_results, 1):
            if np.isfinite(aicc_value):
                print(f"{rank}. {name:30s} AICc = {aicc_value:10.3f}")
            else:
                print(f"   {name:30s} AICc = {'失敗':>10s}")
        
        print(f"{'='*60}\n")
        
        return results


# ========================================
# PPK 計算已移至 pc_preview_dialog.py
# 使用專用的分布計算方法，確保準確性
# ========================================