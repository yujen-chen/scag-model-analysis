import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
import logging

from . import config
from .utils import (
    calculate_period_flow,
    calculate_peak_hour_flow,
    log_analysis_step,
    validate_data,
)


class PeakHourAnalyzer:
    """
    This class calculates peak hour flows for AM and PM periods at two levels:
    1. Segment level
    2. Group level

    Attributes:
        df (pd.DataFrame)
        results (Dict)
    """

    def __init__(self, df: pd.DataFrame) -> None:
        """
        Initialize analyzer to calculate peak hour flow

        Args:
        - df: DataFrame containing segment traffic data with flow columns for all time periods (AM, PM, MD, EVE, NT)

        Example:
        >>> df = pd.read_csv('traffic_data.csv')
        >>> analyzer = PeakHourAnalyzer(df)
        """
        self.df = df.copy()
        self.results = {}

    def calculate_segment_peak_flows(self) -> pd.DataFrame:
        """
        Calculate a AM and PM flow for a single road segment (one row)

        This method calculates:
        - AM peak hour total flow (AM_PEAK_TOTAL)
        - AM peak hour auto flow (AM_PEAK_AUTO)
        - AM peak hour truck flow (AM_PEAK_TRUCK)
        - PM peak hour total flow (PM_PEAK_TOTAL)
        - PM peak hour auto flow (PM_PEAK_AUTO)
        - PM peak hour truck flow (PM_PEAK_TRUCK)

        Returns:
            pd.DataFrame: DataFrame with original data plus new peak hour columns

        Example:
            >>> analyzer = PeakHourAnalyzer(df)
            >>> result_df = analyzer.calculate_segment_peak_flows()
            >>> print(result_df[['AM_PEAK_TOTAL', 'PM_PEAK_TOTAL']].head())
        """
        log_analysis_step(
            step_name="Peak Hour Analyzer",
            message="Starting peak hour flow segment calculation",
        )

        for period in ["AM", "PM"]:
            for flow_type in ["total", "auto", "truck"]:
                period_flow = calculate_period_flow(
                    df=self.df, period=period, flow_type=flow_type
                )
                peak_flow = calculate_peak_hour_flow(
                    period_flow=period_flow, period=period
                )
                col_name = f"{period}_PEAK_{flow_type.upper()}"
                self.df[col_name] = peak_flow

        log_analysis_step(
            "Peak Hour Analyzer", f"Calculated peak flows for {len(self.df)} segments"
        )

        return self.df

    def calculate_group_average_peak(
        self, direction: str, facility_type: str, period: str
    ) -> Optional[Dict]:
        """
        Calculate average peak hour flow for a specific group.

        Args:
            direction: Direction code ('N', 'S', 'E', 'W')
            facility_type: Facility type ('ML' for Main Lanes, 'HV' for HOV Lanes)
            period: Time period ('AM' or 'PM')

        Returns:
        dict: Dictionary containing group peak hour statistics:
            {
                'direction': 'N',
                'type': 'ML',
                'period': 'AM',
                'num_segments': 9,
                'avg_peak_total': 8500,
                'avg_peak_auto': 7650,
                'avg_peak_truck': 850,
                'min_peak_total': 7200,
                'max_peak_total': 9800
                }
        Returns None if no data found for the specified combination.
        Example:
        >>> analyzer = PeakHourAnalyzer(df)
        >>> analyzer.calculate_segment_peak_flows()
        >>> result = analyzer.calculate_group_average_peak('N', 'ML', 'AM')
        >>> print(f"Average AM peak: {result['avg_peak_total']:,.0f}")
        """
        mask = (self.df[config.DIRECTION_FIELD] == direction) & (
            self.df[config.TYPE_FIELD] == facility_type
        )
        group_df = self.df[mask]

        # result = {
        #     "direction": direction,
        #     "type": facility_type,
        #     "period": period,
        #     "num_segments": len(group_df),
        #     "avg_peak_total": float(
        #         self.df["AM_PEAK_TOTAL"].mean() + self.df["PM_PEAK_TOTAL"].mean()
        #     ),
        #     "avg_peak_auto": float(
        #         self.df["AM_PEAK_AUTO"].mean() + self.df["PM_PEAK_AUTO"].mean()
        #     ),
        #     "avg_peak_truck": float(
        #         self.df["AM_PEAK_TRUCK"].mean() + self.df["PM_PEAK_TRUCK"].mean()
        #     ),
        #     "min_peak_total": float()
        # }
