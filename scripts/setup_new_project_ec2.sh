#!/bin/bash
# Complete EC2 setup for new project with spot + on-demand failover (EC2 Fleet)
# Usage: bash scripts/setup_new_project_ec2.sh <project-name>

set -e

# Configuration
PROJECT_NAME="${1:-new-project}"
INSTANCE_TYPE="g5.2xlarge"
AMI_ID="ami-0c02fb55b34f5b9f0"  # Deep Learning AMI Ubuntu 22.04
KEY_NAME="AutoGenKeyPair"
REGION="us-east-1"

if [ -z "$1" ]; then
  echo "Usage: $0 <project-name>"
  echo "Example: $0 my-new-project"
  exit 1
fi

echo "=========================================="
echo "Setting up EC2 Fleet for: $PROJECT_NAME"
echo "=========================================="

# Get VPC and subnet
VPC_ID=$(aws ec2 describe-vpcs --query 'Vpcs[0].VpcId' --output text)
SUBNET_ID=$(aws ec2 describe-subnets --query 'Subnets[0].SubnetId' --output text)
SECURITY_GROUP_ID=$(aws ec2 describe-security-groups --query 'SecurityGroups[0].GroupId' --output text)
AZ=$(aws ec2 describe-subnets --subnet-ids "$SUBNET_ID" --query 'Subnets[0].AvailabilityZone' --output text)

echo "✅ Using VPC: $VPC_ID"
echo "✅ Using Subnet: $SUBNET_ID"
echo "✅ Using Security Group: $SECURITY_GROUP_ID"
echo "✅ Using Availability Zone: $AZ"

# Step 1: Create Persistent EBS Volume (do this first so we can reference it in User Data)
echo ""
echo "Step 1: Creating Persistent EBS Volume..."
VOLUME_ID=$(aws ec2 create-volume \
  --volume-type gp3 \
  --size 100 \
  --availability-zone "$AZ" \
  --tag-specifications "ResourceType=volume,Tags=[{Key=Name,Value=${PROJECT_NAME}-persistent},{Key=Project,Value=${PROJECT_NAME}}]" \
  --query 'VolumeId' \
  --output text)

echo "✅ EBS Volume created: $VOLUME_ID"

# Step 2: Create User Data script for automatic volume attachment
echo ""
echo "Step 2: Creating User Data script for automatic volume attachment..."

