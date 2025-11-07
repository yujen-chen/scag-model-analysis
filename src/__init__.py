"""
SCAG I-5 Activity-Based Model Analysis Package
SCAG I-5 活動基礎模型分析套件

This package provides tools for processing and analyzing traffic data
from the SCAG 2024 Activity-Based Model for Interstate 5.

此套件提供處理和分析來自 SCAG 2024 活動基礎模型
I-5 州際公路交通資料的工具。
"""

__version__ = '1.0.0'
__author__ = 'Caltrans District 12'
__email__ = 'your.email@dot.ca.gov'

from .data_loader import DataLoader
# TODO: Import these modules as they are implemented
# from .aadt_calculator import AADTCalculator
# from .peak_hour_analyzer import PeakHourAnalyzer
# from .capacity_analyzer import CapacityAnalyzer
# from .truck_analyzer import TruckAnalyzer
# from .excel_generator import ExcelGenerator

__all__ = [
    'DataLoader',
    # 'AADTCalculator',
    # 'PeakHourAnalyzer',
    # 'CapacityAnalyzer',
    # 'TruckAnalyzer',
    # 'ExcelGenerator'
]
