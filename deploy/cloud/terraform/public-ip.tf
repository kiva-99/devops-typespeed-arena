resource "yandex_vpc_address" "app_public_ip" {
  name = "typespeed-app-public-ip"

  external_ipv4_address {
    zone_id = var.zone
  }
}
