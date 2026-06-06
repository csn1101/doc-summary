terraform {
  backend "s3" {
    bucket = "599626541533-ap-south-1-doc-summary-tf-state"
    key    = "terraform/state.tfstate"
    region = "ap-south-1"
  }
}

provider "aws" {
  region = var.region
}

# ✅ Account info
data "aws_caller_identity" "current" {}

# ✅ Prefix (IMPORTANT)
locals {
  account_id = data.aws_caller_identity.current.account_id
  prefix     = "${local.account_id}-${var.region}-${var.environment}-doc-summary"
}

# ✅ S3 Buckets
resource "aws_s3_bucket" "input" {
  bucket = "${local.prefix}-input"
}

resource "aws_s3_bucket" "output" {
  bucket = "${local.prefix}-output"
}

# ✅ IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${local.prefix}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

# ✅ Basic logging policy
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# ✅ S3 access policy
resource "aws_iam_policy" "lambda_s3" {
  name = "${local.prefix}-lambda-s3-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = [
        "s3:GetObject",
        "s3:PutObject"
      ],
      Resource = [
        "${aws_s3_bucket.input.arn}/*",
        "${aws_s3_bucket.output.arn}/*"
      ]
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_s3_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_s3.arn
}

# ✅ Lambda Function
resource "aws_lambda_function" "processor" {
  function_name = "${local.prefix}-processor"

  role    = aws_iam_role.lambda_role.arn
  handler = "lambda_function.lambda_handler"
  runtime = "python3.10"

  filename         = "lambda.zip"
  source_code_hash = filebase64sha256("lambda.zip")
}

# ✅ S3 Trigger
resource "aws_s3_bucket_notification" "trigger" {
  bucket = aws_s3_bucket.input.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.processor.arn
    events              = ["s3:ObjectCreated:*"]
  }
}

# ✅ S3 → Lambda permission
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.input.arn
}

# ✅ Step Function role
resource "aws_iam_role" "stepfn_role" {
  name = "${local.prefix}-stepfn-role"

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

# ✅ Step Function policy
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

# ✅ Step Function
resource "aws_sfn_state_machine" "summary_workflow" {
  name     = "${local.prefix}-workflow"
  role_arn = aws_iam_role.stepfn_role.arn

  definition = templatefile("${path.module}/step_function.tpl.json", {
    lambda_arn = aws_lambda_function.processor.arn
  })
}

# ✅ Lambda → Step Function permission
resource "aws_iam_role_policy" "lambda_stepfn_policy" {
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = [
        "states:StartExecution"
      ],
      Resource = aws_sfn_state_machine.summary_workflow.arn
    }]
  })
}