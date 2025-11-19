"""
Utility functions for SCAG I-5 Analysis

This module contains helper functions used throughout the analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Union, Tuple
import logging

# Import configuration
from . import config

# Setup logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)


def get_los_from_vc(vc_ratio: float) -> str:
    """
    Determine Level of Service (LOS) based on V/C ratio.


    Args:
        vc_ratio: Volume to Capacity ratio

    Returns:
        LOS grade (A-F)

    Example:
        >>> get_los_from_vc(0.45)
        'B'
        >>> get_los_from_vc(1.05)
        'F'
    """
    if pd.isna(vc_ratio):
        return "N/A"

    for los_grade, threshold in config.LOS_THRESHOLDS.items():
        if vc_ratio <= threshold:
            return los_grade

    return "F"


def calculate_period_flow(
    df: pd.DataFrame, period: str, flow_type: str = "total"
) -> pd.Series:
    """
    Calculate flow for a specific time period.


    Args:
        df: DataFrame containing flow data
        period: Time period ('AM', 'PM', 'MD', 'EVE', 'NT')
        flow_type: Type of flow ('total', 'auto', 'truck')

    Returns:
        Series containing period flow
    """
    if period not in config.PERIOD_FIELDS:
        raise ValueError(
            f"Invalid period: {period}. Must be one of {list(config.PERIOD_FIELDS.keys())}"
        )

    period_fields = config.PERIOD_FIELDS[period]

    if flow_type == "total":
        # Sum all auto and truck fields
        auto_flow = df[period_fields["auto"]].sum(axis=1)
        truck_flow = df[period_fields["truck"]].sum(axis=1)
        return auto_flow + truck_flow

    elif flow_type == "auto":
        return df[period_fields["auto"]].sum(axis=1)

    elif flow_type == "truck":
        return df[period_fields["truck"]].sum(axis=1)

    else:
        raise ValueError(
            f"Invalid flow_type: {flow_type}. Must be 'total', 'auto', or 'truck'"
        )


def calculate_aadt(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate AADT (Annual Average Daily Traffic) for each segment.


    Args:
        df: DataFrame containing flow data for all periods

    Returns:
        Tuple of (total_aadt, auto_aadt, truck_aadt)

    """
    # Calculate flow for each period
    am_flow = calculate_period_flow(df, "AM", "total")
    pm_flow = calculate_period_flow(df, "PM", "total")
    md_flow = calculate_period_flow(df, "MD", "total")
    eve_flow = calculate_period_flow(df, "EVE", "total")
    nt_flow = calculate_period_flow(df, "NT", "total")

    # Total AADT is sum of all period flows
    total_aadt = am_flow + pm_flow + md_flow + eve_flow + nt_flow

    # Calculate truck AADT
    am_truck = calculate_period_flow(df, "AM", "truck")
    pm_truck = calculate_period_flow(df, "PM", "truck")
    md_truck = calculate_period_flow(df, "MD", "truck")
    eve_truck = calculate_period_flow(df, "EVE", "truck")
    nt_truck = calculate_period_flow(df, "NT", "truck")

    truck_aadt = am_truck + pm_truck + md_truck + eve_truck + nt_truck

    # Auto AADT is total minus truck
    auto_aadt = total_aadt - truck_aadt

    return total_aadt, auto_aadt, truck_aadt


def calculate_peak_hour_flow(
    period_flow: Union[pd.Series, float], period: str
) -> Union[pd.Series, float]:
    """
    Convert period flow to peak hour flow.


    Args:
        period_flow: Flow during the period
        period: 'AM' or 'PM'

    Returns:
        Peak hour flow
    """
    if period == "AM":
        return period_flow * config.AM_PEAK_FACTOR
    elif period == "PM":
        return period_flow * config.PM_PEAK_FACTOR
    else:
        raise ValueError("Period must be 'AM' or 'PM'")


def calculate_pce_flow(
    total_flow: Union[pd.Series, float], truck_flow: Union[pd.Series, float]
) -> Union[pd.Series, float]:
    """
    Calculate PCE (Passenger Car Equivalent) flow.


    PCE flow = auto_flow * AUTO_PCE + truck_flow * TRUCK_PCE
             = (total_flow - truck_flow) * 1.0 + truck_flow * 2.0
             = total_flow + truck_flow

    Args:
        total_flow: Total vehicle flow
        truck_flow: Truck flow

    Returns:
        PCE flow
    """
    return total_flow + truck_flow


def calculate_capacity(
    num_lanes: Union[pd.Series, float, int],
) -> Union[pd.Series, float]:
    """
    Calculate roadway capacity based on number of lanes.

    Args:
        num_lanes: Number of lanes

    Returns:
        Capacity in PCE/hour
    """
    return num_lanes * config.CAPACITY_PER_LANE


def calculate_vc_ratio(
    pce_flow: Union[pd.Series, float], capacity: Union[pd.Series, float]
) -> Union[pd.Series, float]:
    """
    Calculate Volume to Capacity (V/C) ratio.

    Args:
        pce_flow: PCE flow
        capacity: Roadway capacity

    Returns:
        V/C ratio (V/C 比率)
    """
    # Avoid division by zero
    if isinstance(capacity, pd.Series):
        return pce_flow.divide(capacity.replace(0, np.nan))
    else:
        return pce_flow / capacity if capacity > 0 else np.nan


def aggregate_by_direction_facility(
    df: pd.DataFrame, value_column: str, method: str = "mean"
) -> pd.DataFrame:
    """
    Aggregate segment data by direction and facility type.

    Args:
        df: DataFrame with segment data
        value_column: Column name to aggregate
        method: Aggregation method ('mean' or 'sum')

    Returns:
        Aggregated DataFrame
    """
    if method == "mean":
        grouped = df.groupby([config.DIRECTION_FIELD, config.TYPE_FIELD])[
            value_column
        ].mean()
    elif method == "sum":
        grouped = df.groupby([config.DIRECTION_FIELD, config.TYPE_FIELD])[
            value_column
        ].sum()
    else:
        raise ValueError(f"Invalid method: {method}. Must be 'mean' or 'sum'")

    return grouped.reset_index()


