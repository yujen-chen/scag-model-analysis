"""
Configuration file for SCAG I-5 Analysis

This file contains all the constants and parameters used in the analysis.。
"""

# ============================================================================
# TIME PERIOD FACTORS
# ============================================================================

# Peak hour factors for converting period flows to peak hour flows
AM_PEAK_FACTOR = 0.40  # AM peak hour is 40% of AM period (4 hours)
PM_PEAK_FACTOR = 0.30  # PM peak hour is 30% of PM period (4 hours)

# Time period definitions (hours)
TIME_PERIODS = {
    "AM": {"start": 6, "end": 10, "duration": 4},  # 06:00-10:00
    "PM": {"start": 15, "end": 19, "duration": 4},  # 15:00-19:00
    "MD": {"start": 10, "end": 15, "duration": 5},  # 10:00-15:00
    "EVE": {"start": 19, "end": 23, "duration": 4},  # 19:00-23:00
    "NT": {"start": 23, "end": 6, "duration": 7},  # 23:00-06:00 (next day)
}

# ============================================================================
# PCE (PASSENGER CAR EQUIVALENT) FACTORS
# ============================================================================

# PCE factors for different vehicle types

AUTO_PCE = 1.0  # Passenger cars
LHDT_PCE = 1.5  # Light Heavy Duty Trucks
MHDT_PCE = 2.0  # Medium Heavy Duty Trucks
HHDT_PCE = 2.5  # Heavy Heavy Duty Trucks

# Average truck PCE (used for simplified calculations)
TRUCK_PCE_AVG = (LHDT_PCE + MHDT_PCE + HHDT_PCE) / 3  # = 2.0

# ============================================================================
# CAPACITY PARAMETERS (容量參數)
# ============================================================================

# Standard freeway capacity per lane (HCM 2010)

CAPACITY_PER_LANE = 2000  # PCE per hour per lane

# ============================================================================
# LOS (LEVEL OF SERVICE) THRESHOLDS
# ============================================================================

# LOS thresholds based on V/C ratio (HCM 2010)

LOS_THRESHOLDS = {
    "A": 0.35,  # Free flow
    "B": 0.54,  # Reasonably free flow
    "C": 0.77,  # Stable flow
    "D": 0.93,  # Approaching unstable flow
    "E": 1.00,  # Unstable flow
    "F": float("inf"),  # Forced or breakdown flow
}

# LOS descriptions
LOS_DESCRIPTIONS = {
    "A": {
        "en": "Free flow",
        "description": "Vehicles can freely choose speed and lane",
    },
    "B": {
        "en": "Reasonably free flow",
        "description": "Vehicles can still move freely with slight influence",
    },
    "C": {
        "en": "Stable flow",
        "description": "Speed is limited but flow is stable",
    },
    "D": {
        "en": "Approaching unstable flow",
        "description": "Speed significantly reduced, high density",
    },
    "E": {
        "en": "Unstable flow",
        "description": "Near or at capacity, stop-and-go traffic",
    },
    "F": {
        "en": "Forced flow / Breakdown",
        "description": "Over capacity, severe congestion",
    },
}

# ============================================================================
# FIELD MAPPING
# ============================================================================

# CSV column mapping for different time periods and vehicle types

# AM Period fields
AM_FIELDS = {
    "auto": ["AB_FLOW_DA", "AB_FLOW_SR", "AB_FLOW_S1"],
    "truck": ["AB_FLOW_LI", "AB_FLOW_ME", "AB_FLOW_HE"],
}

# PM Period fields
PM_FIELDS = {
    "auto": ["AB_FLOW_D1", "AB_FLOW_S4", "AB_FLOW_S5"],
    "truck": ["AB_FLOW_L1", "AB_FLOW_M1", "AB_FLOW_H1"],
}

# MD (Midday) Period fields
MD_FIELDS = {
    "auto": ["AB_FLOW_D2", "AB_FLOW_S8", "AB_FLOW_S9"],
    "truck": ["AB_FLOW_L2", "AB_FLOW_M2", "AB_FLOW_H2"],
}

# EVE (Evening) Period fields
EVE_FIELDS = {
    "auto": ["AB_FLOW_D3", "AB_FLOW_12", "AB_FLOW_13"],
    "truck": ["AB_FLOW_L3", "AB_FLOW_M3", "AB_FLOW_H3"],
}

# NT (Night) Period fields
NT_FIELDS = {
    "auto": ["AB_FLOW_D4", "AB_FLOW_16", "AB_FLOW_17"],
    "truck": ["AB_FLOW_L4", "AB_FLOW_M4", "AB_FLOW_H4"],
}

