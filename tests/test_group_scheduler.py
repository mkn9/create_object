"""
Tests for group scheduler - CSV reading and validation.

This file demonstrates TDD workflow:
- Invariant tests: Properties that must always hold
- Golden tests: Known input/output scenarios
- Edge case tests: Boundary conditions
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from group_scheduler import GroupScheduler, ValidationError


# ============================================================================
# INVARIANT TESTS - Properties that must always hold
# ============================================================================

@pytest.mark.invariant
def test_start_times_non_negative():
    """All start times must be >= 0"""
    scheduler = GroupScheduler()
    data = pd.DataFrame({
        'group_id': [1, 2],
        'group_size': [10, 15],
        'start_percent': [0, 20],
        'stop_percent': [50, 80]
    })
    
    result = scheduler.validate_data(data)
    assert result is True
    assert all(data['start_percent'] >= 0)


@pytest.mark.invariant
def test_stop_times_within_bounds():
    """All stop times must be <= 100"""
    scheduler = GroupScheduler()
    data = pd.DataFrame({
        'group_id': [1, 2],
        'group_size': [10, 15],
        'start_percent': [0, 20],
        'stop_percent': [50, 80]
    })
    
    result = scheduler.validate_data(data)
    assert result is True
    assert all(data['stop_percent'] <= 100)


@pytest.mark.invariant
def test_start_before_stop():
    """Start time must always be before stop time for each group"""
    scheduler = GroupScheduler()
    data = pd.DataFrame({
        'group_id': [1, 2, 3],
        'group_size': [10, 15, 5],
        'start_percent': [0, 20, 60],
        'stop_percent': [50, 80, 95]
    })
    
    result = scheduler.validate_data(data)
    assert result is True
    assert all(data['start_percent'] < data['stop_percent'])


@pytest.mark.invariant
def test_group_size_positive():
    """Group size must be positive integer"""
    scheduler = GroupScheduler()
    data = pd.DataFrame({
        'group_id': [1, 2],
        'group_size': [10, 15],
        'start_percent': [0, 20],
        'stop_percent': [50, 80]
    })
    
    result = scheduler.validate_data(data)
    assert result is True
    assert all(data['group_size'] > 0)


# ============================================================================
# GOLDEN TESTS - Known input/output scenarios
# ============================================================================

@pytest.mark.golden
@pytest.mark.deterministic
def test_load_valid_csv(tmp_path):
    """Test loading a valid CSV file.
    
    Scenario: Valid CSV with 3 groups
    Expected: Data loaded correctly with all fields
    """
    # Create test CSV
    csv_path = tmp_path / "test_groups.csv"
    test_data = """group_id,group_size,start_percent,stop_percent
