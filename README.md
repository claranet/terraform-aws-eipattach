# terraform-aws-eipattach

Terraform module to automatically attach an Elastic IP address to an instance on startup.

This module will automatically attach an appropriately tagged Elastic IP address to an
appropriately tagged AWS instance when that instance is created (presumably via autoscaling).

## License

MIT

## Usage examples

### Simple

Give the instance tagged `EIP foobar` the EIP tagged `EIP foobar`

```hcl
module "eipattach" {
  source = "claranet/eipattach/aws"
}

resource "aws_eip" "test" {
  tags {
    EIP = "foobar"
  }
}

resource "aws_autoscaling_group" "test" {
  name                 = "test"
  max_size             = 1
  min_size             = 1
  launch_configuration = "${aws_launch_configuration.test.name}"
  vpc_zone_identifier  = ["${aws_subnet.test.id}"]

  tag {
    key                 = "EIP"
    value               = "foobar"
    propagate_at_launch = true
  }
}
```

### Machines with multiple ENIs

If you have machines with multiple ENIs, you must tag the ENI appropriately rather
than the instance:

```hcl
resource "aws_eip" "test_eni" {
  tags {
    EIP = "barbaz"
  }
}

resource "aws_network_interface" "test_eni" {
subnet_id = "${aws_subnet.test.id}"

  tags {
    EIP = "barbaz"
  }
}
```

## Contributing

Please submit pull requests at https://github.com/claranet/terraform-aws-eipattach/

The README.md is generated with
[terraform-docs](https://github.com/segmentio/terraform-docs) - to generate run
`terraform-docs md . > README.md`



## Inputs

| Name | Description | Default | Required |
|------|-------------|:-----:|:-----:|
| name | Name to use for resources | `terraform-aws-eipattach` | no |
| schedule | Schedule for running the Lambda function | `rate(1 minute)` | no |
| tag_name | Tag to use to associate EIPs with instances | `EIP` | no |
| timeout | Lambda function timeout | `60` | no |

