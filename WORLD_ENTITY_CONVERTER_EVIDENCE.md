# World Entity Converter - Test Evidence and Output Demonstration

**Date:** February 12, 2026  
**Module:** `src/world_entity_converter.py`  
**Tests:** 11/11 passing ✅

---

## Evidence Summary

This document provides complete evidence that the World Entity Converter:
1. ✅ Creates the `./trajectories/G/` folder structure
2. ✅ Populates it with tab-delimited trajectory files
3. ✅ Appends multiple WORLD_ENTITY strings into consolidated file
4. ✅ All functionality tested and working

---

## 1. Test Evidence: Creating trajectories/G Folder

### Test Code Location

**File:** `tests/test_world_entity_converter.py`  
**Lines:** 108-124

```python
def test_save_trajectory_file(self, sample_csv_file, tmp_path, cleanup_trajectories):
    """Should save trajectory files in correct format."""
    from src.world_entity_converter import WorldEntityConverter
    
    # Use tmp_path for output
    output_base = tmp_path / 'trajectories'
    
    converter = WorldEntityConverter(output_dir=output_base)
    result = converter.convert_csv_to_world_entities(sample_csv_file)
    
    # Check that files were created
    g_dir = output_base / 'G'
    assert g_dir.exists()                    # ✅ Verifies G folder exists
    
    # Should have 3 trajectory files
    traj_files = list(g_dir.glob('G_*_.txt'))
    assert len(traj_files) == 3              # ✅ Verifies files created
```

### Implementation Code Location

**File:** `src/world_entity_converter.py`  
**Lines:** 115-127

```python
def save_trajectory_file(self, key: int, trajectory_df: pd.DataFrame) -> Path:
    """Save trajectory data to tab-delimited file."""
    # Create G directory if needed
    g_dir = self.output_dir / 'G'
    g_dir.mkdir(parents=True, exist_ok=True)  # ✅ Creates trajectories/G/
    
    # Create filename: G_<key>_.txt
    filename = f"G_{key}_.txt"
    filepath = g_dir / filename
    
    # Save as tab-delimited
    trajectory_df.to_csv(filepath, sep='\t', index=False, na_rep='')
    
    return filepath
```

### Test Result

```bash
$ pytest tests/test_world_entity_converter.py::TestWorldEntityConverter::test_save_trajectory_file -v

============================= test session starts ==============================
tests/test_world_entity_converter.py .                                   [100%]

============================== 1 passed in 0.30s ===============================
```

**Status:** ✅ PASSING - Folder creation verified

---

## 2. Test Evidence: Consolidated WORLD_ENTITIES File

### Test Code Location

**File:** `tests/test_world_entity_converter.py`  
**Lines:** 182-202

```python
def test_consolidated_world_entities_file(self, sample_csv_file, tmp_path, cleanup_trajectories):
    """Should create consolidated file with all WORLD_ENTITY strings."""
    from src.world_entity_converter import WorldEntityConverter
    
    output_base = tmp_path / 'trajectories'
    converter = WorldEntityConverter(output_dir=output_base)
    result = converter.convert_csv_to_world_entities(sample_csv_file)
    
    # Check consolidated file exists
    consolidated_file = output_base / 'all_G_WORLD_ENTITIES.txt'
    assert consolidated_file.exists()        # ✅ Verifies file exists
    
    # Read and check contents
    with open(consolidated_file, 'r') as f:
        content = f.read()
    
    # Should have 3 WORLD_ENTITY blocks
    assert content.count('WORLD_ENTITY {') == 3    # ✅ Verifies 3 entities
    assert content.count('name = G_1') == 1        # ✅ Verifies entity 1
    assert content.count('name = G_2') == 1        # ✅ Verifies entity 2
    assert content.count('name = G_3') == 1        # ✅ Verifies entity 3
```

### Implementation Code Location

**File:** `src/world_entity_converter.py`  
**Lines:** 212-219

```python
# Create consolidated file with all entities
consolidated_content = '\n\n'.join([
    entity_strings[k] for k in sorted(entity_strings.keys())
])  # ✅ Joins all entity strings with blank lines

consolidated_file = self.output_dir / 'all_G_WORLD_ENTITIES.txt'
self.output_dir.mkdir(parents=True, exist_ok=True)

with open(consolidated_file, 'w') as f:
    f.write(consolidated_content)  # ✅ Writes consolidated file
```

### Test Result

```bash
$ pytest tests/test_world_entity_converter.py::TestWorldEntityConverter::test_consolidated_world_entities_file -v

============================= test session starts ==============================
tests/test_world_entity_converter.py .                                   [100%]

============================== 1 passed in 0.23s ===============================
```

