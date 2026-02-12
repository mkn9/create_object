#!/usr/bin/env python3
"""
Spatial Group Simulation Demo

Demonstrates the spatial group simulator with multiple example scenarios.
Generates objects with 3D positions and tracks their movement over time.
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict
from spatial_groups import SpatialGroupSimulator


def create_example_scenarios() -> Dict[str, pd.DataFrame]:
    """
    Create multiple example scenarios for demonstration.
    
    Returns:
        Dictionary mapping scenario name to groups DataFrame
    """
    scenarios = {}
    
    # Scenario 1: Three groups with different categories
    scenarios['three_groups_different_categories'] = pd.DataFrame({
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
    
    # Scenario 2: High overlap - multiple groups active simultaneously
    scenarios['high_overlap'] = pd.DataFrame({
        'group_id': [1, 2, 3, 4],
        'group_size': [3, 4, 3, 2],
        'start_percent': [0, 20, 40, 60],
        'stop_percent': [60, 80, 90, 100],
        'center_north': [0.0, 50.0, 100.0, 150.0],
        'center_east': [0.0, 25.0, 50.0, 75.0],
        'center_down': [0.0, -2.0, -4.0, -6.0],
        'spread_std': [20.0, 18.0, 15.0, 12.0],
        'mean_travel_distance': [80.0, 70.0, 60.0, 50.0],
        'travel_std': [8.0, 7.0, 6.0, 5.0],
        'category': [1, 1, 2, 3]
    })
    
    # Scenario 3: Sequential - no overlap
    scenarios['sequential_no_overlap'] = pd.DataFrame({
        'group_id': [1, 2, 3],
        'group_size': [4, 5, 6],
        'start_percent': [0, 35, 70],
        'stop_percent': [30, 65, 100],
        'center_north': [0.0, 100.0, 200.0],
        'center_east': [0.0, 50.0, 100.0],
        'center_down': [0.0, -3.0, -6.0],
        'spread_std': [12.0, 15.0, 18.0],
        'mean_travel_distance': [40.0, 50.0, 60.0],
        'travel_std': [4.0, 5.0, 6.0],
        'category': [1, 2, 3]
    })
    
    # Scenario 4: Tight cluster - low spread, short travel
    scenarios['tight_cluster'] = pd.DataFrame({
        'group_id': [1, 2],
        'group_size': [8, 6],
        'start_percent': [0, 50],
        'stop_percent': [50, 100],
        'center_north': [100.0, 120.0],
        'center_east': [50.0, 60.0],
        'center_down': [-5.0, -7.0],
        'spread_std': [5.0, 5.0],
        'mean_travel_distance': [15.0, 20.0],
        'travel_std': [2.0, 3.0],
        'category': [1, 1]
    })
    
    # Scenario 5: Wide dispersal - high spread, long travel
    scenarios['wide_dispersal'] = pd.DataFrame({
        'group_id': [1, 2],
        'group_size': [4, 5],
        'start_percent': [0, 40],
        'stop_percent': [60, 100],
        'center_north': [200.0, 300.0],
        'center_east': [100.0, -100.0],
        'center_down': [0.0, 10.0],
        'spread_std': [50.0, 60.0],
        'mean_travel_distance': [150.0, 180.0],
        'travel_std': [20.0, 25.0],
        'category': [2, 3]
    })
    
    return scenarios


def print_scenario_summary(name: str, simulator: SpatialGroupSimulator, objects_df: pd.DataFrame):
    """Print summary of a scenario."""
    print(f"\n{'='*80}")
    print(f"Scenario: {name.replace('_', ' ').title()}")
    print(f"{'='*80}\n")
    
    stats = simulator.get_summary_statistics()
    
    print(f"Groups: {stats['total_groups']}")
    print(f"Total Objects: {stats['total_objects']}")
    print(f"Time Points: {stats['num_time_points']}")
    
    print(f"\nObjects per Group:")
    for gid, count in stats['objects_per_group'].items():
        print(f"  Group {gid}: {count} objects")
    
    print(f"\nCategory Distribution:")
    for cat, count in stats['categories'].items():
        print(f"  {cat}: {count} objects")
    
    print(f"\nTravel Distance Statistics:")
    print(f"  Min: {stats['travel_distance_stats']['min']:.2f}m")
    print(f"  Max: {stats['travel_distance_stats']['max']:.2f}m")
    print(f"  Mean: {stats['travel_distance_stats']['mean']:.2f}m")
    print(f"  Std: {stats['travel_distance_stats']['std']:.2f}m")
    
    # Show sample objects table
    print(f"\n{'-'*80}")
    print(f"Sample Objects (first 10):")
    print(f"{'-'*80}")
    
    sample_df = objects_df.head(10).copy()
    sample_df['start_pos'] = sample_df.apply(
        lambda r: f"({r['start_north']:.1f}, {r['start_east']:.1f}, {r['start_down']:.1f})", axis=1
    )
    sample_df['end_pos'] = sample_df.apply(
        lambda r: f"({r['end_north']:.1f}, {r['end_east']:.1f}, {r['end_down']:.1f})", axis=1
    )
    
    display_cols = ['object_id', 'group_id', 'category', 'start_pos', 'end_pos', 'travel_distance']
    print(sample_df[display_cols].to_string(index=False))
    
    # Time overlap analysis
    print(f"\n{'-'*80}")
    print(f"Group Time Windows:")
    print(f"{'-'*80}")
    
    for _, group in simulator.groups_df.iterrows():
        print(f"  Group {int(group['group_id'])}: {group['start_percent']:.1f}% - {group['stop_percent']:.1f}%")


def print_trajectory_sample(name: str, trajectory_df: pd.DataFrame, num_samples: int = 5):
    """Print sample trajectory points."""
    print(f"\n{'-'*80}")
    print(f"Trajectory Sample (first {num_samples} time points for first object):")
    print(f"{'-'*80}")
    
    # Get first object's trajectory
    first_object_id = trajectory_df['object_id'].iloc[0]
    obj_traj = trajectory_df[trajectory_df['object_id'] == first_object_id].head(num_samples)
    
    obj_traj['position'] = obj_traj.apply(
        lambda r: f"({r['north']:.2f}, {r['east']:.2f}, {r['down']:.2f})", axis=1
    )
    
    display_cols = ['time_percent', 'position']
    print(obj_traj[display_cols].to_string(index=False))


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Spatial Group Simulation Demo - Generate and visualize object movement"
    )
    parser.add_argument(
        '--csv',
        type=Path,
        help='Optional: Path to custom CSV file with group spatial parameters'
    )
    parser.add_argument(
        '--time-points',
        type=int,
        default=50,
        help='Number of time points to simulate (default: 50)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    parser.add_argument(
        '--save',
        action='store_true',
        help='Save outputs to results directory'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('results'),
        help='Directory for output files (default: results/)'
    )
    
    args = parser.parse_args()
    
    # Generate timestamp for outputs
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    if args.csv:
        # Run single scenario from CSV
        print(f"\nLoading spatial groups from: {args.csv}")
        simulator = SpatialGroupSimulator.from_csv(
            args.csv,
            num_time_points=args.time_points,
            random_seed=args.seed
        )
        objects_df = simulator.generate_objects()
        trajectory_df = simulator.generate_trajectories()
        
        print_scenario_summary("custom_scenario", simulator, objects_df)
        print_trajectory_sample("custom_scenario", trajectory_df)
        
        if args.save:
            files = simulator.save_outputs(args.output_dir, prefix=f"{timestamp}_custom")
            print(f"\n{'='*80}")
            print("Outputs saved:")
            for ftype, fpath in files.items():
                print(f"  {ftype}: {fpath}")
            print(f"{'='*80}")
    
    else:
        # Run all example scenarios
        print("\n" + "="*80)
        print("SPATIAL GROUP SIMULATION - MULTIPLE EXAMPLE SCENARIOS")
        print("="*80)
        
        scenarios = create_example_scenarios()
        
        for name, groups_df in scenarios.items():
            simulator = SpatialGroupSimulator(
                groups_df,
                num_time_points=args.time_points,
                random_seed=args.seed
            )
            objects_df = simulator.generate_objects()
            trajectory_df = simulator.generate_trajectories()
            
            print_scenario_summary(name, simulator, objects_df)
            print_trajectory_sample(name, trajectory_df)
            
            if args.save:
                files = simulator.save_outputs(args.output_dir, prefix=f"{timestamp}_{name}")
                print(f"\nOutputs saved to: {args.output_dir}")
        
        if args.save:
            print(f"\n{'='*80}")
            print(f"All scenario outputs saved to: {args.output_dir}")
            print(f"{'='*80}")


if __name__ == '__main__':
    main()

