#!/usr/bin/env python3
"""
Timeline Demo - Show multiple examples of group timeline analysis.

This program demonstrates the timeline visualization with several
different scenarios showing various overlap patterns.

Usage:
    python src/timeline_demo.py
    python src/timeline_demo.py --csv data/sample_groups.csv
    python src/timeline_demo.py --num-points 30
"""

import sys
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
from group_scheduler import GroupScheduler, ValidationError
from group_timeline import GroupTimeline


def print_separator(title: str = ""):
    """Print a section separator."""
    if title:
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}\n")
    else:
        print(f"{'='*70}\n")


def create_example_scenarios() -> Dict[str, pd.DataFrame]:
    """Create several example scenarios showing different overlap patterns."""
    
    scenarios = {}
    
    # Scenario 1: No overlaps - groups in sequence
    scenarios['No Overlaps (Sequential)'] = pd.DataFrame({
        'group_id': [1, 2, 3],
        'group_size': [10, 15, 8],
        'start_percent': [0, 35, 70],
        'stop_percent': [30, 65, 100]
    })
    
    # Scenario 2: Two groups overlapping
    scenarios['Two Groups Overlap'] = pd.DataFrame({
        'group_id': [1, 2],
        'group_size': [20, 15],
        'start_percent': [0, 40],
        'stop_percent': [60, 100]
    })
    
    # Scenario 3: All groups overlapping in middle
    scenarios['Three Groups Overlap'] = pd.DataFrame({
        'group_id': [1, 2, 3],
        'group_size': [10, 15, 12],
        'start_percent': [0, 20, 40],
        'stop_percent': [60, 80, 100]
    })
    
    # Scenario 4: Four groups with various overlaps
    scenarios['Four Groups - Complex'] = pd.DataFrame({
        'group_id': [1, 2, 3, 4],
        'group_size': [10, 15, 8, 12],
        'start_percent': [0, 15, 40, 65],
        'stop_percent': [50, 70, 85, 100]
    })
    
    # Scenario 5: Gaps with no activity
    scenarios['With Gaps (No Activity)'] = pd.DataFrame({
        'group_id': [1, 2, 3],
        'group_size': [10, 15, 8],
        'start_percent': [0, 40, 75],
        'stop_percent': [25, 60, 100]
    })
    
    # Scenario 6: Maximum overlap - all groups active together
    scenarios['Maximum Overlap'] = pd.DataFrame({
        'group_id': [1, 2, 3, 4],
        'group_size': [10, 15, 8, 12],
        'start_percent': [0, 10, 20, 30],
        'stop_percent': [70, 80, 90, 100]
    })
    
    return scenarios


def print_overlap_analysis(overlaps: List[Tuple[int, int]], data: pd.DataFrame):
    """Print analysis of overlapping groups."""
    if not overlaps:
        print("  ➤ No overlapping groups")
        return
    
    print("  ➤ Overlapping Group Pairs:")
    for g1, g2 in overlaps:
        # Get the actual overlap period
        row1 = data[data['group_id'] == g1].iloc[0]
        row2 = data[data['group_id'] == g2].iloc[0]
        
        overlap_start = max(row1['start_percent'], row2['start_percent'])
        overlap_end = min(row1['stop_percent'], row2['stop_percent'])
        
        print(f"     - Groups {g1} and {g2}: overlap from {overlap_start:.1f}% to {overlap_end:.1f}%")


