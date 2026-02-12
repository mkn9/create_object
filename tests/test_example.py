"""
Example test file demonstrating TDD best practices.

This file shows:
- Deterministic tests with fixed random seeds
- Invariant tests (properties that must always hold)
- Golden tests (canonical scenarios with known outputs)
- Proper test organization and documentation
"""

import pytest
import numpy as np


# Example function to test
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
    """
    return a + b


# ============================================================================
# INVARIANT TESTS - Properties that must always hold
# ============================================================================

@pytest.mark.invariant
def test_add_numbers_commutative():
    """Addition must be commutative: a + b = b + a"""
    a, b = 5.0, 3.0
    assert add_numbers(a, b) == add_numbers(b, a)


@pytest.mark.invariant
def test_add_numbers_finite():
    """Result must always be finite (no NaN or Inf)"""
    result = add_numbers(1.0, 2.0)
    assert np.isfinite(result), "Result must be finite"


# ============================================================================
# GOLDEN TESTS - Canonical scenarios with known outputs
# ============================================================================

@pytest.mark.golden
@pytest.mark.deterministic
def test_add_numbers_golden_case():
    """Test addition with canonical scenario.
    
    Scenario: Standard positive numbers
    Expected: Correct sum
    Tolerance: Exact equality for integers
    """
    result = add_numbers(5.0, 3.0)
    expected = 8.0
    assert result == expected


@pytest.mark.golden
@pytest.mark.deterministic
def test_add_numbers_negative():
    """Test addition with negative numbers.
    
    Scenario: Negative numbers
    Expected: Correct sum
    """
    result = add_numbers(-5.0, 3.0)
    expected = -2.0
    np.testing.assert_allclose(result, expected, rtol=1e-10)


# ============================================================================
# EDGE CASES
# ============================================================================

@pytest.mark.unit
def test_add_numbers_zero():
    """Adding zero should not change the value"""
    assert add_numbers(5.0, 0.0) == 5.0


@pytest.mark.unit
def test_add_numbers_negative_zero():
    """Test with negative zero"""
    result = add_numbers(5.0, -0.0)
    assert result == 5.0


# ============================================================================
# DETERMINISTIC TESTS - With fixed random seeds
# ============================================================================

@pytest.mark.deterministic
def test_random_addition_deterministic():
    """Test that random operations are deterministic with fixed seed.
    
    Scenario: Generate random numbers with fixed seed
    Expected: Reproducible results
    Seed: 42
    """
    rng = np.random.default_rng(42)
    a = rng.standard_normal()
    b = rng.standard_normal()
    
    result = add_numbers(a, b)
    
    # With seed 42, first two values should be:
    expected_a = 0.30471707975443135
    expected_b = -1.0347835398876736
    expected_sum = expected_a + expected_b
    
    np.testing.assert_allclose(result, expected_sum, rtol=1e-10)


# ============================================================================
# FIXTURES (if needed)
# ============================================================================

@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {
        'a': 5.0,
        'b': 3.0,
        'expected_sum': 8.0
    }


@pytest.mark.unit
def test_with_fixture(sample_data):
    """Test using fixture data"""
    result = add_numbers(sample_data['a'], sample_data['b'])
    assert result == sample_data['expected_sum']

