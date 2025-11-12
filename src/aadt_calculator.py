"""
AADT Calculator Module for SCAG I-5 Analysis

This module calculates Annual Average Daily Traffic (AADT) for segments and groups.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import logging

from . import config
from .utils import calculate_aadt, log_analysis_step, validate_data

logger = logging.getLogger(__name__)


class AADTCalculator:
    """
    Calculator for AADT (Annual Average Daily Traffic).

    This class calculates AADT at two levels:
    1. Segment level - AADT for each individual road segment
    2. Group level - Average AADT for groups of continuous segments
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize the calculator with traffic data.

        Args:
            df: DataFrame containing segment traffic data
        """
        self.df = df
        self.results = {}

    def calculate_segment_aadt(self) -> pd.DataFrame:
        """
        Calculate AADT for each section
        """
        total_aadt, auto_aadt, truck_aadt = calculate_aadt(self.df)
        self.df["TOTAL_AADT"] = total_aadt
        self.df["AUTO_AADT"] = auto_aadt
        self.df["TRUCK_AADT"] = truck_aadt

        self.df["TRUCK_PCT"] = np.where(
            self.df["TRUCK_AADT"] > 0,
            (self.df["TRUCK_AADT"] / self.df["TOTAL_AADT"]) * 100,
            0,
        )

        return self.df

    def calculate_group_average_aadt(self, direction: str, type: str) -> Dict:
        """
        Calculate avg AADT for a specific section (direction & type)

        Augs:
        - direction (str): N, S, E, W
        - type (str): ML, HV

        Retrun:
        {
        'direction': 'N',
        'type': 'ML',
        'num_segments': 9,
        'avg_total_aadt': 98646,
        'avg_auto_aadt': 89234,
        'avg_truck_aadt': 9412,
        'avg_truck_pct': 9.5,
        'min_aadt': 85000,
        'max_aadt': 110000
        }
        """

        mask = (self.df[config.DIRECTION_FIELD] == direction) & (
            self.df[config.TYPE_FIELD] == type
        )
        group_df = self.df[mask]

        if len(group_df) == 0:
            logger.warning(f"no data for {direction}-{type}")

        result = {
            "direction": direction,
            "type": type,
            "num_segments": len(group_df),
            "avg_total_aadt": group_df["TOTAL_AADT"].mean(),
            "avg_auto_aadt": group_df["AUTO_AADT"].mean(),
            "avg_truck_aadt": group_df["TRUCK_AADT"].mean(),
            "avg_truck_pct": group_df["TRUCK_PCT"].mean(),
            "min_aadt": group_df["TOTAL_AADT"].min(),
            "max_aadt": group_df["TOTAL_AADT"].max(),
        }

        return result

    def calculate_all_groups(self) -> pd.DataFrame:
        """
        use calculate_group_average_aadt function to generate dataframe

        """
        directions = self.df[config.DIRECTION_FIELD].unique()
        types = self.df[config.TYPE_FIELD].unique()

        results_list = []
        for direction in directions:
            for type in types:
                result = self.calculate_group_average_aadt(direction, type)

                if result:
                    results_list.append(result)

        summary_df = pd.DataFrame(results_list)

        col_names = [
            "direction",
            "type",
            "num_segments",
            "total_aadt",
            "auto_aadt",
            "truck_aadt",
            "truck_pct",
            "min_aadt",
            "max_aadt",
        ]

        summary_df.columns = col_names

        return summary_df

    def get_summary_stats(self) -> Dict:
        """
        Args:
        None

        Return:
        {
          'total_segments': 26,
          'total_aadt_sum': 2340567,
          'avg_aadt': 89945,
          'min_aadt': 12345,
          'max_aadt': 125678,
          'avg_truck_pct': 8.9,
          'directions': 2,
          'facilities': 2
          }
        """
        summary_df = self.calculate_all_groups()
        total_segments = summary_df["num_segments"].sum()
        total_aadt_sum = summary_df["total_aadt"].sum()
        avg_aadt = summary_df["total_aadt"].mean()
        min_aadt = summary_df["total_aadt"].min()
        max_aadt = summary_df["total_aadt"].max()
        avg_truck_pct = summary_df["truck_pct"].mean()
        directions = summary_df["direction"].nunique()
        facilities = summary_df["type"].nunique()
        summary_dict = {
            "total_segments": total_segments,
            "total_aadt_sum": total_aadt_sum,
            "avg_aadt": avg_aadt,
            "min_aadt": min_aadt,
            "max_aadt": max_aadt,
            "avg_truck_pct": avg_truck_pct,
            "directions": directions,
            "facilities": facilities,
        }
        return summary_dict
