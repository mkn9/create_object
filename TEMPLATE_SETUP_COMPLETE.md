# Template Setup Complete

**Date:** February 12, 2026  
**Source Template:** template_aws  
**Target Project:** create_object

---

## ✅ What Was Copied

### Core Files

✅ **main_macbook.py** - MacBook interface for EC2 connection and management  
✅ **cursorrules** - AI assistant rules and development standards  
✅ **requirements.md** - Complete project requirements and governance protocols  
✅ **config.yaml** - EC2 and project configuration (customized for create_object)  
✅ **activate_venv.sh** - Virtual environment activation script  
✅ **README.md** - Project documentation and quick start guide  
✅ **requirements.txt** - Python dependencies  
✅ **pytest.ini** - Testing configuration  
✅ **.gitignore** - Git ignore rules

### Scripts Directory (`scripts/`)

✅ **setup_new_project_ec2.sh** - One-command EC2 Fleet setup with automatic failover  
✅ **manage_ec2_fleet.sh** - Fleet management (start, stop, status, IP)  
✅ **save_chat.py** - Chat history saving utility  
✅ **README.md** - Complete scripts documentation

### Directory Structure

✅ **docs/chat_history/** - Documentation and conversation history  
✅ **tests/** - Unit and integration tests (with example test)  
✅ **results/** - Output files (timestamped)  
✅ **artifacts/tdd/** - TDD evidence capture (RED, GREEN, REFACTOR)  
✅ **artifacts/proof/** - Proof bundles per git commit

### Example Files

✅ **tests/test_example.py** - Comprehensive test examples showing:
- Invariant tests
- Golden tests
- Deterministic tests with fixed seeds
- Edge case testing
- Fixture usage

---

## 📋 Project Structure

```
create_object/
├── main_macbook.py           # MacBook ↔ EC2 interface
├── config.yaml               # EC2 configuration (UPDATE IP!)
├── cursorrules               # Development rules
├── requirements.md           # Complete requirements
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── pytest.ini                # Test configuration
├── activate_venv.sh          # Venv activation
├── .gitignore                # Git ignore rules
│
├── scripts/                  # Automation scripts
│   ├── setup_new_project_ec2.sh    # EC2 Fleet setup
│   ├── manage_ec2_fleet.sh         # Fleet management
│   ├── save_chat.py                # Chat history tool
│   └── README.md                   # Scripts docs
│
├── tests/                    # Tests
│   ├── test_example.py       # Example tests
│   └── .gitkeep
│
├── results/                  # Outputs (YYYYMMDD_HHMM_*.ext)
│   └── .gitkeep
│
├── artifacts/                # Evidence and proofs
│   ├── tdd/                  # TDD evidence
│   │   └── .gitkeep
│   └── proof/                # Proof bundles
│       └── .gitkeep
│
└── docs/                     # Documentation
    └── chat_history/         # Conversation history
        └── INDEX.md
```

---

## 🚀 Next Steps

### 1. Setup EC2 Fleet (Required)

```bash
cd /Users/mike/Dropbox/Code/repos/create_object

# Create EC2 Fleet with automatic spot/on-demand failover
bash scripts/setup_new_project_ec2.sh create-object
```

**What this creates:**
- EC2 Fleet with maintain mode (always 1 instance running)
- Priority 1: Spot instance (~$0.40/hr) - 90% of time
- Priority 2: On-Demand instance (~$1.21/hr) - automatic failback
- Persistent EBS volume (100GB, auto-attached)
- S3 bucket for backups
- Configuration file: `.create-object_ec2_config.txt`

**Time:** ~2 minutes

### 2. Update config.yaml

After EC2 setup, update the configuration file:

```yaml
# config.yaml
ec2:
  instance_id: "<your-instance-id>"
  public_ip: "<your-ec2-ip>"
  ssh_user: "ubuntu"
```

### 3. Test Connection

```bash
# Test EC2 connection
python main_macbook.py --test

# Should show:
# ✅ Connection successful!
```

### 4. Start Daily Workflow

```bash
# Start instance
bash scripts/manage_ec2_fleet.sh create-object start

# Get IP
bash scripts/manage_ec2_fleet.sh create-object ip

# Connect
ssh -i /Users/mike/keys/AutoGenKeyPair.pem ubuntu@<IP>

# On EC2: Setup project
cd ~
git clone <your-repo-url> create_object
cd create_object
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run example tests
pytest tests/test_example.py -v

# When done: Exit and stop
exit
bash scripts/manage_ec2_fleet.sh create-object stop
```

---

## 🎯 Key Features

### EC2-Only Computation
- ✅ All Python execution on EC2
- ✅ MacBook for editing and SSH only
- ✅ Automatic spot/on-demand failover
- ✅ Persistent EBS storage

### Test-Driven Development
- ✅ RED → GREEN → REFACTOR workflow
- ✅ Evidence capture in `artifacts/tdd/`
- ✅ Proof bundles per git commit
- ✅ Deterministic tests with fixed seeds

### Documentation Integrity
- ✅ Verification-first documentation
- ✅ Never claim without evidence
- ✅ Three-state model: CODE WRITTEN → CODE EXECUTED → RESULTS VERIFIED
- ✅ Chat history preservation

### Cost Optimization
- ✅ 55% savings vs pure on-demand
- ✅ Automatic spot rebalancing
- ✅ ~$87/month for 160 hours usage

---

## 📚 Documentation

**Complete Requirements:**
- `requirements.md` - All standards, protocols, and workflows

**Quick Reference:**
- `README.md` - Quick start and common operations
- `scripts/README.md` - Scripts documentation

**Development Rules:**
- `cursorrules` - AI assistant rules and best practices

---

## ⚠️ Important Reminders

### EC2-Only Rule
**NEVER run Python scripts on MacBook!**
- ❌ `python script.py` on MacBook
- ❌ `pip install` on MacBook
- ✅ Always SSH to EC2 first
- ✅ Use `python main_macbook.py` for orchestration

### File Naming
**All output files MUST use timestamp prefix:**
```
YYYYMMDD_HHMM_descriptive_name.ext
```

### TDD Workflow
**Always write tests FIRST:**
1. Write failing tests (RED)
2. Implement minimum code to pass (GREEN)
3. Refactor for quality (REFACTOR)
4. Capture evidence with `bash scripts/tdd_capture.sh`

### Documentation Integrity
**Verify every claim:**
- Show file listings for "file exists" claims
- Show test output for "tests passed" claims
- Show data checks for "N samples" claims

---

## 🛠️ Troubleshooting

### Connection Issues
```bash
# Test connection
python main_macbook.py --test

# Check config.yaml for correct IP and key path
cat config.yaml

# Verify AWS credentials
aws sts get-caller-identity
```

### EC2 Fleet Issues
```bash
# Check fleet status
bash scripts/manage_ec2_fleet.sh create-object status

# View instance IP
bash scripts/manage_ec2_fleet.sh create-object ip

# Check fleet errors
aws ec2 describe-fleet-history --fleet-id <FLEET_ID>
```

### Instance Not Starting
- Wait 2-5 minutes for launch
- Check AWS console for errors
- Verify spot capacity available
- Fleet will automatically fallback to on-demand

### Volume Not Attaching
```bash
# SSH to instance
ssh -i /Users/mike/keys/AutoGenKeyPair.pem ubuntu@<IP>

# Check User Data logs
sudo cat /var/log/user-data.log

# Verify volume status
lsblk
df -h
ls -la /mnt/project-data
```

---

## 📞 Support Resources

**Template Source:** `/Users/mike/Dropbox/Code/repos/template_aws`  
**Template Date:** February 8, 2026  
**Template Version:** 1.0 (EC2 Fleet with automatic failover)

**AWS Resources:**
- EC2 Fleet: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-fleet.html
- EBS Volumes: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-volumes.html
- Spot Instances: https://aws.amazon.com/ec2/spot/

**Testing Resources:**
- pytest: https://docs.pytest.org/
- NumPy testing: https://numpy.org/doc/stable/reference/routines.testing.html

---

## ✅ Checklist

Before starting development:

- [ ] EC2 Fleet setup completed
- [ ] Configuration file updated with EC2 IP
- [ ] Connection test passed
- [ ] Git repository initialized
- [ ] Virtual environment created on EC2
- [ ] Dependencies installed on EC2
- [ ] Example tests run successfully
- [ ] Read `requirements.md` Section 3 (Governance Standards)
- [ ] Read `requirements.md` Section 4 (EC2 Setup)
- [ ] Understand TDD workflow (Section 3.4)

---

## 🎉 Ready to Go!

Your create_object project is now setup with:
- ✅ Complete AWS EC2 infrastructure template
- ✅ TDD workflow with evidence capture
- ✅ Documentation integrity protocols
- ✅ Automated deployment scripts
- ✅ Cost-optimized spot/on-demand failover

**Start with:** `bash scripts/setup_new_project_ec2.sh create-object`

---

**Template Setup Completed:** February 12, 2026  
**Status:** Ready for EC2 Fleet setup and development

