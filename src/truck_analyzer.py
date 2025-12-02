"""
Truck Analyzer Module for SCAG I-5 Analysis

This module analyzes truck-specific traffic patterns including:
- Truck volume and percentage
- Truck flow distribution across time periods
- High truck volume segment identification
- Truck composition analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
import logging

from . import config
from .utils import (
    log_analysis_step,
    validate_data,
)

logger = logging.getLogger(__name__)


class TruckAnalyzer:
    """
    Analyzer for truck-specific traffic patterns.

    This class analyzes truck traffic at two levels:
    1. Segment level - Truck metrics for each road segment
    2. Group level - Average truck metrics for groups of continuous segments

    Key Metrics:
    - **Truck AADT**: Annual average daily truck traffic
    - **Truck Percentage**: Truck proportion of total traffic (%)
    - **Truck Intensity**: Truck AADT per lane (measure of truck concentration)
    - **Peak Hour Truck Ratio**: Truck percentage during peak hours (%)

    Attributes:
        df (pd.DataFrame): DataFrame containing segment traffic data
        results (Dict): Dictionary to store analysis results
    """

    def __init__(self, df: pd.DataFrame) -> None:
        """
        Initialize the analyzer with traffic data.

        Args:
            df: DataFrame containing segment traffic data with:
                - AADT columns (AADT, AUTO_AADT, TRUCK_AADT, TRUCK_PCT)
                - Peak hour flow columns (AM_PEAK_TRUCK, PM_PEAK_TRUCK, etc.)
                - Lane count columns (AB_AMLANES, AB_PMLANES)
                - Direction and facility type columns

        Example:
            >>> df = pd.read_csv('traffic_data.csv')
            >>> analyzer = TruckAnalyzer(df)
        """

        self.df = df.copy()
        self.results = {}

    def calculate_segment_truck_metrics(self) -> pd.DataFrame:
        """
        Calculate truck-specific metrics for each segment.

        This method calculates:
        - Truck intensity (truck AADT per lane)
        - AM and PM peak hour truck ratios (truck percentage during peak hours)

        Returns:
            pd.DataFrame: DataFrame with original data plus new columns:
                - TRUCK_INTENSITY: Truck AADT per lane
                - AM_TRUCK_RATIO: Truck percentage in AM peak (%)
                - PM_TRUCK_RATIO: Truck percentage in PM peak (%)

        Example:
            >>> analyzer = TruckAnalyzer(df)
            >>> result_df = analyzer.calculate_segment_truck_metrics()
            >>> print(result_df[['TRUCK_PCT', 'TRUCK_INTENSITY', 'AM_TRUCK_RATIO']].head())

        Steps to implement:
            1. Log the start of calculation
            2. Check if required columns exist: TRUCK_AADT, TRUCK_PCT
            3. Check if peak flow columns exist: AM_PEAK_TOTAL, AM_PEAK_TRUCK, etc.
            4. Check if lane columns exist: AB_AMLANES, AB_PMLANES
            5. Calculate TRUCK_INTENSITY:
               - truck_intensity = TRUCK_AADT / AB_AMLANES
               - Handle division by zero (set to 0 where lanes = 0)
            6. Calculate AM_TRUCK_RATIO:
               - am_ratio = (AM_PEAK_TRUCK / AM_PEAK_TOTAL) * 100
               - Handle division by zero (set to 0 where total = 0)
            7. Calculate PM_TRUCK_RATIO:
               - pm_ratio = (PM_PEAK_TRUCK / PM_PEAK_TOTAL) * 100
               - Handle division by zero (set to 0 where total = 0)
            8. Add all new columns to self.df
            9. Validate truck percentage data using validate_data()
            10. Log completion with segment count
            11. Return self.df
        """

        log_analysis_step("Truck Analyzer", "Start calculating segment truck metrics")

        if "TRUCK_AADT" not in self.df.columns or "TRUCK_PCT" not in self.df.columns:
            raise ValueError("The DataFrame must include 'TRUCK_AADT' and 'TRUCK_PCT'.")

        for value in config.LANE_FIELDS.values():
            if value not in self.df.columns:
                raise ValueError(f"The DataFrame must include {value}.")

        self.df["TRUCK_INTENSITY"] = np.where(
            self.df["AB_AMLANES"] > 0, self.df["TRUCK_AADT"] / self.df["AB_AMLANES"], 0
        )

        self.df["AM_TRUCK_RATIO"] = np.where(
            self.df["AM_PEAK_TOTAL"] > 0,
            (self.df["AM_PEAK_TRUCK"] / self.df["AM_PEAK_TOTAL"]) * 100,
            0,
        )

        self.df["PM_TRUCK_RATIO"] = np.where(
            self.df["PM_PEAK_TOTAL"] > 0,
            (self.df["PM_PEAK_TRUCK"] / self.df["PM_PEAK_TOTAL"]) * 100,
            0,
        )

        # Validate truck percentage data
        validate_data(self.df, "TRUCK_PCT", "truck_pct")

        log_analysis_step(
            "Truck Analyzer",
            f"Completed calculating segment truck metrics for {len(self.df)} segments",
        )

        return self.df

    def calculate_group_truck_metrics(
        self, direction: str, facility_type: str
    ) -> Optional[Dict]:
        """
        Calculate average truck metrics for a specific group.


        Args:
            direction: Direction code ('N', 'S', 'E', 'W')
            facility_type: Facility type ('ML' for Main Lanes, 'HV' for HOV Lanes)

        Returns:
            dict: Dictionary containing group truck statistics:
                {
                    'direction': 'N',
                    'type': 'ML',
                    'num_segments': 9,
                    'avg_truck_aadt': 3500,
                    'avg_truck_pct': 12.5,
                    'avg_truck_intensity': 875,
                    'avg_am_truck_ratio': 8.5,
                    'avg_pm_truck_ratio': 11.2,
                    'min_truck_pct': 8.0,
                    'max_truck_pct': 18.5
                }

            Returns None if no data found for the specified combination.

        Example:
            >>> analyzer = TruckAnalyzer(df)
            >>> analyzer.calculate_segment_truck_metrics()
            >>> result = analyzer.calculate_group_truck_metrics('N', 'ML')
            >>> print(f"Average truck %: {result['avg_truck_pct']:.1f}%")
            >>> print(f"Truck intensity: {result['avg_truck_intensity']:.0f} trucks/lane/day")

        Steps to implement:
            1. Check if truck metric columns exist
            2. Filter data by direction and facility_type using mask
            3. Check if filtered data is empty, log warning and return None
            4. Calculate average truck AADT
            5. Calculate average truck percentage
            6. Calculate average truck intensity
            7. Calculate average AM truck ratio
            8. Calculate average PM truck ratio
            9. Calculate min and max truck percentage
            10. Return dictionary with all statistics
        """
        # TODO: Implement this method
        # Hint: Very similar to calculate_group_average_peak() from Phase 2
        # Hint: Use .mean() for averages, .min() and .max() for ranges

        required_truck_cols = [
            "TRUCK_AADT",
            "TRUCK_PCT",
            "TRUCK_INTENSITY",
            "AM_TRUCK_RATIO",
            "PM_TRUCK_RATIO",
        ]
        missing_truck_cols = [
            col for col in required_truck_cols if col not in self.df.columns
        ]
        if missing_truck_cols:
            raise ValueError(f"Missing columns: {missing_truck_cols}.")

        mask = (self.df[config.DIRECTION_FIELD] == direction) & (
            self.df[config.TYPE_FIELD] == facility_type
        )
        group_df = self.df[mask]

        if len(group_df) == 0:
            logger.warning(
                f"No data found for direction '{direction}' and facility type '{facility_type}'"
            )
            return None

        result_dict = {
            "direction": direction,
            "type": facility_type,
            "num_segments": len(group_df),
            "avg_truck_aadt": float(group_df["TRUCK_AADT"].mean()),
            "avg_truck_pct": float(group_df["TRUCK_PCT"].mean()),
            "avg_truck_intensity": float(group_df["TRUCK_INTENSITY"].mean()),
            "avg_am_truck_ratio": float(group_df["AM_TRUCK_RATIO"].mean()),
            "avg_pm_truck_ratio": float(group_df["PM_TRUCK_RATIO"].mean()),
            "min_truck_pct": float(group_df["TRUCK_PCT"].min()),
            "max_truck_pct": float(group_df["TRUCK_PCT"].max()),
        }

        return result_dict

    def calculate_all_groups_truck(self) -> pd.DataFrame:
        """
        Calculate truck metrics for all direction and facility combinations.


        Returns:
            pd.DataFrame: DataFrame with columns:
                - direction: Direction code
                - type: Facility type
                - num_segments: Number of segments in group
                - avg_truck_aadt: Average truck AADT
                - avg_truck_pct: Average truck percentage (%)
                - avg_truck_intensity: Average truck intensity (trucks/lane/day)
                - avg_am_truck_ratio: Average AM peak truck ratio (%)
                - avg_pm_truck_ratio: Average PM peak truck ratio (%)
                - min_truck_pct: Minimum truck percentage in group
                - max_truck_pct: Maximum truck percentage in group

        Example:
            >>> analyzer = TruckAnalyzer(df)
            >>> analyzer.calculate_segment_truck_metrics()
            >>> summary = analyzer.calculate_all_groups_truck()
            >>> print(summary)

        Steps to implement:
            1. Check if truck metric columns exist
            2. Log the start of calculation
            3. Get unique values for directions and facility types
            4. Loop through all combinations
            5. Call calculate_group_truck_metrics() for each combination
            6. Collect non-None results in a list
            7. Convert list to DataFrame
            8. Sort by direction and type
            9. Log completion
            10. Return DataFrame
        """
        # TODO: Implement this method
        # Hint: Very similar to calculate_all_groups_capacity() from Phase 3
        required_truck_cols = [
            "TRUCK_AADT",
            "TRUCK_PCT",
            "TRUCK_INTENSITY",
            "AM_TRUCK_RATIO",
            "PM_TRUCK_RATIO",
        ]
        missing_truck_cols = [
            col for col in required_truck_cols if col not in self.df.columns
        ]
        if missing_truck_cols:
            raise ValueError(f"Missing columns: {missing_truck_cols}.")

        log_analysis_step(
            "Truck Analyzer", "Start calculating all group truck analysis."
        )

        directions = self.df[config.DIRECTION_FIELD].unique()
        facility_types = self.df[config.TYPE_FIELD].unique()

        result_list = []

        for direction in directions:
            for facility_type in facility_types:
                result = self.calculate_group_truck_metrics(
                    direction=direction, facility_type=facility_type
                )

                if result is not None:
                    result_list.append(result)

        summary_df = pd.DataFrame(result_list)

        summary_df = summary_df.sort_values(["direction", "type"]).reset_index(
            drop=True
        )

        log_analysis_step(
            "Truck Analyzer",
            "Completed calculating all group truck analysis.",
        )

        return summary_df

    def get_truck_summary_stats(self) -> Dict:
        """
        Get overall truck traffic summary statistics.

        Returns:
            dict: Dictionary containing overall truck statistics:
                {
                    'total_segments': 26,
                    'avg_truck_aadt': 3200,
                    'avg_truck_pct': 11.8,
                    'min_truck_pct': 5.2,
                    'max_truck_pct': 22.3,
                    'segments_high_truck': 5,  # >15% truck
                    'percentage_high_truck': 19.2,
                    'avg_truck_intensity': 800,
                    'total_daily_truck_volume': 83200  # sum of all segment truck AADT
                }

        Example:
            >>> analyzer = TruckAnalyzer(df)
            >>> analyzer.calculate_segment_truck_metrics()
            >>> summary = analyzer.get_truck_summary_stats()
            >>> print(f"Average truck %: {summary['avg_truck_pct']:.1f}%")
            >>> print(f"High truck segments: {summary['segments_high_truck']}")

        Steps to implement:
            1. Check if truck metric columns exist
            2. Log the start of calculation
            3. Count total segments
            4. Calculate average, min, max truck AADT
            5. Calculate average, min, max truck percentage
            6. Calculate average truck intensity
            7. Count segments with truck % > 15% (high truck threshold)
            8. Calculate percentage of high truck segments
            9. Calculate total daily truck volume (sum of TRUCK_AADT)
            10. Return dictionary with all statistics
        """

        result_dict = {
            "total_segments": len(self.df),
            "avg_truck_aadt": float(self.df["TRUCK_AADT"].mean()),
            "avg_truck_pct": float(self.df["TRUCK_PCT"].mean()),
            "min_truck_pct": float(self.df["TRUCK_PCT"].min()),
            "max_truck_pct": float(self.df["TRUCK_PCT"].max()),
            "segments_high_truck": (self.df["TRUCK_PCT"] > 15).sum(),  # >15% truck
            "percentage_high_truck": ((self.df["TRUCK_PCT"] > 15).sum() / len(self.df))
            * 100,
            "avg_truck_intensity": float(self.df["TRUCK_INTENSITY"].mean()),
            "total_daily_truck_volume": float(
                self.df["TRUCK_AADT"].sum()
            ),  # sum of all segment truck AADT
        }

        return result_dict

    def identify_high_truck_segments(
        self, truck_pct_threshold: float = 15.0
    ) -> pd.DataFrame:
        """
        Identify segments with high truck percentage.

        Args:
            truck_pct_threshold: Truck percentage threshold (default 15.0%)

        Returns:
            pd.DataFrame: DataFrame containing high truck segments with columns:
                - Segment identification columns (direction, type, etc.)
                - TRUCK_AADT
                - TRUCK_PCT
                - TRUCK_INTENSITY
                - AM_TRUCK_RATIO, PM_TRUCK_RATIO
                - Sorted by TRUCK_PCT (descending)

        Example:
            >>> analyzer = TruckAnalyzer(df)
            >>> analyzer.calculate_segment_truck_metrics()
            >>> high_truck = analyzer.identify_high_truck_segments(truck_pct_threshold=15.0)
            >>> print(f"Found {len(high_truck)} high truck segments")
            >>> print(high_truck[['direction', 'type', 'TRUCK_PCT', 'TRUCK_INTENSITY']])

        Steps to implement:
            1. Validate truck_pct_threshold (should be between 0 and 100)
            2. Check if TRUCK_PCT column exists
            3. Log the start of calculation
            4. Filter segments where TRUCK_PCT > threshold
            5. Select relevant columns (direction, type, TRUCK_AADT, TRUCK_PCT, etc.)
            6. Sort by TRUCK_PCT in descending order
            7. Log how many high truck segments found
            8. Return filtered and sorted DataFrame
        """
        # TODO: Implement this method
        # Hint 1: Filter: self.df[self.df['TRUCK_PCT'] > truck_pct_threshold]
        # Hint 2: Sort: .sort_values('TRUCK_PCT', ascending=False)
        # Hint 3: Similar to identify_bottlenecks() from Phase 3
        if truck_pct_threshold < 0 or truck_pct_threshold > 100:
            raise ValueError("Truck PCT Threshold should be between 0 and 100.")
        if "TRUCK_PCT" not in self.df.columns:
            raise ValueError("'TRUCK_PCT' should be in the DataFrame")
        log_analysis_step("Truck Analyzer", "Start identifying high truck segments.")

        filtered_df = self.df[self.df["TRUCK_PCT"] > truck_pct_threshold]
        filtered_df = filtered_df[
            [
                config.DIRECTION_FIELD,
                config.TYPE_FIELD,
                "TRUCK_AADT",
                "TRUCK_PCT",
                "TRUCK_INTENSITY",
                "AM_TRUCK_RATIO",
                "PM_TRUCK_RATIO",
            ]
        ]
        filtered_df = filtered_df.sort_values(by="TRUCK_PCT", ascending=False)

        log_analysis_step(
            "Truck Analyzer",
            f"Completed identifying high truck segments, there are {len(filtered_df)} high truck segments",
        )

        return filtered_df

    def compare_am_pm_truck_flows(self) -> pd.DataFrame:
        """
        Compare AM and PM truck flow patterns side by side.

        Returns:
            pd.DataFrame: DataFrame with columns:
                - direction: Direction code
                - type: Facility type
                - avg_am_truck: Average AM peak truck flow
                - avg_pm_truck: Average PM peak truck flow
                - am_truck_ratio: Average AM truck ratio (%)
                - pm_truck_ratio: Average PM truck ratio (%)
                - truck_diff: Absolute difference in truck flows (AM - PM)
                - higher_truck_period: 'AM' or 'PM' (period with higher truck flow)

        Example:
            >>> analyzer = TruckAnalyzer(df)
            >>> analyzer.calculate_segment_truck_metrics()
            >>> comparison = analyzer.compare_am_pm_truck_flows()
            >>> print(comparison)

        Steps to implement:
            1. Check if required columns exist
            2. Log the start of calculation
            3. Group by direction and facility_type
            4. Calculate average AM_PEAK_TRUCK and PM_PEAK_TRUCK for each group
            5. Calculate average AM_TRUCK_RATIO and PM_TRUCK_RATIO for each group
            6. Calculate absolute difference in truck flows
            7. Determine which period has higher truck flow using np.where
            8. Reset index to make direction and type regular columns
            9. Log completion
            10. Return comparison DataFrame
        """

        required_truck_cols = [
            "AM_PEAK_TRUCK",
            "PM_PEAK_TRUCK",
            "AM_TRUCK_RATIO",
            "PM_TRUCK_RATIO",
        ]
        missing_truck_cols = [
            col for col in required_truck_cols if col not in self.df.columns
        ]
        if missing_truck_cols:
            raise ValueError(f"Missing truck related cols: {missing_truck_cols}")

        log_analysis_step("Truck Analyzer", "Start comparing am and pm truck flows")

        grouped_df = (
            self.df.groupby([config.DIRECTION_FIELD, config.TYPE_FIELD])
            .agg(
                {
                    "AM_PEAK_TRUCK": "mean",
                    "PM_PEAK_TRUCK": "mean",
                    "AM_TRUCK_RATIO": "mean",
                    "PM_TRUCK_RATIO": "mean",
                }
            )
            .reset_index()
        )

        grouped_df["TRUCK_PEAK_DIFF"] = abs(
            grouped_df["AM_PEAK_TRUCK"] - grouped_df["PM_PEAK_TRUCK"]
        )

        grouped_df["higher_truck_period"] = np.where(
            (grouped_df["AM_PEAK_TRUCK"] > grouped_df["PM_PEAK_TRUCK"]),
            "AM",
            np.where(
                (grouped_df["PM_PEAK_TRUCK"] > grouped_df["AM_PEAK_TRUCK"]),
                "PM",
                "EQUAL",
            ),
        )

        log_analysis_step("Truck Analyzer", "Complete comparing am and pm truck flows")

        return grouped_df

    def get_truck_distribution_by_period(self) -> pd.DataFrame:
        """
        Get truck flow distribution across different time periods.

        Returns:
            pd.DataFrame: DataFrame with columns:
                - direction: Direction code
                - type: Facility type
                - truck_aadt: Daily average truck flow
                - am_peak_truck: AM peak hour truck flow
                - pm_peak_truck: PM peak hour truck flow
                - am_as_pct_of_daily: AM truck as % of daily truck AADT
                - pm_as_pct_of_daily: PM truck as % of daily truck AADT

        Example:
            >>> analyzer = TruckAnalyzer(df)
            >>> analyzer.calculate_segment_truck_metrics()
            >>> distribution = analyzer.get_truck_distribution_by_period()
            >>> print(distribution)

        Steps to implement:
            1. Check if required columns exist
            2. Log the start of calculation
            3. Group by direction and facility_type
            4. Calculate average TRUCK_AADT for each group
            5. Calculate average AM_PEAK_TRUCK for each group
            6. Calculate average PM_PEAK_TRUCK for each group
            7. Calculate AM as % of daily: (AM_PEAK_TRUCK / TRUCK_AADT) * 100
            8. Calculate PM as % of daily: (PM_PEAK_TRUCK / TRUCK_AADT) * 100
            9. Reset index
            10. Log completion
            11. Return distribution DataFrame
        """

        required_truck_cols = [
            "TRUCK_AADT",
            "AM_PEAK_TRUCK",
            "PM_PEAK_TRUCK",
        ]
        missing_truck_cols = [
            col for col in required_truck_cols if col not in self.df.columns
        ]
        if missing_truck_cols:
            raise ValueError(f"Missing truck related cols: {missing_truck_cols}")

        log_analysis_step(
            "Truck Analyzer", "Start calculating truck distribution by am and pm."
        )

        grouped_df = (
            self.df.groupby([config.DIRECTION_FIELD, config.TYPE_FIELD])
            .agg(
                {
                    "TRUCK_AADT": "mean",
                    "AM_PEAK_TRUCK": "mean",
                    "PM_PEAK_TRUCK": "mean",
                }
            )
            .reset_index()
        )

        grouped_df["am_as_pct_of_daily"] = np.where(
            grouped_df["TRUCK_AADT"] == 0,
            np.nan,
            grouped_df["AM_PEAK_TRUCK"] / grouped_df["TRUCK_AADT"],
        )

        grouped_df["pm_as_pct_of_daily"] = np.where(
            grouped_df["TRUCK_AADT"] == 0,
            np.nan,
            grouped_df["PM_PEAK_TRUCK"] / grouped_df["TRUCK_AADT"],
        )

        log_analysis_step(
            "Truck Analyzer", "Complete calculating truck distribution by am and pm."
        )

        return grouped_df

    def analyze_truck_composition(self) -> Dict:
        """
        Analyze truck composition by truck type (LHDT, MHDT, HHDT).

        This method calculates the distribution of different truck types
        in AM and PM periods.

        Returns:
            dict: Dictionary containing truck composition data:
                {
                    'AM': {
                        'total_truck_flow': 2500,
                        'lhdt_flow': 800,
                        'mhdt_flow': 1200,
                        'hhdt_flow': 500,
                        'lhdt_pct': 32.0,
                        'mhdt_pct': 48.0,
                        'hhdt_pct': 20.0
                    },
                    'PM': {
                        'total_truck_flow': 2800,
                        'lhdt_flow': 900,
                        'mhdt_flow': 1300,
                        'hhdt_flow': 600,
                        'lhdt_pct': 32.1,
                        'mhdt_pct': 46.4,
                        'hhdt_pct': 21.4
                    }
                }

        Example:
            >>> analyzer = TruckAnalyzer(df)
            >>> composition = analyzer.analyze_truck_composition()
            >>> print(f"AM MHDT %: {composition['AM']['mhdt_pct']:.1f}%")

        Steps to implement:
            1. Log the start of calculation
            2. Get AM truck type columns from config.AM_FIELDS['truck']
            3. Calculate AM LHDT, MHDT, HHDT total flows (sum all segments)
            4. Calculate AM total truck flow
            5. Calculate AM percentages for each truck type
            6. Get PM truck type columns from config.PM_FIELDS['truck']
            7. Calculate PM LHDT, MHDT, HHDT total flows
            8. Calculate PM total truck flow
            9. Calculate PM percentages for each truck type
            10. Return nested dictionary with AM and PM data
        """

        log_analysis_step("Truck Analyzer", "Start analyzing truck composition.")

        # Get AM truck type columns
        am_truck_cols = config.AM_FIELDS["truck"]  # This is a list of column names
        pm_truck_cols = config.PM_FIELDS["truck"]

        # Calculate AM truck flows
        am_lhdt_flow = float(self.df[am_truck_cols[0]].sum())
        am_mhdt_flow = float(self.df[am_truck_cols[1]].sum())
        am_hhdt_flow = float(self.df[am_truck_cols[2]].sum())
        am_total_truck_flow = am_lhdt_flow + am_mhdt_flow + am_hhdt_flow

        # Calculate AM percentages
        if am_total_truck_flow > 0:
            am_lhdt_pct = (am_lhdt_flow / am_total_truck_flow) * 100
            am_mhdt_pct = (am_mhdt_flow / am_total_truck_flow) * 100
            am_hhdt_pct = (am_hhdt_flow / am_total_truck_flow) * 100
        else:
            am_lhdt_pct = 0.0
            am_mhdt_pct = 0.0
            am_hhdt_pct = 0.0

        # Calculate PM truck flows
        pm_lhdt_flow = float(self.df[pm_truck_cols[0]].sum())
        pm_mhdt_flow = float(self.df[pm_truck_cols[1]].sum())
        pm_hhdt_flow = float(self.df[pm_truck_cols[2]].sum())
        pm_total_truck_flow = pm_lhdt_flow + pm_mhdt_flow + pm_hhdt_flow

        # Calculate PM percentages
        if pm_total_truck_flow > 0:
            pm_lhdt_pct = (pm_lhdt_flow / pm_total_truck_flow) * 100
            pm_mhdt_pct = (pm_mhdt_flow / pm_total_truck_flow) * 100
            pm_hhdt_pct = (pm_hhdt_flow / pm_total_truck_flow) * 100
        else:
            pm_lhdt_pct = 0.0
            pm_mhdt_pct = 0.0
            pm_hhdt_pct = 0.0

        result_dict = {
            "AM": {
                "total_truck_flow": am_total_truck_flow,
                "lhdt_flow": am_lhdt_flow,
                "mhdt_flow": am_mhdt_flow,
                "hhdt_flow": am_hhdt_flow,
                "lhdt_pct": am_lhdt_pct,
                "mhdt_pct": am_mhdt_pct,
                "hhdt_pct": am_hhdt_pct,
            },
            "PM": {
                "total_truck_flow": pm_total_truck_flow,
                "lhdt_flow": pm_lhdt_flow,
                "mhdt_flow": pm_mhdt_flow,
                "hhdt_flow": pm_hhdt_flow,
                "lhdt_pct": pm_lhdt_pct,
                "mhdt_pct": pm_mhdt_pct,
                "hhdt_pct": pm_hhdt_pct,
            },
        }

        log_analysis_step("Truck Analyzer", "Completed analyzing truck composition.")

        return result_dict
