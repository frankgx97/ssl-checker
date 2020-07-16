provider "aws" {}

variable "accountId" {
  type = string
}

resource "aws_cloudwatch_event_rule" "one_day" {
  name                = "one_day"
  description         = "Fires every one day"
  schedule_expression = "rate(1 day)"
}

resource "aws_cloudwatch_event_target" "trigger_every_day" {
  rule      = "${aws_cloudwatch_event_rule.one_day.name}"
  target_id = "ssl_checker_lambda"
  arn       = "${aws_lambda_function.ssl_checker_lambda.arn}"
}

resource "aws_lambda_permission" "allow_cloudwatch_trigger_lambda" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.ssl_checker_lambda.function_name}"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.one_day.arn}"
}


resource "aws_lambda_function" "ssl_checker_lambda" {
  filename      = "lambda.zip"
  function_name = "ssl_checker_lambda"
  role          = "${aws_iam_role.role.arn}"
  #role          = "arn:aws:iam:${var.accountId}:root"
  handler = "ssl_checker.handler"
  runtime = "python3.7"

  # The filebase64sha256() function is available in Terraform 0.11.12 and later
  # For Terraform 0.11.11 and earlier, use the base64sha256() function and the file() function:
  # source_code_hash = "${base64sha256(file("lambda.zip"))}"
  source_code_hash = "${filebase64sha256("lambda.zip")}"
}

resource "aws_iam_role" "role" {
  name = "ssl_checker_lambda"

  assume_role_policy = <<EOF
{
   "Version": "2012-10-17",
   "Statement": [
     {
       "Action": "sts:AssumeRole",
       "Principal": {
         "Service": "lambda.amazonaws.com"
       },
       "Effect": "Allow",
       "Sid": ""
     }
   ]
 }
 EOF
}

terraform {
  backend "s3" {
    # Replace this with your bucket name!
    bucket         = "terraform-state-ssl-checker"
    key            = "global/s3/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-lock-ssl-checker"
    encrypt        = true
  }
}