"""
版本資訊管理模組
集中管理應用程式的版本號、作者和更新日期等資訊
"""

# 應用程式版本資訊
APP_NAME = "Data Analysis Tools"
APP_VERSION = "1.3"
APP_AUTHOR = "SC Hsiao"
APP_UPDATE_DATE = "2025/01/27"
APP_DESCRIPTION = "用於數據分析和處理的工具集"

# 獲取格式化的版本資訊
def get_version_info():
    """返回格式化的版本資訊字串"""
    return f"Version: {APP_VERSION}"
    # return f"Version: {APP_VERSION}        Author: {APP_AUTHOR}"

# 獲取應用程式標題
def get_app_title():
    """返回應用程式標題，包含版本號"""
    return f"{APP_NAME} v{APP_VERSION}" 