"""
World Entity Converter

Converts trajectory CSV files to WORLD_ENTITY format for simulation environments.
Creates unique keys for each object/group combination and generates:
- Individual trajectory files (tab-delimited)
- WORLD_ENTITY configuration strings
- Consolidated entity file
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
from datetime import datetime


class WorldEntityConverter:
    """
    Converts trajectory CSV files to WORLD_ENTITY format.
    
    For each unique object_id/group_id combination:
    - Assigns a unique integer key (starting at 1)
    - Creates a tab-delimited trajectory file
    - Generates a WORLD_ENTITY configuration string
    
    Output format matches simulation environment requirements with:
    - FIELDS, FRAME, TIME, POS_N, POS_E, POS_D columns
    - Files saved in ./trajectories/G/ directory
    - Consolidated entity definitions file
    """
    
    def __init__(self, output_dir: Path = Path('./trajectories')):
        """
        Initialize converter.
        
        Args:
            output_dir: Base directory for trajectory outputs (default: ./trajectories)
        """
        self.output_dir = Path(output_dir)
        self.key_counter = 1
        self.key_mapping = {}  # Maps (object_id, group_id) to unique_key
    
    def create_unique_keys(self, trajectories_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create unique keys for each object_id/group_id combination.
        
        Args:
            trajectories_df: DataFrame with trajectory data
            
        Returns:
            DataFrame with added 'unique_key' column
        """
        df = trajectories_df.copy()
        
        # Get unique object/group combinations
        unique_combos = df[['object_id', 'group_id']].drop_duplicates()
        
        # Assign keys starting at 1
        for idx, row in unique_combos.iterrows():
            obj_id = row['object_id']
            grp_id = row['group_id']
            
            if (obj_id, grp_id) not in self.key_mapping:
                self.key_mapping[(obj_id, grp_id)] = self.key_counter
                self.key_counter += 1
        
        # Add unique_key column to dataframe
        df['unique_key'] = df.apply(
            lambda r: self.key_mapping[(r['object_id'], r['group_id'])],
            axis=1
        )
        
        return df
    
    def format_trajectory_data(self, key_data: pd.DataFrame) -> pd.DataFrame:
        """
        Format trajectory data for a single unique key.
        
        Creates output format:
        - FIELDS: empty string (not NaN)
        - FRAME: 0.0
        - TIME: from time_percent
        - POS_N: from north
        - POS_E: from east
        - POS_D: from down
        
        Args:
            key_data: DataFrame rows for a single unique key
            
        Returns:
            Formatted DataFrame with required columns
        """
        formatted = pd.DataFrame({
            'FIELDS': [''] * len(key_data),  # Empty string, not NaN
            'FRAME': [0.0] * len(key_data),
            'TIME': key_data['time_percent'].values,
            'POS_N': key_data['north'].values,
            'POS_E': key_data['east'].values,
            'POS_D': key_data['down'].values
        })
        
        return formatted
    
    def save_trajectory_file(self, key: int, trajectory_df: pd.DataFrame) -> Path:
        """
        Save trajectory data to tab-delimited file.
        
        Args:
            key: Unique key for this trajectory
            trajectory_df: Formatted trajectory data
            
        Returns:
            Path to saved file
        """
        # Create G directory if needed
        g_dir = self.output_dir / 'G'
        g_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename: G_<key>_.txt
        filename = f"G_{key}_.txt"
        filepath = g_dir / filename
        
        # Save as tab-delimited (ensure empty strings stay empty, not NaN)
        trajectory_df.to_csv(filepath, sep='\t', index=False, na_rep='')
        
        return filepath
    
    def create_world_entity_string(self, key: int, key_data: pd.DataFrame) -> str:
        """
        Create WORLD_ENTITY configuration string for a single key.
        
        Format:
        WORLD_ENTITY {
            name = G_<key>
            position = "<first_north>, <first_east>, <first_down>"
            scale =
            stateAttsLoadFilename = './trajectories/G/G_<key>_.txt'
        }
        
        Args:
            key: Unique key
            key_data: DataFrame rows for this key
            
        Returns:
            Formatted WORLD_ENTITY string
        """
        # Get first position
        first_row = key_data.iloc[0]
        pos_n = first_row['north']
        pos_e = first_row['east']
        pos_d = first_row['down']
        
        # Format position string
        position_str = f'"{pos_n}, {pos_e}, {pos_d}"'
        
        # Create entity string
        entity_string = f"""WORLD_ENTITY {{
    name = G_{key}
    position = {position_str}
    scale =
    stateAttsLoadFilename = './trajectories/G/G_{key}_.txt'
}}"""
        
        return entity_string
    
    def convert_csv_to_world_entities(self, csv_path: Path) -> Dict:
        """
        Convert trajectory CSV to WORLD_ENTITY format.
        
        Main conversion function that:
        1. Reads trajectory CSV
        2. Creates unique keys
        3. Saves individual trajectory files
        4. Creates WORLD_ENTITY strings
        5. Saves consolidated entity file
        
        Args:
            csv_path: Path to trajectory CSV file
            
        Returns:
            Dictionary with:
                - entity_strings: Dict mapping key to WORLD_ENTITY string
                - trajectory_files: Dict mapping key to trajectory file path
                - consolidated_file: Path to consolidated entities file
        """
        # Read CSV
        trajectories_df = pd.read_csv(csv_path)
        
        # Create unique keys
        trajectories_with_keys = self.create_unique_keys(trajectories_df)
        
        # Process each unique key
        entity_strings = {}
        trajectory_files = {}
        
        for key in sorted(trajectories_with_keys['unique_key'].unique()):
            # Get data for this key
            key_data = trajectories_with_keys[trajectories_with_keys['unique_key'] == key]
            
            # Format trajectory data
            formatted_trajectory = self.format_trajectory_data(key_data)
            
            # Save trajectory file
            traj_file = self.save_trajectory_file(key, formatted_trajectory)
            trajectory_files[key] = traj_file
            
            # Create WORLD_ENTITY string
            entity_string = self.create_world_entity_string(key, key_data)
            entity_strings[key] = entity_string
        
        # Create consolidated file with all entities
        consolidated_content = '\n\n'.join([entity_strings[k] for k in sorted(entity_strings.keys())])
        
        consolidated_file = self.output_dir / 'all_G_WORLD_ENTITIES.txt'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(consolidated_file, 'w') as f:
            f.write(consolidated_content)
        
        return {
            'entity_strings': entity_strings,
            'trajectory_files': trajectory_files,
            'consolidated_file': consolidated_file,
            'num_entities': len(entity_strings)
        }
    
    def process_multiple_csvs(self, csv_paths: list) -> Dict:
        """
        Process multiple CSV files, maintaining consistent key numbering.
        
        Args:
            csv_paths: List of paths to trajectory CSV files
            
        Returns:
            Dictionary with combined results from all files
        """
        all_results = {
            'entity_strings': {},
            'trajectory_files': {},
            'files_processed': []
        }
        
        for csv_path in csv_paths:
            result = self.convert_csv_to_world_entities(csv_path)
            
            # Merge results
            all_results['entity_strings'].update(result['entity_strings'])
            all_results['trajectory_files'].update(result['trajectory_files'])
            all_results['files_processed'].append(csv_path)
        
        # Update consolidated file with all entities
        consolidated_content = '\n\n'.join([
            all_results['entity_strings'][k] 
            for k in sorted(all_results['entity_strings'].keys())
        ])
        
        consolidated_file = self.output_dir / 'all_G_WORLD_ENTITIES.txt'
        with open(consolidated_file, 'w') as f:
            f.write(consolidated_content)
        
        all_results['consolidated_file'] = consolidated_file
        all_results['num_entities'] = len(all_results['entity_strings'])
        
        return all_results


