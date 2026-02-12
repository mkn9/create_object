#!/bin/bash
# Manage EC2 Fleet instance for a project (start, stop, status, get IP)
# Usage: bash scripts/manage_ec2_fleet.sh <project-name> <action>
# Actions: start, stop, status, ip

set -e

PROJECT_NAME="${1}"
ACTION="${2}"

if [ -z "$PROJECT_NAME" ] || [ -z "$ACTION" ]; then
  echo "Usage: $0 <project-name> <action>"
  echo "Actions: start, stop, status, ip"
  echo "Example: $0 my-project start"
  exit 1
fi

# Load configuration
CONFIG_FILE=".${PROJECT_NAME}_ec2_config.txt"
if [ ! -f "$CONFIG_FILE" ]; then
  echo "❌ Configuration file not found: $CONFIG_FILE"
  echo "   Run setup script first: bash scripts/setup_new_project_ec2.sh $PROJECT_NAME"
  exit 1
fi

source "$CONFIG_FILE"

case "$ACTION" in
  start)
    echo "Starting instance in Fleet: $FLEET_NAME"
    echo "Setting target capacity to 1 (spot preferred, on-demand fallback)..."
    
    aws ec2 modify-fleet \
      --fleet-id "$FLEET_ID" \
      --target-capacity-specification "{
        \"TotalTargetCapacity\": 1,
        \"OnDemandTargetCapacity\": 0,
        \"SpotTargetCapacity\": 1,
        \"DefaultTargetCapacityType\": \"spot\"
      }"
    
    echo "✅ Fleet target capacity set to 1"
    echo "   Fleet will try spot first, automatically fall back to on-demand if unavailable"
    echo "   Wait 2-5 minutes for instance to launch, then check status"
    ;;
    
  stop)
    echo "Stopping instance in Fleet: $FLEET_NAME"
    echo "Setting target capacity to 0..."
    
    aws ec2 modify-fleet \
      --fleet-id "$FLEET_ID" \
      --target-capacity-specification "{
        \"TotalTargetCapacity\": 0,
        \"OnDemandTargetCapacity\": 0,
        \"SpotTargetCapacity\": 0,
        \"DefaultTargetCapacityType\": \"spot\"
      }"
    
    echo "✅ Fleet target capacity set to 0"
    echo "   Instance will be terminated (EBS volume persists)"
    ;;
    
  status)
    # Get fleet status
    FLEET_INFO=$(aws ec2 describe-fleets \
      --fleet-ids "$FLEET_ID" \
      --query 'Fleets[0]' \
      --output json)
    
    TARGET_CAPACITY=$(echo "$FLEET_INFO" | jq -r '.TargetCapacitySpecification.TotalTargetCapacity')
    FULFILLED_CAPACITY=$(echo "$FLEET_INFO" | jq -r '.FulfilledCapacity // 0')
    FLEET_STATE=$(echo "$FLEET_INFO" | jq -r '.FleetState')
    
    echo "Fleet Status:"
    echo "  Name: $FLEET_NAME"
    echo "  ID: $FLEET_ID"
    echo "  State: $FLEET_STATE"
    echo "  Target Capacity: $TARGET_CAPACITY"
    echo "  Fulfilled Capacity: $FULFILLED_CAPACITY"
    echo ""
    
    # Get instances in fleet
    INSTANCE_IDS=$(aws ec2 describe-fleet-instances \
      --fleet-id "$FLEET_ID" \
      --query 'ActiveInstances[*].InstanceId' \
      --output text)
    
    if [ -z "$INSTANCE_IDS" ] || [ "$INSTANCE_IDS" == "None" ]; then
      echo "Instances: None running"
    else
      echo "Instances:"
      for INSTANCE_ID in $INSTANCE_IDS; do
        INSTANCE_INFO=$(aws ec2 describe-instances \
          --instance-ids "$INSTANCE_ID" \
          --query 'Reservations[0].Instances[0]' \
          --output json)
        
        STATE=$(echo "$INSTANCE_INFO" | jq -r '.State.Name')
        INSTANCE_TYPE=$(echo "$INSTANCE_INFO" | jq -r '.InstanceType')
        INSTANCE_LIFECYCLE=$(echo "$INSTANCE_INFO" | jq -r '.InstanceLifecycle // "on-demand"')
        IP=$(echo "$INSTANCE_INFO" | jq -r '.PublicIpAddress // "N/A"')
        
        echo "  Instance ID: $INSTANCE_ID"
        echo "    State: $STATE"
        echo "    Type: $INSTANCE_TYPE"
        echo "    Lifecycle: $INSTANCE_LIFECYCLE"
        echo "    IP: $IP"
        echo ""
      done
    fi
    
    # Check EBS volume
    VOLUME_STATE=$(aws ec2 describe-volumes \
      --volume-ids "$EBS_VOLUME_ID" \
      --query 'Volumes[0].State' \
      --output text)
    
    ATTACHED_TO=$(aws ec2 describe-volumes \
      --volume-ids "$EBS_VOLUME_ID" \
      --query 'Volumes[0].Attachments[0].InstanceId' \
      --output text)
    
    echo "EBS Volume:"
    echo "  Volume ID: $EBS_VOLUME_ID"
    echo "  State: $VOLUME_STATE"
    if [ "$ATTACHED_TO" != "None" ] && [ -n "$ATTACHED_TO" ]; then
      echo "  Attached to: $ATTACHED_TO"
    else
      echo "  Attached to: None"
    fi
    ;;
    
  ip)
    # Get instances in fleet
    INSTANCE_IDS=$(aws ec2 describe-fleet-instances \
      --fleet-id "$FLEET_ID" \
      --query 'ActiveInstances[*].InstanceId' \
      --output text)
    
    if [ -z "$INSTANCE_IDS" ] || [ "$INSTANCE_IDS" == "None" ]; then
      echo "❌ No running instance found in fleet"
      exit 1
    fi
    
    # Get first instance IP
    FIRST_INSTANCE_ID=$(echo "$INSTANCE_IDS" | awk '{print $1}')
    
    IP=$(aws ec2 describe-instances \
      --instance-ids "$FIRST_INSTANCE_ID" \
      --query 'Reservations[0].Instances[0].PublicIpAddress' \
      --output text)
    
    if [ -z "$IP" ] || [ "$IP" == "None" ]; then
      echo "❌ Instance not ready yet (no IP assigned)"
      exit 1
    fi
    
    echo "$IP"
    ;;
    
  *)
    echo "❌ Unknown action: $ACTION"
    echo "Valid actions: start, stop, status, ip"
    exit 1
    ;;
esac

