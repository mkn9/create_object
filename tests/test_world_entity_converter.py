"""
Test suite for World Entity Converter.

Converts trajectory CSV files to WORLD_ENTITY format for simulation.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import shutil


@pytest.fixture
def sample_trajectories_df():
    """Sample trajectory data for testing."""
    return pd.DataFrame({
        'object_id': [1, 1, 1, 2, 2, 2, 3, 3, 3],
        'group_id': [1, 1, 1, 1, 1, 1, 2, 2, 2],
        'category': [1, 1, 1, 1, 1, 1, 2, 2, 2],
        'time_percent': [0.0, 10.0, 20.0, 0.0, 10.0, 20.0, 30.0, 40.0, 50.0],
        'north': [100.0, 105.0, 110.0, 150.0, 155.0, 160.0, 200.0, 210.0, 220.0],
        'east': [50.0, 52.0, 54.0, 60.0, 62.0, 64.0, 70.0, 72.0, 74.0],
        'down': [0.0, -1.0, -2.0, 5.0, 6.0, 7.0, -10.0, -11.0, -12.0]
    })


@pytest.fixture
def sample_csv_file(tmp_path, sample_trajectories_df):
    """Create a sample CSV file."""
    csv_file = tmp_path / "test_trajectories.csv"
    sample_trajectories_df.to_csv(csv_file, index=False)
    return csv_file


@pytest.fixture
def cleanup_trajectories():
    """Cleanup trajectories directory after tests."""
    yield
    # Cleanup
    traj_dir = Path('./trajectories')
    if traj_dir.exists():
        shutil.rmtree(traj_dir)


class TestWorldEntityConverter:
    """Test World Entity Converter."""
    
    def test_create_unique_keys(self, sample_trajectories_df):
        """Should create unique keys starting at 1."""
        from src.world_entity_converter import WorldEntityConverter
        
        converter = WorldEntityConverter()
        keys_df = converter.create_unique_keys(sample_trajectories_df)
        
        # Should have 3 unique object/group combinations
        unique_combos = keys_df[['object_id', 'group_id', 'unique_key']].drop_duplicates()
        assert len(unique_combos) == 3
        
        # Keys should be 1, 2, 3
        assert set(unique_combos['unique_key']) == {1, 2, 3}
    
    def test_unique_keys_increment_by_one(self, sample_trajectories_df):
        """Keys should increment by 1."""
        from src.world_entity_converter import WorldEntityConverter
        
        converter = WorldEntityConverter()
        keys_df = converter.create_unique_keys(sample_trajectories_df)
        
        unique_keys = sorted(keys_df['unique_key'].unique())
        for i, key in enumerate(unique_keys, start=1):
            assert key == i
    
    def test_unique_keys_consistent_for_same_object_group(self, sample_trajectories_df):
        """Same object_id/group_id should get same unique_key."""
        from src.world_entity_converter import WorldEntityConverter
        
        converter = WorldEntityConverter()
        keys_df = converter.create_unique_keys(sample_trajectories_df)
        
        # All rows with object_id=1, group_id=1 should have same key
        obj1_keys = keys_df[(keys_df['object_id'] == 1) & (keys_df['group_id'] == 1)]['unique_key']
        assert len(obj1_keys.unique()) == 1
    
    def test_create_trajectory_output_format(self, sample_trajectories_df):
        """Should create properly formatted trajectory DataFrame."""
        from src.world_entity_converter import WorldEntityConverter
        
        converter = WorldEntityConverter()
        keys_df = converter.create_unique_keys(sample_trajectories_df)
        
        # Get data for first key
        key_data = keys_df[keys_df['unique_key'] == 1]
        trajectory_df = converter.format_trajectory_data(key_data)
        
        # Check columns
        assert list(trajectory_df.columns) == ['FIELDS', 'FRAME', 'TIME', 'POS_N', 'POS_E', 'POS_D']
        
        # Check FIELDS is empty string
        assert (trajectory_df['FIELDS'] == '').all()
        
        # Check FRAME is 0.0
        assert (trajectory_df['FRAME'] == 0.0).all()
        
        # Check TIME matches time_percent
        assert trajectory_df['TIME'].tolist() == key_data['time_percent'].tolist()
    
    def test_save_trajectory_file(self, sample_csv_file, tmp_path, cleanup_trajectories):
        """Should save trajectory files in correct format."""
        from src.world_entity_converter import WorldEntityConverter
        
        # Use tmp_path for output
        output_base = tmp_path / 'trajectories'
        
        converter = WorldEntityConverter(output_dir=output_base)
        result = converter.convert_csv_to_world_entities(sample_csv_file)
        
        # Check that files were created
        g_dir = output_base / 'G'
        assert g_dir.exists()
        
        # Should have 3 trajectory files
        traj_files = list(g_dir.glob('G_*_.txt'))
        assert len(traj_files) == 3
    
    def test_trajectory_file_tab_delimited(self, sample_csv_file, tmp_path, cleanup_trajectories):
        """Trajectory files should be tab-delimited."""
        from src.world_entity_converter import WorldEntityConverter
        
        output_base = tmp_path / 'trajectories'
        converter = WorldEntityConverter(output_dir=output_base)
        converter.convert_csv_to_world_entities(sample_csv_file)
        
        # Read one file and check format
        g_dir = output_base / 'G'
        traj_file = list(g_dir.glob('G_*_.txt'))[0]
        
        with open(traj_file, 'r') as f:
            first_line = f.readline()
            # Should have tabs
            assert '\t' in first_line
            # Should have 6 columns (FIELDS, FRAME, TIME, POS_N, POS_E, POS_D)
            assert len(first_line.strip().split('\t')) == 6
    
    def test_create_world_entity_string(self, sample_trajectories_df):
        """Should create properly formatted WORLD_ENTITY string."""
        from src.world_entity_converter import WorldEntityConverter
        
        converter = WorldEntityConverter()
        keys_df = converter.create_unique_keys(sample_trajectories_df)
        key_data = keys_df[keys_df['unique_key'] == 1]
        
        entity_string = converter.create_world_entity_string(1, key_data)
        
        # Check format
        assert 'WORLD_ENTITY {' in entity_string
        assert 'name = G_1' in entity_string
        assert 'position = ' in entity_string
        assert 'scale =' in entity_string
        assert 'stateAttsLoadFilename = ' in entity_string
        assert './trajectories/G/G_1_.txt' in entity_string
        assert '}' in entity_string
    
    def test_world_entity_position_format(self, sample_trajectories_df):
        """Position should be formatted as 'N, E, D'."""
        from src.world_entity_converter import WorldEntityConverter
        
        converter = WorldEntityConverter()
        keys_df = converter.create_unique_keys(sample_trajectories_df)
        key_data = keys_df[keys_df['unique_key'] == 1]
        
        entity_string = converter.create_world_entity_string(1, key_data)
        
        # Extract position line
        lines = entity_string.split('\n')
        position_line = [l for l in lines if 'position = ' in l][0]
        
        # Should have format: position = "100.0, 50.0, 0.0"
        assert '"' in position_line
        assert ', ' in position_line
    
    def test_consolidated_world_entities_file(self, sample_csv_file, tmp_path, cleanup_trajectories):
        """Should create consolidated file with all WORLD_ENTITY strings."""
        from src.world_entity_converter import WorldEntityConverter
        
        output_base = tmp_path / 'trajectories'
        converter = WorldEntityConverter(output_dir=output_base)
        result = converter.convert_csv_to_world_entities(sample_csv_file)
        
        # Check consolidated file exists
        consolidated_file = output_base / 'all_G_WORLD_ENTITIES.txt'
        assert consolidated_file.exists()
        
        # Read and check contents
        with open(consolidated_file, 'r') as f:
            content = f.read()
        
        # Should have 3 WORLD_ENTITY blocks
        assert content.count('WORLD_ENTITY {') == 3
        assert content.count('name = G_1') == 1
        assert content.count('name = G_2') == 1
        assert content.count('name = G_3') == 1
    
    def test_return_entity_mapping(self, sample_csv_file, tmp_path, cleanup_trajectories):
        """Should return mapping of keys to entity strings."""
        from src.world_entity_converter import WorldEntityConverter
        
        output_base = tmp_path / 'trajectories'
        converter = WorldEntityConverter(output_dir=output_base)
        result = converter.convert_csv_to_world_entities(sample_csv_file)
        
        # Should have 3 entities
        assert len(result['entity_strings']) == 3
        assert 1 in result['entity_strings']
        assert 2 in result['entity_strings']
        assert 3 in result['entity_strings']
    
    def test_fields_column_empty_not_nan(self, sample_csv_file, tmp_path, cleanup_trajectories):
        """FIELDS column should be empty string, not NaN."""
        from src.world_entity_converter import WorldEntityConverter
        
        output_base = tmp_path / 'trajectories'
        converter = WorldEntityConverter(output_dir=output_base)
        converter.convert_csv_to_world_entities(sample_csv_file)
        
        # Read trajectory file
        g_dir = output_base / 'G'
        traj_file = list(g_dir.glob('G_*_.txt'))[0]
        
        df = pd.read_csv(traj_file, sep='\t', keep_default_na=False)
        
        # FIELDS should not have NaN (with keep_default_na=False)
        assert not df['FIELDS'].isna().any()
        # FIELDS should be empty strings
        assert (df['FIELDS'] == '').all()

