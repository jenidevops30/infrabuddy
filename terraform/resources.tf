# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.app_name}-lambda-exec-role"

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

# Read-only Telemetry & Bedrock Policy
resource "aws_iam_role_policy" "telemetry_policy" {
  name = "${var.app_name}-telemetry-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "ec2:Describe*",
          "elasticloadbalancing:Describe*",
          "autoscaling:Describe*",
          "rds:Describe*",
          "cloudwatch:GetMetricData",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics",
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "bedrock:Converse"
        ]
        Resource = "*"
      }
    ]
  })
}

# Lambda Function
resource "aws_lambda_function" "infrabuddy" {
  function_name = "${var.app_name}-agent"
  role          = aws_iam_role.lambda_role.arn
  handler       = "server.handler"
  runtime       = "python3.12"
  timeout       = 60
  memory_size   = 512

  filename         = "${path.module}/../infrabuddy_lambda.zip"
  source_code_hash = fileexists("${path.module}/../infrabuddy_lambda.zip") ? filebase64sha256("${path.module}/../infrabuddy_lambda.zip") : null

  environment {
    variables = {
      MODEL_PROVIDER       = var.model_provider
      MODEL_NAME           = var.model_name
      SLACK_BOT_TOKEN      = var.slack_bot_token
      SLACK_SIGNING_SECRET = var.slack_signing_secret
    }
  }
}

# HTTP API Gateway (v2)
resource "aws_apigatewayv2_api" "http_api" {
  name          = "${var.app_name}-http-api"
  protocol_type = "HTTP"
  target        = aws_lambda_function.infrabuddy.arn
}

# Permission for API Gateway to invoke Lambda
resource "aws_lambda_permission" "api_gw_permission" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.infrabuddy.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*"
}
