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

logger = logging.getLogger(__name__)


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

        # Validate peak flow data
        is_valid, errors = validate_data(self.df, "AM_PEAK_TOTAL", "peak_flow")
        if not is_valid:
            logger.warning(f"AM peak flow validation warnings: {errors}")

        is_valid, errors = validate_data(self.df, "PM_PEAK_TOTAL", "peak_flow")
        if not is_valid:
            logger.warning(f"PM peak flow validation warnings: {errors}")

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
        # Validate period parameter
        if period not in ["AM", "PM"]:
            raise ValueError(f"Invalid period: {period}. Must be 'AM' or 'PM'")

        # Check if peak flow columns exist
        peak_total_col = f"{period}_PEAK_TOTAL"
        if peak_total_col not in self.df.columns:
            raise ValueError(
                f"Peak flow columns not found. "
                f"Please run calculate_segment_peak_flows() first."
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

        # Use the period parameter to select correct columns
        peak_auto_col = f"{period}_PEAK_AUTO"
        peak_truck_col = f"{period}_PEAK_TRUCK"

        result = {
            "direction": direction,
            "type": facility_type,
            "period": period,
            "num_segments": len(group_df),
            "avg_peak_total": float(group_df[peak_total_col].mean()),
            "avg_peak_auto": float(group_df[peak_auto_col].mean()),
            "avg_peak_truck": float(group_df[peak_truck_col].mean()),
            "min_peak_total": float(group_df[peak_total_col].min()),
            "max_peak_total": float(group_df[peak_total_col].max()),
        }
        return result

    def calculate_all_groups_peak(self, period: str) -> pd.DataFrame:
        """
        Calculate average peak hour flows for all direction and facility combinations.

        Args:
            period: AM or PM

        Returns:
            pd.DataFrame: DataFrame with columns:
                - direction: Direction code
                - type: Facility type
                - period: Time period (AM or PM)
                - num_segments: Number of segments in group
                - avg_peak_total: Average total peak hour flow
                - avg_peak_auto: Average auto peak hour flow
                - avg_peak_truck: Average truck peak hour flow
                - min_peak_total: Minimum peak hour flow in group
                - max_peak_total: Maximum peak hour flow in group
        Example:
            >>> analyzer = PeakHourAnalyzer(df)
            >>> analyzer.calculate_segment_peak_flows()
            >>> am_summary = analyzer.calculate_all_groups_peak('AM')
            >>> pm_summary = analyzer.calculate_all_groups_peak('PM')
            >>> print(am_summary.head())
        """
        # Validate period parameter
        if period not in ["AM", "PM"]:
            raise ValueError(f"Invalid period: {period}. Must be 'AM' or 'PM'")

        # Check if peak flow columns exist
        peak_col = f"{period}_PEAK_TOTAL"
        if peak_col not in self.df.columns:
            raise ValueError(
                f"Peak flow columns not found. "
                f"Please run calculate_segment_peak_flows() first."
            )

        log_analysis_step(
            "Peak Hour Analyzer", f"Calculating {period} peak flow for all groups."
        )
        directions = self.df[config.DIRECTION_FIELD].unique()
        facility_types = self.df[config.TYPE_FIELD].unique()

        result_list = []
        for direction in directions:
            for facility_type in facility_types:
                result = self.calculate_group_average_peak(
                    direction=direction, facility_type=facility_type, period=period
                )
                if result is not None:
                    result_list.append(result)

        summary_df = pd.DataFrame(result_list)

        log_analysis_step(
            "Peak Hour Analyzer", f"Calculated peak flows for {len(summary_df)} groups"
        )
        summary_df = summary_df.sort_values(["direction", "type"]).reset_index(
            drop=True
        )
        return summary_df

    def get_peak_summary_stats(self, period: str) -> Dict:
        """
        Calculate overall summary statistics for peak hour flows.

        Args:
            period: Time period ('AM' or 'PM')

        Returns:
            dict: Dictionary containing summary statistics:
                {
                    'period': 'AM',
                    'total_segments': 26,
                    'avg_peak_flow': 8234,
                    'min_peak_flow': 5600,
                    'max_peak_flow': 11200,
                    'directions': 2,
                    'facilities': 2
                }

        Example:
            >>> analyzer = PeakHourAnalyzer(df)
            >>> analyzer.calculate_segment_peak_flows()
            >>> am_stats = analyzer.get_peak_summary_stats('AM')
            >>> pm_stats = analyzer.get_peak_summary_stats('PM')
            >>> print(f"AM average: {am_stats['avg_peak_flow']:,.0f}")
            >>> print(f"PM average: {pm_stats['avg_peak_flow']:,.0f}")
        """
        # Validate period parameter
        if period not in ["AM", "PM"]:
            raise ValueError(f"Invalid period: {period}. Must be 'AM' or 'PM'")

        # Check if peak flow columns exist
        peak_total_col = f"{period}_PEAK_TOTAL"
        if peak_total_col not in self.df.columns:
            raise ValueError(
                f"Peak flow columns not found. "
                f"Please run calculate_segment_peak_flows() first."
            )

        log_analysis_step(
            "Peak Hour Analyzer", f"Calculating {period} peak flow summary statistics"
        )

        result_dict = {
            "period": period,
            "total_segments": len(self.df),
            "avg_peak_flow": float(self.df[peak_total_col].mean()),
            "min_peak_flow": float(self.df[peak_total_col].min()),
            "max_peak_flow": float(self.df[peak_total_col].max()),
            "directions": self.df[config.DIRECTION_FIELD].nunique(),
            "facility_types": self.df[config.TYPE_FIELD].nunique(),
        }
        return result_dict

    def compare_am_pm_peaks(self) -> pd.DataFrame:
        """
        Compare AM and PM peak hour flows side by side.

        Returns:
            pd.DataFrame: DataFrame with columns:
                - direction: Direction code
                - type: Facility type
                - am_peak: Average AM peak flow
                - pm_peak: Average PM peak flow
                - peak_diff: Absolute difference (|PM - AM|)
                - peak_ratio: Ratio (PM / AM), NaN if AM = 0
                - dominant_period: 'AM', 'PM', or 'EQUAL' (whichever is higher)

        Example:
            >>> analyzer = PeakHourAnalyzer(df)
            >>> analyzer.calculate_segment_peak_flows()
            >>> comparison = analyzer.compare_am_pm_peaks()
            >>> print(comparison)
        """
        # Check if peak flow columns exist
        if (
            "AM_PEAK_TOTAL" not in self.df.columns
            or "PM_PEAK_TOTAL" not in self.df.columns
        ):
            raise ValueError(
                f"Peak flow columns not found. "
                f"Please run calculate_segment_peak_flows() first."
            )

        log_analysis_step(
            "Peak Hour Analyzer", "Comparing AM and PM peak hour flows side by side"
        )
        am_peak_df = self.calculate_all_groups_peak("AM")
        pm_peak_df = self.calculate_all_groups_peak("PM")

        am_cols = am_peak_df[["direction", "type", "avg_peak_total"]].rename(
            columns={"avg_peak_total": "am_peak"}
        )
        pm_cols = pm_peak_df[["direction", "type", "avg_peak_total"]].rename(
            columns={"avg_peak_total": "pm_peak"}
        )

        summary_df = am_cols.merge(pm_cols, on=["direction", "type"])

        summary_df["peak_diff"] = (summary_df["pm_peak"] - summary_df["am_peak"]).abs()

        # Calculate ratio with division by zero handling
        summary_df["peak_ratio"] = np.where(
            summary_df["am_peak"] == 0,
            np.nan,
            summary_df["pm_peak"] / summary_df["am_peak"],
        )
        summary_df["peak_ratio"] = summary_df["peak_ratio"].round(2)

        # Determine dominant period
        summary_df["dominant_period"] = np.where(
            summary_df["pm_peak"] > summary_df["am_peak"],
            "PM",
            np.where(summary_df["pm_peak"] < summary_df["am_peak"], "AM", "EQUAL"),
        )

        log_analysis_step(
            "Peak Hour Analyzer",
            f"Compared {len(summary_df)} groups",
        )

        return summary_df
