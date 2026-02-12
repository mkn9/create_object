# Scripts Directory

**Project:** template_aws  
**Purpose:** Automation scripts for EC2 Fleet management, testing, and deployment  
**Last Updated:** February 8, 2026

---

## Overview

This directory contains automation scripts for managing AWS EC2 infrastructure with automatic spot/on-demand failover, persistent storage, and project lifecycle management.

**Key Features:**
- One-command EC2 Fleet setup
- Automatic spot → on-demand failover
- Persistent EBS volumes (auto-attach)
- S3 backup integration
- Simple management commands

---

## EC2 Fleet Management Scripts

### 1. `setup_new_project_ec2.sh` - One-Command Setup

**Purpose:** Complete EC2 Fleet setup for new projects with automatic failover and persistent storage.

**Usage:**
```bash
bash scripts/setup_new_project_ec2.sh <project-name>
```

**Example:**
```bash
bash scripts/setup_new_project_ec2.sh my-ml-project
```

**What It Creates:**
1. **Launch Template** - With User Data script for automatic EBS attachment
2. **EC2 Fleet** - With maintain mode (always 1 instance, spot preferred)
3. **Persistent EBS Volume** - 100GB gp3 SSD
4. **S3 Bucket** - For backups and checkpoints
5. **Configuration File** - `.project-name_ec2_config.txt`

**Configuration Details:**
- **Instance Type:** g5.2xlarge (configurable in script)
- **AMI:** Deep Learning AMI Ubuntu 22.04
- **EBS Volume:** 100GB gp3 SSD
- **Mount Point:** `/mnt/project-data` (auto-mounted)
- **Spot/On-Demand:** Automatic failover

**Time:** ~2 minutes

**Output:**
- Creates `.project-name_ec2_config.txt` with all resource IDs
- Displays summary of created resources
- Shows next steps for starting/stopping instance

**Requirements:**
- AWS CLI installed and configured
- IAM permissions for EC2, EBS, S3
- KeyPair: `AutoGenKeyPair` (or modify script)

---

### 2. `manage_ec2_fleet.sh` - Fleet Management

**Purpose:** Start, stop, check status, and get IP of EC2 Fleet instances.

**Usage:**
```bash
bash scripts/manage_ec2_fleet.sh <project-name> <action>
```

**Actions:**
- `start` - Start instance (spot preferred, on-demand fallback)
- `stop` - Stop instance (EBS volume persists)
- `status` - Show fleet status, instance details, EBS status
- `ip` - Get public IP address of running instance

**Examples:**

#### Start Instance:
```bash
bash scripts/manage_ec2_fleet.sh my-ml-project start
```
- Sets fleet target capacity to 1
- Fleet tries spot first (~$0.40/hr)
- Automatically falls back to on-demand (~$1.21/hr) if spot unavailable
- Wait 2-5 minutes for instance to launch
- User Data script automatically attaches and mounts EBS volume

#### Get IP Address:
```bash
bash scripts/manage_ec2_fleet.sh my-ml-project ip
```
Output: `54.123.45.67`

#### Connect to Instance:
```bash
IP=$(bash scripts/manage_ec2_fleet.sh my-ml-project ip)
ssh -i /Users/mike/keys/AutoGenKeyPair.pem ubuntu@$IP
```

Once connected:
```bash
cd /mnt/project-data  # Your persistent data is here!
ls -la                # Check for .volume-attached marker
```

#### Check Status:
```bash
bash scripts/manage_ec2_fleet.sh my-ml-project status
```
Shows:
- Fleet state and capacity
- Instance details (ID, state, type, lifecycle, IP)
- EBS volume status and attachment

#### Stop Instance:
```bash
bash scripts/manage_ec2_fleet.sh my-ml-project stop
```
- Terminates instance
- EBS volume persists (data safe)
- Can restart anytime with `start`

**Requirements:**
- Configuration file `.project-name_ec2_config.txt` (created by setup script)
- AWS CLI installed and configured
- `jq` installed for JSON parsing

---

## Complete Workflow Example

### Initial Setup (One Time):

```bash
# 1. Setup project
bash scripts/setup_new_project_ec2.sh my-ml-project
# Creates all AWS resources, takes ~2 minutes

# Output shows configuration saved to .my-ml-project_ec2_config.txt
```

### Daily Workflow:

```bash
# 1. Start instance
bash scripts/manage_ec2_fleet.sh my-ml-project start
# Wait 2-5 minutes for instance to launch

# 2. Get IP
bash scripts/manage_ec2_fleet.sh my-ml-project ip
# Output: 54.123.45.67

# 3. Connect
ssh -i /Users/mike/keys/AutoGenKeyPair.pem ubuntu@54.123.45.67

# 4. On instance - work with persistent data
cd /mnt/project-data
ls -la  # Your data is here!
# Do your work...

# 5. When done - exit and stop
exit
bash scripts/manage_ec2_fleet.sh my-ml-project stop
```

