## 📦 Terraform Backend Setup

### 📌 Objective

The first implementation step in this project is to configure a **remote backend for Terraform state management**.

Instead of storing state locally, Terraform is configured to use **AWS S3 and DynamoDB**, which enables safe, scalable, and collaborative infrastructure provisioning. This forms the foundational layer for all future infrastructure deployments.

---

### 🧠 Why a Backend is Needed

Terraform maintains a **state file (`terraform.tfstate`)** that tracks all infrastructure resources it manages. This file is critical because it represents the current state of your infrastructure.

By default, Terraform stores this state file locally, which introduces several limitations:

- ❌ Not shareable across team members  
- ❌ Prone to accidental deletion or corruption  
- ❌ Unsafe for concurrent executions  
- ❌ Not suitable for CI/CD pipelines  

To overcome these limitations, we implement a **remote backend**, ensuring centralized and reliable state management.

---

### ⚙️ Solution Approach

The backend is implemented using AWS managed services:

#### ✅ Amazon S3 (State Storage)

- Stores the Terraform state file in a centralized location  
- Ensures high durability and availability  
- Requires globally unique bucket naming  
- Acts as the single source of truth for infrastructure  

#### ✅ DynamoDB (State Locking)

- Prevents multiple Terraform executions at the same time  
- Ensures consistency during infrastructure updates  
- Avoids state corruption due to concurrent changes  

---

### 🔐 Security & Reliability Enhancements

To align with production-grade standards, the backend is configured with the following safeguards:

- ✅ **Versioning enabled**  
  Ensures historical versions of the state file are retained, enabling rollback in case of corruption  

- ✅ **Server-side encryption (AES256)**  
  Protects sensitive infrastructure details stored in the state file  

- ✅ **Block all public access**  
  Prevents accidental exposure of the state file  

- ✅ **Lifecycle protection (`prevent_destroy`)**  
  Prevents accidental deletion of the backend S3 bucket  

---

### 📂 Implementation Details

The backend infrastructure is defined using Terraform in: bootstrap/main.tf

This configuration provisions:

- S3 bucket for Terraform state storage  
- DynamoDB table for state locking  
- Security configurations (encryption, versioning, access blocking)  

---

### ▶️ Execution Steps

The backend was successfully provisioned using the following Terraform commands:

terraform init
terraform validate
terraform plan
terraform apply

## Verification

Post-deployment, the following checks were performed:
- aws s3 ls
- result - 599626541533-terraform-state-backend-global
- aws dynamodb list-tables
- result -     "TableNames": ["terraform-locks"]

## 🔐 IAM & Environment Setup

### 📌 Objective

The goal of this step is to establish **logical separation between environments (Dev, QA, Prod)** using AWS IAM roles.

This enables controlled and structured infrastructure deployment, simulating an enterprise-grade multi-environment architecture within a single AWS account.

---

### 🧠 Design Approach

Instead of using separate AWS accounts at this stage, environments are isolated using **dedicated IAM roles**:

- terraform-dev-role  
- terraform-qa-role  
- terraform-prod-role  

Each role represents a specific environment and can be assumed independently for deploying infrastructure.

---

### ⚙️ Implementation Details

#### ✅ Environment Definition

A centralized list of environments is defined:

```hcl
locals {
  environments = ["dev", "qa", "prod"]
}
```

This enables scalable and dynamic resource creation.

---

#### ✅ Dynamic Role Creation

Using Terraform `for_each`, IAM roles are created dynamically:

```hcl
resource "aws_iam_role" "terraform_roles" {
  for_each = toset(local.environments)

  name = "terraform-${each.value}-role"
}
```

This approach avoids duplication and ensures consistency.

---

#### ✅ Shared IAM Policy

A common IAM policy is created and attached to all roles.

- Current setup: full access (`*`)
- Purpose: simplify initial development

⚠️ This will be refined later using **least privilege principles**.

---

#### ✅ Policy Attachment

Each role is automatically attached to the shared policy, ensuring consistent permissions across environments.

---

### 🔄 Scalability & Future Enhancements

This design allows seamless expansion of environments.

To add new environments (e.g., UAT, staging), update:

```hcl
environments = ["dev", "qa", "prod", "uat"]
```

