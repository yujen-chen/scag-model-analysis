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
            pce_flow=self.df[f"{period}_PCE_FLOW"],
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

    def calculate_all_periods_capacity(self) -> pd.DataFrame:
        """
        Calculate capacity metrics for both AM and PM periods.


        This is a convenience method that calls calculate_segment_capacity()
        for both AM and PM periods.

        Returns:
            pd.DataFrame: DataFrame with capacity metrics for both periods

        Example:
            >>> analyzer = CapacityAnalyzer(df)
            >>> result_df = analyzer.calculate_all_periods_capacity()
            >>> print(result_df[['AM_LOS', 'PM_LOS']].head())

        Steps to implement:
            1. Call calculate_segment_capacity('AM')
            2. Call calculate_segment_capacity('PM')
            3. Return self.df
        """

        self.df = self.calculate_segment_capacity(period="AM")
        self.df = self.calculate_segment_capacity(period="PM")

        return self.df

    def calculate_group_capacity(
        self, direction: str, facility_type: str, period: str
    ) -> Optional[Dict]:
        """
        Calculate average capacity metrics for a specific group.

        Note: This function should be executed after calculate_segment_capacity()
        has been run for the requested period. If you want to analyze both AM and PM,
        run calculate_all_periods_capacity() first.

        Args:
            direction: Direction code ('N', 'S', 'E', 'W')
            facility_type: Facility type ('ML' for Main Lanes, 'HV' for HOV Lanes)
            period: Time period ('AM' or 'PM')

        Returns:
            dict: Dictionary containing group capacity statistics:
                {
                    'direction': 'N',
                    'type': 'ML',
                    'period': 'AM',
                    'num_segments': 9,
                    'avg_pce_flow': 8900,
                    'avg_capacity': 10000,
                    'avg_vc_ratio': 0.89,
                    'min_vc_ratio': 0.75,
                    'max_vc_ratio': 0.98,
                    'dominant_los': 'D',
                    'los_counts': {'C': 2, 'D': 5, 'E': 2}
                }

            Returns None if no data found for the specified combination.

        Example:
            >>> analyzer = CapacityAnalyzer(df)
            >>> analyzer.calculate_all_periods_capacity()
            >>> result = analyzer.calculate_group_capacity('N', 'ML', 'AM')
            >>> print(f"Average V/C: {result['avg_vc_ratio']:.2f}")
            >>> print(f"Dominant LOS: {result['dominant_los']}")

        """

        if period not in ["AM", "PM"]:
            raise ValueError(f"Period {period} wrong. Should be 'AM' or 'PM'.")

        required_cols = [
            f"{period}_PCE_FLOW",
            f"{period}_CAPACITY",
            f"{period}_VC_RATIO",
            f"{period}_LOS",
        ]
        missing_cols = [col for col in required_cols if col not in self.df.columns]
        if missing_cols:
            raise ValueError(
                f"Missing columns: {missing_cols}. Run calculate_segment_capacity() first."
            )

        mask = (self.df[config.DIRECTION_FIELD] == direction) & (
            self.df[config.TYPE_FIELD] == facility_type
        )

        group_df = self.df[mask]

        if len(group_df) == 0:
            logger.warning(
                f"No data found for direction '{direction}' and facility type '{facility_type}'"
            )
            return None

        los_counts = group_df[f"{period}_LOS"].value_counts()
        result = {
            "direction": direction,
            "type": facility_type,
            "period": period,
            "num_segments": len(group_df),
            "avg_pce_flow": float(group_df[f"{period}_PCE_FLOW"].mean()),
            "avg_capacity": float(group_df[f"{period}_CAPACITY"].mean()),
            "avg_vc_ratio": float(group_df[f"{period}_VC_RATIO"].mean()),
            "min_vc_ratio": float(group_df[f"{period}_VC_RATIO"].min()),
            "max_vc_ratio": float(group_df[f"{period}_VC_RATIO"].max()),
            "dominant_los": los_counts.idxmax() if len(los_counts) > 0 else "N/A",
            "los_counts": group_df[f"{period}_LOS"].value_counts().to_dict(),
        }

        return result

    def calculate_all_groups_capacity(self, period: str) -> pd.DataFrame:
        """
        Calculate capacity metrics for all direction and facility combinations.


        Args:
            period: Time period ('AM' or 'PM')

        Returns:
            pd.DataFrame: DataFrame with columns:
                - direction: Direction code
                - type: Facility type
                - period: Time period (AM or PM)
                - num_segments: Number of segments in group
                - avg_pce_flow: Average PCE flow
                - avg_capacity: Average roadway capacity
                - avg_vc_ratio: Average V/C ratio
                - min_vc_ratio: Minimum V/C ratio in group
                - max_vc_ratio: Maximum V/C ratio in group
                - dominant_los: Most frequent LOS grade in group

        Example:
            >>> analyzer = CapacityAnalyzer(df)
            >>> analyzer.calculate_all_periods_capacity()
            >>> am_summary = analyzer.calculate_all_groups_capacity('AM')
            >>> pm_summary = analyzer.calculate_all_groups_capacity('PM')
            >>> print(am_summary)

        Steps to implement:
            1. Validate period parameter
            2. Check if capacity columns exist
            3. Log the start of calculation
            4. Get unique values for directions and facility types
            5. Loop through all combinations
            6. Call calculate_group_capacity() for each combination
            7. Collect non-None results in a list
            8. Convert list to DataFrame
            9. Sort by direction and type
            10. Log completion
            11. Return DataFrame
        """
        # TODO: Implement this method
        # Hint: Very similar to calculate_all_groups_peak() from Phase 2

        if period not in ["AM", "PM"]:
            raise ValueError("period should only be 'AM' or 'PM.")

        if f"{period}_CAPACITY" not in self.df.columns:
            raise ValueError(f"{period}_CAPACITY column should be in the DataFrame")

        log_analysis_step("Capacity Analyze", "Analyzing {period} Group Capacity.")

        directions = self.df[config.DIRECTION_FIELD].unique()
        facility_types = self.df[config.TYPE_FIELD].unique()

        result_list = []
        for direction in directions:
            for facility_type in facility_types:
                result = self.calculate_group_capacity(
                    direction=direction, facility_type=facility_type, period=period
                )

                result_list.append(result)

        summary_df = pd.DataFrame(result_list)

        summary_df = summary_df.sort_values(["direction", "type"]).reset_index(
            drop=True
        )

        return summary_df

    def get_los_distribution(self, period: str) -> Dict:
        """
        Get the distribution of LOS grades for a specific period.

        Args:
            period: Time period ('AM' or 'PM')

        Returns:
            dict: Dictionary containing LOS distribution:
                {
                    'period': 'AM',
                    'total_segments': 26,
                    'los_counts': {'A': 2, 'B': 5, 'C': 8, 'D': 7, 'E': 3, 'F': 1},
                    'los_percentages': {'A': 7.7, 'B': 19.2, 'C': 30.8, 'D': 26.9, 'E': 11.5, 'F': 3.8},
                    'avg_vc_ratio': 0.78,
                    'segments_over_capacity': 1,
                    'percentage_over_capacity': 3.8
                }

        Example:
            >>> analyzer = CapacityAnalyzer(df)
            >>> analyzer.calculate_all_periods_capacity()
            >>> am_dist = analyzer.get_los_distribution('AM')
            >>> print(f"LOS distribution: {am_dist['los_percentages']}")
            >>> print(f"Over capacity: {am_dist['percentage_over_capacity']:.1f}%")

        Steps to implement:
            1. Validate period parameter
            2. Check if LOS column exists
            3. Log the start of calculation
            4. Get LOS column for the period
            5. Count LOS occurrences using value_counts()
            6. Calculate percentages for each LOS
            7. Calculate average V/C ratio
            8. Count segments with V/C > 1.0 (over capacity)
            9. Calculate percentage over capacity
            10. Return dictionary with all statistics
        """
        # TODO: Implement this method
        # Hint 1: Use value_counts() to get LOS counts
        # Hint 2: Calculate percentages: (count / total) * 100
        # Hint 3: Over capacity: len(self.df[self.df[vc_col] > 1.0])

        # Validate period parameter
        if period not in ["AM", "PM"]:
            raise ValueError(f"Invalid period: {period}. Must be 'AM' or 'PM'")

        if f"{period}_LOS" not in self.df.columns:
            raise ValueError(f"{period}_LOS column is missing.")

        log_analysis_step(
            "Peak Hour Analyzer", f"Getting LOS distributions for {period}."
        )
        pass
