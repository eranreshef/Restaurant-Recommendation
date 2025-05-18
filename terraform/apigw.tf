# Creates an HTTP API Gateway to expose the Lambda function
resource "aws_apigatewayv2_api" "http_api" {
  name          = "restaurant-api"
  protocol_type = "HTTP"
}

# Defines an integration between the API Gateway and a Lambda function
resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id                  = aws_apigatewayv2_api.http_api.id
  integration_type        = "AWS_PROXY"
  integration_uri         = aws_lambda_function.restaurant_api.invoke_arn
  integration_method      = "POST"
  payload_format_version  = "2.0"
}

# Configures a route to connect incoming requests to the Lambda integration
resource "aws_apigatewayv2_route" "lambda_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /recommend"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# Defines a deployment stage (like "dev", "prod", or "$default")
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}

# Grants API Gateway permission to invoke the Lambda function
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.restaurant_api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}
