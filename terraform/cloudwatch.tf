# Creates a CloudWatch Log Group for the Lambda function
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.restaurant_api.function_name}"
  retention_in_days = 30
  kms_key_id        = aws_kms_key.cloudwatch_logs.arn
}


# Creates a customer-managed AWS KMS key for encrypting CloudWatch Logs
resource "aws_kms_key" "cloudwatch_logs" {
  description             = "KMS key for encrypting CloudWatch Logs"
  enable_key_rotation     = true
  deletion_window_in_days = 10
  policy = jsonencode({
    Version = "2012-10-17",
    Id      = "log-key-policy",
    Statement = [
      {
        Sid       = "Enable IAM User Permissions",
        Effect    = "Allow",
        Principal = {
          "AWS": "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        },
        Action    = "kms:*",
        Resource  = "*"
      },
      {
        Sid      = "Allow Lambda to use the key",
        Effect   = "Allow",
        Principal = {
          Service = "logs.${var.aws_region}.amazonaws.com"
        },
        Action   = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ],
        Resource = "*"
      }
    ]
  })
}

# Data source to get the current AWS account ID for use in KMS policy
data "aws_caller_identity" "current" {}

