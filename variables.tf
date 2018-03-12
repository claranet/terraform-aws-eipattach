variable "name" {
  description = "Name to use for resources"
  default     = "terraform-aws-eipattach"
}

variable "tag_name" {
  description = "Tag to use to associate EIPs with instances"
  default     = "EIP"
}

variable "schedule" {
  description = "Schedule for running the Lambda function"
  default     = "rate(1 minute)"
}

variable "timeout" {
  description = "Lambda function timeout"
  default     = "60"
}

variable "dryrun" {
  description = "If true, don't actually attach EIPs"
  default     = false
}