**Status:** ✅ PASSING - Consolidated file creation verified

---

## 3. Live Demonstration with Real Data

### Input File

**File:** `results/20260212_1743_tight_cluster_trajectories.csv`  
**Objects:** 14 (from tight cluster scenario)  
**Rows:** 366 trajectory points

### Command Executed

```bash
$ python src/world_entity_converter.py results/20260212_1743_tight_cluster_trajectories.csv

✅ Conversion Complete!
Entities created: 14
Trajectory files: 14
Consolidated file: trajectories/all_G_WORLD_ENTITIES.txt

Entity keys: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
```

---

## 4. Output Verification: Directory Structure

### Created Directories

```bash
$ ls -lh trajectories/
total 8
drwxr-xr-x@ 16 mike  staff   512B Feb 12 21:56 G
-rw-r--r--@  1 mike  staff   2.4K Feb 12 21:56 all_G_WORLD_ENTITIES.txt
```

**Evidence:** ✅ Both `G/` folder and `all_G_WORLD_ENTITIES.txt` created

### Created Trajectory Files

```bash
$ ls -lh trajectories/G/
total 112
-rw-r--r--@ 1 mike  staff   2.0K Feb 12 21:56 G_10_.txt
-rw-r--r--@ 1 mike  staff   2.0K Feb 12 21:56 G_11_.txt
-rw-r--r--@ 1 mike  staff   2.0K Feb 12 21:56 G_12_.txt
-rw-r--r--@ 1 mike  staff   2.0K Feb 12 21:56 G_13_.txt
-rw-r--r--@ 1 mike  staff   2.0K Feb 12 21:56 G_14_.txt
-rw-r--r--@ 1 mike  staff   2.0K Feb 12 21:56 G_1_.txt
-rw-r--r--@ 1 mike  staff   2.0K Feb 12 21:56 G_2_.txt
-rw-r--r--@ 1 mike  staff   2.0K Feb 12 21:56 G_3_.txt
-rw-r--r--@ 1 mike  staff   2.0K Feb 12 21:56 G_4_.txt
-rw-r--r--@ 1 mike  staff   2.0K Feb 12 21:56 G_5_.txt
-rw-r--r--@ 1 mike  staff   2.0K Feb 12 21:56 G_6_.txt
-rw-r--r--@ 1 mike  staff   2.0K Feb 12 21:56 G_7_.txt
-rw-r--r--@ 1 mike  staff   2.0K Feb 12 21:56 G_8_.txt
-rw-r--r--@ 1 mike  staff   2.0K Feb 12 21:56 G_9_.txt
```

**Evidence:** ✅ All 14 trajectory files created with naming convention `G_<key>_.txt`

---

## 5. Output Verification: Trajectory File Format

### Sample Trajectory File (G_1_.txt)

```
FIELDS	FRAME	TIME	POS_N	POS_E	POS_D
	0.0	0.0	102.48357076505616	49.308678494144075	-1.7615573094965375
	0.0	2.0408163265306123	102.37668180652304	49.20179703018064	-1.040660532539286
	0.0	4.081632653061225	102.26979284798996	49.09491556621721	-0.3197637555820343
	0.0	6.122448979591837	102.16290388945684	48.98803410225378	0.4011330213752173
	0.0	8.16326530612245	102.05601493092374	48.881152638290345	1.122029798332469
	0.0	10.20408163265306	101.94912597239065	48.77427117432691	1.84292657528972
	0.0	12.244897959183676	101.84223701385751	48.66738971036348	2.563823352246972
```

**Verification:**
- ✅ FIELDS column: empty (not NaN)
- ✅ FRAME column: 0.0
- ✅ TIME column: time_percent values
- ✅ POS_N, POS_E, POS_D: coordinate values
- ✅ Tab-delimited format

### Tab Verification (using od command)

```bash
$ head -3 trajectories/G/G_5_.txt | od -c | head -10
0000000    F   I   E   L   D   S  \t   F   R   A   M   E  \t   T   I   M
0000020    E  \t   P   O   S   _   N  \t   P   O   S   _   E  \t   P   O
0000040    S   _   D  \n  \t   0   .   0  \t   0   .   0  \t   9   6   .
```

**Evidence:** ✅ Tabs confirmed (shown as `\t` in output)

---

## 6. Output Verification: Consolidated WORLD_ENTITIES File

### File Contents (all 14 entities)

```bash
$ cat trajectories/all_G_WORLD_ENTITIES.txt
```

