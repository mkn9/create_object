"""
Test suite for spatial group object tracking and simulation.

Tests cover:
- Input validation for spatial parameters
- Object generation within groups
- Position tracking over time
- Movement simulation with statistical constraints
- Output format validation
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path


@pytest.fixture
def sample_spatial_groups_df():
    """Sample spatial group parameters for testing."""
    return pd.DataFrame({
        'group_id': [1, 2, 3],
        'group_size': [5, 3, 4],
        'start_percent': [0, 30, 60],
        'stop_percent': [40, 70, 100],
        'center_north': [100.0, 200.0, 150.0],
        'center_east': [50.0, -30.0, 80.0],
        'center_down': [0.0, -5.0, -2.0],
        'spread_std': [10.0, 15.0, 8.0],
        'mean_travel_distance': [50.0, 30.0, 40.0],
        'travel_std': [5.0, 3.0, 4.0],
        'category': [1, 2, 3]
    })


class TestSpatialGroupInputValidation:
    """Test validation of spatial group input parameters."""
    
    def test_valid_spatial_groups_accepted(self, sample_spatial_groups_df):
        """Valid spatial group data should be accepted."""
        from src.spatial_groups import SpatialGroupSimulator
        
        simulator = SpatialGroupSimulator(sample_spatial_groups_df, num_time_points=10)
        assert simulator is not None
        assert len(simulator.groups_df) == 3
    
    def test_reject_invalid_category_values(self, sample_spatial_groups_df):
        """Categories must be 1, 2, or 3."""
        from src.spatial_groups import SpatialGroupSimulator
        
        invalid_df = sample_spatial_groups_df.copy()
        invalid_df.loc[0, 'category'] = 5
        
        with pytest.raises(ValueError, match="Category must be 1, 2, or 3"):
            SpatialGroupSimulator(invalid_df, num_time_points=10)
    
    def test_reject_negative_spread_std(self, sample_spatial_groups_df):
        """Standard deviation for spread must be positive."""
        from src.spatial_groups import SpatialGroupSimulator
        
        invalid_df = sample_spatial_groups_df.copy()
        invalid_df.loc[0, 'spread_std'] = -5.0
        
        with pytest.raises(ValueError, match="spread_std must be positive"):
            SpatialGroupSimulator(invalid_df, num_time_points=10)
    
    def test_reject_negative_travel_distance(self, sample_spatial_groups_df):
        """Mean travel distance must be non-negative."""
        from src.spatial_groups import SpatialGroupSimulator
        
        invalid_df = sample_spatial_groups_df.copy()
        invalid_df.loc[0, 'mean_travel_distance'] = -10.0
        
        with pytest.raises(ValueError, match="mean_travel_distance must be non-negative"):
            SpatialGroupSimulator(invalid_df, num_time_points=10)


class TestObjectGeneration:
    """Test object generation within groups."""
    
    def test_correct_number_of_objects_generated(self, sample_spatial_groups_df):
        """Should generate correct number of objects per group."""
        from src.spatial_groups import SpatialGroupSimulator
        
        simulator = SpatialGroupSimulator(sample_spatial_groups_df, num_time_points=10, random_seed=42)
        objects_df = simulator.generate_objects()
        
        # Total objects should equal sum of group_size
        expected_total = sample_spatial_groups_df['group_size'].sum()
        assert len(objects_df) == expected_total
        
        # Check objects per group
        for _, group in sample_spatial_groups_df.iterrows():
            group_objects = objects_df[objects_df['group_id'] == group['group_id']]
            assert len(group_objects) == group['group_size']
    
    def test_objects_have_required_columns(self, sample_spatial_groups_df):
        """Generated objects should have all required columns."""
        from src.spatial_groups import SpatialGroupSimulator
        
        simulator = SpatialGroupSimulator(sample_spatial_groups_df, num_time_points=10, random_seed=42)
        objects_df = simulator.generate_objects()
        
        required_columns = [
            'object_id', 'group_id', 'category',
            'start_north', 'start_east', 'start_down',
            'end_north', 'end_east', 'end_down',
            'travel_distance'
        ]
        
        for col in required_columns:
            assert col in objects_df.columns
    
    def test_category_matches_group(self, sample_spatial_groups_df):
        """Objects should inherit category from their group."""
        from src.spatial_groups import SpatialGroupSimulator
        
        simulator = SpatialGroupSimulator(sample_spatial_groups_df, num_time_points=10, random_seed=42)
        objects_df = simulator.generate_objects()
        
        for _, group in sample_spatial_groups_df.iterrows():
            group_objects = objects_df[objects_df['group_id'] == group['group_id']]
            assert (group_objects['category'] == group['category']).all()
    
    def test_starting_positions_near_center(self, sample_spatial_groups_df):
        """Starting positions should be near group center (within 3 std devs)."""
        from src.spatial_groups import SpatialGroupSimulator
        
        simulator = SpatialGroupSimulator(sample_spatial_groups_df, num_time_points=10, random_seed=42)
        objects_df = simulator.generate_objects()
        
        for _, group in sample_spatial_groups_df.iterrows():
            group_objects = objects_df[objects_df['group_id'] == group['group_id']]
            
            # Calculate distances from center
            distances = np.sqrt(
                (group_objects['start_north'] - group['center_north'])**2 +
                (group_objects['start_east'] - group['center_east'])**2 +
                (group_objects['start_down'] - group['center_down'])**2
            )
            
            # All should be within 3 standard deviations
            assert (distances <= 3 * group['spread_std']).all()


class TestTrajectoryGeneration:
    """Test object trajectory generation over time."""
    
    def test_trajectory_has_correct_time_points(self, sample_spatial_groups_df):
        """Trajectory should have time points covering the simulation range."""
        from src.spatial_groups import SpatialGroupSimulator
        
        num_time_points = 20
        simulator = SpatialGroupSimulator(sample_spatial_groups_df, num_time_points=num_time_points, random_seed=42)
        simulator.generate_objects()
        trajectory_df = simulator.generate_trajectories()
        
        # Should have entries for each active object at each time
        time_values = trajectory_df['time_percent'].unique()
        # Should have at least the base time points (may have more due to exact start/stop times)
        assert len(time_values) >= num_time_points
        # Time values should span from 0 to 100
        assert time_values.min() >= 0
        assert time_values.max() <= 100
    
    def test_objects_only_present_during_group_active_time(self, sample_spatial_groups_df):
        """Objects should only appear when their group is active."""
        from src.spatial_groups import SpatialGroupSimulator
        
        simulator = SpatialGroupSimulator(sample_spatial_groups_df, num_time_points=100, random_seed=42)
        objects_df = simulator.generate_objects()
        trajectory_df = simulator.generate_trajectories()
        
        for _, obj in objects_df.iterrows():
            obj_trajectory = trajectory_df[trajectory_df['object_id'] == obj['object_id']]
            group = sample_spatial_groups_df[sample_spatial_groups_df['group_id'] == obj['group_id']].iloc[0]
            
            # All time points should be within group's active period
            assert obj_trajectory['time_percent'].min() >= group['start_percent']
            assert obj_trajectory['time_percent'].max() <= group['stop_percent']
    
    def test_trajectory_starts_at_start_position(self, sample_spatial_groups_df):
        """First position in trajectory should match start position."""
        from src.spatial_groups import SpatialGroupSimulator
        
        simulator = SpatialGroupSimulator(sample_spatial_groups_df, num_time_points=20, random_seed=42)
        objects_df = simulator.generate_objects()
        trajectory_df = simulator.generate_trajectories()
        
        for _, obj in objects_df.iterrows():
            obj_trajectory = trajectory_df[trajectory_df['object_id'] == obj['object_id']].sort_values('time_percent')
            first_pos = obj_trajectory.iloc[0]
            
            assert np.isclose(first_pos['north'], obj['start_north'], atol=0.01)
            assert np.isclose(first_pos['east'], obj['start_east'], atol=0.01)
            assert np.isclose(first_pos['down'], obj['start_down'], atol=0.01)
    
    def test_trajectory_ends_at_end_position(self, sample_spatial_groups_df):
        """Last position in trajectory should match end position."""
        from src.spatial_groups import SpatialGroupSimulator
        
        simulator = SpatialGroupSimulator(sample_spatial_groups_df, num_time_points=20, random_seed=42)
        objects_df = simulator.generate_objects()
        trajectory_df = simulator.generate_trajectories()
        
        for _, obj in objects_df.iterrows():
            obj_trajectory = trajectory_df[trajectory_df['object_id'] == obj['object_id']].sort_values('time_percent')
            last_pos = obj_trajectory.iloc[-1]
            
            assert np.isclose(last_pos['north'], obj['end_north'], atol=0.01)
            assert np.isclose(last_pos['east'], obj['end_east'], atol=0.01)
            assert np.isclose(last_pos['down'], obj['end_down'], atol=0.01)


class TestStatisticalProperties:
    """Test statistical properties of generated data."""
    
    def test_travel_distances_approximate_mean(self, sample_spatial_groups_df):
        """Travel distances should approximate specified mean (within 3 std devs)."""
        from src.spatial_groups import SpatialGroupSimulator
        
        simulator = SpatialGroupSimulator(sample_spatial_groups_df, num_time_points=20, random_seed=42)
        objects_df = simulator.generate_objects()
        
        for _, group in sample_spatial_groups_df.iterrows():
            group_objects = objects_df[objects_df['group_id'] == group['group_id']]
            
            # Travel distances should be near the mean
            mean_dist = group['mean_travel_distance']
            std_dist = group['travel_std']
            
            # Check all within reasonable bounds (mean ± 3*std)
            assert (group_objects['travel_distance'] >= mean_dist - 3*std_dist).all()
            assert (group_objects['travel_distance'] <= mean_dist + 3*std_dist).all()


class TestOutputFormat:
    """Test output format and structure."""
    
    def test_can_save_objects_to_csv(self, sample_spatial_groups_df, tmp_path):
        """Should be able to save objects DataFrame to CSV."""
        from src.spatial_groups import SpatialGroupSimulator
        
        simulator = SpatialGroupSimulator(sample_spatial_groups_df, num_time_points=10, random_seed=42)
        objects_df = simulator.generate_objects()
        
        output_file = tmp_path / "test_objects.csv"
        objects_df.to_csv(output_file, index=False)
        
        # Verify file exists and can be read
        assert output_file.exists()
        loaded_df = pd.read_csv(output_file)
        assert len(loaded_df) == len(objects_df)
    
    def test_can_save_trajectories_to_csv(self, sample_spatial_groups_df, tmp_path):
        """Should be able to save trajectories DataFrame to CSV."""
        from src.spatial_groups import SpatialGroupSimulator
        
        simulator = SpatialGroupSimulator(sample_spatial_groups_df, num_time_points=10, random_seed=42)
        simulator.generate_objects()
        trajectory_df = simulator.generate_trajectories()
        
        output_file = tmp_path / "test_trajectories.csv"
        trajectory_df.to_csv(output_file, index=False)
        
        # Verify file exists and can be read
        assert output_file.exists()
        loaded_df = pd.read_csv(output_file)
        assert len(loaded_df) == len(trajectory_df)


class TestDeterminism:
    """Test deterministic behavior with random seeds."""
    
    def test_same_seed_produces_identical_results(self, sample_spatial_groups_df):
        """Same random seed should produce identical results."""
        from src.spatial_groups import SpatialGroupSimulator
        
        sim1 = SpatialGroupSimulator(sample_spatial_groups_df, num_time_points=10, random_seed=42)
        objects1 = sim1.generate_objects()
        traj1 = sim1.generate_trajectories()
        
        sim2 = SpatialGroupSimulator(sample_spatial_groups_df, num_time_points=10, random_seed=42)
        objects2 = sim2.generate_objects()
        traj2 = sim2.generate_trajectories()
        
        # Objects should be identical
        pd.testing.assert_frame_equal(objects1, objects2)
        
        # Trajectories should be identical
        pd.testing.assert_frame_equal(traj1, traj2)
    
    def test_different_seeds_produce_different_results(self, sample_spatial_groups_df):
        """Different random seeds should produce different results."""
        from src.spatial_groups import SpatialGroupSimulator
        
        sim1 = SpatialGroupSimulator(sample_spatial_groups_df, num_time_points=10, random_seed=42)
        objects1 = sim1.generate_objects()
        
        sim2 = SpatialGroupSimulator(sample_spatial_groups_df, num_time_points=10, random_seed=99)
        objects2 = sim2.generate_objects()
        
        # Starting positions should be different
        assert not np.allclose(objects1['start_north'].values, objects2['start_north'].values)