def convert_trajectory_csv(csv_path: Path, output_dir: Path = Path('./trajectories')) -> Dict:
    """
    Convenience function to convert a single trajectory CSV file.
    
    Args:
        csv_path: Path to trajectory CSV file
        output_dir: Output directory for trajectory files
        
    Returns:
        Dictionary with conversion results
    """
    converter = WorldEntityConverter(output_dir=output_dir)
    return converter.convert_csv_to_world_entities(csv_path)


def convert_multiple_csvs(csv_paths: list, output_dir: Path = Path('./trajectories')) -> Dict:
    """
    Convenience function to convert multiple trajectory CSV files.
    
    Keys will be unique across all files (continuing numbering).
    
    Args:
        csv_paths: List of paths to trajectory CSV files
        output_dir: Output directory for trajectory files
        
    Returns:
        Dictionary with combined conversion results
    """
    converter = WorldEntityConverter(output_dir=output_dir)
    return converter.process_multiple_csvs(csv_paths)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert trajectory CSV files to WORLD_ENTITY format'
    )
    parser.add_argument(
        'csv_files',
        nargs='+',
        type=Path,
        help='Path(s) to trajectory CSV file(s)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('./trajectories'),
        help='Output directory for trajectory files (default: ./trajectories)'
    )
    
    args = parser.parse_args()
    
    # Convert files
    if len(args.csv_files) == 1:
        result = convert_trajectory_csv(args.csv_files[0], args.output_dir)
    else:
        result = convert_multiple_csvs(args.csv_files, args.output_dir)
    
    # Print summary
    print(f"\n✅ Conversion Complete!")
    print(f"Entities created: {result['num_entities']}")
    print(f"Trajectory files: {len(result['trajectory_files'])}")
    print(f"Consolidated file: {result['consolidated_file']}")
    
    print(f"\nEntity keys: {sorted(result['entity_strings'].keys())}")