---

## Automatic Features

### 1. Automatic Spot/On-Demand Failover

**Spot Interruption Scenario:**
1. AWS sends 2-minute interruption notice
2. EC2 Fleet automatically launches replacement
   - Tries spot first
   - Falls back to on-demand if spot unavailable
3. New instance boots (2-3 minutes)
4. User Data script runs automatically:
   - Detects and attaches EBS volume
   - Mounts to `/mnt/project-data`
   - Sets ownership and permissions
5. Reconnect with new IP - data is already there!

**Downtime:** 2-3 minutes (instance launch time)

### 2. Automatic Spot Rebalancing

**When Spot Becomes Available:**
1. Fleet detects spot capacity
2. Fleet automatically launches spot instance
3. Terminates on-demand instance (saves money)
4. User Data script attaches volume to new spot instance
5. Reconnect seamlessly (new IP)

### 3. Automatic EBS Volume Attachment

**User Data Script (runs on every boot):**
- Detects EBS volume by ID
- Detaches from old instance if needed
- Attaches to current instance
- Creates partition if first time
- Creates filesystem if first time
- Mounts to `/mnt/project-data`
- Sets ownership to `ubuntu:ubuntu`
- Adds to `/etc/fstab` for persistence
- Creates marker file `.volume-attached`

**Time:** ~30-60 seconds after instance boot

---

## Cost Analysis

### Monthly Usage (160 hours):

**With EC2 Fleet (Spot + On-Demand):**
- Spot (90%): 144 hrs × $0.40 = $57.60
- On-demand (10%): 16 hrs × $1.21 = $19.36
- EBS storage: 100GB = $10.00
- S3 backups: ~$0.50
- **Total: ~$87/month**

**Pure On-Demand:**
- On-demand: 160 hrs × $1.21 = $193.60
- EBS storage: 100GB = $10.00
- **Total: $204/month**

**Savings: $117/month (57%)**

---

## Configuration File Format

After running `setup_new_project_ec2.sh`, configuration is saved to `.project-name_ec2_config.txt`:

```bash
# EC2 Fleet Configuration for project-name
# Created: 2026-02-08 12:00:00

PROJECT_NAME=project-name
LAUNCH_TEMPLATE=project-name-template
LAUNCH_TEMPLATE_ID=lt-xxxxxxxxxxxxx
FLEET_NAME=project-name-fleet
FLEET_ID=fleet-xxxxxxxxxxxxx
EBS_VOLUME_ID=vol-xxxxxxxxxxxxx
S3_BUCKET=project-name-backups-20260208
REGION=us-east-1
INSTANCE_TYPE=g5.2xlarge
KEY_NAME=AutoGenKeyPair
AVAILABILITY_ZONE=us-east-1a
MOUNT_POINT=/mnt/project-data
```

**Used By:** `manage_ec2_fleet.sh` to identify and control resources

**Location:** Project root directory

**Security:** Don't commit to public repos (contains resource IDs)

---

## Troubleshooting

### Instance Not Starting

**Check Fleet Status:**
```bash
bash scripts/manage_ec2_fleet.sh project-name status
```

**Check Fleet Errors:**
```bash
# Get fleet ID from config file
source .project-name_ec2_config.txt

# Check fleet history
aws ec2 describe-fleet-history \
  --fleet-id $FLEET_ID \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S)
```

**Common Issues:**
- No spot capacity available (will auto-fallback to on-demand)
- Service limits reached (check AWS quotas)
- Invalid AMI ID (update in script)

### Volume Not Attaching

**Check User Data Logs:**
```bash
# SSH to instance
ssh -i /Users/mike/keys/AutoGenKeyPair.pem ubuntu@<IP>

# Check User Data script logs
sudo cat /var/log/user-data.log
```

**Check Volume Status:**
```bash
# On MacBook
bash scripts/manage_ec2_fleet.sh project-name status
# Shows volume state and attachment

# On instance
lsblk                    # Should show /dev/xvdf or /dev/nvme1n1
df -h                    # Should show /mnt/project-data
ls -la /mnt/project-data # Should show .volume-attached marker
```

**Common Issues:**
- Volume attached to different instance (script will detach/reattach)
- Permissions issue (script sets ownership to ubuntu:ubuntu)
- Device naming difference (script handles both /dev/xvdf and /dev/nvme1n1)

### Cannot Get IP

**Check Instance State:**
```bash
bash scripts/manage_ec2_fleet.sh project-name status
```

**Wait for Instance:**
- Instance may still be launching (wait 2-5 minutes)
- Check status for "State: running"
- IP assignment takes ~1-2 minutes after instance starts

