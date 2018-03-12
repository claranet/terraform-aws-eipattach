terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "aws" {
  region = "eu-west-1"
}

resource "aws_vpc" "test" {
  cidr_block = "10.255.255.0/24"

  tags {
    Name = "terraform-aws-eipattach-test"
  }
}

resource "aws_internet_gateway" "test" {
  vpc_id = "${aws_vpc.test.id}"
}

resource "aws_subnet" "test" {
  vpc_id     = "${aws_vpc.test.id}"
  cidr_block = "${aws_vpc.test.cidr_block}"
}

resource "aws_route_table" "test" {
  vpc_id = "${aws_vpc.test.id}"

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = "${aws_internet_gateway.test.id}"
  }
}

resource "aws_route_table_association" "test" {
  subnet_id      = "${aws_subnet.test.id}"
  route_table_id = "${aws_route_table.test.id}"
}

resource "aws_eip" "test_ignore" {
  tags {
    Ignore = "IGNOREME"
  }
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

resource "aws_launch_configuration" "test" {
  name          = "test"
  image_id      = "ami-25e7705c"
  instance_type = "t2.nano"
}

module "eip" {
  source = "../"
}
