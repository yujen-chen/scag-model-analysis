"""
SCAG I-5 Activity-Based Model Analysis Package

This package provides tools for processing and analyzing traffic data
from the SCAG 2024 Activity-Based Model for Interstate 5.

"""

__version__ = "1.0.0"
__author__ = "Yu-Jen Chen"

from .data_loader import DataLoader

# TODO: Import these modules as they are implemented
# from .aadt_calculator import AADTCalculator
# from .peak_hour_analyzer import PeakHourAnalyzer
# from .capacity_analyzer import CapacityAnalyzer
# from .truck_analyzer import TruckAnalyzer
# from .excel_generator import ExcelGenerator

__all__ = [
    "DataLoader",
    # 'AADTCalculator',
    # 'PeakHourAnalyzer',
    # 'CapacityAnalyzer',
    # 'TruckAnalyzer',
    # 'ExcelGenerator'
]