Terraform will automatically create:

- terraform-uat-role  

This ensures:

- ✅ Minimal code changes  
- ✅ High scalability  
- ✅ Consistent naming and structure  

---

### ⚠️ Known Issue & Resolution (Provider Download)

During execution, an issue occurred while running:

```bash
terraform init
```

#### ❌ Error

```
Failed to install provider
connection was aborted by the software in your host machine
```

#### 🧠 Root Cause

- Corporate network restrictions blocked access to:
  https://releases.hashicorp.com  
- Common causes in enterprise environments:
  - Firewall rules  
  - Endpoint security software  
  - Restricted outbound access  

---

#### ✅ Solution

The issue was resolved by reusing the locally available Terraform provider:

1. Copied `.terraform` folder from:

```
bootstrap/.terraform/
```

2. Pasted into:

```
iam/.terraform/
```

This allowed Terraform to use a **cached provider instead of downloading from the internet**.

---

#### 🚀 Enterprise Insight

In real-world enterprise environments:

- Direct internet access is often restricted  
- Terraform providers are managed through:
  - Local caches  
  - Internal artifact repositories  
  - Controlled proxy configurations  

---

### ✅ Outcome

- Successfully created environment-specific IAM roles  
- Established logical separation between environments  
- Enabled scalable IAM configuration using Terraform  
- Prepared system for CI/CD integration using role-based access  

---

### 🔐 Future Improvements

- Implement least-privilege IAM policies  
- Restrict role assumption to trusted principals (CI/CD)  
- Transition to multi-account architecture for stronger isolation  

## 🚀 Application Infrastructure Setup (S3 + Lambda Pipeline)

### 📌 Objective

The goal of this step is to build the **core application pipeline** for document summarization using an event-driven serverless architecture.

This includes:

- Input ingestion via S3  
- Automatic processing using AWS Lambda  
- Output storage in S3  

---

### 🧭 High-Level Architecture

```
S3 (Input Bucket)
        │
        ▼  (Object Created Event)
AWS Lambda (Processing Function)
        │
        ▼
S3 (Output Bucket)
```

---

### ⚙️ Implementation Components

#### ✅ 1. Input S3 Bucket

- Receives raw text input files  
- Triggers Lambda execution on file upload  

**Naming Convention:**
```
<account_id>-<region>-doc-summary-input
```

---

#### ✅ 2. Output S3 Bucket

- Stores the summarized output generated by Lambda  

**Naming Convention:**
```
<account_id>-<region>-doc-summary-output
```

---

#### ✅ 3. Lambda Function (Processor)

A Python-based AWS Lambda function performs the summarization logic.

**Key Responsibilities:**

- Read input file from S3  
- Process text (simple summarization logic)  
- Write summarized output to output bucket  

---

#### ✅ Lambda Code (Core Logic)

```python
def summarize(text):
    sentences = text.split(".")
    return ".".join(sentences[:2])
```

> Note: This is a basic implementation and will be enhanced later.

---

#### ✅ 4. IAM Role for Lambda

A dedicated IAM role is created for the Lambda function with:

- Basic execution permissions (CloudWatch logging)  
- Access to read from input S3 bucket  
- Access to write to output S3 bucket  

---

#### ✅ 5. S3 Event Trigger

The input S3 bucket is configured with an event notification:

- Event: `s3:ObjectCreated:*`  
- Target: Lambda function  

This ensures automatic execution on file upload.

---

#### ✅ 6. Lambda Invocation Permission

Permission is explicitly granted to allow:

```
S3 → Lambda invocation
```

---

### 📂 Implementation Files

```
app/
├── main.tf            # Infrastructure definition
├── variables.tf       # Configurable parameters
├── lambda_function.py # Summarization logic
├── lambda.zip         # Packaged Lambda code
```

---

### ▶️ Deployment Steps

```bash
terraform init
terraform plan
terraform apply
```

---

### ⚠️ Known Constraint & Resolution

Due to restricted network access, Terraform provider downloads were blocked.

#### ✅ Solution

Reused locally cached provider by copying:

```
bootstrap/.terraform/ → app/.terraform/
```

This bypassed the need for external downloads.

---

### ✅ Verification

