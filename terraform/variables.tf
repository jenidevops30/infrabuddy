variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS Region for deployment"
}

variable "app_name" {
  type        = string
  default     = "infrabuddy"
  description = "Application name prefix"
}

variable "model_provider" {
  type        = string
  default     = "bedrock"
  description = "LLM provider: bedrock or sample"
}

variable "model_name" {
  type        = string
  default     = "amazon.nova-pro-v1:0"
  description = "Bedrock Model ID"
}

variable "slack_bot_token" {
  type        = string
  default     = ""
  sensitive   = true
  description = "Slack Bot OAuth Token (xoxb-...)"
}

variable "slack_signing_secret" {
  type        = string
  default     = ""
  sensitive   = true
  description = "Slack Signing Secret"
}
