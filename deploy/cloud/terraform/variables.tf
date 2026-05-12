variable "yc_service_account_key_file" {
  description = "Path to Yandex Cloud service account key file"
  type        = string
}

variable "cloud_id" {
  description = "Yandex Cloud ID"
  type        = string
}

variable "folder_id" {
  description = "Yandex Cloud Folder ID"
  type        = string
}

variable "zone" {
  description = "Yandex Cloud zone"
  type        = string
  default     = "ru-central1-a"
}

variable "network_name" {
  description = "VPC network name"
  type        = string
  default     = "typespeed-network"
}

variable "subnet_name" {
  description = "Subnet name"
  type        = string
  default     = "typespeed-subnet"
}

variable "subnet_cidr" {
  description = "Subnet CIDR"
  type        = string
  default     = "10.10.10.0/24"
}

variable "registry_name" {
  description = "Container Registry name"
  type        = string
  default     = "typespeed-registry"
}

variable "my_ip_cidr" {
  description = "Your public IP address in CIDR format for SSH access"
  type        = string
}

variable "backup_bucket_name" {
  description = "Object Storage bucket name for PostgreSQL backups"
  type        = string
}

variable "backup_sa_name" {
  description = "Service account name for backup uploads"
  type        = string
  default     = "typespeed-backup-sa"
}

variable "ssh_public_key" {
  description = "SSH public key for VM access"
  type        = string
}

variable "vm_image_family" {
  description = "Ubuntu image family"
  type        = string
  default     = "ubuntu-2204-lts"
}

variable "vm_platform_id" {
  description = "VM platform"
  type        = string
  default     = "standard-v3"
}