USER_DATA_SCRIPT=$(cat <<EOF
#!/bin/bash
# Auto-attach and mount persistent EBS volume
# This script runs automatically when instance starts

set -e

PROJECT_NAME="${PROJECT_NAME}"
VOLUME_ID="${VOLUME_ID}"
MOUNT_POINT="/mnt/project-data"

# Log everything
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "=========================================="
echo "User Data Script: Auto-attaching EBS Volume"
echo "Project: \$PROJECT_NAME"
echo "Volume ID: \$VOLUME_ID"
echo "Time: \$(date)"
echo "=========================================="

# Wait for instance to be fully ready
echo "Waiting for instance to be ready..."
sleep 10

# Install AWS CLI if not present
if ! command -v aws &> /dev/null; then
    echo "Installing AWS CLI..."
    apt-get update -qq
    apt-get install -y -qq awscli
fi

# Get instance ID and region
INSTANCE_ID=\$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
REGION=\$(curl -s http://169.254.169.254/latest/meta-data/placement/region)

echo "Instance ID: \$INSTANCE_ID"
echo "Region: \$REGION"

# Check if volume is already attached
ATTACHED_INSTANCE=\$(aws ec2 describe-volumes \
  --region \$REGION \
  --volume-ids \$VOLUME_ID \
  --query 'Volumes[0].Attachments[0].InstanceId' \
  --output text 2>/dev/null || echo "None")

if [ "\$ATTACHED_INSTANCE" == "\$INSTANCE_ID" ]; then
  echo "✅ Volume already attached to this instance"
else
  # Detach volume if attached to another instance
  if [ "\$ATTACHED_INSTANCE" != "None" ] && [ -n "\$ATTACHED_INSTANCE" ]; then
    echo "⚠️  Volume attached to different instance: \$ATTACHED_INSTANCE"
    echo "   Detaching..."
    aws ec2 detach-volume --region \$REGION --volume-id \$VOLUME_ID --force || true
    echo "   Waiting for detachment..."
    sleep 10
  fi

  # Attach volume to this instance
  echo "Attaching volume \$VOLUME_ID to instance \$INSTANCE_ID..."
  aws ec2 attach-volume \
    --region \$REGION \
    --volume-id \$VOLUME_ID \
    --instance-id \$INSTANCE_ID \
    --device /dev/sdf

  echo "Waiting for volume to attach..."
  sleep 5
  
  # Wait for volume to be available
  for i in {1..30}; do
    if [ -b /dev/xvdf ] || [ -b /dev/nvme1n1 ]; then
      break
    fi
    sleep 2
  done
fi

# Find the device (could be /dev/xvdf or /dev/nvme1n1)
if [ -b /dev/nvme1n1 ]; then
  DEVICE="/dev/nvme1n1"
  PARTITION="/dev/nvme1n1p1"
elif [ -b /dev/xvdf ]; then
  DEVICE="/dev/xvdf"
  PARTITION="/dev/xvdf1"
else
  echo "❌ ERROR: Could not find attached volume device"
  exit 1
fi

echo "Found device: \$DEVICE"

# Check if partition exists, if not create it
if [ ! -b "\$PARTITION" ]; then
  echo "Creating partition on \$DEVICE..."
  parted -s \$DEVICE mklabel gpt
  parted -s \$DEVICE mkpart primary ext4 0% 100%
  sleep 2
fi

# Check if filesystem exists, if not create it
if ! blkid \$PARTITION &> /dev/null; then
  echo "Creating ext4 filesystem on \$PARTITION..."
  mkfs.ext4 -F \$PARTITION
fi

# Create mount point
mkdir -p \$MOUNT_POINT

# Mount the volume
echo "Mounting \$PARTITION to \$MOUNT_POINT..."
mount \$PARTITION \$MOUNT_POINT

# Set ownership
chown -R ubuntu:ubuntu \$MOUNT_POINT

# Add to fstab for persistence across reboots
if ! grep -q "\$PARTITION" /etc/fstab; then
  echo "\$PARTITION \$MOUNT_POINT ext4 defaults,nofail 0 2" >> /etc/fstab
fi

echo "=========================================="
echo "✅ Volume attached and mounted successfully!"
echo "Mount point: \$MOUNT_POINT"
echo "Time: \$(date)"
echo "=========================================="

# Create a marker file to indicate setup is complete
touch \$MOUNT_POINT/.volume-attached
echo "Volume setup complete at \$(date)" > \$MOUNT_POINT/.volume-attached
EOF
)

# Base64 encode User Data
USER_DATA_B64=$(echo "$USER_DATA_SCRIPT" | base64)

# Step 3: Create Launch Template with User Data
echo ""
echo "Step 3: Creating Launch Template..."
TEMPLATE_NAME="${PROJECT_NAME}-template"

# Check if template already exists
if aws ec2 describe-launch-templates --launch-template-names "$TEMPLATE_NAME" &>/dev/null; then
  echo "⚠️  Launch template $TEMPLATE_NAME already exists. Creating new version..."
  aws ec2 create-launch-template-version \
    --launch-template-name "$TEMPLATE_NAME" \
    --version-description "Spot + On-Demand with auto-attach EBS" \
    --launch-template-data "{
      \"ImageId\": \"$AMI_ID\",
      \"InstanceType\": \"$INSTANCE_TYPE\",
      \"KeyName\": \"$KEY_NAME\",
      \"SecurityGroupIds\": [\"$SECURITY_GROUP_ID\"],
      \"UserData\": \"$USER_DATA_B64\",
      \"BlockDeviceMappings\": [{
        \"DeviceName\": \"/dev/sda1\",
        \"Ebs\": {
          \"VolumeSize\": 100,
          \"VolumeType\": \"gp3\",
          \"DeleteOnTermination\": false
        }
      }],
      \"TagSpecifications\": [{
        \"ResourceType\": \"instance\",
        \"Tags\": [
          {\"Key\": \"Name\", \"Value\": \"${PROJECT_NAME}-instance\"},
          {\"Key\": \"Project\", \"Value\": \"$PROJECT_NAME\"}
        ]
      }]
    }" > /dev/null
  echo "✅ Launch Template version created: $TEMPLATE_NAME"
else
  aws ec2 create-launch-template \
    --launch-template-name "$TEMPLATE_NAME" \
    --version-description "Spot + On-Demand with auto-attach EBS" \
    --launch-template-data "{
      \"ImageId\": \"$AMI_ID\",
      \"InstanceType\": \"$INSTANCE_TYPE\",
      \"KeyName\": \"$KEY_NAME\",
      \"SecurityGroupIds\": [\"$SECURITY_GROUP_ID\"],
      \"UserData\": \"$USER_DATA_B64\",
      \"BlockDeviceMappings\": [{
        \"DeviceName\": \"/dev/sda1\",
        \"Ebs\": {
          \"VolumeSize\": 100,
          \"VolumeType\": \"gp3\",
          \"DeleteOnTermination\": false
        }
      }],
      \"TagSpecifications\": [{
        \"ResourceType\": \"instance\",
        \"Tags\": [
          {\"Key\": \"Name\", \"Value\": \"${PROJECT_NAME}-instance\"},
          {\"Key\": \"Project\", \"Value\": \"$PROJECT_NAME\"}
        ]
      }]
    }" > /dev/null

  echo "✅ Launch Template created: $TEMPLATE_NAME"
fi

