"""
Capacity Analyzer Module for SCAG I-5 Analysis

This module calculates capacity, V/C ratios, and Level of Service (LOS) for freeway segments.
"""

import pandas as pd
import numpy as np

from typing import Dict, Tuple, Optional
import logging

from . import config
from .utils import (
    calculate_pce_flow,
    calculate_capacity,
    calculate_vc_ratio,
    get_los_from_vc,
    log_analysis_step,
    validate_data,
)

logger = logging.getLogger(__name__)


class CapacityAnalyzer:
    """
    Analyzer for roadway capacity and Level of Service (LOS).

    This class calculates capacity-related metrics for AM and PM periods at two levels:
    1. Segment level - Capacity, V/C ratio, and LOS for each road segment
    2. Group level - Average capacity metrics for groups of continuous segments

    Key Concepts:
    - **Capacity**: Maximum hourly flow a roadway can handle (PCE/hour)
    - **PCE Flow**: Passenger Car Equivalent flow (accounts for trucks)
    - **V/C Ratio**: Volume to Capacity ratio (measures congestion level)
    - **LOS**: Level of Service (A-F grade based on V/C ratio)

    Attributes:
        df (pd.DataFrame): DataFrame containing segment traffic data
        results (Dict): Dictionary to store analysis results
    """

    def __init__(self, df: pd.DataFrame) -> None:
        """
        Initialize the analyzer with traffic data.

        Args:
            df: DataFrame containing segment traffic data with:
                - Peak hour flow columns (AM_PEAK_TOTAL, PM_PEAK_TOTAL, etc.)
                - Lane count columns (AB_AMLANES, AB_PMLANES)
                - Direction and facility type columns

        Example:
            >>> df = pd.read_csv('traffic_data.csv')
            >>> analyzer = CapacityAnalyzer(df)
        """

        self.df = df.copy()
        self.results = {}

    def calculate_segment_capacity(self, period: str) -> pd.DataFrame:
        """
        Calculate capacity metrics for each segment for a specific period.

        This method calculates for the specified period (AM or PM):
        - PCE flow (considering truck PCE factors)
        - Roadway capacity (based on lane count and standard capacity per lane)
        - V/C ratio (Volume to Capacity ratio)
        - LOS grade (A-F based on V/C ratio)

        Args:
            period: Time period ('AM' or 'PM')

        Returns:
            pd.DataFrame: DataFrame with original data plus new capacity columns:
                - {period}_PCE_FLOW: PCE flow for the period
                - {period}_CAPACITY: Roadway capacity for the period
                - {period}_VC_RATIO: Volume to Capacity ratio
                - {period}_LOS: Level of Service grade (A-F)

        Example:
            >>> analyzer = CapacityAnalyzer(df)
            >>> result_df = analyzer.calculate_segment_capacity('AM')
            >>> print(result_df[['AM_VC_RATIO', 'AM_LOS']].head())

        Steps to implement:
            1. Validate period parameter (must be 'AM' or 'PM')
            2. Check if required peak flow columns exist
            3. Log the start of calculation
            4. Get peak total and truck flow columns for the period
            5. Calculate PCE flow using calculate_pce_flow()
            6. Get lane count column for the period from config.LANE_FIELDS
            7. Calculate capacity using calculate_capacity()
            8. Calculate V/C ratio using calculate_vc_ratio()
            9. Determine LOS grade for each segment using get_los_from_vc()
            10. Add all new columns to self.df
            11. Validate V/C ratio data using validate_data()
            12. Log completion with segment count
            13. Return self.df
        """

        # Validate period parameter
        if period not in ["AM", "PM"]:
            raise ValueError(f"Invalid period: {period}. Must be 'AM' or 'PM'.")

        peak_total_col = f"{period}_PEAK_TOTAL"
        peak_truck_col = f"{period}_PEAK_TRUCK"

        if (
            peak_total_col not in self.df.columns
            or peak_truck_col not in self.df.columns
        ):
            raise ValueError(f"{peak_total_col} or {peak_truck_col} is missing.")

        log_analysis_step(
            step_name="Capacity Analyzer",
            message=f"Starting {period} capacity segment calculation",
        )

        period_peak_total = self.df[peak_total_col]
        period_peak_truck = self.df[peak_truck_col]

        # PCE flow
        self.df[f"{period}_PCE_FLOW"] = calculate_pce_flow(
            total_flow=period_peak_total, truck_flow=period_peak_truck
        )

        # lane number
        period_lane = config.LANE_FIELDS[period]

        if period_lane not in self.df.columns:
            raise ValueError(f"Lane column '{period_lane}' not found in DataFrame.")

        # calculate lane capacity
        self.df[f"{period}_CAPACITY"] = calculate_capacity(self.df[period_lane])

        self.df[f"{period}_VC_ratio"] = calculate_vc_ratio(
            pce_flow=self.df[f"{period}_PCE_flow"],
            capacity=self.df[f"{period}_CAPACITY"],
        )

        # determine los
        self.df[f"{period}_LOS"] = self.df[f"{period}_VC_RATIO"].apply(get_los_from_vc)

        # validate vc ratio
        is_valid, errors = validate_data(self.df, f"{period}_VC_RATIO", "vc_ratio")

        if not is_valid:
            logger.warning(f"{period} V/C ratio error: {errors}")

        log_analysis_step(
            "Capacity Analyzer", f"Analyzed Capacity for {len(self.df)} segments."
        )

        return self.df
