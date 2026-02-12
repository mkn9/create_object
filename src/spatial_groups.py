"""
Spatial Group Simulator - Track objects in 3D space over time.

This module simulates objects moving within groups, tracking their positions
in North-East-Down (NED) coordinates over time. Each group has spatial parameters
including centerpoint, spread, and movement characteristics.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
from datetime import datetime


class SpatialGroupSimulator:
    """
    Simulates spatial objects within groups over time.
    
    Each group has:
    - Geographic centerpoint (NED coordinates)
    - Spread (standard deviation of object positions from center)
    - Movement characteristics (mean and std of travel distance)
    - Category (1, 2, or 3 for object shape)
    - Temporal activity window (start_percent, stop_percent)
    
    Objects within a group:
    - Start near the group centerpoint
    - Move a distance sampled from group's travel distribution
    - Are only active during the group's time window
    - Inherit the group's category
    """
    
    def __init__(self, groups_df: pd.DataFrame, num_time_points: int = 100, random_seed: Optional[int] = None):
        """
        Initialize spatial group simulator.
        
        Args:
            groups_df: DataFrame with group spatial parameters
            num_time_points: Number of time points to simulate (default 100)
            random_seed: Random seed for reproducibility (default None)
        """
        self.groups_df = groups_df.copy()
        self.num_time_points = num_time_points
        self.random_seed = random_seed
        self.objects_df: Optional[pd.DataFrame] = None
        self.trajectory_df: Optional[pd.DataFrame] = None
        
        # Set random seed if provided
        if random_seed is not None:
            np.random.seed(random_seed)
        
        self._validate_groups()
    
    @classmethod
    def from_csv(cls, csv_path: Path, num_time_points: int = 100, random_seed: Optional[int] = None):
        """
        Load spatial groups from CSV file.
        
        Args:
            csv_path: Path to CSV file with group spatial parameters
            num_time_points: Number of time points to simulate
            random_seed: Random seed for reproducibility
            
        Returns:
            SpatialGroupSimulator instance
        """
        groups_df = pd.read_csv(csv_path)
        return cls(groups_df, num_time_points, random_seed)
    
    def _validate_groups(self):
        """Validate group spatial parameters."""
        required_columns = [
            'group_id', 'group_size', 'start_percent', 'stop_percent',
            'center_north', 'center_east', 'center_down',
            'spread_std', 'mean_travel_distance', 'travel_std', 'category'
        ]
        
        # Check required columns exist
        missing_cols = set(required_columns) - set(self.groups_df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Validate category values (must be 1, 2, or 3)
        if not self.groups_df['category'].isin([1, 2, 3]).all():
            raise ValueError("Category must be 1, 2, or 3")
        
        # Validate spread_std (must be positive)
        if (self.groups_df['spread_std'] <= 0).any():
            raise ValueError("spread_std must be positive")
        
        # Validate mean_travel_distance (must be non-negative)
        if (self.groups_df['mean_travel_distance'] < 0).any():
            raise ValueError("mean_travel_distance must be non-negative")
        
        # Validate travel_std (must be positive)
        if (self.groups_df['travel_std'] <= 0).any():
            raise ValueError("travel_std must be positive")
        
        # Validate group_size (must be positive integer)
        if (self.groups_df['group_size'] <= 0).any():
            raise ValueError("group_size must be positive")
        
        # Validate time windows
        if (self.groups_df['start_percent'] < 0).any() or (self.groups_df['start_percent'] > 100).any():
            raise ValueError("start_percent must be between 0 and 100")
        
        if (self.groups_df['stop_percent'] < 0).any() or (self.groups_df['stop_percent'] > 100).any():
            raise ValueError("stop_percent must be between 0 and 100")
        
        if (self.groups_df['stop_percent'] <= self.groups_df['start_percent']).any():
            raise ValueError("stop_percent must be greater than start_percent")
    
    def generate_objects(self) -> pd.DataFrame:
        """
        Generate objects within each group.
        
        For each group, creates the specified number of objects with:
        - Unique object ID
        - Starting position (sampled near group centerpoint)
        - Ending position (after travel distance)
        - Travel distance (sampled from group distribution)
        - Category (inherited from group)
        
        Returns:
            DataFrame with object parameters
        """
        objects_list = []
        object_counter = 1
        
        for _, group in self.groups_df.iterrows():
            group_id = int(group['group_id'])
            group_size = int(group['group_size'])
            
            # Group spatial parameters
            center = np.array([group['center_north'], group['center_east'], group['center_down']])
            spread_std = group['spread_std']
            mean_travel = group['mean_travel_distance']
            travel_std = group['travel_std']
            category = int(group['category'])
            
            for _ in range(group_size):
                # Generate starting position (near group center)
                start_pos = center + np.random.randn(3) * spread_std
                
                # Generate travel distance
                travel_distance = max(0, np.random.randn() * travel_std + mean_travel)
                
                # Generate random direction for movement
                direction = np.random.randn(3)
                direction = direction / np.linalg.norm(direction)  # Normalize
                
                # Calculate ending position
                end_pos = start_pos + direction * travel_distance
                
                objects_list.append({
                    'object_id': object_counter,
                    'group_id': group_id,
                    'category': category,
                    'start_north': start_pos[0],
                    'start_east': start_pos[1],
                    'start_down': start_pos[2],
                    'end_north': end_pos[0],
                    'end_east': end_pos[1],
                    'end_down': end_pos[2],
                    'travel_distance': travel_distance
                })
                
                object_counter += 1
        
        self.objects_df = pd.DataFrame(objects_list)
        return self.objects_df
    
    def generate_trajectories(self) -> pd.DataFrame:
        """
        Generate complete trajectories for all objects over time.
        
        For each object, creates position data at each time point when the
        object's group is active. Positions are linearly interpolated between
        start and end positions.
        
        Returns:
            DataFrame with object positions at each time point
        """
        if self.objects_df is None:
            raise ValueError("Must call generate_objects() first")
        
        # Generate time points (0 to 100 percent)
        time_points = np.linspace(0, 100, self.num_time_points)
        
        trajectory_list = []
        
        for _, obj in self.objects_df.iterrows():
            object_id = obj['object_id']
            group_id = obj['group_id']
            
            # Get group's active time window
            group = self.groups_df[self.groups_df['group_id'] == group_id].iloc[0]
            start_percent = group['start_percent']
            stop_percent = group['stop_percent']
            
            # Filter time points to group's active window
            # Include exact start and stop times if not already in time_points
            active_times = time_points[(time_points >= start_percent) & (time_points <= stop_percent)]
            
            # Ensure we have exact start and stop times
            active_times_list = list(active_times)
            if len(active_times_list) == 0 or active_times_list[0] != start_percent:
                active_times_list.insert(0, start_percent)
            if active_times_list[-1] != stop_percent:
                active_times_list.append(stop_percent)
            active_times = np.array(active_times_list)
            
            # Get start and end positions
            start_pos = np.array([obj['start_north'], obj['start_east'], obj['start_down']])
            end_pos = np.array([obj['end_north'], obj['end_east'], obj['end_down']])
            
            # Linear interpolation for each time point
            for t in active_times:
                # Calculate interpolation factor (0 at start_percent, 1 at stop_percent)
                if stop_percent == start_percent:
                    alpha = 0
                else:
                    alpha = (t - start_percent) / (stop_percent - start_percent)
                
                # Interpolate position
                pos = start_pos + alpha * (end_pos - start_pos)
                
                trajectory_list.append({
                    'object_id': object_id,
                    'group_id': group_id,
                    'category': obj['category'],
                    'time_percent': t,
                    'north': pos[0],
                    'east': pos[1],
                    'down': pos[2]
                })
        
        self.trajectory_df = pd.DataFrame(trajectory_list)
        return self.trajectory_df
    
    def get_summary_statistics(self) -> Dict:
        """
        Get summary statistics for the simulation.
        
        Returns:
            Dictionary with summary statistics
        """
        if self.objects_df is None:
            raise ValueError("Must call generate_objects() first")
        
        stats = {
            'total_groups': len(self.groups_df),
            'total_objects': len(self.objects_df),
            'num_time_points': self.num_time_points,
            'objects_per_group': self.objects_df.groupby('group_id').size().to_dict(),
            'categories': {
                'category_1': len(self.objects_df[self.objects_df['category'] == 1]),
                'category_2': len(self.objects_df[self.objects_df['category'] == 2]),
                'category_3': len(self.objects_df[self.objects_df['category'] == 3])
            },
            'travel_distance_stats': {
                'min': float(self.objects_df['travel_distance'].min()),
                'max': float(self.objects_df['travel_distance'].max()),
                'mean': float(self.objects_df['travel_distance'].mean()),
                'std': float(self.objects_df['travel_distance'].std())
            }
        }
        
        if self.trajectory_df is not None:
            stats['total_trajectory_points'] = len(self.trajectory_df)
        
        return stats
    
    def save_outputs(self, output_dir: Path, prefix: Optional[str] = None) -> Dict[str, Path]:
        """
        Save simulation outputs to CSV files.
        
        Args:
            output_dir: Directory to save outputs
            prefix: Optional prefix for filenames (default: timestamp)
            
        Returns:
            Dictionary mapping output type to file path
        """
        if self.objects_df is None:
            raise ValueError("Must call generate_objects() first")
        
        # Create output directory if needed
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate prefix if not provided
        if prefix is None:
            prefix = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Save files
        files = {}
        
        # Save input groups
        groups_file = output_dir / f"{prefix}_input_groups.csv"
        self.groups_df.to_csv(groups_file, index=False)
        files['input_groups'] = groups_file
        
        # Save objects
        objects_file = output_dir / f"{prefix}_objects.csv"
        self.objects_df.to_csv(objects_file, index=False)
        files['objects'] = objects_file
        
        # Save trajectories if generated
        if self.trajectory_df is not None:
            trajectories_file = output_dir / f"{prefix}_trajectories.csv"
            self.trajectory_df.to_csv(trajectories_file, index=False)
            files['trajectories'] = trajectories_file
        
        # Save summary statistics
        summary_file = output_dir / f"{prefix}_summary.txt"
        stats = self.get_summary_statistics()
        with open(summary_file, 'w') as f:
            f.write("Spatial Group Simulation Summary\n")
            f.write("=" * 60 + "\n\n")
            for key, value in stats.items():
                f.write(f"{key}: {value}\n")
        files['summary'] = summary_file
        
        return files

