# CLAUDE.md - AI Assistant Guide for SCAG Model Analysis

This document provides comprehensive guidance for AI assistants working with the SCAG I-5 Activity-Based Model Analysis codebase.

## Project Overview

**Project Name:** SCAG I-5 Activity-Based Model Analysis
**Version:** 1.0.0
**Author:** Yu-Jen Chen
**Purpose:** Transportation modeling and AADT (Annual Average Daily Traffic) calculations for Interstate 5 corridor analysis

This project analyzes traffic data from the SCAG 2024 Activity-Based Model for Interstate 5, performing calculations for:
- Annual Average Daily Traffic (AADT)
- Peak hour flows (AM/PM)
- Volume-to-Capacity (V/C) ratios
- Level of Service (LOS) analysis
- Truck traffic analysis

### Analysis Years and Sections
- **Base Year:** 2019
- **Forecast Year:** 2045
- **Sections:** 3 sections of I-5 corridor (Northern, Central, Santa Ana Freeway)

## Codebase Structure

```
scag-model-analysis/
├── src/                           # Source code
│   ├── __init__.py               # Package initialization
│   ├── config.py                 # Configuration constants and parameters
│   ├── data_loader.py            # Data loading and preprocessing
│   ├── aadt_calculator.py        # AADT calculation logic
│   ├── peak_hour_analyzer.py    # Peak hour flow analysis
│   └── utils.py                  # Utility functions
├── tests/                         # Test suite
│   ├── test_data_loader.py       # DataLoader tests
│   ├── test_aadt_actual.py       # AADT calculator tests
│   └── test_utils.py             # Utility function tests
├── data/                          # Data directory
│   ├── input/                    # Input CSV files (traffic data)
│   └── output/                   # Generated Excel reports
├── pyproject.toml                # Project configuration and dependencies
├── uv.lock                       # Dependency lock file
├── .python-version               # Python version specification
└── .gitignore                    # Git ignore patterns
```

## Module Architecture

### 1. Configuration Module (`config.py`)

Central configuration file containing all constants and parameters:

**Time Period Definitions:**
- AM: 06:00-10:00 (4 hours, peak factor: 0.40)
- PM: 15:00-19:00 (4 hours, peak factor: 0.30)
- MD: 10:00-15:00 (5 hours)
- EVE: 19:00-23:00 (4 hours)
- NT: 23:00-06:00 (7 hours)

**PCE (Passenger Car Equivalent) Factors:**
- AUTO_PCE = 1.0
- LHDT_PCE = 1.5 (Light Heavy Duty Trucks)
- MHDT_PCE = 2.0 (Medium Heavy Duty Trucks)
- HHDT_PCE = 2.5 (Heavy Heavy Duty Trucks)

**Capacity & LOS:**
- Capacity per lane: 2000 PCE/hour (HCM 2010)
- LOS Thresholds: A (≤0.35), B (≤0.54), C (≤0.77), D (≤0.93), E (≤1.00), F (>1.00)

**Field Mappings:**
- `PERIOD_FIELDS`: Maps time periods to CSV column names
- `LANE_FIELDS`: Maps periods to lane number columns
- `DIRECTION_FIELD`: "DIRECT" (N/S/E/W)
- `TYPE_FIELD`: "TYPE" (ML=Main Lanes, HV=HOV Lanes)

**File Naming:**
- Input pattern: `i5-cmcp-{year}-sec{section}.csv`
- Output default: `I5_Analysis_Output.xlsx`

### 2. Data Loader Module (`data_loader.py`)

**Class:** `DataLoader`

**Key Methods:**
- `load_section_data(year, section)` - Load single section/year
- `load_all_sections(year)` - Load all sections for a year
- `load_all_data()` - Load all available data
- `filter_by_direction(df, direction)` - Filter by N/S/E/W
- `filter_by_facility(df, facility)` - Filter by ML/HV
- `get_direction_facility_groups(df)` - Group by direction+facility
- `get_data_summary(df)` - Generate summary statistics

