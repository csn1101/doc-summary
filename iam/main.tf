provider "aws" {
  region = "ap-south-1"
}

locals {
  environments = ["dev", "qa", "prod"]
}

# IAM Policy (shared)
resource "aws_iam_policy" "terraform_policy" {
  name = "terraform-base-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = "*",
        Resource = "*"
      }
    ]
  })
}

# IAM Roles per environment
resource "aws_iam_role" "terraform_roles" {
  for_each = toset(local.environments)

  name = "terraform-${each.value}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          AWS = "*"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Attach policy
resource "aws_iam_role_policy_attachment" "attach" {
  for_each = aws_iam_role.terraform_roles

  role       = each.value.name
  policy_arn = aws_iam_policy.terraform_policy.arn
}
