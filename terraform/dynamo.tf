# terraform/dynamo.tf
resource "aws_dynamodb_table" "twilio_conversations" {
  name         = "twilio_conversations"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "call_sid"

  attribute {
    name = "call_sid"
    type = "S"
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }
}