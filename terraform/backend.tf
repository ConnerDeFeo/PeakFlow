terraform {
    backend "s3" {
      bucket         = "peak-flow-ai-automation-tfstate"
      key            = "terraform.tfstate"
      region         = "us-east-2"
      use_lockfile   = true
      encrypt        = true
      profile        = "peak_flow_admin"
    }
}