# All period fields combined
PERIOD_FIELDS = {
    "AM": AM_FIELDS,
    "PM": PM_FIELDS,
    "MD": MD_FIELDS,
    "EVE": EVE_FIELDS,
    "NT": NT_FIELDS,
}

# Lane number fields for different periods

LANE_FIELDS = {
    "AM": "AB_AMLANES",
    "PM": "AB_PMLANES",
    "MD": "AB_MDLANES",
    "EVE": "AB_EVELANE",
    "NT": "AB_NTLANES",
}

# ============================================================================
# LANE TYPES AND DIRECTIONS
# ============================================================================

# Lane types
LANE_TYPES = {"ML": "Main Lanes", "HV": "HOV Lanes"}

# Direction codes
DIRECTIONS = {
    "N": "Northbound",
    "S": "Southbound",
    "E": "Eastbound",
    "W": "Westbound",
}

# Direction field name in CSV
DIRECTION_FIELD = "DIRECT"

# Lane type field name in CSV
TYPE_FIELD = "TYPE"

# ============================================================================
# SECTION DEFINITIONS
# ============================================================================

# Section names and descriptions
SECTIONS = {
    1: {
        "name": "Section 1",
        "description": "I-5 Corridor - Northern Segment",
        "route": "Interstate 5",
    },
    2: {
        "name": "Section 2",
        "description": "I-5 Corridor - Central Segment",
        "route": "Interstate 5",
    },
    3: {
        "name": "Section 3",
        "description": "I-5 Santa Ana Freeway",
        "route": "Interstate 5",
    },
}

# ============================================================================
# FILE PATHS
# ============================================================================

# Input data directory
INPUT_DIR = "data/input"

# Output data directory
OUTPUT_DIR = "data/output"

# File naming patterns
INPUT_FILE_PATTERN = "i5-cmcp-{year}-sec{section}.csv"
OUTPUT_FILE_DEFAULT = "I5_Analysis_Output.xlsx"

# ============================================================================
# ANALYSIS YEARS
# ============================================================================

BASE_YEAR = 2019  # Base year
FORECAST_YEAR = 2045  # Forecast year
ANALYSIS_YEARS = [BASE_YEAR, FORECAST_YEAR]

# ============================================================================
# EXCEL OUTPUT SETTINGS
# ============================================================================

# Sheet names for Excel output

EXCEL_SHEETS = {
    "summary": "Summary_all",
    "raw_data": "Raw_Data",
    "calculations": "Calculations",
    "truck_analysis": "Truck_Analysis",
    "peak_analysis": "Peak_Hour_Analysis",
    "los_analysis": "LOS_Analysis",
}

# Column widths for Excel formatting (in characters)

COLUMN_WIDTHS = {
    "year": 8,
    "section": 10,
    "direction": 12,
    "facility": 15,
    "segments": 15,
    "aadt": 20,
    "peak": 20,
    "vc": 10,
    "los": 8,
}

# Number formats for Excel
NUMBER_FORMATS = {
    "integer": "#,##0",
    "decimal_1": "#,##0.0",
    "decimal_2": "#,##0.00",
    "decimal_3": "#,##0.000",
    "percent_1": "0.0%",
    "percent_2": "0.00%",
}

# ============================================================================
# VALIDATION RULES
# ============================================================================

# Minimum and maximum reasonable values for validation

VALIDATION_RANGES = {
    "aadt": {"min": 0, "max": 500000},  # AADT range
    "peak_flow": {"min": 0, "max": 25000},  # Peak hour flow range
    "lanes": {"min": 1, "max": 10},  # Number of lanes
    "vc_ratio": {"min": 0, "max": 3.0},  # V/C ratio range
    "truck_pct": {"min": 0, "max": 100},  # Truck percentage
}

# ============================================================================
# LOGGING SETTINGS
# ============================================================================

# Log level

LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

# Log format

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================================================
# METADATA
# ============================================================================

# Analysis metadata
METADATA = {
    "model": "SCAG 2024 Activity-Based Model",
    "agency": "Southern California Association of Governments (SCAG)",
    "analyst": "Caltrans District 12",
    "reference": "Highway Capacity Manual (HCM) 2010",
    "version": "1.0.0",
    "last_updated": "2025-10-31",
}

# ============================================================================
# CALCULATION METHODS
# ============================================================================

# Method for aggregating link values

AGGREGATION_METHOD = "AVERAGE"  # Use AVERAGE for continuous freeway segments


# Alternative: 'SUM' (not recommended for continuous segments)
