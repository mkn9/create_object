# Group Scheduler

**Created:** February 12, 2026  
**Status:** Complete and Tested

---

## Overview

The Group Scheduler is a Python program that reads group timing data from CSV files, validates the data against constraints, and provides summary statistics.

### Features

- ✅ CSV file input with group scheduling data
- ✅ Comprehensive data validation
- ✅ Summary statistics generation
- ✅ Optional time conversion (percent to minutes)
- ✅ Timestamped output files
- ✅ 17 comprehensive unit tests

---

## CSV File Format

### Required Columns

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `group_id` | int | Unique group identifier | Positive integer |
| `group_size` | int | Number of people in group | > 0 |
| `start_percent` | float | Start time as % of total | 0 ≤ start < stop |
| `stop_percent` | float | Stop time as % of total | start < stop ≤ 100 |

### Constraints

- **Maximum groups:** 5
- **Time range:** 0 to 100 (percent)
- **Start time:** Must be ≥ 0
- **Stop time:** Must be ≤ 100
- **Group size:** Must be positive integer
- **Timing:** Start time must be < stop time for each group

### Example CSV

```csv
group_id,group_size,start_percent,stop_percent
1,20,0,25
2,15,20,50
3,18,45,75
4,12,70,95
5,10,90,100
```

**Explanation:**
- Group 1: 20 people, active from 0% to 25% of total time
- Group 2: 15 people, active from 20% to 50% of total time
- Group 3: 18 people, active from 45% to 75% of total time
- Group 4: 12 people, active from 70% to 95% of total time
- Group 5: 10 people, active from 90% to 100% of total time

**Note:** Groups can overlap in time (e.g., Groups 1 and 2 overlap from 20-25%).

---

## Usage

### Basic Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Run with CSV file
python src/main.py data/sample_groups.csv
```

### With Total Time

```bash
# Convert percentages to actual minutes
python src/main.py data/sample_groups.csv --total-time 120
```

This will show actual start/stop times in minutes. For example, if total time is 120 minutes:
- 0% = 0 minutes
- 25% = 30 minutes
- 100% = 120 minutes

### Specify Output Directory

```bash
python src/main.py data/sample_groups.csv --output-dir my_results
```

---

## Output

### Console Output

The program displays:
1. **Loading status** - Confirms CSV loaded successfully
2. **Validation status** - Confirms all constraints satisfied
3. **Group data table** - All groups with their parameters
4. **Summary statistics** - Aggregate information
5. **Time conversions** - If `--total-time` provided

### File Output

The program creates a timestamped summary file in the results directory:

**Format:** `YYYYMMDD_HHMM_group_summary.txt`

**Example:** `20260212_1700_group_summary.txt`

**Contents:**
- Input file path
- Generation timestamp
- Complete group data table
- Summary statistics

---

## Validation Rules

The program validates data against these rules:

### ✅ Passes Validation

```csv
group_id,group_size,start_percent,stop_percent
1,10,0,30      # Valid: 0 ≤ start < stop ≤ 100
2,15,25,60     # Valid: Overlaps allowed
3,8,55,95      # Valid: Within bounds
```

### ❌ Fails Validation

```csv
# Too many groups (>5)
1,10,0,20
2,10,20,40
3,10,40,60
4,10,60,80
5,10,80,90
6,10,90,100    # ❌ Error: Maximum 5 groups allowed
```

```csv
# Negative start time
1,10,-5,20     # ❌ Error: Start times must be >= 0
```

```csv
# Stop time over 100
1,10,80,105    # ❌ Error: Stop times must be <= 100
```

```csv
# Start >= stop
1,10,60,50     # ❌ Error: Start must be before stop
```

```csv
# Zero or negative group size
1,0,20,40      # ❌ Error: Group size must be positive
1,-5,20,40     # ❌ Error: Group size must be positive
```

---

## Testing

### Run All Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests with verbose output
pytest tests/test_group_scheduler.py -v
```

### Test Coverage

```bash
# Run with coverage report
pytest tests/test_group_scheduler.py --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### Test Categories

**Invariant Tests (4):**
- Start times non-negative
- Stop times within bounds
- Start before stop
- Group size positive

**Golden Tests (2):**
- Load valid CSV
- Validate golden case

**Validation Error Tests (6):**
- Reject too many groups
- Reject negative start time
- Reject stop time > 100
- Reject start >= stop
- Reject zero group size

**Edge Case Tests (4):**
- Exactly 5 groups (boundary)
- Start time = 0 (boundary)
- Stop time = 100 (boundary)
- Single group

**Integration Tests (2):**
- Load and validate workflow
- Get summary statistics

**Total: 17 tests, all passing ✅**

---

## Code Structure

```
create_object/
├── src/
│   ├── __init__.py
│   ├── group_scheduler.py    # Core module
│   └── main.py               # CLI program
│
├── tests/
│   └── test_group_scheduler.py  # 17 comprehensive tests
│
├── data/
│   └── sample_groups.csv     # Example CSV file
│
└── results/
    └── YYYYMMDD_HHMM_group_summary.txt  # Output files
