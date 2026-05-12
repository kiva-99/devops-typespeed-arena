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
