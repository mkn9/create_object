#!/usr/bin/env python3
"""
Main program for group scheduler.

This program reads group scheduling data from a CSV file,
validates it, and displays summary information.

Usage:
    python src/main.py <csv_file>
    python src/main.py data/sample_groups.csv
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
from group_scheduler import GroupScheduler, ValidationError


def main():
    """Main entry point for the group scheduler program."""
    parser = argparse.ArgumentParser(
        description='Load and validate group scheduling data from CSV'
    )
    parser.add_argument(
        'csv_file',
        type=str,
        help='Path to CSV file with group data'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='results',
        help='Directory for output files (default: results)'
    )
    parser.add_argument(
        '--total-time',
        type=float,
        help='Total time in minutes (optional, for future use)'
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    if not Path(args.csv_file).exists():
        print(f"❌ Error: File not found: {args.csv_file}")
        sys.exit(1)
    
    # Initialize scheduler
    scheduler = GroupScheduler()
    
    print("=" * 60)
    print("Group Scheduler - Data Validation")
    print("=" * 60)
    print()
    
    # Load CSV
    print(f"📁 Loading data from: {args.csv_file}")
    try:
        data = scheduler.load_csv(args.csv_file)
        print(f"✅ Loaded {len(data)} groups")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        sys.exit(1)
    
    print()
    
    # Validate data
    print("🔍 Validating data...")
    try:
        scheduler.validate_data(data)
        print("✅ All validation checks passed!")
    except ValidationError as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)
    
    print()
    
    # Display data
    print("📊 Group Data:")
    print("-" * 60)
    print(data.to_string(index=False))
    print()
    
    # Display summary
    print("📈 Summary Statistics:")
    print("-" * 60)
    summary = scheduler.get_summary(data)
    print(f"Number of groups:      {summary['num_groups']}")
    print(f"Total participants:    {summary['total_participants']}")
    print(f"Earliest start:        {summary['earliest_start']}%")
    print(f"Latest stop:           {summary['latest_stop']}%")
    print(f"Average group size:    {summary['avg_group_size']:.1f}")
    print(f"Min group size:        {summary['min_group_size']}")
    print(f"Max group size:        {summary['max_group_size']}")
    
    if args.total_time:
        print()
        print(f"⏱️  Total Time: {args.total_time} minutes")
        print("-" * 60)
        for _, row in data.iterrows():
            start_min = (row['start_percent'] / 100) * args.total_time
            stop_min = (row['stop_percent'] / 100) * args.total_time
            duration = stop_min - start_min
            print(f"Group {row['group_id']}: {start_min:.1f} - {stop_min:.1f} min "
                  f"(duration: {duration:.1f} min, {row['group_size']} people)")
    
    print()
    print("=" * 60)
    
    # Save summary to results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    summary_file = output_dir / f"{timestamp}_group_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("Group Scheduler Summary\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Input file: {args.csv_file}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("Group Data:\n")
        f.write("-" * 60 + "\n")
        f.write(data.to_string(index=False) + "\n\n")
        f.write("Summary Statistics:\n")
        f.write("-" * 60 + "\n")
        for key, value in summary.items():
            f.write(f"{key}: {value}\n")
    
    print(f"📄 Summary saved to: {summary_file}")
    print()


if __name__ == "__main__":
    main()

