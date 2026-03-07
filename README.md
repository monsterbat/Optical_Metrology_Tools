# Optical Metrology Tools

A Python-based desktop application for optical and display measurement data analysis, featuring **Process Capability (PPK)** calculation, **Best Fit Distribution** analysis, and statistical visualization tools.

Designed for engineers working with optical metrology data, this tool automates the workflow from raw measurement data to process capability reports — eliminating the need for expensive commercial statistical software.

## ✨ Features

| Feature | Description |
|---|---|
| **Process Capability (PPK)** | Calculate Ppk/Cpk indices with customizable spec limits (LSL, USL, Target) |
| **Best Fit Distribution** | AICc-based distribution fitting (Normal, LogNormal, Gamma, Weibull, Exponential) |
| **Box Plot Analysis** | Interactive box plot visualization with spec limit overlay |
| **Correlation Analysis** | Scatter plots with regression fitting and R² calculation |
| **Data Preprocessing** | Duplicate removal (AAB logic), outlier exclusion (quantile-based) |
| **JMP Integration** | Generate JMP-compatible JSL scripts; read JMP exports as CSV or Excel |
| **Excel Report Export** | One-click export of analysis results to formatted Excel reports |
| **Spec Limit Setup** | GUI-based specification limit management for multiple variables |

## 🏗️ Architecture

```
Optical_Metrology_Tools/
├── app/                    # Application entry points
│   ├── main.py             # Full version (JMP + Python)
│   ├── main_python.py      # Python-only version (no JMP dependency)
│   └── main_jmp.py         # JMP-dependent version
├── src/
│   ├── core/               # Core computation modules
│   │   ├── pc_calculator.py        # Process Capability calculator
│   │   ├── aicc_calculator.py      # AICc distribution fitting
│   │   ├── data_processor.py       # Data loading & preprocessing
│   │   ├── distribution_fitter.py  # Statistical distribution fitting
│   │   ├── box_plot_analyzer.py    # Box plot analysis engine
│   │   └── correlation_analyzer.py # Correlation analysis engine
│   ├── ui/                 # GUI components (tkinter)
│   ├── io/                 # File I/O operations
│   └── utils/              # Utility modules
├── scripts/jsl/            # JMP Scripting Language scripts
├── config/                 # Configuration files
├── build_tools/            # PyInstaller build specs
└── requirements.txt        # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+ recommended
- JMP (optional, for JMP integration features)

### Installation

```bash
# Clone the repository
git clone https://github.com/monsterbat/Optical_Metrology_Tools.git
cd Optical_Metrology_Tools

# Install dependencies
pip install -r requirements.txt
```

### Run

```bash
# Python-only version (recommended, no JMP required)
python app/main_python.py

# Full version (requires JMP installed)
python app/main.py
```

## 📦 Tech Stack

| Category | Technology |
|---|---|
| Language | Python 3.12+ |
| GUI | tkinter |
| Data Processing | pandas, numpy |
| Statistics | scipy (stats, optimize, special) |
| Visualization | matplotlib |
| Excel I/O | openpyxl |
| JMP File Reader | jmptools by Thomas K. Reynolds (MIT, vendored) |

## 📄 License

This project is for personal and educational purposes.

---

# Optical Metrology Tools（光學量測數據分析工具）

一套基於 Python 的桌面應用程式，專為光學與顯示器量測數據分析而設計，具備 **製程能力 (PPK)** 計算、**最佳擬合分佈** 分析，以及統計可視化工具。

此工具為從事光學量測的工程師設計，能自動化從原始量測數據到製程能力報告的完整流程，無需依賴昂貴的商業統計軟體。

## ✨ 功能特色

| 功能 | 說明 |
|---|---|
| **製程能力 (PPK)** | 計算 Ppk/Cpk 指標，支援自訂規格限制 (LSL、USL、Target) |
| **最佳擬合分佈** | 基於 AICc 的分佈擬合（Normal、LogNormal、Gamma、Weibull、Exponential） |
| **箱形圖分析** | 互動式箱形圖視覺化，可疊加規格限制線 |
| **相關性分析** | 散佈圖搭配迴歸擬合及 R² 計算 |
| **數據前處理** | 重複值移除（AAB 邏輯）、異常值排除（分位數法） |
| **JMP 整合** | 產生 JMP 相容的 JSL 腳本；讀取 JMP 匯出的 CSV 或 Excel |
| **Excel 報告匯出** | 一鍵匯出格式化的分析結果至 Excel |
| **規格限制設定** | 圖形介面管理多變數的規格限制 |

## 🚀 快速開始

### 環境需求

- 建議使用 Python 3.12+
- JMP（選用，僅 JMP 整合功能需要）

### 安裝

```bash
# 複製專案
git clone https://github.com/monsterbat/Optical_Metrology_Tools.git
cd Optical_Metrology_Tools

# 安裝相依套件
pip install -r requirements.txt
```

### 執行

```bash
# Python 獨立版（推薦，不需要安裝 JMP）
python app/main_python.py

# 完整版（需要已安裝 JMP）
python app/main.py
```
