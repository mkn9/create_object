"""
Tests for group timeline visualization and overlap analysis.

TDD Process: These tests are written FIRST, before implementation.
Expected: All tests should FAIL initially (RED phase).

Features to test:
- Generate activity timeline matrix (groups vs time)
- Identify overlapping groups
- Calculate concurrent activity statistics
- Display formatted output table
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from group_timeline import GroupTimeline, TimelineGenerator


# ============================================================================
# INVARIANT TESTS - Properties that must always hold
# ============================================================================

@pytest.mark.invariant
def test_timeline_values_binary():
    """Timeline values must be only 0 or 1"""
    timeline = GroupTimeline()
    data = pd.DataFrame({
        'group_id': [1, 2],
        'group_size': [10, 15],
        'start_percent': [0, 50],
        'stop_percent': [50, 100]
    })
    
    matrix, time_points = timeline.generate_timeline(data, num_points=10)
    unique_values = np.unique(matrix)
    assert all(v in [0, 1] for v in unique_values), "Timeline must contain only 0 and 1"


@pytest.mark.invariant
def test_timeline_shape_matches_groups_and_times():
    """Timeline matrix dimensions must match groups and time points"""
    timeline = GroupTimeline()
    data = pd.DataFrame({
        'group_id': [1, 2, 3],
        'group_size': [10, 15, 8],
        'start_percent': [0, 25, 60],
        'stop_percent': [30, 60, 95]
    })
    
    num_points = 20
    matrix, time_points = timeline.generate_timeline(data, num_points=num_points)
    
    assert matrix.shape[0] == len(data), f"Rows should be {len(data)}, got {matrix.shape[0]}"
    assert matrix.shape[1] == num_points, f"Columns should be {num_points}, got {matrix.shape[1]}"
    assert len(time_points) == num_points, f"Time points should be {num_points}, got {len(time_points)}"


@pytest.mark.invariant
def test_group_active_within_bounds():
    """Groups should only be active within their start/stop times"""
    timeline = GroupTimeline()
    data = pd.DataFrame({
        'group_id': [1],
        'group_size': [10],
        'start_percent': [25],
        'stop_percent': [75]
    })
    
    num_points = 100
    matrix, time_points = timeline.generate_timeline(data, num_points=num_points)
    
    # Check group is inactive before start
    early_times = [i for i, t in enumerate(time_points) if t < 25]
    for idx in early_times:
        assert matrix[0, idx] == 0, f"Group should be inactive before start at time {time_points[idx]}"
    
    # Check group is inactive after stop
    late_times = [i for i, t in enumerate(time_points) if t > 75]
    for idx in late_times:
        assert matrix[0, idx] == 0, f"Group should be inactive after stop at time {time_points[idx]}"


# ============================================================================
# GOLDEN TESTS - Known scenarios with expected outputs
# ============================================================================

@pytest.mark.golden
@pytest.mark.deterministic
def test_non_overlapping_groups():
    """Test two groups that don't overlap.
    
    Scenario: Group 1: 0-40%, Group 2: 60-100%
    Expected: No time points with both active
    """
    timeline = GroupTimeline()
    data = pd.DataFrame({
        'group_id': [1, 2],
        'group_size': [10, 15],
        'start_percent': [0, 60],
        'stop_percent': [40, 100]
    })
    
    matrix, time_points = timeline.generate_timeline(data, num_points=10)
    
    # Check no time has both groups active
    concurrent = np.sum(matrix, axis=0)
    assert np.max(concurrent) <= 1, "Groups should not overlap"


@pytest.mark.golden
@pytest.mark.deterministic
def test_overlapping_two_groups():
    """Test two groups with overlap.
    
    Scenario: Group 1: 0-60%, Group 2: 40-100%
    Expected: Some time points with both active (overlap 40-60%)
    """
    timeline = GroupTimeline()
    data = pd.DataFrame({
        'group_id': [1, 2],
        'group_size': [10, 15],
        'start_percent': [0, 40],
        'stop_percent': [60, 100]
    })
    
    matrix, time_points = timeline.generate_timeline(data, num_points=20)
    
    # Check there are times with both groups active
    concurrent = np.sum(matrix, axis=0)
    assert np.max(concurrent) >= 2, "Should have times with 2 groups active"
    
    # Check overlap region (40-60%)
    overlap_times = [i for i, t in enumerate(time_points) if 40 <= t <= 60]
    for idx in overlap_times:
        assert concurrent[idx] >= 1, f"Should have activity in overlap region at time {time_points[idx]}"


@pytest.mark.golden
def test_zero_groups_active():
    """Test that there can be times with zero groups active.
    
    Scenario: Group 1: 0-30%, Group 2: 70-100%
    Expected: Gap with no groups active (30-70%)
    """
    timeline = GroupTimeline()
    data = pd.DataFrame({
        'group_id': [1, 2],
        'group_size': [10, 15],
        'start_percent': [0, 70],
        'stop_percent': [30, 100]
    })
    
    matrix, time_points = timeline.generate_timeline(data, num_points=20)
    concurrent = np.sum(matrix, axis=0)
    
    # Should have some times with zero groups
    assert np.min(concurrent) == 0, "Should have times with no groups active"
    
    # Check gap region (30-70%)
    gap_times = [i for i, t in enumerate(time_points) if 30 < t < 70]
    if gap_times:
        assert any(concurrent[idx] == 0 for idx in gap_times), "Should have inactive times in gap"


@pytest.mark.golden
def test_three_groups_overlapping():
    """Test scenario with three groups active simultaneously.
    
    Scenario: Groups with overlapping periods
    Expected: At least one time point with 3 groups active
    """
    timeline = GroupTimeline()
    data = pd.DataFrame({
        'group_id': [1, 2, 3],
        'group_size': [10, 15, 8],
        'start_percent': [0, 20, 40],
        'stop_percent': [60, 80, 100]
    })
    
    matrix, time_points = timeline.generate_timeline(data, num_points=30)
    concurrent = np.sum(matrix, axis=0)
    
    # Should have times with 3 groups active (around 40-60%)
    assert np.max(concurrent) >= 3, "Should have times with 3 groups active"


# ============================================================================
# OVERLAP ANALYSIS TESTS
# ============================================================================

@pytest.mark.unit
def test_identify_overlaps():
    """Test identification of overlapping groups."""
    timeline = GroupTimeline()
    data = pd.DataFrame({
        'group_id': [1, 2, 3],
        'group_size': [10, 15, 8],
        'start_percent': [0, 20, 60],
        'stop_percent': [50, 70, 100]
    })
    
    overlaps = timeline.get_overlapping_groups(data)
    
    # Groups 1 and 2 overlap (20-50%)
    assert (1, 2) in overlaps or (2, 1) in overlaps, "Groups 1 and 2 should overlap"
    
    # Groups 2 and 3 overlap (60-70%)
    assert (2, 3) in overlaps or (3, 2) in overlaps, "Groups 2 and 3 should overlap"
    
    # Groups 1 and 3 don't overlap
    assert (1, 3) not in overlaps and (3, 1) not in overlaps, "Groups 1 and 3 should not overlap"


@pytest.mark.unit
def test_concurrent_statistics():
    """Test calculation of concurrent activity statistics."""
    timeline = GroupTimeline()
    data = pd.DataFrame({
        'group_id': [1, 2, 3],
        'group_size': [10, 15, 8],
        'start_percent': [0, 25, 50],
        'stop_percent': [50, 75, 100]
    })
    
    matrix, time_points = timeline.generate_timeline(data, num_points=20)
    stats = timeline.get_concurrent_stats(matrix)
    
    assert 'max_concurrent' in stats
    assert 'min_concurrent' in stats
    assert 'avg_concurrent' in stats
    assert stats['max_concurrent'] >= 1
    assert stats['min_concurrent'] >= 0


@pytest.mark.unit
def test_get_active_groups_at_time():
    """Test getting list of active groups at specific time."""
    timeline = GroupTimeline()
    data = pd.DataFrame({
        'group_id': [1, 2, 3],
        'group_size': [10, 15, 8],
        'start_percent': [0, 20, 60],
        'stop_percent': [50, 70, 100]
    })
    
    # At time 30%, groups 1 and 2 should be active
    active = timeline.get_active_groups_at_time(data, 30)
    assert 1 in active
    assert 2 in active
    assert 3 not in active
    
    # At time 65%, groups 2 and 3 should be active
    active = timeline.get_active_groups_at_time(data, 65)
    assert 1 not in active
    assert 2 in active
    assert 3 in active


# ============================================================================
# DISPLAY/FORMATTING TESTS
# ============================================================================

@pytest.mark.unit
def test_format_timeline_table():
    """Test formatting timeline as display table."""
    timeline = GroupTimeline()
    data = pd.DataFrame({
        'group_id': [1, 2],
        'group_size': [10, 15],
        'start_percent': [0, 50],
        'stop_percent': [50, 100]
    })
    
    matrix, time_points = timeline.generate_timeline(data, num_points=10)
    table_str = timeline.format_as_table(matrix, time_points, data)
    
    # Check it returns a string
    assert isinstance(table_str, str)
    
    # Check it contains group headers
    assert 'Group' in table_str
    
    # Check it contains time values
    assert any(str(int(t)) in table_str for t in time_points)


@pytest.mark.integration
def test_generate_complete_report():
    """Test generating complete analysis report."""
    timeline = GroupTimeline()
    data = pd.DataFrame({
        'group_id': [1, 2, 3],
        'group_size': [10, 15, 8],
        'start_percent': [0, 20, 60],
        'stop_percent': [50, 70, 100]
    })
    
    report = timeline.generate_report(data, num_points=20)
    
    assert 'timeline_table' in report
    assert 'overlapping_groups' in report
    assert 'concurrent_stats' in report
    assert isinstance(report['timeline_table'], str)
    assert isinstance(report['overlapping_groups'], list)
    assert isinstance(report['concurrent_stats'], dict)


# ============================================================================
# EDGE CASES
# ============================================================================

@pytest.mark.unit
def test_single_group_no_overlaps():
    """Test single group produces no overlaps."""
    timeline = GroupTimeline()
    data = pd.DataFrame({
        'group_id': [1],
        'group_size': [10],
        'start_percent': [0],
        'stop_percent': [100]
    })
    
    overlaps = timeline.get_overlapping_groups(data)
    assert len(overlaps) == 0, "Single group should have no overlaps"


@pytest.mark.unit
def test_all_groups_overlapping():
    """Test all groups overlapping in middle."""
    timeline = GroupTimeline()
    data = pd.DataFrame({
        'group_id': [1, 2, 3, 4],
        'group_size': [10, 15, 8, 12],
        'start_percent': [0, 10, 20, 30],
        'stop_percent': [60, 70, 80, 90]
    })
    
    matrix, time_points = timeline.generate_timeline(data, num_points=30)
    concurrent = np.sum(matrix, axis=0)
    
    # Should have at least one time with 4 groups active
    assert np.max(concurrent) >= 4, "Should have times with all 4 groups active"

