"""
Quick test script for TruckAnalyzer
"""

import sys
import pandas as pd

# Use absolute import
from src.data_loader import DataLoader
from src.aadt_calculator import AADTCalculator
from src.peak_hour_analyzer import PeakHourAnalyzer
from src.truck_analyzer import TruckAnalyzer

def test_truck_analyzer():
    print("=" * 60)
    print("Testing TruckAnalyzer Implementation")
    print("=" * 60)

    # Load data
    print("\n1. Loading data...")
    loader = DataLoader()
    df = loader.load_section_data(2019, 1)
    print(f"   ✓ Loaded {len(df)} segments")

    # Calculate AADT (need TRUCK_AADT and TRUCK_PCT)
    print("\n2. Calculating AADT...")
    aadt_calc = AADTCalculator(df)
    df = aadt_calc.calculate_segment_aadt()
    print(f"   ✓ AADT calculated")

    # Use TOTAL_AADT (the actual column name)
    print(f"   ✓ Average Total AADT: {df['TOTAL_AADT'].mean():,.0f}")
    print(f"   ✓ Average Truck AADT: {df['TRUCK_AADT'].mean():,.0f}")
    print(f"   ✓ Average Truck %: {df['TRUCK_PCT'].mean():.1f}%")

    # Calculate peak flows (need AM_PEAK_TRUCK, PM_PEAK_TRUCK)
    print("\n3. Calculating peak flows...")
    peak_analyzer = PeakHourAnalyzer(df)
    df = peak_analyzer.calculate_segment_peak_flows()
    print(f"   ✓ Peak flows calculated")

    # Create truck analyzer
    print("\n4. Creating TruckAnalyzer...")
    truck_analyzer = TruckAnalyzer(df)
    print(f"   ✓ TruckAnalyzer initialized")

    # Test workflow
    print("\n5. Testing calculate_segment_truck_metrics()...")
    result_df = truck_analyzer.calculate_segment_truck_metrics()
    print(f"   ✓ Added truck metrics columns")
    print(f"   ✓ Average truck %: {result_df['TRUCK_PCT'].mean():.1f}%")
    print(f"   ✓ Average truck intensity: {result_df['TRUCK_INTENSITY'].mean():.0f}")
    print(f"   ✓ Average AM truck ratio: {result_df['AM_TRUCK_RATIO'].mean():.1f}%")
    print(f"   ✓ Average PM truck ratio: {result_df['PM_TRUCK_RATIO'].mean():.1f}%")

    print("\n6. Testing get_truck_summary_stats()...")
    summary = truck_analyzer.get_truck_summary_stats()
    print(f"   ✓ Total segments: {summary['total_segments']}")
    print(f"   ✓ Average truck %: {summary['avg_truck_pct']:.1f}%")
    print(f"   ✓ High truck segments (>15%): {summary['segments_high_truck']}")
    print(f"   ✓ Total daily truck volume: {summary['total_daily_truck_volume']:,.0f}")

    print("\n7. Testing identify_high_truck_segments()...")
    high_truck = truck_analyzer.identify_high_truck_segments(truck_pct_threshold=15.0)
    print(f"   ✓ Found {len(high_truck)} high truck segments")
    if len(high_truck) > 0:
        print(f"   ✓ Highest truck %: {high_truck['TRUCK_PCT'].iloc[0]:.1f}%")

    print("\n8. Testing compare_am_pm_truck_flows()...")
    comparison = truck_analyzer.compare_am_pm_truck_flows()
    print(f"   ✓ Compared {len(comparison)} groups")
    print(f"   ✓ Columns: {list(comparison.columns)}")

    print("\n9. Testing calculate_all_groups_truck()...")
    all_groups = truck_analyzer.calculate_all_groups_truck()
    print(f"   ✓ Analyzed {len(all_groups)} groups")
    print(f"   ✓ Columns: {list(all_groups.columns)}")

    print("\n10. Testing get_truck_distribution_by_period()...")
    distribution = truck_analyzer.get_truck_distribution_by_period()
    print(f"   ✓ Got distribution for {len(distribution)} groups")

    print("\n11. Testing analyze_truck_composition()...")
    composition = truck_analyzer.analyze_truck_composition()
    print(f"   ✓ AM total truck flow: {composition['AM']['total_truck_flow']:,.0f}")
    print(f"   ✓ AM LHDT: {composition['AM']['lhdt_pct']:.1f}%")
    print(f"   ✓ AM MHDT: {composition['AM']['mhdt_pct']:.1f}%")
    print(f"   ✓ AM HHDT: {composition['AM']['hhdt_pct']:.1f}%")
    print(f"   ✓ PM total truck flow: {composition['PM']['total_truck_flow']:,.0f}")
    print(f"   ✓ PM LHDT: {composition['PM']['lhdt_pct']:.1f}%")
    print(f"   ✓ PM MHDT: {composition['PM']['mhdt_pct']:.1f}%")
    print(f"   ✓ PM HHDT: {composition['PM']['hhdt_pct']:.1f}%")

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_truck_analyzer()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
