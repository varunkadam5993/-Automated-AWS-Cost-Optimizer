# AWS EC2 Cost Control Automation ☁️

A serverless AWS solution that automatically identifies selected EC2 instances and shuts them down according to a predefined schedule. The workflow combines **AWS Lambda**, **Amazon EventBridge Scheduler**, **Amazon EC2**, **IAM**, and **CloudWatch**.

---

## 📖 About the Project

Keeping EC2 instances running when they are not required can result in avoidable compute charges.

This project introduces a tag-driven automation workflow. Instead of manually stopping development or testing servers every day, AWS Lambda checks EC2 resources for specific tags and performs the required action automatically.

The automation can operate in two modes:

* **CHECK** – identifies matching instances without changing their state.
* **STOP** – shuts down instances that satisfy the configured conditions.

The scheduled execution is handled by **Amazon EventBridge Scheduler**.

---

## 🎯 Project Goal

The primary goal is to reduce unnecessary EC2 running time by automatically stopping selected instances during predefined periods.

### Key idea

```text
EC2 Tags
   ↓
Identify Target Instances
   ↓
Lambda Validation
   ↓
Scheduled Decision
   ↓
Stop Eligible Instances
```

---

## 🏛️ Solution Architecture

```text
                 ┌───────────────────────────┐
                 │   EventBridge Scheduler    │
                 │                           │
                 │    Daily - 8:00 PM IST    │
                 └─────────────┬─────────────┘
                               │
                               │ action = stop
                               ▼
                 ┌───────────────────────────┐
                 │        AWS Lambda         │
                 │                           │
                 │ EC2 Cost Control Function │
                 └─────────────┬─────────────┘
                               │
                               │ Inspect Tags
                               ▼
                 ┌───────────────────────────┐
                 │        Amazon EC2         │
                 │                           │
                 │  Tagged Target Instance   │
                 └─────────────┬─────────────┘
                               │
                         Matching Tags?
                         /             \
                       YES              NO
                        │                │
                        ▼                ▼
                 Stop Instance       Skip
                        │
                        ▼
                 ┌───────────────────────────┐
                 │      Amazon CloudWatch     │
                 │                           │
                 │     Execution Logs        │
                 └───────────────────────────┘
```

---

## ☁️ AWS Components

| Service                          | Role in the Solution                                                     |
| -------------------------------- | ------------------------------------------------------------------------ |
| **Amazon EC2**                   | Provides the virtual machine that is controlled by the automation        |
| **AWS Lambda**                   | Runs the Python logic responsible for identifying and stopping instances |
| **Amazon EventBridge Scheduler** | Starts the Lambda function according to the configured timetable         |
| **AWS IAM**                      | Controls access to EC2, Lambda, and CloudWatch resources                 |
| **Amazon CloudWatch**            | Stores Lambda execution and decision logs                                |

---

## 🔄 Workflow

The complete process works as follows:

1. Launch an EC2 instance for testing.
2. Add the required identification tags.
3. Invoke the Lambda function.
4. Lambda searches for EC2 instances matching the configured criteria.
5. Use **CHECK** mode to verify which resources qualify.
6. Configure EventBridge Scheduler for the desired execution time.
7. The scheduler sends a `stop` request to Lambda.
8. Lambda evaluates the tagged instances.
9. Matching running instances are stopped.
10. Execution information is written to CloudWatch Logs.

### Scheduler Payload

```json
{
  "action": "stop"
}
```

---

## 🏷️ Resource Identification Through Tags

The automation does not blindly stop every EC2 instance.

Instead, the target server is identified through a collection of tags.

| Key             | Value                        |
| --------------- | ---------------------------- |
| `Project`       | `AWS-Cost-Optimizer`         |
| `CostOptimizer` | `enabled`                    |
| `Environment`   | `dev`                        |
| `AutoStop`      | `true`                       |
| `AutoSchedule`  | `yes`                        |
| `Name`          | `cost-optimizer-test-server` |

This approach makes the automation more controlled because only resources carrying the expected metadata are considered.

