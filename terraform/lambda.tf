resource "aws_lambda_function" "restaurant_api" {
  function_name = "restaurant-api"
  handler       = "lambda_handler.handler"
  runtime       = "python3.11"
  role          = aws_iam_role.lambda_exec.arn
  filename      = "${path.module}/package.zip"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  environment {
    variables = {
      RESTAURANT_TABLE = aws_dynamodb_table.restaurants.name
    }
  }
  depends_on = [aws_iam_role_policy_attachment.lambda_logs]
}

resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../api"
  output_path = "${path.module}/package.zip"
}