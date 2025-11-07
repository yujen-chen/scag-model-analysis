"""
Data Loader Module for SCAG I-5 Analysis
This module handles loading and preprocessing of SCAG ABM data.

"""

import pandas as pd
import os
from typing import Optional, List, Dict
import logging

from . import config
from .utils import log_analysis_step, validate_data, create_summary_stats

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Class for loading and preprocessing SCAG ABM traffic data.
    """

    def __init__(self, data_dir: str = None):
        """
        Initialize DataLoader.

        Args:
            data_dir: Path to data directory
                     If None, uses config.INPUT_DIR
        """
        self.data_dir = data_dir or config.INPUT_DIR
        log_analysis_step("DataLoader", f"Initialized with data_dir: {self.data_dir}")

    def load_section_data(self, year: int, section: int) -> pd.DataFrame:
        """
        Load data for a specific year and section.

        Args:
            year: Analysis year (2019 or 2045)
            section: Section number

        Returns:
            DataFrame containing section data (DataFrame)
        """
        # Construct filename
        filename = config.INPUT_FILE_PATTERN.format(year=year, section=section)
        filepath = os.path.join(self.data_dir, filename)

        log_analysis_step("DataLoader", f"Loading data from: {filepath}")

        # Check if file exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Data file not found: {filepath}")

        try:
            # Load CSV file
            df = pd.read_csv(filepath, encoding="utf-8-sig")

            log_analysis_step(
                "DataLoader", f"Successfully loaded {len(df)} segments from {filename}"
            )

            # Basic data validation
            self._validate_required_fields(df)

            # Add metadata columns
            df["YEAR"] = year
            df["SECTION"] = section

            return df

        except Exception as e:
            logger.error(f"Error loading data from {filepath}: {str(e)}")
            raise

    def load_all_sections(self, year: int) -> Dict[int, pd.DataFrame]:
        """
        Load data for all sections of a specific year.


        Args:
            year: Analysis year

        Returns:
            Dictionary mapping section number to DataFrame

        """
        log_analysis_step("DataLoader", f"Loading all sections for year {year}")

        sections_data = {}
        for section in [1, 2, 3]:
            try:
                df = self.load_section_data(year, section)
                sections_data[section] = df
                log_analysis_step(
                    "DataLoader", f"Loaded section {section}: {len(df)} segments"
                )
            except FileNotFoundError:
                logger.warning(f"Section {section} data not found for year {year}")
                continue

        return sections_data

    def load_all_data(self) -> Dict[int, Dict[int, pd.DataFrame]]:
        """
        Load all available data (all years and sections).

        Returns:
            Nested dictionary: {year: {section: DataFrame}}
        """
        log_analysis_step("DataLoader", "Loading all available data")

        all_data = {}
        for year in config.ANALYSIS_YEARS:
            all_data[year] = self.load_all_sections(year)

        # Log summary
        total_sections = sum(len(sections) for sections in all_data.values())
        log_analysis_step(
            "DataLoader",
            f"Loaded data for {len(all_data)} years, {total_sections} sections total",
        )

        return all_data

    def _validate_required_fields(self, df: pd.DataFrame):
        """
        Validate that DataFrame contains required fields.


        Args:
            df: DataFrame to validate

        Raises:
            ValueError: If required fields are missing
        """
        required_fields = [
            config.DIRECTION_FIELD,
            config.FACILITY_FIELD,
            "ID",
            "LENGTH",
        ]

        # Check for required fields
        missing_fields = [field for field in required_fields if field not in df.columns]

        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        # Check for flow fields (at least AM and PM should exist)
        am_fields_exist = any(
            field in df.columns
            for field in config.AM_FIELDS["auto"] + config.AM_FIELDS["truck"]
        )
        pm_fields_exist = any(
            field in df.columns
            for field in config.PM_FIELDS["auto"] + config.PM_FIELDS["truck"]
        )

        if not (am_fields_exist and pm_fields_exist):
            raise ValueError("Missing required flow fields (AM or PM period data)")

        log_analysis_step("DataLoader", "Data validation passed")

    def filter_by_direction(self, df: pd.DataFrame, direction: str) -> pd.DataFrame:
        """
        Filter data by direction.

        Args:
            df: DataFrame to filter
            direction: Direction code ('N' or 'S')

        Returns:
            Filtered DataFrame
        """
        if direction not in ["N", "S"]:
            raise ValueError("Direction must be 'N' or 'S'")

        filtered = df[df[config.DIRECTION_FIELD] == direction].copy()
        log_analysis_step(
            "DataLoader", f"Filtered by direction {direction}: {len(filtered)} segments"
        )

        return filtered

    def filter_by_facility(self, df: pd.DataFrame, facility: str) -> pd.DataFrame:
        """
        Filter data by facility type.

        Args:
            df: DataFrame to filter
            facility: Facility code

        Returns:
            Filtered DataFrame
        """
        filtered = df[df[config.FACILITY_FIELD] == facility].copy()
        log_analysis_step(
            "DataLoader", f"Filtered by facility {facility}: {len(filtered)} segments"
        )

        return filtered

    def get_direction_facility_groups(
        self, df: pd.DataFrame
    ) -> Dict[tuple, pd.DataFrame]:
        """
        Group data by direction and facility type.

        Args:
            df: DataFrame to group

        Returns:
            Dictionary mapping (direction, facility) to DataFrame
        """
        groups = {}

        for direction in df[config.DIRECTION_FIELD].unique():
            for facility in df[config.FACILITY_FIELD].unique():
                mask = (df[config.DIRECTION_FIELD] == direction) & (
                    df[config.FACILITY_FIELD] == facility
                )
                group_df = df[mask].copy()

                if len(group_df) > 0:
                    groups[(direction, facility)] = group_df
                    log_analysis_step(
                        "DataLoader",
                        f"Group ({direction}, {facility}): {len(group_df)} segments",
                    )

        return groups

    def get_data_summary(self, df: pd.DataFrame) -> Dict:
        """
        Get summary statistics for loaded data.

        Args:
            df: DataFrame to summarize

        Returns:
            Dictionary of summary statistics
        """
        summary = create_summary_stats(df)

        # Add additional summary info
        if "YEAR" in df.columns:
            summary["year"] = df["YEAR"].iloc[0] if len(df) > 0 else None
        if "SECTION" in df.columns:
            summary["section"] = df["SECTION"].iloc[0] if len(df) > 0 else None

        # Count segments by direction and facility
        if config.DIRECTION_FIELD in df.columns and config.FACILITY_FIELD in df.columns:
            summary["segments_by_group"] = (
                df.groupby([config.DIRECTION_FIELD, config.FACILITY_FIELD])
                .size()
                .to_dict()
            )

        return summary

    def export_to_csv(self, df: pd.DataFrame, filename: str, output_dir: str = None):
        """
        Export DataFrame to CSV file.


        Args:
            df: DataFrame to export
            filename: Output filename
            output_dir: Output directory
                       If None, uses config.OUTPUT_DIR
        """
        output_dir = output_dir or config.OUTPUT_DIR
        os.makedirs(output_dir, exist_ok=True)

        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath, index=False, encoding="utf-8-sig")

        log_analysis_step("DataLoader", f"Exported data to: {filepath}")


if __name__ == "__main__":
    """
    Test the DataLoader class

    """
    print("Testing DataLoader...")
    print("=" * 60)

    # Test with actual data path
    test_data_dir = "../data/input"
    if not os.path.exists(test_data_dir):
        test_data_dir = "/mnt/user-data/uploads"

    loader = DataLoader(data_dir=test_data_dir)

    # Test loading single section
    print("\n1. Testing load_section_data...")
    try:
        df_2019_sec1 = loader.load_section_data(year=2019, section=1)
        print(f"   ✓ Loaded 2019 Section 1: {len(df_2019_sec1)} segments")
        print(f"   Columns: {list(df_2019_sec1.columns[:10])}...")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test data summary
    print("\n2. Testing get_data_summary...")
    try:
        summary = loader.get_data_summary(df_2019_sec1)
        print("   Summary:")
        for key, value in summary.items():
            print(f"     {key}: {value}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test filtering
    print("\n3. Testing filter functions...")
    try:
        df_northbound = loader.filter_by_direction(df_2019_sec1, "N")
        print(f"   ✓ Northbound segments: {len(df_northbound)}")

        df_ml = loader.filter_by_facility(df_2019_sec1, "ML")
        print(f"   ✓ Main Lanes segments: {len(df_ml)}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test grouping
    print("\n4. Testing get_direction_facility_groups...")
    try:
        groups = loader.get_direction_facility_groups(df_2019_sec1)
        print(f"   ✓ Found {len(groups)} groups:")
        for (dir, fac), group_df in groups.items():
            print(f"     ({dir}, {fac}): {len(group_df)} segments")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n" + "=" * 60)
    print("✓ DataLoader tests completed!")