---

## 🔎 CHECK Mode

Before allowing the automation to make changes, the Lambda function supports a non-destructive testing mode.

Use the following event:

```json
{
  "action": "check"
}
```

CHECK mode performs the resource-selection logic but does **not** start or stop an EC2 instance.

### Example Result

```text
AWS COST OPTIMIZER
------------------

Requested action : check

Instance ID      : <EC2_INSTANCE_ID>
Current state    : running
Decision         : ELIGIBLE

CHECK MODE
No EC2 state change was performed.
```

This makes it possible to verify the tagging and selection rules before enabling the shutdown operation.

---

## 🛑 STOP Mode

Once the selection logic has been verified, the Lambda function can receive:

```json
{
  "action": "stop"
}
```

Lambda then evaluates the EC2 resources and stops instances that satisfy the configured conditions.

### Example Test Environment

```text
Instance Name : cost-optimizer-test-server
Instance Type : t3.micro
Region        : ap-south-1
```

For security and portability, actual instance identifiers should not be hard-coded into public documentation.

---

## ⏰ Scheduled Execution

The automation uses an **Amazon EventBridge Scheduler** to trigger Lambda automatically.

### Current Configuration

```text
Schedule Name : aws-cost-optimizer-daily
Status        : Enabled
Frequency     : Daily
Execution     : 8:00 PM IST
Time Zone     : Asia/Calcutta
```

The scheduler invokes:

```text
automated-aws-cost-optimizer
```

with:

```json
{
  "action": "stop"
}
```

---

## 🔐 IAM Configuration

AWS IAM is used instead of placing AWS access keys inside the Lambda source code.

The Lambda execution role requires access for tasks such as:

```text
EC2
 ├── Describe instances
 └── Stop instances

CloudWatch
 └── Write execution logs
```

EventBridge Scheduler also requires permission to invoke the Lambda function.

### Least-Privilege Approach

Only the permissions required by the automation should be granted to the associated IAM roles. This reduces the potential impact of an incorrectly configured function.

---

## 📊 Monitoring With CloudWatch

Lambda execution activity can be reviewed through Amazon CloudWatch Logs.

The project uses the following log group:

```text
/aws/lambda/automated-aws-cost-optimizer
```

The logs can contain information such as:

* Requested operation
* Instance identifier
* Current EC2 state
* Eligibility result
* Stop operation
* Execution outcome

### Example

```text
AWS COST OPTIMIZER
------------------

Requested action : check
Instance ID      : <EC2_INSTANCE_ID>
Current state    : running
Decision         : ELIGIBLE

CHECK MODE
No EC2 instances were started or stopped.
```

---

## 🧪 Validation & Testing

The solution can be validated in several stages.

### 1. EC2 Discovery

Confirm that Lambda can locate the EC2 instance carrying the required tags.

```text
State    : running
Decision : ELIGIBLE
```

### 2. CHECK Validation

Run the Lambda with:

```json
{
  "action": "check"
}
```

The expected result is that the instance is identified without modifying its state.

### 3. STOP Verification

Run:

```json
{
  "action": "stop"
}
```

The target instance should move through the normal EC2 lifecycle:

```text
Running
   ↓
Stopping
   ↓
Stopped
```

### 4. Scheduler Test

Verify that EventBridge Scheduler invokes the Lambda at the configured daily time.

---

## 📂 Repository Layout

```text
aws-cost-optimizer/
│
├── lambda_function.py
├── README.md
│
└── screenshots/
    ├── ec2-instance-tags.png
    ├── lambda-function.png
    ├── lambda-check-test.png
    ├── lambda-stop-test.png
    ├── eventbridge-schedule.png
    └── cloudwatch-logs.png
```

> The exact repository structure can be adjusted depending on how the Lambda source and supporting files are organized.

---

## 🚀 Deployment Guide

### Step 1 — Launch an EC2 Instance

Create a test EC2 instance and apply the tags required by the automation.

---

### Step 2 — Configure IAM

Create an IAM role for Lambda.