```

---

## API Documentation

### GroupScheduler Class

```python
from src.group_scheduler import GroupScheduler

scheduler = GroupScheduler()
```

#### Methods

**`load_csv(filepath: str) -> pd.DataFrame`**

Load group data from CSV file.

```python
data = scheduler.load_csv('data/sample_groups.csv')
```

**Returns:** DataFrame with columns `group_id`, `group_size`, `start_percent`, `stop_percent`

**Raises:** 
- `FileNotFoundError` if file doesn't exist
- `ValueError` if CSV format is invalid

---

**`validate_data(data: pd.DataFrame) -> bool`**

Validate data against all constraints.

```python
result = scheduler.validate_data(data)  # Returns True or raises ValidationError
```

**Returns:** `True` if all validations pass

**Raises:** `ValidationError` if any constraint violated

---

**`get_total_participants(data: pd.DataFrame) -> int`**

Calculate total number of participants.

```python
total = scheduler.get_total_participants(data)
```

---

**`get_summary(data: pd.DataFrame) -> Dict[str, Any]`**

Get summary statistics.

```python
summary = scheduler.get_summary(data)
# Returns: {
#     'num_groups': 5,
#     'total_participants': 75,
#     'earliest_start': 0.0,
#     'latest_stop': 100.0,
#     'avg_group_size': 15.0,
#     'min_group_size': 10,
#     'max_group_size': 20
# }
```

---

## Example Usage in Python

```python
from src.group_scheduler import GroupScheduler, ValidationError

# Initialize scheduler
scheduler = GroupScheduler()

# Load data
try:
    data = scheduler.load_csv('data/sample_groups.csv')
    print(f"Loaded {len(data)} groups")
except FileNotFoundError as e:
    print(f"File not found: {e}")
    exit(1)

# Validate data
try:
    scheduler.validate_data(data)
    print("✅ Validation passed!")
except ValidationError as e:
    print(f"❌ Validation failed: {e}")
    exit(1)

# Get summary
summary = scheduler.get_summary(data)
print(f"Total participants: {summary['total_participants']}")

# Calculate actual times (if total time is 120 minutes)
total_time = 120
for _, row in data.iterrows():
    start_min = (row['start_percent'] / 100) * total_time
    stop_min = (row['stop_percent'] / 100) * total_time
    print(f"Group {row['group_id']}: {start_min:.1f} - {stop_min:.1f} min")
```

---

## Development Process

This feature was developed using **Test-Driven Development (TDD)**:

### RED Phase ✅
- Wrote 17 comprehensive tests first
- Tests covered invariants, golden cases, errors, edge cases, and integration
- All tests initially failed (expected)

### GREEN Phase ✅
- Implemented `GroupScheduler` class
- Implemented all validation logic
- Implemented CSV loading and summary statistics
- All 17 tests now pass

### REFACTOR Phase ✅
- Added comprehensive docstrings
- Created CLI program with user-friendly output
- Added timestamped file output
- Created documentation

---

## Future Enhancements

Potential additions for future development:

1. **Visualization**
   - Gantt chart of group timings
   - Timeline visualization with overlaps

2. **Conflict Detection**
   - Identify overlapping groups
   - Calculate maximum concurrent participants

3. **Optimization**
   - Suggest optimal scheduling
   - Minimize overlaps or maximize coverage

4. **Export Formats**
   - JSON output
   - Excel export
   - PDF reports

5. **Interactive Mode**
   - Add/edit groups interactively
   - Real-time validation
   - GUI interface

---

## Troubleshooting

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Ensure pandas is installed
pip install pandas
```

### CSV Not Found

```bash
# Check file path
ls data/sample_groups.csv

# Use absolute path if needed
python src/main.py /full/path/to/file.csv
```

### Validation Fails

Check that your CSV meets all constraints:
- Maximum 5 groups
- Start times ≥ 0
- Stop times ≤ 100
- Start < stop for each group
- Group sizes > 0

---

## References

- **Code:** `src/group_scheduler.py`
- **Tests:** `tests/test_group_scheduler.py`
- **CLI:** `src/main.py`
- **Sample Data:** `data/sample_groups.csv`

---

**Development Complete:** February 12, 2026  
**Test Status:** 17/17 passing ✅  
**Coverage:** 100% of core functionality