1,10,0,30
2,15,25,60
3,8,55,95
"""
    csv_path.write_text(test_data)
    
    scheduler = GroupScheduler()
    data = scheduler.load_csv(str(csv_path))
    
    assert len(data) == 3
    assert list(data['group_id']) == [1, 2, 3]
    assert list(data['group_size']) == [10, 15, 8]
    assert list(data['start_percent']) == [0, 25, 55]
    assert list(data['stop_percent']) == [30, 60, 95]


@pytest.mark.golden
def test_validate_golden_case():
    """Test validation with valid data.
    
    Scenario: All constraints satisfied
    Expected: Validation passes
    """
    scheduler = GroupScheduler()
    data = pd.DataFrame({
        'group_id': [1, 2, 3],
        'group_size': [10, 15, 5],
        'start_percent': [0, 20, 60],
        'stop_percent': [50, 80, 95]
    })
    
    result = scheduler.validate_data(data)
    assert result is True


# ============================================================================
# VALIDATION ERROR TESTS - Invalid data scenarios
# ============================================================================

@pytest.mark.unit
def test_reject_too_many_groups():
    """Should reject more than 5 groups"""
    scheduler = GroupScheduler()
    data = pd.DataFrame({
        'group_id': [1, 2, 3, 4, 5, 6],
        'group_size': [10, 10, 10, 10, 10, 10],
        'start_percent': [0, 15, 30, 45, 60, 75],
        'stop_percent': [10, 25, 40, 55, 70, 90]
    })
    
    with pytest.raises(ValidationError, match="Maximum 5 groups allowed"):
        scheduler.validate_data(data)


@pytest.mark.unit
def test_reject_negative_start_time():
    """Should reject negative start times"""
    scheduler = GroupScheduler()
    data = pd.DataFrame({
        'group_id': [1, 2],
        'group_size': [10, 15],
        'start_percent': [-5, 20],
        'stop_percent': [50, 80]
    })
    
    with pytest.raises(ValidationError, match="Start times must be >= 0"):
        scheduler.validate_data(data)


@pytest.mark.unit
def test_reject_stop_time_over_100():
    """Should reject stop times > 100"""
    scheduler = GroupScheduler()
    data = pd.DataFrame({
        'group_id': [1, 2],
        'group_size': [10, 15],
        'start_percent': [0, 20],
        'stop_percent': [50, 105]
    })
    
    with pytest.raises(ValidationError, match="Stop times must be <= 100"):
        scheduler.validate_data(data)


@pytest.mark.unit
def test_reject_start_after_stop():
    """Should reject when start time >= stop time"""
    scheduler = GroupScheduler()
    data = pd.DataFrame({
        'group_id': [1, 2],
        'group_size': [10, 15],
        'start_percent': [60, 20],
        'stop_percent': [50, 80]
    })
    
    with pytest.raises(ValidationError, match="Start time must be before stop time"):
        scheduler.validate_data(data)


@pytest.mark.unit
def test_reject_zero_group_size():
    """Should reject zero or negative group size"""
    scheduler = GroupScheduler()
    data = pd.DataFrame({
        'group_id': [1, 2],
        'group_size': [10, 0],
        'start_percent': [0, 20],
        'stop_percent': [50, 80]
    })
    
    with pytest.raises(ValidationError, match="Group size must be positive"):
        scheduler.validate_data(data)


# ============================================================================
# EDGE CASES
# ============================================================================

@pytest.mark.unit
def test_exactly_five_groups():
    """Should accept exactly 5 groups (boundary case)"""
    scheduler = GroupScheduler()
    data = pd.DataFrame({
        'group_id': [1, 2, 3, 4, 5],
        'group_size': [10, 10, 10, 10, 10],
        'start_percent': [0, 20, 40, 60, 80],
        'stop_percent': [15, 35, 55, 75, 100]
    })
    
    result = scheduler.validate_data(data)
    assert result is True


@pytest.mark.unit
def test_earliest_start_is_zero():
    """Should accept start time of 0 (boundary case)"""
    scheduler = GroupScheduler()
    data = pd.DataFrame({
        'group_id': [1],
        'group_size': [10],
        'start_percent': [0],
        'stop_percent': [50]
    })
    
    result = scheduler.validate_data(data)
    assert result is True


@pytest.mark.unit
def test_latest_stop_is_100():
    """Should accept stop time of 100 (boundary case)"""
    scheduler = GroupScheduler()
    data = pd.DataFrame({
        'group_id': [1],
        'group_size': [10],
        'start_percent': [50],
        'stop_percent': [100]
    })
    
    result = scheduler.validate_data(data)
    assert result is True


@pytest.mark.unit
def test_single_group():
    """Should handle single group correctly"""
    scheduler = GroupScheduler()
    data = pd.DataFrame({
        'group_id': [1],
        'group_size': [25],
        'start_percent': [0],
        'stop_percent': [100]
    })
    
    result = scheduler.validate_data(data)
    assert result is True


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
def test_load_and_validate_workflow(tmp_path):
    """Test complete workflow: load CSV and validate.
    
    Scenario: End-to-end workflow with valid data
    Expected: Data loads and validates successfully
    """
    # Create test CSV
    csv_path = tmp_path / "integration_test.csv"
    test_data = """group_id,group_size,start_percent,stop_percent
1,20,0,25
2,15,20,50
3,10,45,75
4,12,70,95
"""
    csv_path.write_text(test_data)
    
    scheduler = GroupScheduler()
    data = scheduler.load_csv(str(csv_path))
    result = scheduler.validate_data(data)
    
    assert result is True
    assert len(data) == 4
    assert scheduler.get_total_participants(data) == 57


@pytest.mark.integration
def test_get_summary_statistics(tmp_path):
    """Test getting summary statistics from data"""
    csv_path = tmp_path / "summary_test.csv"
    test_data = """group_id,group_size,start_percent,stop_percent
1,10,0,30
2,15,25,60
3,8,55,95
"""
    csv_path.write_text(test_data)
    
    scheduler = GroupScheduler()
    data = scheduler.load_csv(str(csv_path))
    summary = scheduler.get_summary(data)
    
    assert summary['num_groups'] == 3
    assert summary['total_participants'] == 33
    assert summary['earliest_start'] == 0
    assert summary['latest_stop'] == 95

