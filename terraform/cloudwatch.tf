resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.restaurant_api.function_name}"
  retention_in_days = 30
  kms_key_id        = aws_kms_key.cloudwatch_logs.arn
}

# resource "aws_cloudwatch_log_data_protection_policy" "lambda_logs_protection" {
#   log_group_name = aws_cloudwatch_log_group.lambda_logs.name
#   policy_document = jsonencode({
#     "Name": "data-protection-policy",
#     "Description": "",
#     "Version": "2021-06-01",
#     "Statement": [
#       {
#         "Sid": "audit-policy",
#         "DataIdentifier": [
#           "all"
#         ],
#         "Operation": {
#           "Audit": {
#             "FindingsDestination": {}
#           }
#         }
#       },
#       {
#         "Sid": "redact-policy",
#         "DataIdentifier": [
#           "all"
#         ],
#         "Operation": {
#           "Deidentify": {
#             "MaskConfig": {}
#           }
#         }
#       }
#     ],
#     "Configuration": {
#       "CustomDataIdentifier": [
#         {
#           "Name": "all",
#           "Regex": ".*"
#         }
#       ]
#     }
#   })
# }

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
        Principal = { "AWS": "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root" },
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

data "aws_caller_identity" "current" {}