Grant the role the permissions required to:

* Inspect EC2 instances
* Stop selected EC2 instances
* Create CloudWatch log entries

---

### Step 3 — Create the Lambda Function

Create a Lambda function named:

```text
automated-aws-cost-optimizer
```

Upload the Python automation code.

---

### Step 4 — Perform a Safe Test

Use the following Lambda test event:

```json
{
  "action": "check"
}
```

Confirm that the expected EC2 instance is detected.

---

### Step 5 — Test the Stop Operation

After confirming the selection logic, test:

```json
{
  "action": "stop"
}
```

Verify that the intended EC2 instance is stopped.

---

### Step 6 — Create the Scheduler

Create an EventBridge Scheduler:

```text
aws-cost-optimizer-daily
```

Configure it for:

```text
Daily
8:00 PM IST
```

---

### Step 7 — Set Lambda as the Target

Select the Lambda function:

```text
automated-aws-cost-optimizer
```

Use this event payload:

```json
{
  "action": "stop"
}
```

---

### Step 8 — Review CloudWatch

After execution, open the Lambda log group:

```text
/aws/lambda/automated-aws-cost-optimizer
```

Review the execution result and confirm that the expected instance was processed.

---

## ✅ Advantages

This project provides several practical benefits:

* Minimizes unnecessary EC2 running hours
* Reduces manual shutdown tasks
* Uses metadata-based resource selection
* Supports a non-destructive CHECK mode
* Provides centralized execution logs
* Uses serverless AWS Lambda
* Automates execution with EventBridge Scheduler
* Can be extended to support additional cost-control rules

---

## ⚠️ Safety Notes

Automatic EC2 shutdown should be enabled carefully because stopping an instance may interrupt applications or services running on it.

Recommended precautions:

1. Apply the required tags only to intended resources.
2. Avoid tagging production instances unless automatic shutdown is explicitly required.
3. Run CHECK mode before enabling STOP mode.
4. Follow IAM least-privilege practices.
5. Exclude critical workloads from the automation.
6. Test the workflow using a non-production instance first.

---

## 🔮 Potential Improvements

The current implementation can be expanded with additional capabilities, such as:

* Environment-specific start/stop schedules
* Estimated monthly savings
* SNS notifications after shutdown
* DynamoDB-based execution history
* Cost-optimization dashboard
* CloudWatch-based idle-instance detection
* EBS optimization
* Automated savings reports
* Multi-region support
* Multi-account AWS environments

---

## 🎓 Project Details

| Item              | Details                                             |
| ----------------- | --------------------------------------------------- |
| **Project**       | AWS EC2 Cost Control Automation                     |
| **Platform**      | Amazon Web Services                                 |
| **Architecture**  | Serverless                                          |
| **Core Services** | EC2, Lambda, EventBridge Scheduler, IAM, CloudWatch |
| **AWS Region**    | Asia Pacific (Mumbai) — `ap-south-1`                |
| **Schedule**      | Daily at 8:00 PM IST                                |
| **Category**      | Cloud Automation / Cost Optimization                |

---

## 👨‍💻 Author

Varun Kadam

Cloud / AWS Project

---

## 📝 Summary

This project demonstrates how AWS serverless services can work together to automate EC2 cost-control operations.

EC2 resources are selected through tags, Lambda evaluates those resources, and EventBridge Scheduler provides the recurring trigger. CHECK mode allows the configuration to be validated safely before shutdown actions are enabled. CloudWatch provides visibility into the Lambda executions, while IAM controls access to AWS resources.

### Technologies Demonstrated

```text
AWS Lambda
Amazon EC2
Amazon EventBridge Scheduler
AWS IAM
Amazon CloudWatch
Python
Serverless Automation
EC2 Tag Management
Cloud Cost Optimization
```

---

## ⭐ Project Outcome

The result is a lightweight AWS automation workflow that can reduce unnecessary EC2 runtime while demonstrating practical knowledge of **serverless architecture, IAM permissions, event scheduling, resource tagging, monitoring, and AWS cost optimization**.