```
WORLD_ENTITY {
    name = G_1
    position = "102.48357076505616, 49.308678494144075, -1.7615573094965375"
    scale =
    stateAttsLoadFilename = './trajectories/G/G_1_.txt'
}

WORLD_ENTITY {
    name = G_2
    position = "103.83717364576457, 47.65262807032524, -2.287199782070177"
    scale =
    stateAttsLoadFilename = './trajectories/G/G_2_.txt'
}

WORLD_ENTITY {
    name = G_3
    position = "91.37541083743484, 47.188562353795135, -10.06415560167212"
    scale =
    stateAttsLoadFilename = './trajectories/G/G_3_.txt'
}

WORLD_ENTITY {
    name = G_4
    position = "98.87111849756732, 50.337641023439616, -12.123740931067283"
    scale =
    stateAttsLoadFilename = './trajectories/G/G_4_.txt'
}

WORLD_ENTITY {
    name = G_5
    position = "96.99680655040598, 48.54153125103362, -8.008533061146984"
    scale =
    stateAttsLoadFilename = './trajectories/G/G_5_.txt'
}

WORLD_ENTITY {
    name = G_6
    position = "93.89578175014488, 51.04431797502378, -14.798350619398878"
    scale =
    stateAttsLoadFilename = './trajectories/G/G_6_.txt'
}

WORLD_ENTITY {
    name = G_7
    position = "99.4217585880588, 48.494481522053555, -12.392609951837136"
    scale =
    stateAttsLoadFilename = './trajectories/G/G_7_.txt'
}

WORLD_ENTITY {
    name = G_8
    position = "91.18479922318632, 51.620419846973974, -6.925411402081583"
    scale =
    stateAttsLoadFilename = './trajectories/G/G_8_.txt'
}

WORLD_ENTITY {
    name = G_9
    position = "115.8039123838868, 58.45393812074393, -5.34368284298218"
    scale =
    stateAttsLoadFilename = './trajectories/G/G_9_.txt'
}

WORLD_ENTITY {
    name = G_10
    position = "114.01896687959665, 64.06262911197099, -0.2187998571458855"
    scale =
    stateAttsLoadFilename = './trajectories/G/G_10_.txt'
}

WORLD_ENTITY {
    name = G_11
    position = "121.80697802754209, 67.69018283232984, -7.1791301955497575"
    scale =
    stateAttsLoadFilename = './trajectories/G/G_11_.txt'
}

WORLD_ENTITY {
    name = G_12
    position = "118.50496324767066, 60.458803882677515, -16.937844573004462"
    scale =
    stateAttsLoadFilename = './trajectories/G/G_12_.txt'
}

WORLD_ENTITY {
    name = G_13
    position = "115.95753198553406, 57.491214782077314, -2.4229894114896293"
    scale =
    stateAttsLoadFilename = './trajectories/G/G_13_.txt'
}

WORLD_ENTITY {
    name = G_14
    position = "124.84322495266444, 56.48973453061324, -8.638310732988842"
    scale =
    stateAttsLoadFilename = './trajectories/G/G_14_.txt'
}
```

### Entity Count Verification

```bash
$ grep -c "WORLD_ENTITY {" trajectories/all_G_WORLD_ENTITIES.txt
14
```

**Evidence:** ✅ All 14 WORLD_ENTITY strings successfully appended to consolidated file

---

## 7. Code Flow: How Entities Are Appended

### Step 1: Process Each Key (Lines 195-210)

```python
entity_strings = {}  # Dictionary to store all entity strings

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
    entity_strings[key] = entity_string  # ✅ Store in dictionary
```

### Step 2: Join All Entity Strings (Line 213)

```python
# Create consolidated file with all entities
consolidated_content = '\n\n'.join([
    entity_strings[k] for k in sorted(entity_strings.keys())
])
# ✅ This line appends all entity strings with blank lines between them
```

**Breakdown:**
1. `sorted(entity_strings.keys())` → `[1, 2, 3, ..., 14]`
2. `[entity_strings[k] for k in ...]` → List of all WORLD_ENTITY strings
3. `'\n\n'.join(...)` → Joins with two newlines (blank line between entities)

### Step 3: Write Consolidated File (Lines 215-219)

```python
consolidated_file = self.output_dir / 'all_G_WORLD_ENTITIES.txt'
self.output_dir.mkdir(parents=True, exist_ok=True)

with open(consolidated_file, 'w') as f:
    f.write(consolidated_content)  # ✅ Writes all appended content
```

---

## 8. Complete Test Suite Results

### All Tests Passing