The infrastructure was verified using:

- ✅ S3 bucket creation  
- ✅ Lambda function deployment  
- ✅ IAM role attachment  
- ✅ S3 event trigger configuration  

---

### 🧪 Functional Test (Next Step)

The system will be tested by:

1. Uploading a text file to the input bucket  
2. Verifying Lambda execution  
3. Checking output bucket for summarized result  

---

### ✅ Outcome

A fully functional **event-driven serverless pipeline** has been successfully deployed.

This system:

- Automatically processes input files  
- Performs summarization using Lambda  
- Stores results without manual intervention  

---

### 🧠 Enterprise Insight

This architecture reflects real-world production patterns used in:

- Data processing pipelines  
- Log processing systems  
- ETL workflows  
- Machine learning preprocessing pipelines  

---

### 🔐 Future Enhancements

- Replace basic summarization with NLP/ML models  
- Add API Gateway for external access  
- Build UI for user interaction  
- Introduce environment-based deployment (Dev/QA/Prod)  
- Implement CI/CD using GitHub Actions  

## 🗂️ Repository Setup & Branching Strategy

### 📌 Objective

The objective of this step is to establish a structured **version control system** using Git and GitHub, enabling controlled and systematic promotion of infrastructure and application changes across environments.

This aligns the project with **enterprise DevOps practices**, ensuring maintainability, traceability, and safe deployments.

---

### 🧭 Branching Strategy

The repository follows a **multi-branch environment mapping strategy**:

| Branch   | Environment | Purpose |
|----------|-------------|---------|
| main     | Production  | Stable, production-ready code |
| release  | QA          | Testing and validation before production |
| develop  | Dev         | Active development and experimentation |

---

### 🔄 Development Workflow

All changes follow a controlled promotion path:

```
feature/* → develop → release → main
```

---

#### ✅ Workflow Description

1. **Feature Development**
   - Developers create feature branches:
     ```
     feature/<feature-name>
     ```

2. **Development Integration**
   - Feature branches are merged into:
     ```
     develop
     ```
   - Represents the **Dev environment**

3. **Quality Assurance**
   - Code is promoted to:
     ```
     release
     ```
   - Used for **QA testing and validation**

4. **Production Deployment**
   - Final changes are merged into:
     ```
     main
     ```
   - Represents the **Production environment**

---

### 🔐 Branch Protection (Production - main)

To ensure production stability and prevent direct changes, branch protection rules are applied to the `main` branch:

- ✅ Require pull request before merging  
- ✅ Direct commits to `main` are restricted  
- ✅ All changes must go through a pull request  

---

### ⚙️ Repository Configuration

#### ✅ .gitignore

The repository excludes unnecessary and sensitive files using `.gitignore`:

```
# Terraform
.terraform/
*.tfstate
*.tfstate.backup

# Python
venv/
__pycache__/

# Build artifacts
*.zip

# Test outputs
test/output/

# OS files
.DS_Store
Thumbs.db
```

---

### ✅ Code Organization

The repository is structured into clearly defined components:

```
bootstrap/  → Backend infrastructure (S3 + DynamoDB)
iam/        → IAM roles and permissions
app/        → Core application (S3 + Lambda)
test/       → Testing scripts and validation
```

---

### ✅ Outcome

The repository now supports:

- ✅ Structured development workflow  
- ✅ Clear environment separation (Dev, QA, Prod)  
- ✅ Safe promotion of changes  
- ✅ Version control and traceability  
- ✅ Readiness for CI/CD pipeline integration  

---

### 🧠 Enterprise Insight

This branching and repository setup mirrors industry-standard practices used in large organizations:

- Controlled release cycles  
- Environment-based deployments  
- Pull request-based validation  
- Separation of development and production concerns  

---

### 🔮 Future Enhancements

- Integrate GitHub Actions for CI/CD automation  
- Enforce approval requirements on production branch  
- Add automated Terraform validation and plan checks  
- Introduce version tagging and release management  

## ✅ Test Update - Pipeline Validation
This is a test change to validate branch promotion workflow.

## 🔄 Step 6 — Workflow Orchestration using Step Functions

### 📌 Objective

Enhance the existing event-driven pipeline by introducing **AWS Step Functions** to enable structured workflow execution, orchestration, and extensibility.