def print_concurrent_analysis(stats: Dict[str, Any], matrix: np.ndarray, 
                              time_points: np.ndarray):
    """Print concurrent activity analysis."""
    print("  ➤ Concurrent Activity Statistics:")
    print(f"     - Maximum concurrent: {stats['max_concurrent']} groups")
    print(f"     - Minimum concurrent: {stats['min_concurrent']} groups")
    print(f"     - Average concurrent: {stats['avg_concurrent']:.2f} groups")
    print(f"     - Time points with zero activity: {stats['times_with_zero']}")
    print(f"     - Time points at maximum: {stats['times_with_max']}")
    
    # Find times with different concurrency levels
    concurrent = np.sum(matrix, axis=0)
    
    print("\n  ➤ Activity Patterns:")
    for level in range(stats['min_concurrent'], stats['max_concurrent'] + 1):
        count = np.sum(concurrent == level)
        if count > 0:
            times = [f"{time_points[i]:.1f}%" for i, c in enumerate(concurrent) if c == level]
            if len(times) <= 5:
                times_str = ", ".join(times)
            else:
                times_str = ", ".join(times[:3]) + f" ... ({len(times)} total)"
            print(f"     - {level} groups active: {count} time points (e.g., {times_str})")


def run_scenario(name: str, data: pd.DataFrame, num_points: int = 20):
    """Run and display one scenario."""
    print_separator(name)
    
    # Validate data
    scheduler = GroupScheduler()
    try:
        scheduler.validate_data(data)
    except ValidationError as e:
        print(f"❌ Invalid data: {e}")
        return
    
    # Show group info
    print("Groups:")
    for _, row in data.iterrows():
        print(f"  - Group {row['group_id']}: "
              f"{row['group_size']} people, "
              f"{row['start_percent']:.0f}%-{row['stop_percent']:.0f}%")
    
    # Generate timeline
    timeline = GroupTimeline()
    report = timeline.generate_report(data, num_points=num_points)
    
    # Display timeline table
    print(f"\nActivity Timeline ({num_points} time points):")
    print(report['timeline_table'])
    
    # Display overlap analysis
    print("\nOverlap Analysis:")
    print_overlap_analysis(report['overlapping_groups'], data)
    
    # Display concurrent analysis
    print("\nConcurrent Activity:")
    print_concurrent_analysis(report['concurrent_stats'], 
                             report['timeline_matrix'], 
                             report['time_points'])
    
    print()


def save_report(name: str, report: Dict[str, Any], output_dir: Path):
    """Save report to file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"{timestamp}_timeline_{name.lower().replace(' ', '_')}.txt"
    filepath = output_dir / filename
    
    with open(filepath, 'w') as f:
        f.write(f"Timeline Report: {name}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(report['timeline_table'])
        f.write(f"\n\nOverlapping Groups: {report['overlapping_groups']}\n")
        f.write(f"Concurrent Stats: {report['concurrent_stats']}\n")
    
    return filepath


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Demonstrate group timeline visualization'
    )
    parser.add_argument(
        '--csv',
        type=str,
        help='Use custom CSV file instead of examples'
    )
    parser.add_argument(
        '--num-points',
        type=int,
        default=20,
        help='Number of time points to sample (default: 20)'
    )
    parser.add_argument(
        '--save',
        action='store_true',
        help='Save reports to results directory'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='results',
        help='Output directory for reports (default: results)'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("  GROUP TIMELINE VISUALIZATION - DEMONSTRATION")
    print("=" * 70)
    
    if args.csv:
        # Load custom CSV
        print(f"\nLoading data from: {args.csv}")
        scheduler = GroupScheduler()
        try:
            data = scheduler.load_csv(args.csv)
            run_scenario("Custom Data", data, args.num_points)
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            sys.exit(1)
    else:
        # Run all example scenarios
        scenarios = create_example_scenarios()
        
        print(f"\nRunning {len(scenarios)} example scenarios...")
        print(f"Time points per scenario: {args.num_points}")
        
        output_dir = Path(args.output_dir)
        if args.save:
            output_dir.mkdir(exist_ok=True)
        
        for name, data in scenarios.items():
            run_scenario(name, data, args.num_points)
            
            if args.save:
                timeline = GroupTimeline()
                report = timeline.generate_report(data, num_points=args.num_points)
                filepath = save_report(name, report, output_dir)
                print(f"  📄 Report saved: {filepath}")
                print()
    
    print_separator()
    print("✅ Demonstration complete!")
    print()


if __name__ == "__main__":
    main()