**Data Validation:**
Required fields in CSV files:
- `DIRECT` (direction)
- `TYPE` (facility type)
- `ID` (segment ID)
- `LENGTH` (segment length)
- Flow fields for AM and PM periods

### 3. AADT Calculator Module (`aadt_calculator.py`)

**Class:** `AADTCalculator`

**Calculation Levels:**
1. **Segment Level** - Individual road segments
2. **Group Level** - Aggregated by direction and facility type

**Key Methods:**
- `calculate_segment_aadt()` - Calculate AADT for each segment
  - Returns: `TOTAL_AADT`, `AUTO_AADT`, `TRUCK_AADT`, `TRUCK_PCT`
- `calculate_group_average_aadt(direction, facility_type)` - Group averages
- `calculate_all_groups()` - All direction/facility combinations
- `get_summary_stats()` - Overall statistics

**Formula:**
```
AADT = AM_flow + PM_flow + MD_flow + EVE_flow + NT_flow
TRUCK_PCT = (TRUCK_AADT / TOTAL_AADT) * 100
```

### 4. Peak Hour Analyzer Module (`peak_hour_analyzer.py`)

**Class:** `PeakHourAnalyzer`

**Key Methods:**
- `calculate_segment_peak_flows()` - Calculate AM/PM peak for each segment
  - Returns: `{AM|PM}_PEAK_{TOTAL|AUTO|TRUCK}`
- `calculate_group_average_peak(direction, facility_type, period)` - Group peak averages
- `calculate_all_groups_peak(period)` - All groups for AM or PM
- `get_peak_summary_stats(period)` - Summary statistics
- `compare_am_pm_peaks()` - Side-by-side AM/PM comparison

**Formula:**
```
AM Peak Hour Flow = AM Period Flow × 0.40
PM Peak Hour Flow = PM Period Flow × 0.30
```

### 5. Utilities Module (`utils.py`)

**Key Functions:**

**Flow Calculations:**
- `calculate_period_flow(df, period, flow_type)` - Period flow calculation
- `calculate_aadt(df)` - Full AADT calculation
- `calculate_peak_hour_flow(period_flow, period)` - Peak conversion

**Capacity & LOS:**
- `calculate_pce_flow(total_flow, truck_flow)` - PCE conversion
- `calculate_capacity(num_lanes)` - Capacity calculation
- `calculate_vc_ratio(pce_flow, capacity)` - V/C ratio
- `get_los_from_vc(vc_ratio)` - LOS determination

**Data Processing:**
- `aggregate_by_direction_facility(df, value_column, method)` - Aggregation
- `validate_data(df, column, range_key)` - Data validation

**Formatting:**
- `format_number(value, format_type)` - Number formatting
- `get_direction_name(direction_code, language)` - Direction labels
- `get_facility_name(facility_code, language)` - Facility labels

**Logging:**
- `log_analysis_step(step_name, message, level)` - Consistent logging

## Development Workflow

### Environment Setup

**Python Version:** 3.12+ (specified in `.python-version`)

**Package Manager:** Uses `uv` for dependency management

```bash
# Install dependencies
uv pip install -e .

# Install with test dependencies
uv pip install -e ".[test]"

# Install all dependencies (test + dev)
uv pip install -e ".[all]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_data_loader.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run verbose
pytest -v
```

### Code Quality

**Linting:**
```bash
flake8 src/
```

**Formatting:**
```bash
black src/ tests/
```

**Type Checking:**
```bash
mypy src/
```

## Key Conventions

### 1. Code Organization

**Class-Based Design:**
- Each major analysis component is a class (DataLoader, AADTCalculator, PeakHourAnalyzer)
- Classes accept DataFrame inputs and store results
- Methods follow single responsibility principle

**Separation of Concerns:**
- `config.py` - All constants and parameters
- `utils.py` - Reusable utility functions
- Module files - Domain-specific logic

