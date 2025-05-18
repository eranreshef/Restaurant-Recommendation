# Creates a DynamoDB table named "restaurants"
resource "aws_dynamodb_table" "restaurants" {
  name         = "restaurants"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "name"

  # Defines the key schema attribute
  attribute {
    name = "name"
    type = "S"
  }
}

# Defines a resource-based policy allowing a Lambda function to access the DynamoDB table
resource "aws_dynamodb_resource_policy" "lambda_restaurants" {
  resource_arn = aws_dynamodb_table.restaurants.arn
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "ListAndDescribe",
        "Effect": "Allow",
        "Principal": {
          "AWS": "${aws_iam_role.lambda_exec.arn}"
        },
        "Action": [
          "dynamodb:List*",
          "dynamodb:DescribeTimeToLive"
        ],
        "Resource": "*"
      },
      {
        "Sid": "SpecificTable",
        "Effect": "Allow",
        "Principal": {
          "AWS": "${aws_iam_role.lambda_exec.arn}"
        },
        "Action": [
          "dynamodb:BatchGet*",
	  "dynamodb:DescribeTable",
	  "dynamodb:Get*",
          "dynamodb:Query",
	  "dynamodb:Scan",
          "dynamodb:BatchWrite*",
	  "dynamodb:Delete*",
	  "dynamodb:Update*",
          "dynamodb:PutItem"
        ],
        "Resource": [
          "${aws_dynamodb_table.restaurants.arn}",
          "${aws_dynamodb_table.restaurants.arn}/*"
        ]
      }
    ]
  })
}
