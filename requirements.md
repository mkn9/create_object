# Project Requirements

**Local MacBook Development Project**

**Last Updated:** February 12, 2026

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Functional Requirements](#2-functional-requirements)
3. [Governance & Integrity Standards](#3-governance--integrity-standards)
   - 3.1 [Documentation Integrity Protocol](#31-documentation-integrity-protocol)
   - 3.2 [Proof Bundle System - Definition of "Done"](#32-proof-bundle-system---definition-of-done)
   - 3.3 [Scientific Integrity Protocol](#33-scientific-integrity-protocol)
   - 3.4 [Testing Standards (TDD)](#34-testing-standards-tdd)
   - 3.5 [Chat History Protocol](#35-chat-history-protocol)
4. [Development Environment & Setup](#4-development-environment--setup)
   - 4.1 [EC2 Computation Rule](#41-ec2-computation-rule-mandatory)
   - 4.2 [EC2 Connection](#42-ec2-connection)
   - 4.3 [Development Workflow](#43-development-workflow)
   - 4.4 [Package Installation](#44-package-installation)
   - 4.5 [EC2 Fleet Setup for New Projects](#45-ec2-fleet-setup-for-new-projects-spot--on-demand-failover)
5. [Technical Requirements](#5-technical-requirements)
   - 5.5 [Project Organization Requirements](#55-project-organization-requirements-mandatory)
6. [Testing Implementation Guide](#6-testing-implementation-guide)

---

## 1. Project Overview

This is a local MacBook development project with comprehensive TDD, governance standards, and parallel development support.

### Key Capabilities
- Enforced Test-Driven Development (TDD)
- Proof-bundle system as primary gate for "done"
- Documentation integrity protocols
- Git tree management for parallel development
- Component-based project organization
- Automated evidence capture

### System Architecture
- **Local Development**: All computation on MacBook using virtual environment
- **Git Tree**: Parallel branches for multiple workers/components
- **TDD Workflow**: RED → GREEN → REFACTOR with evidence
- **Proof Bundle**: Verification tied to git commits
- **Component Isolation**: Separate directories per major component

---

## 2. Functional Requirements

### 2.1 Development Workflow
- Local MacBook development with virtual environment
- All Python execution, testing, and package installation on MacBook
- Git tree management for parallel development
- Results stored locally in project directories

### 2.2 Testing Requirements
- All tests must be deterministic (fixed seeds, explicit tolerances)
- TDD evidence captured for RED, GREEN, REFACTOR phases
- Proof bundle generated for task completion verification
- Component tests isolated per directory

### 2.3 Result Management
- All results use timestamp naming: `YYYYMMDD_HHMM_descriptive.ext`
- Results separated per component
- Results stored locally in component directories
- Optional cloud backup capability for data persistence

---

## 3. Governance & Integrity Standards

### 3.1 Documentation Integrity Protocol

#### Core Principle
> **VERIFY EVERY CLAIM BEFORE DOCUMENTING IT**

If you cannot verify a claim with concrete evidence, do not present it as fact.

#### Mandatory Verification Steps

**1. File Existence Claims**

BEFORE writing: "File X exists" or "Visualization Y was generated"

REQUIRED VERIFICATION:
```bash
# Check file exists
ls path/to/file.png
# OR
find . -name "file.png" -type f
# OR use read_file tool
```

Show in documentation:
```markdown
**Verification:**
```bash
$ ls component_a/results/
20260208_1430_model_accuracy.png  5.5K
```
File confirmed to exist.
```

**NEVER claim files exist without this verification.**

**2. Data Count Claims**

BEFORE writing: "N samples generated" or "Dataset contains X items"

REQUIRED VERIFICATION:
```python
import numpy as np
data = np.load('dataset.npz')
print(f"Actual count: {len(data['key'])}")
print(f"Actual shape: {data['key'].shape}")
```

**NEVER claim sample counts without loading and checking the data.**

**3. Success/Completion Claims**

BEFORE writing: "100% success" or "All tests passed"

REQUIRED VERIFICATION:
```bash
# Run and show actual output
python -m pytest -v
# OR
bash scripts/prove.sh
```

**NEVER claim success without showing actual results.**

#### Language Standards

**✅ ACCEPTABLE Language (Verified Work)**

When work HAS been completed and verified:
- "Verification confirms N samples exist" + [show evidence]
- "File listing shows output.png was created" + [show ls output]
- "Test execution demonstrates 36/36 tests passed" + [show test output]

**✅ ACCEPTABLE Language (Unverified/Planned Work)**

When work has NOT been completed or cannot be verified:
- "Code has been written to generate N samples"
- "Designed to produce visualizations"
- "Intended to create the following outputs"
- "**NOT YET EXECUTED**"
- "**PLAN:** Will generate..."

**❌ PROHIBITED Language (Integrity Violations)**

NEVER use these without verification:
- "Successfully generated N samples" ← requires verification
- "Results show..." ← must show actual results
- "File X contains..." ← must verify file exists
- "100% success rate" ← must measure and prove
- "All tests passed" ← must show test output

#### The Three-State Model

ALL work falls into one of three states. Be explicit about which state:

**State 1: CODE WRITTEN**
- Code files exist in repository
- Functions/classes are implemented
- Tests are written
- **Documentation:** "Code has been written to..."

**State 2: CODE EXECUTED**
- Code has been run
- Output files were generated
- Logs/results are available
- **Documentation:** "Execution produced..." + [show evidence]

**State 3: RESULTS VERIFIED**
- Output files confirmed to exist
- Data counts validated
- Metrics measured and documented
- **Documentation:** "Verification confirms..." + [show proof]

**NEVER conflate State 1 with State 2 or 3.**

---

### 3.2 Proof Bundle System - Definition of "Done"

**PRIMARY GATE: A task is complete ONLY if `bash scripts/prove.sh` exits 0.**

#### Core Principle

One command defines "done" for any task:

```bash
bash scripts/prove.sh
```

- **Exit 0** → Task complete with proof bundle
- **Exit != 0** → Task incomplete

No exceptions. No partial credit. No "mostly done".

#### What prove.sh Does

1. Captures environment (git SHA, timestamp, python version)
2. Runs all tests (`pytest -q`)
3. Optionally runs component contracts (`contracts/*.yaml`)
4. Creates file manifest with checksums
5. Saves everything to `artifacts/proof/<git_sha>/`

#### Proof Bundle Structure

```
artifacts/proof/<git_sha>/
├── prove.log       # Full test output
├── meta.txt        # Git commit, timestamp, environment
├── manifest.txt    # File checksums (tamper-evident)
├── pip_freeze.txt  # Python dependencies
└── contracts.log   # Optional contract results
```

**Key Feature:** Everything tied to a specific git commit. No ambiguity.

#### Rules

**Rule 1:** Cannot claim "done" without proof bundle  
**Rule 2:** Tests must be deterministic (fixed seeds, explicit tolerances)  
**Rule 3:** Commit proof bundles (don't .gitignore them)  
**Rule 4:** If cannot run prove.sh, state: "NOT VERIFIED. Run: bash scripts/prove.sh"

---

### 3.3 Scientific Integrity Protocol

#### Purpose
Prevent synthetic/fake data from being presented as real experimental results.

#### Data Source Verification

**BEFORE** creating any visualization or analysis, MUST verify:

- [ ] **Data Origin**: Is this from actual trained networks or real experiments?
- [ ] **Training Evidence**: Are there training logs, model weights, convergence curves?
- [ ] **Ground Truth**: Physical measurements or neural network outputs?

#### Synthetic Data Identification

If data is synthetic or simulated, it MUST be:

- [ ] **Clearly Labeled**: All plots, filenames, descriptions include "SYNTHETIC" or "SIMULATED"
- [ ] **Purpose Stated**: Why is synthetic data used (testing, demonstration, validation)?
- [ ] **Limitations Noted**: How does it differ from real data?

#### Prohibited Actions

STRICTLY FORBIDDEN:
- ❌ Creating synthetic data and presenting it as real
- ❌ Using placeholder data without clear labeling
- ❌ Generating fake neural network outputs
- ❌ Mixing synthetic and real data without distinction

---

### 3.4 Testing Standards (TDD)

#### Evidence-or-Abstain Requirement

**MANDATORY: All TDD claims must include captured evidence.**

##### Core Principle

> **NEVER claim tests were run without captured evidence.**

If you cannot provide evidence, you must explicitly state: "Tests not run; here is command to run."

##### Evidence Capture Tools

**Tool 1: Full TDD Workflow** (Recommended for new features)

```bash
# Run complete RED → GREEN → REFACTOR cycle with automatic evidence capture
bash scripts/tdd_capture.sh
```

This script:
- Runs tests before implementation (RED phase)
- Validates tests actually fail (prevents fake TDD)
- Saves `artifacts/tdd_red.txt`
- Runs tests after implementation (GREEN phase)
- Saves `artifacts/tdd_green.txt`
- Runs tests after refactoring (REFACTOR phase)
- Saves `artifacts/tdd_refactor.txt`

#### The Red → Green → Refactor Cycle

**This is mandatory for all new functionality.**

##### RED Phase: Tests First

**Step 1: Write Tests FIRST**

Write two types of tests:

**a) Invariant Tests** (properties that MUST always hold):

```python
def test_function_produces_finite_values():
    """Function must never produce NaN or Inf values."""
    result = my_function(input_data)
    assert np.all(np.isfinite(result)), "Result contains NaN/Inf"
```

**b) Golden Tests** (canonical scenario with known output):

```python
def test_function_golden_case():
    """Test function with canonical scenario.
    
    Scenario: Standard input case
    Expected: Known correct output
    Seed: 42 (deterministic)
    Tolerance: atol=0.01, rtol=1e-5
    """
    np.random.seed(42)
    result = my_function(test_input)
    np.testing.assert_allclose(result, expected, atol=0.01, rtol=1e-5)
```

**Step 2: Run Tests and Confirm Failure**

```bash
bash scripts/tdd_capture.sh
```

Expected: RED phase with failures.

##### GREEN Phase: Minimum Implementation

Now implement the minimum code to pass tests.

##### REFACTOR Phase: Improve Code Quality

Only after tests pass, refactor for clarity/performance.

#### Deterministic Testing Requirements

**✅ CORRECT: Explicit Generator with seed**
```python
def generate_data(rng=None):
    if rng is None:
        rng = np.random.default_rng(42)
    return rng.standard_normal(size=(100, 3))

def test_generation_deterministic():
    """Test generation is deterministic with fixed seed.
    
    Seed: 42
    """
    rng = np.random.default_rng(42)
    data = generate_data(rng)
    expected_first = np.array([0.49671415, -0.1382643, 0.64768854])
    np.testing.assert_allclose(data[0], expected_first, rtol=1e-10)
```

---

### 3.5 Chat History Protocol

#### Core Principle

> **PRESERVE ALL DEVELOPMENT CONVERSATIONS AS PROJECT DOCUMENTATION**

Chat history is a critical part of project documentation, providing context for technical decisions, problem-solving approaches, and implementation rationale.

#### Mandatory Requirements

**1. Complete Preservation**
- ❌ **NEVER** delete chat history
- ❌ **NEVER** clean up or archive conversations
- ✅ Keep complete historical record
- ✅ All history committed to version control

**2. Standard Workflow**

```bash
# Use save_chat.py script
python3 scripts/save_chat.py
```

Follow prompts to save conversation with topic, tags, and metadata.

---

## 4. Development Environment & Setup

### 4.1 Local MacBook Development (STANDARD WORKFLOW)

**All computation is performed locally on MacBook:**

- **Python Version**: Python 3.13.1
- **Virtual Environment**: Use venv for dependency isolation
- **Package Management**: pip install in virtual environment
- **Testing**: Run pytest locally
- **Development**: Code, test, and execute all on MacBook

### 4.2 Virtual Environment Setup

```bash
# Navigate to project
cd /Users/mike/Dropbox/Code/repos/create_object

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4.3 Development Workflow

1. **Activate venv**: `source venv/bin/activate`
2. **Edit files**: Make code changes
3. **Run tests**: `pytest` or `pytest tests/`
4. **Execute code**: `python script.py`
5. **Check results**: Review outputs in `results/`
6. **Commit changes**: `git add` and `git commit`
7. **Deactivate venv**: `deactivate` (when done)

### 4.4 Package Installation

**Local package installation:**
```bash
# Activate virtual environment first
source venv/bin/activate

# Install from requirements.txt
pip install -r requirements.txt

# Install individual packages
pip install package-name

# Freeze dependencies
pip freeze > requirements.txt
```

### 4.5 Optional: Remote Execution Setup

If you need to run on remote instances in the future, see the original template_aws project for EC2 Fleet setup instructions.

### 4.6 Jupyter Notebook Setup (Optional)

**Note:** This project is configured for local MacBook development. Remote execution setup is not required.

---

## 5. Technical Requirements

### 5.1 Performance Requirements

- **Frame Rate**: Target 30 FPS for live processing
- **Latency**: <100ms end-to-end processing delay
- **Memory Usage**: <2GB RAM for standard operation

### 5.2 Dependencies

#### Core Dependencies
- Python 3.8+
- OpenCV >= 4.5.0
- NumPy >= 1.20.0
- Pandas >= 1.3.0
- Matplotlib >= 3.4.0
- PyYAML >= 6.0

#### Testing Framework
- pytest >= 7.0.0
- pytest-cov >= 4.0.0

#### ML Framework (EC2 ONLY)
- PyTorch >= 2.0.0 (if needed)

### 5.3 Output File Naming Convention

**MANDATORY:** All output files in any `results/` directory must have a datetime prefix.

**Format:** `YYYYMMDD_HHMM_descriptive_name.ext`

**Example:**
```
component_a/results/
├── 20260208_1430_model_accuracy.png
├── 20260208_1430_training_loss.csv
└── 20260208_1445_final_model.pt
```

Python helper:
```python
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
filename = f"{timestamp}_descriptive_name.png"
```

### 5.4 pytest Configuration

Create `pytest.ini`:

```ini
[pytest]
addopts = -q --strict-markers --tb=short
testpaths = tests
markers =
    unit: Unit tests
    integration: Integration tests
    golden: Golden tests
    invariant: Invariant tests
    deterministic: Deterministic tests
```

---

## 5.5 Project Organization Requirements (MANDATORY)

### Core Principle

> **ALL distinct project components MUST be developed in separate directories with their own code and results folders.**

This is **non-negotiable** for:
- Code organization and maintainability
- Parallel development support
- Clear responsibility boundaries
- Result isolation and tracking
- Easy cleanup and archival

### 5.5.1 Component Isolation (MANDATORY)

**REQUIRED:** Each major component, worker, experiment, or module MUST have its own directory.

**Minimum Required Structure:**

```
component_name/
├── README.md               # REQUIRED: Component documentation
├── requirements.txt        # REQUIRED: Component dependencies
├── src/                    # Source code
│   └── *.py
├── tests/                  # REQUIRED: Component tests
│   └── test_*.py
└── results/                # REQUIRED: Component outputs (timestamped)
    └── .gitkeep
```

**Example Project Structure:**

```
project_root/
├── worker1_extraction/
│   ├── README.md
│   ├── requirements.txt
│   ├── src/
│   ├── tests/
│   └── results/           # Worker 1 outputs ONLY
│
├── worker2_training/
│   ├── README.md
│   ├── requirements.txt
│   ├── src/
│   ├── tests/
│   └── results/           # Worker 2 outputs ONLY
│
├── worker3_evaluation/
│   ├── README.md
│   ├── requirements.txt
│   ├── src/
│   ├── tests/
│   └── results/           # Worker 3 outputs ONLY
│
└── shared/                # Shared utilities (3+ components)
    └── utils/
```

### 5.5.2 Results Separation (MANDATORY)

**PROHIBITED:**
- ❌ Mixing results from different components in single directory
- ❌ Component A writing to Component B's results folder
- ❌ Shared results directory without clear component prefixes

**REQUIRED:**
- ✅ Each component has its OWN `results/` directory
- ✅ All results use timestamp naming (YYYYMMDD_HHMM)
- ✅ Results stay within component boundaries

### 5.5.3 Code Separation (MANDATORY)

Each component MUST have its own source code directory with clear boundaries.

**Structure Options:**

**Option A: Flat Structure (Small Components)**
```
component_a/
├── module1.py
├── module2.py
├── tests/
└── results/
```

**Option B: src/ Structure (Medium Components)**
```
component_a/
├── src/
│   ├── __init__.py
│   ├── module1.py
│   └── module2.py
├── tests/
└── results/
```

**Option C: Package Structure (Large Components)**
```
component_a/
├── src/
│   └── component_a/
│       ├── __init__.py
│       ├── core/
│       ├── utils/
│       └── models/
├── tests/
└── results/
```

### 5.5.4 Test Separation (MANDATORY)

Each component MUST have its own `tests/` directory.

**Benefits:**
- Component tests run independently
- Clear test ownership
- Easier CI/CD pipeline configuration
- Isolated test failures

### 5.5.5 Naming Conventions

**Directory Names:** `lowercase_with_underscores` or `kebab-case`

**Good Examples:**
- `worker1_feature_extraction/`
- `worker2_model_training/`
- `experiment_baseline/`

**Bad Examples:**
- ❌ `Worker1/` (capitalized)
- ❌ `Feature Extraction/` (spaces)
- ❌ `w1/` (unclear abbreviation)

### 5.5.6 Shared Code Requirements

**Use `shared/` for:**
- ✅ Utilities used by 3+ components
- ✅ Common data structures
- ✅ Shared configuration schemas

**Do NOT use `shared/` for:**
- ❌ Component-specific logic
- ❌ Code used by only 1-2 components
- ❌ Experimental/unstable code

**Shared Directory Structure:**

```
shared/
├── utils/
│   ├── __init__.py
│   ├── file_utils.py
│   ├── data_utils.py
│   └── viz_utils.py
├── config/
│   └── base_config.yaml
├── tests/
│   └── test_utils.py
└── README.md              # Documents what's shared and why
```

### 5.5.7 Git Branch Organization

**When developing components in parallel, use separate branches:**

```bash
# Component A development
git checkout -b component-a-implementation
# Work in component_a/ directory only

# Component B development  
git checkout -b component-b-implementation
# Work in component_b/ directory only
```

**Configure in config.yaml:**

```yaml
tasks:
  component_a_development:
    branch: "component-a-implementation"
    script: "component_a/src/main.py"
    output_dir: "component_a/results"
    description: "Develop Component A"
    
  component_b_development:
    branch: "component-b-implementation"
    script: "component_b/src/main.py"
    output_dir: "component_b/results"
    description: "Develop Component B"
```

### 5.5.8 Component README.md Template

**Every component MUST have README.md with:**

```markdown
# Component Name

## Purpose
Brief description of what this component does.

## Dependencies
See requirements.txt

## Usage
```bash
python src/main.py --config config.yaml
```

## Input
- What data/inputs does this component expect?

## Output
- What outputs does this component produce?
- Where are outputs written?

## Testing
```bash
pytest tests/ -v
```

## Results
- Description of results directory contents
- Cleanup policy

## Integration
- How does this integrate with other components?
```

### 5.5.9 Verification Checklist

**Before committing new component:**

- [ ] Component has its own directory
- [ ] Component has `README.md`
- [ ] Component has `requirements.txt`
- [ ] Component has `tests/` directory
- [ ] Component has `results/` directory
- [ ] Results use timestamp naming (YYYYMMDD_HHMM)
- [ ] Tests pass: `pytest component_name/tests/ -v`
- [ ] No results in other component directories
- [ ] Documentation explains purpose and usage

**Verification Commands:**

```bash
# Check each component has required structure
for dir in component_* worker_*; do
    echo "Checking $dir"
    [ -f "$dir/README.md" ] || echo "  ❌ Missing README.md"
    [ -f "$dir/requirements.txt" ] || echo "  ❌ Missing requirements.txt"
    [ -d "$dir/tests" ] || echo "  ❌ Missing tests/"
    [ -d "$dir/results" ] || echo "  ❌ Missing results/"
done

# Check results use timestamp naming
find */results/ -type f ! -name "YYYYMMDD_HHMM_*" ! -name ".gitkeep"
# Expected: Empty (all files follow convention)
```

### 5.5.10 Anti-Patterns to Avoid

**❌ Anti-Pattern 1: Monolithic Directory**
```
project_root/
├── all_code.py           # Everything in one place
├── all_tests.py
└── results/              # All results mixed together
```

**❌ Anti-Pattern 2: Code Without Tests**
```
component_a/
├── src/                  # Has code
└── results/              # Has results
# ❌ No tests/ directory
```

**❌ Anti-Pattern 3: Shared Results Directory**
```
project_root/
├── component_a/src/
├── component_b/src/
└── results/              # ❌ All components write here
```

### 5.5.11 Benefits of This Organization

1. **Parallel Development** - Multiple developers work independently
2. **Isolated Testing** - Component tests run separately
3. **Clear Responsibility** - Each directory has clear owner
4. **Easy Cleanup** - Archive/delete per component
5. **Scalability** - Add components without restructuring
6. **CI/CD Integration** - Test/deploy components separately

---

## 6. Testing Implementation Guide

### 6.1 Test Organization

```
project_root/
├── tests/                       # Integration tests (cross-component)
│   ├── __init__.py
│   ├── conftest.py             # Shared fixtures
│   └── test_integration.py
│
├── component_a/
│   └── tests/                  # Component A tests
│       ├── test_module1.py
│       └── test_module2.py
│
└── component_b/
    └── tests/                  # Component B tests
        └── test_module1.py
```

### 6.2 Test Execution Commands

```bash
# Run all tests
pytest

# Run specific component tests
pytest component_a/tests/ -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run tests with specific marker
pytest -m golden
```

### 6.3 Shared Fixtures

Create `tests/conftest.py` for shared fixtures:

```python
import pytest
import numpy as np

@pytest.fixture
def rng():
    """Provide deterministic RNG for tests."""
    return np.random.default_rng(42)
```

### 6.4 Coverage Requirements

- **Critical Functions**: 100% coverage
- **Utility Functions**: 90% coverage
- **Visualization Functions**: 80% coverage
- **Error Handling**: 100% coverage

---

## References

- **PEP 8 Style Guide**: https://pep8.org/
- **NumPy Testing**: https://numpy.org/doc/stable/reference/routines.testing.html
- **pytest Documentation**: https://docs.pytest.org/
- **PyTorch Documentation**: https://pytorch.org/docs/stable/index.html

---

**This document is the single source of truth for all project requirements and standards.**

**Version:** 1.0  
**Date:** February 8, 2026  
**Status:** Complete with Project Organization Requirements
