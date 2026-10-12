output "api_endpoint" {
  description = "Base URL of HTTP API Gateway"
  value       = aws_apigatewayv2_api.http_api.api_endpoint
}

output "health_url" {
  description = "Health Check URL"
  value       = "${aws_apigatewayv2_api.http_api.api_endpoint}/health"
}

output "slack_events_url" {
  description = "Slack Request Webhook URL"
  value       = "${aws_apigatewayv2_api.http_api.api_endpoint}/slack/events"
}

output "teams_messages_url" {
  description = "Teams Messaging Endpoint URL"
  value       = "${aws_apigatewayv2_api.http_api.api_endpoint}/teams/messages"
}
