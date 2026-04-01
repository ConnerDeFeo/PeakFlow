# Security group for the EC2 instance
resource "aws_security_group" "voice_bot_sg" {
  name        = "voice-bot-sg"
  description = "Allow SSH and HTTP access to voice bot server"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "voice-bot-sg"
  }
}

# Make an t3 small EC2 instance
resource "aws_instance" "receptionist" {
  ami           = "ami-0edc0a81903bf24ef"
  instance_type = "t3.small"

  key_name = "voice-bot-key"

  vpc_security_group_ids = [aws_security_group.voice_bot_sg.id]

  tags = {
    Name = "voice-bot-server"
  }
}

# Elastic IP for the EC2 instance
resource "aws_eip" "voice_bot_eip" {
  instance = aws_instance.receptionist.id
  domain   = "vpc"

  tags = {
    Name = "voice-bot-eip"
  }
}

output "server_ip" {
  value = aws_eip.voice_bot_eip.public_ip
}