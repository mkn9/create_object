# Data Directory

This directory contains CSV files for the group scheduler.

## Sample Files

### sample_groups.csv

Example CSV file demonstrating the required format and constraints.

**Contents:**
- 5 groups (maximum allowed)
- Start times range: 0-90%
- Stop times range: 25-100%
- Group sizes: 10-20 people
- Total participants: 75 people

**Usage:**
```bash
python src/main.py data/sample_groups.csv
python src/main.py data/sample_groups.csv --total-time 120
```

## CSV File Format

### Required Columns

| Column | Type | Description |
|--------|------|-------------|
| `group_id` | int | Unique group identifier |
| `group_size` | int | Number of people in group (must be > 0) |
| `start_percent` | float | Start time as % of total (0-100) |
| `stop_percent` | float | Stop time as % of total (0-100) |

### Constraints

- ✅ Maximum 5 groups
- ✅ Start times: 0 ≤ start < stop
- ✅ Stop times: start < stop ≤ 100
- ✅ Group sizes: Must be positive integers
- ✅ Times in percent: 0 to 100

### Example

```csv
group_id,group_size,start_percent,stop_percent
1,20,0,25
2,15,20,50
3,18,45,75
```

## Creating Your Own CSV

1. Create a new CSV file in this directory
2. Include the header row exactly as shown
3. Add up to 5 groups
4. Ensure all constraints are met
5. Test with: `python src/main.py data/your_file.csv`

## Validation

The program will automatically validate your CSV against all constraints and report any errors.

**See:** `docs/GROUP_SCHEDULER.md` for complete documentation.

