# Define local map for Lambda function locations
locals {
  lambdas = {
    "AutoSMSReply" = {
      source_dir  = "../lambdas/AutoSMSReply"
      output_path = "../lambdas/zips/AutoSMSReply.zip"
      layers      = ["twilio"]
    },
    "AskForConsent" = {
      source_dir  = "../lambdas/AskForConsent"
      output_path = "../lambdas/zips/AskForConsent.zip"
      layers      = ["twilio"]
    },
    "ConsentAnswer" = {
      source_dir  = "../lambdas/ConsentAnswer"
      output_path = "../lambdas/zips/ConsentAnswer.zip"
      layers      = ["twilio"]
    },
    "Receptionist" = {
      source_dir  = "../lambdas/Receptionist"
      output_path = "../lambdas/zips/Receptionist.zip"
      layers      = ["twilio"]
    }

  }
  layers = {
    "twilio" = {
      source_dir  = "../layers/twilio/"
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
  handler          = "${each.key}.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.lambda_archives[each.key].output_path
  source_code_hash = data.archive_file.lambda_archives[each.key].output_base64sha256
  timeout          = 500
  memory_size      = 512

  environment {
    variables = {
      TWILIO_ACCOUNT_SID = var.twilio_account_sid
      TWILIO_AUTH_TOKEN  = var.twilio_auth_token
      RECEPTIONIST_LAMBDA_URL = var.receptionist_lambda_url
    }
  }

  layers           = [for layer_name in each.value.layers : aws_lambda_layer_version.lambda_layers[layer_name].arn]
}

# Create Lambda function URLs
resource "aws_lambda_function_url" "lambda_urls" {
  for_each = aws_lambda_function.lambdas

  function_name = each.value.function_name
  authorization_type = "NONE"

  cors {
    allow_origins = ["*"]
    allow_methods = ["POST", "GET"]
    allow_headers = ["*"]
  }
}

# Allow public invoke of lambda function URLs
resource "aws_lambda_permission" "allow_public_invoke" {
  for_each = aws_lambda_function.lambdas

  statement_id           = "AllowPublicAccess-${each.key}"
  action                 = "lambda:InvokeFunctionUrl"
  function_name          = each.value.function_name
  principal              = "*"
  function_url_auth_type = "NONE"
}

# Allow public invoke function
resource "aws_lambda_permission" "allow_public_invoke_function" {
  for_each = aws_lambda_function.lambdas

  statement_id  = "AllowPublicInvoke-${each.key}"
  action        = "lambda:InvokeFunction"
  function_name = each.value.function_name
  principal     = "*"
}

# Output Lambda function URLs
output "lambda_function_urls" {
  value = { for key, lambda in aws_lambda_function_url.lambda_urls : key => lambda.function_url }
}