### 2. Data Flow

**Standard Analysis Pipeline:**
```python
# 1. Load data
loader = DataLoader()
df = loader.load_section_data(year=2019, section=1)

# 2. Calculate AADT
aadt_calc = AADTCalculator(df)
df_with_aadt = aadt_calc.calculate_segment_aadt()
summary = aadt_calc.calculate_all_groups()

# 3. Analyze peak hours
peak_analyzer = PeakHourAnalyzer(df_with_aadt)
df_with_peaks = peak_analyzer.calculate_segment_peak_flows()
am_summary = peak_analyzer.calculate_all_groups_peak('AM')
pm_summary = peak_analyzer.calculate_all_groups_peak('PM')
```

### 3. Naming Conventions

**Variables:**
- Snake_case for variables and functions: `total_aadt`, `calculate_peak_flow()`
- UPPER_CASE for constants: `AM_PEAK_FACTOR`, `CAPACITY_PER_LANE`

**DataFrame Columns:**
- Original CSV columns: As-is (e.g., "AB_FLOW_DA", "DIRECT")
- Calculated columns: UPPER_CASE with underscores (e.g., "TOTAL_AADT", "AM_PEAK_TOTAL")

**Direction/Facility Codes:**
- Direction: N, S, E, W
- Facility: ML (Main Lanes), HV (HOV Lanes)

### 4. Documentation

**Docstrings:**
- All classes and public methods have docstrings
- Include Args, Returns, and Example sections
- Use type hints in function signatures

**Logging:**
- Use `log_analysis_step()` for consistent logging
- Log at INFO level for major operations
- Log at WARNING for validation issues
- Log at ERROR for failures

### 5. Error Handling

**File Operations:**
- Check file existence before loading
- Raise FileNotFoundError with descriptive messages
- Use try-except blocks for file I/O

**Data Validation:**
- Validate required fields after loading
- Check value ranges using `validate_data()`
- Handle division by zero in calculations

## Data File Structure

### Input Files (CSV)

**Location:** `data/input/`

**Naming:** `i5-cmcp-{year}-sec{section}.csv`

**Examples:**
- `i5-cmcp-2019-sec1.csv`
- `i5-cmcp-2045-sec3.csv`

**Required Columns:**
- `ID` - Segment identifier
- `LENGTH` - Segment length
- `DIRECT` - Direction (N/S/E/W)
- `TYPE` - Facility type (ML/HV)
- `AB_AMLANES`, `AB_PMLANES` - Lane counts
- Flow columns: `AB_FLOW_*` (various period/vehicle combinations)

### Output Files (Excel)

**Location:** `data/output/`

**Format:** Multi-sheet Excel workbooks with analysis results

**Typical Sheets:**
- Summary_all - Overall summary
- Raw_Data - Original data
- Calculations - AADT and peak calculations
- Truck_Analysis - Truck-specific analysis
- Peak_Hour_Analysis - Peak hour details
- LOS_Analysis - Level of service analysis

## Common Tasks

### Adding New Analysis Years

1. Add CSV files to `data/input/` with correct naming
2. Update `ANALYSIS_YEARS` in `config.py`:
   ```python
   ANALYSIS_YEARS = [2019, 2045, 2050]  # Add new year
   ```

### Adding New Sections

1. Add section definition in `config.py`:
   ```python
   SECTIONS = {
       1: {...},
       2: {...},
       3: {...},
       4: {"name": "Section 4", "description": "...", "route": "..."}
   }
   ```
2. Add corresponding CSV files

### Modifying Peak Hour Factors

Edit factors in `config.py`:
```python
AM_PEAK_FACTOR = 0.40  # Modify as needed
PM_PEAK_FACTOR = 0.30  # Modify as needed
```

### Adding New Validation Rules

Add to `VALIDATION_RANGES` in `config.py`:
```python
VALIDATION_RANGES = {
    "new_metric": {"min": 0, "max": 1000},
    ...
}
```

