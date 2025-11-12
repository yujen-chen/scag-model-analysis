"""
Unit tests for DataLoader class
"""

import pytest
import pandas as pd
from src.data_loader import DataLoader


class TestDataLoader:
    """Test cases for DataLoader class"""

    def test_initialization(self):
        """Test DataLoader initialization"""
        loader = DataLoader()
        assert loader is not None
        assert hasattr(loader, "data_dir")

    def test_load_section_data(self):
        """Test loading section data"""
        loader = DataLoader()
        df = loader.load_section_data(2019, 1)

        # Check DataFrame is not empty
        assert not df.empty
        assert len(df) > 0

        # Check required columns exist
        required_columns = ["AADT", "DIR", "AB_FACILIT", "LENGTH"]
        for col in required_columns:
            assert col in df.columns, f"Missing column: {col}"

    def test_load_section_data_returns_dataframe(self):
        """Test that load_section_data returns a pandas DataFrame"""
        loader = DataLoader()
        df = loader.load_section_data(2019, 1)
        assert isinstance(df, pd.DataFrame)

    def test_data_has_correct_types(self):
        """Test that loaded data has correct data types"""
        loader = DataLoader()
        df = loader.load_section_data(2019, 1)

        # AADT should be numeric
        assert pd.api.types.is_numeric_dtype(df["AADT"])
        # LENGTH should be numeric
        assert pd.api.types.is_numeric_dtype(df["LENGTH"])


if __name__ == "__main__":
    # Allow running this file directly
    pytest.main([__file__, "-v"])
