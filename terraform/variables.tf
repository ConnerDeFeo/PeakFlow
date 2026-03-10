variable "twilio_account_sid" {
  description = "Twilio Account SID for sending SMS messages"
  type        = string
  sensitive   = true
}

variable "twilio_auth_token" {
  description = "Twilio Auth Token for sending SMS messages"
  type        = string
  sensitive   = true
}
