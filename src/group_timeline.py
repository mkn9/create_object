"""
Group Timeline Visualization and Overlap Analysis.

This module provides functionality to:
- Generate activity timeline matrices (groups vs time)
- Identify overlapping groups
- Calculate concurrent activity statistics
- Format display tables showing when groups are active
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any, Set


class TimelineGenerator:
    """Helper class for generating timeline matrices."""
    
    @staticmethod
    def create_time_points(num_points: int, start: float = 0, end: float = 100) -> np.ndarray:
        """Create evenly spaced time points.
        
        Args:
            num_points: Number of time points to generate
            start: Start time (default 0)
            end: End time (default 100)
            
        Returns:
            Array of time points
        """
        return np.linspace(start, end, num_points)
    
    @staticmethod
    def is_active(time: float, start: float, stop: float) -> int:
        """Check if group is active at given time.
        
        Args:
            time: Time point to check
            start: Group start time
            stop: Group stop time
            
        Returns:
            1 if active, 0 if inactive
        """
        return 1 if start <= time <= stop else 0


class GroupTimeline:
    """Analyze and visualize group activity timelines.
    
    Features:
    - Generate binary activity matrices
    - Identify overlapping groups
    - Calculate concurrent activity statistics
    - Format display tables
    """
    
    def __init__(self):
        """Initialize the timeline analyzer."""
        self.generator = TimelineGenerator()
    
    def generate_timeline(self, data: pd.DataFrame, num_points: int = 20) -> Tuple[np.ndarray, np.ndarray]:
        """Generate activity timeline matrix.
        
        Args:
            data: DataFrame with group scheduling data
            num_points: Number of time points to sample
            
        Returns:
            Tuple of (activity_matrix, time_points)
            - activity_matrix: Shape (num_groups, num_points) with 0/1 values
            - time_points: Array of time values
        """
        time_points = self.generator.create_time_points(num_points)
        num_groups = len(data)
        
        # Create matrix: rows = groups, columns = time points
        matrix = np.zeros((num_groups, num_points), dtype=int)
        
        for i, row in data.iterrows():
            start = row['start_percent']
            stop = row['stop_percent']
            
            for j, time in enumerate(time_points):
                matrix[i, j] = self.generator.is_active(time, start, stop)
        
        return matrix, time_points
    
    def get_overlapping_groups(self, data: pd.DataFrame) -> List[Tuple[int, int]]:
        """Identify pairs of groups that overlap in time.
        
        Args:
            data: DataFrame with group scheduling data
            
        Returns:
            List of tuples (group_id1, group_id2) for overlapping groups
        """
        overlaps = []
        
        for i, row1 in data.iterrows():
            for j, row2 in data.iterrows():
                if i >= j:  # Avoid duplicates and self-comparison
                    continue
                
                # Check if time ranges overlap
                # Overlap if: start1 < stop2 AND start2 < stop1
                if (row1['start_percent'] < row2['stop_percent'] and 
                    row2['start_percent'] < row1['stop_percent']):
                    overlaps.append((int(row1['group_id']), int(row2['group_id'])))
        
        return overlaps
    
    def get_active_groups_at_time(self, data: pd.DataFrame, time: float) -> List[int]:
        """Get list of groups active at specific time.
        
        Args:
            data: DataFrame with group scheduling data
            time: Time point to check (0-100)
            
        Returns:
            List of group IDs active at the given time
        """
        active = []
        
        for _, row in data.iterrows():
            if row['start_percent'] <= time <= row['stop_percent']:
                active.append(int(row['group_id']))
        
        return active
    
    def get_concurrent_stats(self, matrix: np.ndarray) -> Dict[str, Any]:
        """Calculate statistics about concurrent group activity.
        
        Args:
            matrix: Activity matrix from generate_timeline()
            
        Returns:
            Dictionary with statistics:
            - max_concurrent: Maximum number of groups active at once
            - min_concurrent: Minimum number of groups active
            - avg_concurrent: Average number of groups active
            - times_with_zero: Number of time points with no groups
            - times_with_max: Number of time points at maximum concurrency
        """
        # Sum across groups (rows) to get concurrent count at each time
        concurrent = np.sum(matrix, axis=0)
        
        return {
            'max_concurrent': int(np.max(concurrent)),
            'min_concurrent': int(np.min(concurrent)),
            'avg_concurrent': float(np.mean(concurrent)),
            'times_with_zero': int(np.sum(concurrent == 0)),
            'times_with_max': int(np.sum(concurrent == np.max(concurrent)))
        }
    
    def format_as_table(self, matrix: np.ndarray, time_points: np.ndarray, 
                       data: pd.DataFrame) -> str:
        """Format timeline matrix as readable table.
        
        Args:
            matrix: Activity matrix
            time_points: Time values
            data: Group data for labels
            
        Returns:
            Formatted string table
        """
        lines = []
        
        # Header
        header = "Time%  |"
        for _, row in data.iterrows():
            header += f" Group{row['group_id']:2d} |"
        header += " Total |"
        lines.append(header)
        lines.append("-" * len(header))
        
        # Data rows
        for j, time in enumerate(time_points):
            row_str = f"{time:5.1f}  |"
            for i in range(matrix.shape[0]):
                row_str += f"   {matrix[i, j]}    |"
            
            # Add total concurrent
            total = np.sum(matrix[:, j])
            row_str += f"   {total}   |"
            lines.append(row_str)
        
        return "\n".join(lines)
    
    def generate_report(self, data: pd.DataFrame, num_points: int = 20) -> Dict[str, Any]:
        """Generate complete timeline analysis report.
        
        Args:
            data: DataFrame with group scheduling data
            num_points: Number of time points to sample
            
        Returns:
            Dictionary containing:
            - timeline_table: Formatted timeline table string
            - timeline_matrix: Activity matrix
            - time_points: Time point values
            - overlapping_groups: List of overlapping group pairs
            - concurrent_stats: Concurrency statistics
        """
        matrix, time_points = self.generate_timeline(data, num_points)
        overlaps = self.get_overlapping_groups(data)
        stats = self.get_concurrent_stats(matrix)
        table = self.format_as_table(matrix, time_points, data)
        
        return {
            'timeline_table': table,
            'timeline_matrix': matrix,
            'time_points': time_points,
            'overlapping_groups': overlaps,
            'concurrent_stats': stats
        }

