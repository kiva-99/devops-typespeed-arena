output "network_id" {
  value = yandex_vpc_network.typespeed_network.id
}

output "subnet_id" {
  value = yandex_vpc_subnet.typespeed_subnet.id
}

output "registry_id" {
  value = yandex_container_registry.typespeed_registry.id
}

output "app_security_group_id" {
  value = yandex_vpc_security_group.app_sg.id
}

output "db_security_group_id" {
  value = yandex_vpc_security_group.db_sg.id
}

output "monitoring_security_group_id" {
  value = yandex_vpc_security_group.monitoring_sg.id
}

output "backup_bucket_name" {
  value = yandex_storage_bucket.backup_bucket.bucket
}

output "backup_service_account_id" {
  value = yandex_iam_service_account.backup_sa.id
}

output "backup_access_key" {
  value     = yandex_iam_service_account_static_access_key.backup_sa_static_key.access_key
  sensitive = true
}

output "backup_secret_key" {
  value     = yandex_iam_service_account_static_access_key.backup_sa_static_key.secret_key
  sensitive = true
}

output "registry_pull_access_key" {
  value     = yandex_iam_service_account_static_access_key.registry_pull_static_key.access_key
  sensitive = true
}

output "registry_pull_secret_key" {
  value     = yandex_iam_service_account_static_access_key.registry_pull_static_key.secret_key
  sensitive = true
}

output "app_node_public_ip" {
  value = yandex_compute_instance.app_node.network_interface[0].nat_ip_address
}

output "app_node_private_ip" {
  value = yandex_compute_instance.app_node.network_interface[0].ip_address
}

output "db_node_public_ip" {
  value = yandex_compute_instance.db_node.network_interface[0].nat_ip_address
}

output "db_node_private_ip" {
  value = yandex_compute_instance.db_node.network_interface[0].ip_address
}

output "monitoring_node_public_ip" {
  value = yandex_compute_instance.monitoring_node.network_interface[0].nat_ip_address
}

output "monitoring_node_private_ip" {
  value = yandex_compute_instance.monitoring_node.network_interface[0].ip_address
}