## Testing Guidelines

### Test Organization

- One test file per module
- Use pytest framework
- Group related tests in classes

### Test Pattern

```python
class TestModuleName:
    """Test cases for ModuleName class"""

    def test_initialization(self):
        """Test object initialization"""
        obj = ModuleName()
        assert obj is not None

    def test_method_name(self):
        """Test specific method"""
        # Arrange
        obj = ModuleName()

        # Act
        result = obj.method()

        # Assert
        assert result is not None
```

### Running Individual Tests

```bash
# Run specific test class
pytest tests/test_data_loader.py::TestDataLoader

# Run specific test method
pytest tests/test_data_loader.py::TestDataLoader::test_initialization
```

## Git Workflow

### Branch Strategy

- Main branch: Production-ready code
- Feature branches: Named `claude/claude-md-*` for AI-assisted development

### Commit Messages

Follow conventional commit style:
- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
- `docs:` - Documentation updates

### Recent Development

Recent commits show progression:
1. Initial code testing
2. AADT calculator implementation
3. Peak hour analyzer development
4. Minor fixes and refinements

## Important Notes for AI Assistants

### When Making Changes

1. **Always preserve existing functionality** - This is production analysis code
2. **Maintain configuration-driven design** - Use `config.py` for parameters
3. **Follow the established data flow** - Load → Calculate → Analyze
4. **Add appropriate logging** - Use `log_analysis_step()` consistently
5. **Validate inputs** - Check data ranges and required fields
6. **Update tests** - Add tests for new functionality

### When Adding Features

1. Check if configuration changes are needed in `config.py`
2. Add new methods to existing classes when appropriate
3. Create new utility functions in `utils.py` for reusable logic
4. Update docstrings with examples
5. Add corresponding tests

### When Debugging

1. Check `config.py` for parameter values
2. Review logging output for analysis steps
3. Verify input data format and required columns
4. Check validation ranges in `config.VALIDATION_RANGES`
5. Ensure proper direction/facility code usage

### Transportation Domain Knowledge

**AADT (Annual Average Daily Traffic):**
- Sum of all daily traffic volumes over a year divided by 365
- In this project: Sum of all time period flows

**Peak Hour:**
- Highest traffic hour within a time period
- Calculated using period-specific factors

**PCE (Passenger Car Equivalent):**
- Converts mixed traffic to equivalent passenger cars
- Trucks have higher PCE values (1.5-2.5 vs 1.0 for cars)

**V/C Ratio (Volume-to-Capacity):**
- Measure of congestion
- Higher values indicate more congestion
- Used to determine Level of Service (LOS)

**LOS (Level of Service):**
- A-F grading scale for traffic flow quality
- A = Free flow, F = Breakdown/forced flow

## Dependencies

### Core Dependencies
- `pandas>=2.0.0` - Data processing
- `numpy>=1.24.0` - Numerical operations
- `openpyxl>=3.1.0` - Excel file reading
- `xlsxwriter>=3.1.0` - Excel file writing
- `pydantic>=2.0.0` - Data validation
- `tqdm>=4.65.0` - Progress bars
- `click>=8.1.0` - CLI interface

### Test Dependencies
- `pytest>=7.4.0` - Testing framework
- `pytest-cov>=4.1.0` - Coverage reporting

### Development Dependencies
- `black>=23.0.0` - Code formatting
- `flake8>=6.0.0` - Linting
- `mypy>=1.5.0` - Type checking

## Version History

- **v1.0.0** - Initial release with AADT and peak hour analysis
  - DataLoader implementation
  - AADT Calculator
  - Peak Hour Analyzer
  - Comprehensive utility functions
  - Test suite

---

**Last Updated:** 2025-11-15
**Maintainer:** Yu-Jen Chen
**For AI Assistants:** This document should be consulted before making any code changes to ensure consistency with project architecture and conventions.
