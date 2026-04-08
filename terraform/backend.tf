terraform {
    backend "s3" {
      bucket         = "ai-automation-tfstate"
      key            = "terraform.tfstate"
      region         = "us-east-2"
      use_lockfile   = true
      encrypt        = true
      profile        = "default"
    }
}