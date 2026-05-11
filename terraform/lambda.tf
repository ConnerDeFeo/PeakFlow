# IAM role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "contact-form-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_role.name
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "contact-form-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["ses:SendEmail", "ses:SendRawEmail"]
        Resource = "*"
      }
    ]
  })
}

locals {
  lambdas = toset([
    "contact_form_handler",
    "auto_email_send"
  ])
}

data "archive_file" "lambda_zip" {
  for_each    = local.lambdas
  type        = "zip"
  source_file = "../lambda/${each.key}.py"
  output_path = "../lambda/zips/${each.key}.zip"
}

resource "aws_lambda_function" "lambda" {
  for_each         = local.lambdas
  filename         = "../lambda/zips/${each.key}.zip"
  function_name    = replace(each.key, "_", "-")
  role             = aws_iam_role.lambda_role.arn
  handler          = "${each.key}.lambda_handler"
  runtime          = "python3.12"
  source_code_hash = data.archive_file.lambda_zip[each.key].output_base64sha256
}

resource "aws_lambda_function_url" "lambda_url" {
  for_each           = local.lambdas
  function_name      = aws_lambda_function.lambda[each.key].function_name
  authorization_type = "NONE"

  cors {
    allow_origins = ["*"]
    allow_methods = ["*"]
    allow_headers = ["*"]
  }
}

resource "aws_apigatewayv2_api" "contact_api" {
  name          = "peak-flow-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["POST", "OPTIONS"]
    allow_headers = ["Content-Type"]
  }
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  for_each               = local.lambdas
  api_id                 = aws_apigatewayv2_api.contact_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.lambda[each.key].invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "lambda_route" {
  for_each  = local.lambdas
  api_id    = aws_apigatewayv2_api.contact_api.id
  route_key = "POST /${replace(each.key, "_", "-")}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration[each.key].id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.contact_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "api_gateway" {
  for_each      = local.lambdas
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda[each.key].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.contact_api.execution_arn}/*/*"
}

output "api_endpoints" {
  value = { for k in local.lambdas : k => "${aws_apigatewayv2_stage.default.invoke_url}${replace(k, "_", "-")}" }
}