```bash
$ pytest tests/test_world_entity_converter.py -v

============================= test session starts ==============================
platform darwin -- Python 3.13.1, pytest-9.0.2, pluggy-1.6.0
rootdir: /Users/mike/Dropbox/Code/repos/create_object
configfile: pytest.ini
plugins: cov-7.0.0
collected 11 items

tests/test_world_entity_converter.py ...........                         [100%]

============================== 11 passed in 0.23s ==============================
```

### Test Coverage

| Test | What It Verifies | Status |
|------|------------------|--------|
| `test_create_unique_keys` | Unique key generation | ✅ PASS |
| `test_unique_keys_increment_by_one` | Sequential numbering | ✅ PASS |
| `test_unique_keys_consistent_for_same_object_group` | Key consistency | ✅ PASS |
| `test_create_trajectory_output_format` | Column format | ✅ PASS |
| `test_save_trajectory_file` | **G folder creation** | ✅ PASS |
| `test_trajectory_file_tab_delimited` | Tab-delimited format | ✅ PASS |
| `test_create_world_entity_string` | Entity string format | ✅ PASS |
| `test_world_entity_position_format` | Position format | ✅ PASS |
| `test_consolidated_world_entities_file` | **Consolidated file with all entities** | ✅ PASS |
| `test_return_entity_mapping` | Return value structure | ✅ PASS |
| `test_fields_column_empty_not_nan` | FIELDS column format | ✅ PASS |

---

## 9. Why Output Files Not in results/ Folder

### By Design

The `trajectories/` folder is **intentionally separate** from `results/` because:

1. **Different Purpose:**
   - `results/` = Spatial simulation outputs (CSV files)
   - `trajectories/` = WORLD_ENTITY simulation format (TXT files)

2. **Different Format:**
   - `results/` contains trajectory CSVs with columns: `object_id, group_id, category, time_percent, north, east, down`
   - `trajectories/` contains formatted TXT files with columns: `FIELDS, FRAME, TIME, POS_N, POS_E, POS_D`

3. **Workflow Separation:**
   ```
   Step 1: Generate trajectories → results/*.csv
   Step 2: Convert to WORLD_ENTITY → trajectories/G/*.txt
   ```

4. **Excluded from Git:**
   - `trajectories/` is in `.gitignore` (generated output)
   - `results/` is tracked in git (example data)

### Location

The `trajectories/` folder is created in the **current working directory** when you run:

```bash
python src/world_entity_converter.py <input.csv>
```

Or you can specify a custom location:

```bash
python src/world_entity_converter.py <input.csv> --output-dir my_custom_path/
```

---

## 10. Summary of Evidence

### ✅ trajectories/G Folder Creation

**Test:** `test_save_trajectory_file` (Line 108-124)  
**Implementation:** `save_trajectory_file()` (Line 115-127)  
**Live Demo:** 14 files created in `trajectories/G/`  
**Status:** VERIFIED ✅

### ✅ Multiple WORLD_ENTITY Strings Appended

**Test:** `test_consolidated_world_entities_file` (Line 182-202)  
**Implementation:** `convert_csv_to_world_entities()` (Line 212-219)  
**Live Demo:** 14 entities in `all_G_WORLD_ENTITIES.txt`  
**Status:** VERIFIED ✅

### ✅ Tab-Delimited Format

**Test:** `test_trajectory_file_tab_delimited` (Line 126-143)  
**Implementation:** `to_csv(filepath, sep='\t', ...)` (Line 125)  
**Live Demo:** Tabs confirmed with `od -c` command  
**Status:** VERIFIED ✅

### ✅ All Requirements Met

- [x] Unique key assignment (starting at 1, incrementing by 1)
- [x] Tab-delimited trajectory files
- [x] FIELDS column empty (not NaN)
- [x] FRAME column = 0.0
- [x] TIME, POS_N, POS_E, POS_D columns from input
- [x] WORLD_ENTITY string generation
- [x] Consolidated file with all entities
- [x] Directory creation (./trajectories/G/)
- [x] File naming convention (G_<key>_.txt)
- [x] Position format ("N, E, D")

---

## Conclusion

**All functionality has been:**
1. ✅ Implemented in code
2. ✅ Tested with 11 comprehensive tests
3. ✅ Demonstrated with real data (14 entities)
4. ✅ Verified with actual output files
5. ✅ Documented with complete evidence

**The World Entity Converter is production-ready and fully functional.**

---

**Date:** February 12, 2026  
**Tests:** 11/11 passing  
**Live Demo:** 14 entities successfully converted  
**Status:** ✅ Complete with full evidence

