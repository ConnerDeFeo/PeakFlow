# Define local map for Lambda function locations
locals {
  lambdas = {
    "AutoSMSReply" = {
      source_dir  = "../lambdas/AutoSMSReply"
      output_path = "../lambdas/zips/AutoSMSReply.zip"
      layers      = ["twilio"]
    }
  }
  layers = {
    "twilio" = {
      source_dir  = "../layers/twilio/python"
      output_path = "../layers/twilio/twilio.zip"
    },
  }
}

# Data layers
data "archive_file" "lambda_layers" {
  for_each    = local.layers
  type        = "zip"
  source_dir  = each.value.source_dir
  output_path = each.value.output_path
}

resource "aws_lambda_layer_version" "lambda_layers" {
  for_each            = local.layers
  filename            = data.archive_file.lambda_layers[each.key].output_path
  layer_name          = each.key
  compatible_runtimes = ["python3.12"]
  source_code_hash    = data.archive_file.lambda_layers[each.key].output_base64sha256
}

# Archive files using for_each
data "archive_file" "lambda_archives" {
  for_each = local.lambdas
  
  type        = "zip"
  source_dir  = each.value.source_dir
  output_path = each.value.output_path
}

resource "aws_lambda_function" "lambdas" {
  for_each = local.lambdas

  function_name    = each.key
  role             = aws_iam_role.ai_automation_lambda_role.arn
  handler          = "${each.key}.${each.key}"
  runtime          = "python3.12"
  filename         = data.archive_file.lambda_archives[each.key].output_path
  source_code_hash = data.archive_file.lambda_archives[each.key].output_base64sha256
  timeout          = 500
  memory_size      = 512

  environment {
    variables = {
      TWILIO_ACCOUNT_SID = var.twilio_account_sid
      TWILIO_AUTH_TOKEN  = var.twilio_auth_token
    }
  }

  layers           = [for layer_name in each.value.layers : aws_lambda_layer_version.lambda_layers[layer_name].arn]
}

# Create Lambda function URLs
resource "aws_lambda_function_url" "lambda_urls" {
  for_each = aws_lambda_function.lambdas

  function_name = each.value.function_name
  authorization_type = "NONE"
}

# Output Lambda function URLs
output "lambda_function_urls" {
  value = { for key, lambda in aws_lambda_function_url.lambda_urls : key => lambda.function_url }
}