def validate_data(
    df: pd.DataFrame, column: str, range_key: str
) -> Tuple[bool, List[str]]:
    """
    Validate data values are within reasonable ranges.

    Args:
        df: DataFrame to validate
        column: Column name to validate
        range_key: Key in VALIDATION_RANGES config

    Returns:
        Tuple of (is_valid, error_messages)
    """
    is_valid = True
    errors = []

    if range_key not in config.VALIDATION_RANGES:
        return False, [f"Unknown validation range: {range_key}"]

    min_val = config.VALIDATION_RANGES[range_key]["min"]
    max_val = config.VALIDATION_RANGES[range_key]["max"]

    # Check for values outside range
    below_min = df[column] < min_val
    above_max = df[column] > max_val

    if below_min.any():
        is_valid = False
        count = below_min.sum()
        errors.append(f"{count} values in '{column}' below minimum ({min_val})")

    if above_max.any():
        is_valid = False
        count = above_max.sum()
        errors.append(f"{count} values in '{column}' above maximum ({max_val})")

    return is_valid, errors


def format_number(value: float, format_type: str = "integer") -> str:
    """
    Format number according to specified format type.

    Args:
        value: Number to format
        format_type: Format type from config.NUMBER_FORMATS

    Returns:
        Formatted string
    """
    if pd.isna(value):
        return "-"

    if format_type == "integer":
        return f"{int(value):,}"
    elif format_type == "decimal_1":
        return f"{value:,.1f}"
    elif format_type == "decimal_2":
        return f"{value:,.2f}"
    elif format_type == "decimal_3":
        return f"{value:,.3f}"
    elif format_type == "percent_1":
        return f"{value:.1%}"
    elif format_type == "percent_2":
        return f"{value:.2%}"
    else:
        return str(value)


def get_direction_name(direction_code: str, language: str = "en") -> str:
    """
    Get full direction name from direction code.

    Args:
        direction_code: 'N' or 'S'
        language: 'en' for English, 'zh' for Chinese (預設 'en')

    Returns:
        Full direction name (完整方向名稱)
    """
    if direction_code == "N":
        return "Northbound" if language == "en" else "北向"
    elif direction_code == "S":
        return "Southbound" if language == "en" else "南向"
    else:
        return direction_code


def get_facility_name(facility_code: str, language: str = "en") -> str:
    """
    Get full facility name from facility code.
    從設施代碼獲取完整設施名稱。

    Args:
        facility_code: Facility type code (設施類型代碼)
        language: 'en' for English, 'zh' for Chinese (預設 'en')

    Returns:
        Full facility name (完整設施名稱)
    """
    if facility_code == "ML":
        return "Main Lanes" if language == "en" else "主線"
    elif facility_code == "HV":
        return "HOV Lanes" if language == "en" else "HOV 車道"
    else:
        return facility_code


def create_summary_stats(df: pd.DataFrame) -> Dict:
    """
    Create summary statistics for a DataFrame.

    Args:
        df: DataFrame to summarize

    Returns:
        Dictionary of summary statistics
    """
    summary = {
        "total_segments": len(df),
        "directions": (
            df[config.DIRECTION_FIELD].nunique()
            if config.DIRECTION_FIELD in df.columns
            else 0
        ),
        "facility_types": (
            df[config.FACILITY_FIELD].nunique()
            if config.FACILITY_FIELD in df.columns
            else 0
        ),
    }

    return summary


def log_analysis_step(step_name: str, message: str, level: str = "INFO"):
    """
    Log an analysis step with consistent formatting.


    Args:
        step_name: Name of the analysis step
        message: Log message
        level: Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
    """
    formatted_message = f"[{step_name}] {message}"

    if level == "DEBUG":
        logger.debug(formatted_message)
    elif level == "INFO":
        logger.info(formatted_message)
    elif level == "WARNING":
        logger.warning(formatted_message)
    elif level == "ERROR":
        logger.error(formatted_message)
    else:
        logger.info(formatted_message)


if __name__ == "__main__":
    # Test utility functions
    print("Testing utility functions...")

    # Test LOS determination
    test_vc_ratios = [0.3, 0.5, 0.7, 0.9, 0.98, 1.05]
    print("\nLOS determination tests:")
    for vc in test_vc_ratios:
        los = get_los_from_vc(vc)
        print(f"  V/C = {vc:.2f} → LOS {los}")

    # Test peak hour calculation
    print("\nPeak hour calculation tests:")
    period_flow = 20000
    am_peak = calculate_peak_hour_flow(period_flow, "AM")
    pm_peak = calculate_peak_hour_flow(period_flow, "PM")
    print(f"  Period flow: {period_flow:,}")
    print(f"  AM peak hour: {am_peak:,.0f} (40% of period)")
    print(f"  PM peak hour: {pm_peak:,.0f} (30% of period)")

    # Test PCE calculation
    print("\nPCE calculation test:")
    total = 10000
    truck = 1000
    pce = calculate_pce_flow(total, truck)
    print(f"  Total flow: {total:,}, Truck flow: {truck:,}")
    print(f"  PCE flow: {pce:,.0f}")

    # Test capacity calculation
    print("\nCapacity calculation test:")
    lanes = 5
    capacity = calculate_capacity(lanes)
    print(f"  Lanes: {lanes}, Capacity: {capacity:,.0f} PCE/hr")

    print("\n✓ All tests completed!")
