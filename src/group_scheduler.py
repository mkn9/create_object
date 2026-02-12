"""
Group Scheduler - Read and validate group timing data from CSV.

This module provides functionality to:
- Load group scheduling data from CSV files
- Validate data against constraints
- Provide summary statistics
"""

import pandas as pd
from typing import Dict, Any
from pathlib import Path


class ValidationError(Exception):
    """Custom exception for data validation errors."""
    pass


class GroupScheduler:
    """Handle loading and validation of group scheduling data.
    
    Constraints:
    - Maximum 5 groups
    - Start times: 0 <= start < stop
    - Stop times: start < stop <= 100
    - Times are in percent (0-100)
    - Group sizes must be positive integers
    """
    
    MAX_GROUPS = 5
    MIN_TIME = 0
    MAX_TIME = 100
    
    def __init__(self):
        """Initialize the scheduler."""
        pass
    
    def load_csv(self, filepath: str) -> pd.DataFrame:
        """Load group data from CSV file.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            DataFrame with columns: group_id, group_size, start_percent, stop_percent
            
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If CSV format is invalid
        """
        if not Path(filepath).exists():
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        
        try:
            data = pd.read_csv(filepath)
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}")
        
        # Check required columns
        required_cols = ['group_id', 'group_size', 'start_percent', 'stop_percent']
        missing_cols = set(required_cols) - set(data.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        return data
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate group scheduling data against constraints.
        
        Args:
            data: DataFrame with group scheduling data
            
        Returns:
            True if all validations pass
            
        Raises:
            ValidationError: If any constraint is violated
        """
        # Check number of groups
        if len(data) > self.MAX_GROUPS:
            raise ValidationError(f"Maximum {self.MAX_GROUPS} groups allowed, got {len(data)}")
        
        # Check start times >= 0
        if any(data['start_percent'] < self.MIN_TIME):
            raise ValidationError(f"Start times must be >= {self.MIN_TIME}")
        
        # Check stop times <= 100
        if any(data['stop_percent'] > self.MAX_TIME):
            raise ValidationError(f"Stop times must be <= {self.MAX_TIME}")
        
        # Check start < stop for each group
        if any(data['start_percent'] >= data['stop_percent']):
            raise ValidationError("Start time must be before stop time for all groups")
        
        # Check group sizes are positive
        if any(data['group_size'] <= 0):
            raise ValidationError("Group size must be positive")
        
        return True
    
    def get_total_participants(self, data: pd.DataFrame) -> int:
        """Calculate total number of participants across all groups.
        
        Args:
            data: DataFrame with group scheduling data
            
        Returns:
            Total number of participants
        """
        return int(data['group_size'].sum())
    
    def get_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics from the data.
        
        Args:
            data: DataFrame with group scheduling data
            
        Returns:
            Dictionary with summary statistics
        """
        return {
            'num_groups': len(data),
            'total_participants': self.get_total_participants(data),
            'earliest_start': float(data['start_percent'].min()),
            'latest_stop': float(data['stop_percent'].max()),
            'avg_group_size': float(data['group_size'].mean()),
            'min_group_size': int(data['group_size'].min()),
            'max_group_size': int(data['group_size'].max())
        }