This step transitions the system from:

```
S3 → Lambda
```

to a more controlled architecture:

```
Step Function → Lambda
```

---

### 🧭 Key Design Principle

The implementation is done incrementally to:

- ✅ Avoid breaking existing functionality  
- ✅ Introduce orchestration layer safely  
- ✅ Maintain backward compatibility  

---

## ✅ Step 6.1 — Step Function IAM Role

### 📌 Objective

Create an IAM role that allows AWS Step Functions to assume and execute workflows.

---

### ✅ Implementation

```hcl
resource "aws_iam_role" "stepfn_role" {
  name = "${var.suffix}-stepfn-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "states.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}
```

---

### ✅ Outcome

- Step Functions can assume this role  
- Acts as the **execution identity** for workflows  

---

## ✅ Step 6.2 — Lambda Invocation Permission

### 📌 Objective

Allow Step Function to invoke the existing Lambda function.

---

### ✅ Implementation

```hcl
resource "aws_iam_role_policy" "stepfn_policy" {
  role = aws_iam_role.stepfn_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = [
        "lambda:InvokeFunction"
      ],
      Resource = aws_lambda_function.processor.arn
    }]
  })
}
```

---

### ✅ Outcome

- Step Function can invoke Lambda  
- Establishes **workflow → execution linkage**

---

## ✅ Step 6.3 — Step Function State Machine

### 📌 Objective

Define a workflow that invokes Lambda using a structured state machine.

---

### 📂 Template File

```
app/step_function.tpl.json
```

---

### ✅ Template Definition

```json
{
  "Comment": "Simple document processing workflow",
  "StartAt": "ProcessText",
  "States": {
    "ProcessText": {
      "Type": "Task",
      "Resource": "${lambda_arn}",
      "End": true
    }
  }
}
```

---

### ✅ Terraform Integration

```hcl
resource "aws_sfn_state_machine" "summary_workflow" {
  name     = "${var.suffix}-workflow"
  role_arn = aws_iam_role.stepfn_role.arn

  definition = templatefile("${path.module}/step_function.tpl.json", {
    lambda_arn = aws_lambda_function.processor.arn
  })
}
```

---

### ✅ Outcome

- Step Function created successfully  
- Workflow performs:

```
Start → Invoke Lambda → End
```

---

### 🧠 Design Insight

Using a `.tpl.json` template provides:

- ✅ Separation of concerns (infrastructure vs workflow logic)  
- ✅ Better readability and maintainability  
- ✅ Easy extensibility for future workflow stages  
- ✅ Dynamic variable injection (e.g., Lambda ARN)  

---

## ✅ Current Architecture (After Step 6.3)

```
Existing Flow:
S3 → Lambda ✅ (still active)

New Flow:
Step Function → Lambda ✅ (introduced)
```

---

## ⚠️ Current Limitation

- Step Function currently sends default input:
  ```
  {}
  ```

- Lambda expects S3 event structure:
  ```python
  event["Records"]
  ```

👉 This mismatch prevents full execution and will be resolved next.

---

## ✅ Outcome Summary

- ✅ Workflow orchestration layer introduced  
- ✅ IAM role and permissions configured  
- ✅ Step Function successfully deployed  
- ✅ Existing event-driven pipeline remains intact  

---

## 🔮 Next Step

### Step 6.4 — Functional Integration

- Modify Lambda to support Step Function input  
- OR pass appropriate structured input  
- Enable end-to-end execution via Step Function  

---

## 🧠 Enterprise Insight

This orchestration pattern is widely used in:

- Data processing pipelines  
- Document processing systems  
- ETL workflows  
- Microservice orchestration  

---

### ✅ Benefits Achieved

- Improved workflow control  
- Better extensibility  
- Structured execution model  
- Readiness for retries, branching, and error handling  

## ✅ Step 6.5 — Final Orchestration (S3 → Step Function → Lambda)

### 🎯 Objective

Transition from direct event-driven processing to a fully orchestrated workflow using AWS Step Functions.

---

## ✅ Final Architecture

```
S3 Upload
   ↓
Lambda (Trigger Only)
   ↓
Step Function
   ↓
Lambda (Processing)
```

