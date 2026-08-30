```python
import boto3
from datetime import datetime, timezone

ec2 = boto3.client("ec2")


def lambda_handler(event, context):

    # Get requested action
    action = event.get("action", "check").lower()

    print("=" * 40)
    print("AWS COST OPTIMIZER")
    print("=" * 40)
    print(f"Requested action: {action}")
    print(f"Execution time: {datetime.now(timezone.utc)}")

    # Find EC2 instances with CostOptimizer=enabled
    response = ec2.describe_instances(
        Filters=[
            {
                "Name": "tag:CostOptimizer",
                "Values": ["enabled"]
            },
            {
                "Name": "tag:AutoStop",
                "Values": ["true"]
            }
        ]
    )

    eligible_instances = []

    # Check all matching reservations and instances
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:

            instance_id = instance["InstanceId"]
            state = instance["State"]["Name"]

            print("-" * 36)
            print(f"Instance ID: {instance_id}")
            print(f"Current state: {state}")

            # Only running instances can be stopped
            if state == "running":

                print("Decision: ELIGIBLE")
                eligible_instances.append(instance_id)

                # Safe check mode
                if action == "check":
                    print("CHECK MODE: No EC2 action will be performed.")

                # Actual stop mode
                elif action == "stop":
                    print(f"Stopping instance: {instance_id}")

                    ec2.stop_instances(
                        InstanceIds=[instance_id]
                    )

                    print(f"STOP command sent successfully: {instance_id}")

            else:
                print("Decision: NOT ELIGIBLE")
                print("Reason: Instance is not running.")

    print("-" * 36)
    print(f"Eligible instances: {eligible_instances}")

    # Summary
    if action == "check":

        print("-" * 36)
        print("CHECK MODE")
        print("No EC2 instances were started or stopped.")

    elif action == "stop":

        print("-" * 36)
        print("STOP MODE")
        print("Eligible EC2 instances were sent the STOP command.")

    else:

        print("-" * 36)
        print(f"Unknown action: {action}")
        print("Supported actions: check, stop")

    print("=" * 40)

    return {
        "statusCode": 200,
        "action": action,
        "eligible_instances": eligible_instances
    }
```