### Configuration File Not Found

**Error:** `❌ Configuration file not found: .project-name_ec2_config.txt`

**Solution:**
```bash
# Run setup script first
bash scripts/setup_new_project_ec2.sh project-name
```

### jq Not Installed

**Error:** Command not found: jq

**Solution:**
```bash
# On MacBook
brew install jq

# On Ubuntu/EC2
sudo apt-get update
sudo apt-get install -y jq
```

---

## Requirements

### MacBook Requirements:
- AWS CLI installed and configured
- IAM permissions: EC2, EBS, S3, IAM
- `jq` installed (for JSON parsing)
- SSH key: `/Users/mike/keys/AutoGenKeyPair.pem`

### IAM Permissions Needed:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:CreateLaunchTemplate",
        "ec2:CreateLaunchTemplateVersion",
        "ec2:CreateFleet",
        "ec2:ModifyFleet",
        "ec2:DescribeFleets",
        "ec2:DescribeFleetInstances",
        "ec2:DescribeInstances",
        "ec2:CreateVolume",
        "ec2:AttachVolume",
        "ec2:DetachVolume",
        "ec2:DescribeVolumes",
        "ec2:CreateTags",
        "s3:CreateBucket",
        "s3:ListBucket",
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "*"
    }
  ]
}
```

### Instance Requirements:
- AMI: Deep Learning AMI Ubuntu 22.04 (or compatible)
- Instance profile with S3 permissions (for backups)
- Security group allowing SSH (port 22)

---

## Advanced Usage

### Customize Instance Type

Edit `setup_new_project_ec2.sh`:
```bash
# Change line 9
INSTANCE_TYPE="g5.4xlarge"  # Or any other instance type
```

### Customize EBS Volume Size

Edit `setup_new_project_ec2.sh`:
```bash
# Change line 39
--size 200 \  # Change from 100GB to 200GB
```

### Customize AMI

Edit `setup_new_project_ec2.sh`:
```bash
# Change line 10
AMI_ID="ami-xxxxxxxxx"  # Your custom AMI
```

### Multiple Projects

Each project gets its own resources:
```bash
bash scripts/setup_new_project_ec2.sh project-a
bash scripts/setup_new_project_ec2.sh project-b
bash scripts/setup_new_project_ec2.sh project-c
```

Each has its own:
- Launch template
- EC2 Fleet
- EBS volume
- S3 bucket
- Configuration file

---

## Cleanup/Deletion

To delete a project's resources:

```bash
# Load configuration
source .project-name_ec2_config.txt

# 1. Stop instance (if running)
bash scripts/manage_ec2_fleet.sh project-name stop

# 2. Delete fleet
aws ec2 delete-fleets --fleet-ids $FLEET_ID --terminate-instances

# 3. Delete EBS volume (WARNING: DATA LOSS)
aws ec2 delete-volume --volume-id $EBS_VOLUME_ID

# 4. Delete S3 bucket (WARNING: DATA LOSS)
aws s3 rb s3://$S3_BUCKET --force

# 5. Delete launch template
aws ec2 delete-launch-template --launch-template-id $LAUNCH_TEMPLATE_ID

# 6. Delete configuration file
rm .project-name_ec2_config.txt
```

**⚠️ WARNING:** This permanently deletes all data. Backup first!

---

## S3 Backup Integration

### Backup to S3 (from EC2):
```bash
# Backup checkpoints
aws s3 sync /mnt/project-data/checkpoints s3://$S3_BUCKET/checkpoints

# Backup results
aws s3 sync /mnt/project-data/results s3://$S3_BUCKET/results
```

### Restore from S3:
```bash
# Restore checkpoints
aws s3 sync s3://$S3_BUCKET/checkpoints /mnt/project-data/checkpoints

# Restore results
aws s3 sync s3://$S3_BUCKET/results /mnt/project-data/results
```

---

## Integration with requirements.md

**See:** requirements.md Section 4.5 for complete documentation

**Topics Covered:**
- Overview and architecture
- Quick start guide
- Fleet management commands
- Automatic failover explanation
- Storage configuration
- Troubleshooting
- Cost breakdown

---

## Future Scripts (Planned)

- `s3_backup.sh` - Automated S3 backup
- `s3_restore.sh` - Automated S3 restore
- `prove.sh` - Test verification and proof bundle
- `tdd_capture.sh` - TDD evidence capture

---

## Support

**Documentation:** See requirements.md Section 4.5  
**Issues:** Check troubleshooting section above  
**Questions:** Review requirements.md for complete context

---

**Last Updated:** February 8, 2026  
**Scripts Version:** Option 1 (EC2 Fleet with automatic failover)  
**Source:** liquid_mono_to_3d project