---

## ✅ Flow Description

1. File is uploaded to S3
2. S3 triggers Lambda
3. Lambda starts Step Function execution
4. Step Function invokes Lambda for processing
5. Processing result is returned

---

## ✅ Key Enhancements

- ✅ Decoupled architecture  
- ✅ Centralized workflow control  
- ✅ Improved scalability  
- ✅ Extensible pipeline  

---

## ✅ Testing Approach

An automated test script performs:

- Upload test file to S3  
- Trigger full pipeline  
- Track Step Function execution  
- Log results with run tracking  

---

## ✅ Logging & Observability

Each test run includes:

- Unique run ID  
- Execution ARN  
- Status tracking  
- Input/output logs  
- Timestamped entries  

Logs are stored locally at:

```
test/log/s3_upload_sfn_log.txt
```

---

## ✅ Sample Execution Flow

```
START → Upload → Trigger → Execute → SUCCEEDED ✅
```

---

## ✅ Outcome

- Step Function orchestrates processing ✅  
- Lambda acts as trigger + processor ✅  
- End-to-end pipeline validated ✅  
- Full observability implemented ✅  

---

## 🔮 Next Steps

- CI/CD pipeline integration  
- Retry & error handling  
- Parallel workflows  
- Output persistence (S3)  


## 🚀 Step 7 — CI/CD Pipeline (Terraform + GitHub Actions)

---

### 🎯 Objective

Automate infrastructure deployment using Terraform through GitHub Actions, enabling fully Git-driven deployments without manual intervention.

---

## ✅ CI/CD Workflow

Code Push → GitHub Actions → Terraform → AWS Deployment

---

### ✅ Pipeline Execution Flow

1. Developer pushes code to repository  
2. Changes are promoted via:
   feature → develop → release → main  
3. Merge into `main` triggers GitHub Actions workflow  
4. Workflow performs:
   - Code checkout  
   - AWS authentication  
   - Lambda packaging  
   - Terraform initialization  
   - Terraform plan & apply  

---

## ✅ GitHub Actions Pipeline

### 🔧 Workflow Steps

- Checkout repository  
- Configure AWS credentials (via GitHub Secrets)  
- Package Lambda function  
- Run `terraform init`  
- Run `terraform plan`  
- Run `terraform apply`  

---

## ✅ Lambda Build Automation

Lambda package is generated dynamically inside the pipeline:

    zip -r lambda.zip lambda_function.py

---

## ✅ Terraform Backend (State Management)

Terraform state is stored remotely in an S3 bucket:

- Bucket: 599626541533-ap-south-1-doc-summary-tf-state  
- Key: terraform/state.tfstate  
- Region: ap-south-1  

---

### ✅ Benefits of Remote State

- Shared state across local and CI/CD environments  
- Prevents duplicate resource creation  
- Ensures consistency and reliability  
- Enables team collaboration  

---

## ✅ Security

AWS access is managed securely using GitHub Secrets:

- AWS_ACCESS_KEY_ID  
- AWS_SECRET_ACCESS_KEY  

✔️ No credentials are hardcoded in the repository  

---

## ✅ Deployment Behavior

- Changes are automatically deployed on push to `main`  
- Terraform detects existing infrastructure via S3 state  
- Only incremental updates are applied  

---

## ✅ End-to-End Architecture

S3 Upload  
↓  
Lambda (Trigger)  
↓  
Step Function  
↓  
Lambda (Processor)  

---

## ✅ Automated Testing

A test script validates the entire pipeline:

- Uploads file to S3  
- Triggers Step Function  
- Tracks execution  
- Logs results with run tracking  

---

### ✅ Logging

Logs include:

- Unique run ID  
- Execution ARN  
- Status tracking  
- Input/output details  

Stored at:

test/log/s3_upload_sfn_log.txt

---

## ✅ Outcome

- Fully automated infrastructure deployment  
- Event-driven orchestration pipeline  
- End-to-end test automation  
- Production-ready DevOps workflow  

---

## 🔮 Next Enhancements

- Multi-environment deployment (dev / prod)  
- Terraform state locking (DynamoDB)  
- CI/CD safety controls (plan vs apply)  
- Enhanced error handling & retries  