# Get latest template version
TEMPLATE_ID=$(aws ec2 describe-launch-templates \
  --launch-template-names "$TEMPLATE_NAME" \
  --query 'LaunchTemplates[0].LaunchTemplateId' \
  --output text)

# Step 4: Create EC2 Fleet with Maintain Mode
echo ""
echo "Step 4: Creating EC2 Fleet with automatic failover..."
FLEET_NAME="${PROJECT_NAME}-fleet"

# Check if fleet already exists
if aws ec2 describe-fleets --fleet-ids "$FLEET_NAME" &>/dev/null 2>&1; then
  echo "⚠️  Fleet $FLEET_NAME already exists. Skipping..."
else
  # Create fleet with maintain mode
  FLEET_ID=$(aws ec2 create-fleet \
    --fleet-type maintain \
    --launch-template-configs "[{
      \"LaunchTemplateSpecification\": {
        \"LaunchTemplateId\": \"$TEMPLATE_ID\",
        \"Version\": \"\$Latest\"
      },
      \"Overrides\": [{
        \"InstanceType\": \"$INSTANCE_TYPE\",
        \"SubnetId\": \"$SUBNET_ID\",
        \"AvailabilityZone\": \"$AZ\"
      }]
    }]" \
    --target-capacity-specification "{
      \"TotalTargetCapacity\": 0,
      \"OnDemandTargetCapacity\": 0,
      \"SpotTargetCapacity\": 0,
      \"DefaultTargetCapacityType\": \"spot\"
    }" \
    --on-demand-options '{
      "AllocationStrategy": "lowest-price"
    }' \
    --spot-options '{
      "AllocationStrategy": "price-capacity-optimized",
      "InstanceInterruptionBehavior": "terminate",
      "InstancePoolsToUseCount": 2,
      "MaxTotalPrice": "0.50"
    }' \
    --replace-unhealthy-instances \
    --tag-specifications "ResourceType=fleet,Tags=[{Key=Name,Value=${PROJECT_NAME}-fleet},{Key=Project,Value=${PROJECT_NAME}}]" \
    --query 'FleetId' \
    --output text)

  echo "✅ EC2 Fleet created: $FLEET_ID"
fi

# Step 5: Create S3 Bucket for Backups
echo ""
echo "Step 5: Creating S3 Bucket for Backups..."
BUCKET_NAME="${PROJECT_NAME}-backups-$(date +%Y%m%d)"

if aws s3 ls "s3://$BUCKET_NAME" &>/dev/null 2>&1; then
  echo "⚠️  S3 Bucket $BUCKET_NAME already exists. Skipping..."
else
  aws s3 mb "s3://$BUCKET_NAME" --region "$REGION" 2>/dev/null || echo "Bucket may already exist"
  echo "✅ S3 Bucket created: $BUCKET_NAME"
fi

# Save configuration to file
CONFIG_FILE=".${PROJECT_NAME}_ec2_config.txt"
cat > "$CONFIG_FILE" << EOF
# EC2 Fleet Configuration for $PROJECT_NAME
# Created: $(date)

PROJECT_NAME=$PROJECT_NAME
LAUNCH_TEMPLATE=$TEMPLATE_NAME
LAUNCH_TEMPLATE_ID=$TEMPLATE_ID
FLEET_NAME=$FLEET_NAME
FLEET_ID=$FLEET_ID
EBS_VOLUME_ID=$VOLUME_ID
S3_BUCKET=$BUCKET_NAME
REGION=$REGION
INSTANCE_TYPE=$INSTANCE_TYPE
KEY_NAME=$KEY_NAME
AVAILABILITY_ZONE=$AZ
MOUNT_POINT=/mnt/project-data
EOF

# Summary
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Resources Created:"
echo "  Launch Template: $TEMPLATE_NAME (ID: $TEMPLATE_ID)"
echo "  EC2 Fleet: $FLEET_NAME (ID: $FLEET_ID)"
echo "  EBS Volume: $VOLUME_ID"
echo "  S3 Bucket: $BUCKET_NAME"
echo ""
echo "Configuration saved to: $CONFIG_FILE"
echo ""
echo "Features:"
echo "  ✅ Automatic spot → on-demand failover"
echo "  ✅ Automatic on-demand → spot rebalancing"
echo "  ✅ Automatic EBS volume attachment (via User Data)"
echo "  ✅ Volume auto-mounted at /mnt/project-data"
echo ""
echo "To Start Instance:"
echo "  bash scripts/manage_ec2_fleet.sh $PROJECT_NAME start"
echo ""
echo "To Get Instance IP:"
echo "  bash scripts/manage_ec2_fleet.sh $PROJECT_NAME ip"
echo ""
echo "To Stop Instance:"
echo "  bash scripts/manage_ec2_fleet.sh $PROJECT_NAME stop"
echo ""
echo "Note: When instance starts, the EBS volume will be"
echo "      automatically attached and mounted at /mnt/project-data"
echo "      (takes ~30-60 seconds after instance boot)"
echo ""
