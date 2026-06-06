terraform {
  backend "s3" {
    bucket = "typespeed-tfstate-b1g04tcucevnnibrg2r7"
    key    = "terraform/terraform.tfstate"
    region = "ru-central1"

    endpoints = {
      s3 = "https://storage.yandexcloud.net"
    }

    skip_region_validation      = true
    skip_credentials_validation = true
    skip_requesting_account_id  = true
    skip_s3_checksum            = true
  }
}
