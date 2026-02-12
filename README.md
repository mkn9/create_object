# Create Object Project

**Last Updated:** February 12, 2026

---

## Overview

This is a Python development project running locally on MacBook with comprehensive TDD, governance standards, and organized workflow.

### Current Features

**Group Scheduler** (Complete ✅)
- CSV-based group timing and scheduling
- Data validation with comprehensive constraints
- Summary statistics and time conversions
- 17 comprehensive unit tests (all passing)
- Full documentation available

### Project Capabilities

- **Local Development**: All Python execution on MacBook
- **Test-Driven Development**: Comprehensive TDD workflow with evidence capture
- **Virtual Environment**: Isolated dependency management
- **Documentation Integrity**: Verification-first documentation standards
- **Component Organization**: Clean separation of concerns

---

## Quick Start

### 1. Setup Virtual Environment

```bash
# Navigate to project
cd /Users/mike/Dropbox/Code/repos/create_object

# Create virtual environment (or use helper script)
source activate_venv.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Group Scheduler

```bash
# Activate virtual environment
source venv/bin/activate

# Run with sample data
python src/main.py data/sample_groups.csv

# Run with time conversion (120 minutes total)
python src/main.py data/sample_groups.csv --total-time 120
```

### 3. Run Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_example.py -v
```

### 3. Development Workflow

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Make code changes
# Edit files as needed

# 3. Run tests (TDD workflow)
pytest

# 4. Execute scripts
python your_script.py

# 5. Check results
ls results/

# 6. Commit changes
git add .
git commit -m "Your commit message"

# 7. Deactivate when done
deactivate
```

---

## Project Structure

```
create_object/
├── README.md                 # This file
├── requirements.md           # Complete project requirements
├── cursorrules               # AI assistant rules
├── requirements.txt          # Python dependencies
├── pytest.ini                # Test configuration
├── .gitignore                # Git ignore rules
├── activate_venv.sh          # Quick venv activation
│
├── scripts/                  # Utility scripts
│   ├── save_chat.py          # Chat history tool
│   └── README.md             # Scripts documentation
│
├── tests/                    # Unit and integration tests
│   ├── test_example.py       # Example tests
│   └── .gitkeep
│
├── results/                  # Output files (timestamped)
│   └── .gitkeep
│
├── artifacts/                # TDD evidence and proof bundles
│   ├── tdd/                  # RED, GREEN, REFACTOR evidence
│   └── proof/                # Proof bundles per git SHA
│
├── docs/                     # Documentation
│   └── chat_history/         # Conversation history
│       └── INDEX.md
│
├── venv/                     # Virtual environment (not in git)
└── src/                      # Source code (create as needed)
```

---

## Development Rules

### Local MacBook Development

**All computation runs locally:**

- ✅ **Python 3.13.1** installed on MacBook
- ✅ **Virtual Environment**: Activate with `source venv/bin/activate`
- ✅ **Package Installation**: `pip install` in activated venv
- ✅ **Testing**: `pytest` runs locally
- ✅ **Execution**: All scripts run on MacBook

### Test-Driven Development (TDD)

**All new functionality requires TDD workflow:**

1. **RED Phase**: Write tests first, confirm they fail
2. **GREEN Phase**: Implement minimum code to pass tests
3. **REFACTOR Phase**: Improve code quality while tests pass

**Evidence Capture:**

```bash
# Run complete TDD cycle with evidence capture
bash scripts/tdd_capture.sh
```

Generates:
- `artifacts/tdd_red.txt` - Failing tests
- `artifacts/tdd_green.txt` - Passing tests
- `artifacts/tdd_refactor.txt` - Refactored tests

### Documentation Integrity

**VERIFY EVERY CLAIM BEFORE DOCUMENTING IT**

- ❌ Don't claim "file exists" without verification
- ❌ Don't claim "tests passed" without showing output
- ❌ Don't claim "N samples generated" without checking data
- ✅ Show evidence for all claims

### File Naming Convention

**All output files MUST use timestamp prefix:**

```
YYYYMMDD_HHMM_descriptive_name.ext
```

Example:
```
results/
├── 20260212_1430_analysis_results.png
├── 20260212_1430_model_accuracy.csv
└── 20260212_1445_final_model.pt
```

---

## Testing

### Run Tests Locally

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_module.py -v

# Run tests by marker
pytest -m unit  # Unit tests only
pytest -m golden  # Golden tests only
```

### Test Markers

Available test markers (see `pytest.ini`):
- `unit` - Unit tests
- `integration` - Integration tests
- `golden` - Golden tests (known expected outputs)
- `invariant` - Invariant tests (properties that must hold)
- `deterministic` - Deterministic tests (fixed random seeds)

### Proof Bundle (Definition of "Done")

A task is complete ONLY if the proof bundle is generated:

```bash
bash scripts/prove.sh
```

- **Exit 0**: Task complete with proof bundle
- **Exit != 0**: Task incomplete

---

## Virtual Environment Management

### Create Virtual Environment

```bash
python3 -m venv venv
```

### Activate Virtual Environment

```bash
# Using activation script
source activate_venv.sh

# Or directly
source venv/bin/activate
```

### Install Dependencies

```bash
# Make sure venv is activated first
source venv/bin/activate

# Install from requirements.txt
pip install -r requirements.txt

# Install specific package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

### Deactivate Virtual Environment

```bash
deactivate
```

---

## Documentation

### Project Documentation
- **README.md**: This file - project overview and quick start
- **requirements.md**: Complete project requirements and standards
- **cursorrules**: AI assistant rules and best practices
- **LOCAL_DEVELOPMENT_SETUP.md**: Comprehensive setup guide

### Feature Documentation
- **docs/GROUP_SCHEDULER.md**: Complete group scheduler documentation
- **data/README.md**: CSV file format and examples

### Additional Documentation
- **scripts/README.md**: Scripts documentation and usage
- **docs/chat_history/**: Development conversation history

---

## Support

**Python Issues:**
1. Check Python version: `python3 --version` (should be 3.13.1)
2. Verify virtual environment: `which python` (should show venv path)
3. Reinstall dependencies: `pip install -r requirements.txt`

**Testing Issues:**
1. Activate virtual environment first
2. Use fixed random seeds for deterministic tests
3. Check pytest configuration in `pytest.ini`

**Import Errors:**
1. Ensure virtual environment is activated
2. Install missing packages: `pip install package-name`
3. Update requirements.txt: `pip freeze > requirements.txt`

---

## Chat History

Save important conversations:

```bash
python scripts/save_chat.py
```

Follow prompts to save with topic, tags, and metadata.

---

## Next Steps

1. **Create Virtual Environment**: `python3 -m venv venv`
2. **Activate Environment**: `source venv/bin/activate`
3. **Install Dependencies**: `pip install -r requirements.txt`
4. **Run Example Tests**: `pytest tests/test_example.py -v`
5. **Start Development**: Write tests first, implement, verify

---

**Project Template Version:** 1.0 (Local MacBook)  
**Based on:** template_aws (adapted for local development)  
**Python Version:** 3.13.1  
**Status:** Ready for local development
