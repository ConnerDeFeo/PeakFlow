# Dynamo Tables
locals {
  tables = toset([
    "personal_appointments",
    "roofing_rochester_appointments",
    "adonis_roofing_appointments"
  ])
}

# Per customer data store for roofing appointments. Stores customer information and appointment details.
resource "aws_dynamodb_table" "appointment_tables" {
  for_each = local.tables
  name         = each.value
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "customer_phone_number"

  attribute {
    name = "customer_phone_number"
    type = "S"
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }
}