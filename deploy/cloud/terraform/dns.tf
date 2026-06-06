resource "yandex_dns_zone" "typespeedarena_zone" {
  name        = "typespeedarena-zone"
  description = "Public DNS zone for TypeSpeed Arena domain"
  zone        = "typespeedarena.ru."
  public      = true
}

resource "yandex_dns_recordset" "typespeedarena_root_a" {
  zone_id = yandex_dns_zone.typespeedarena_zone.id
  name    = "typespeedarena.ru."
  type    = "A"
  ttl     = 300
  data = [
    yandex_compute_instance.app_node.network_interface[0].nat_ip_address
  ]
}

resource "yandex_dns_recordset" "typespeedarena_www_a" {
  zone_id = yandex_dns_zone.typespeedarena_zone.id
  name    = "www.typespeedarena.ru."
  type    = "A"
  ttl     = 300
  data = [
    yandex_compute_instance.app_node.network_interface[0].nat_ip_address
  ]
}

resource "yandex_dns_recordset" "typespeedarena_globalsign_txt" {
  zone_id = yandex_dns_zone.typespeedarena_zone.id
  name    = "_globalsign-domain-verification.typespeedarena.ru."
  type    = "TXT"
  ttl     = 300
  data = [
    "globalsign-domain-verification=Z7w30wzIrr4y9d1HdtU8NmRvT5NxYU5k147tlNr8lG"
  ]
}

resource "yandex_dns_recordset" "typespeedarena_cdn_cname" {
  zone_id = yandex_dns_zone.typespeedarena_zone.id
  name    = "cdn.typespeedarena.ru."
  type    = "CNAME"
  ttl     = 3600
  data = [
    "7aae7b166e022b18.topology.gslb.yccdn.ru."
  ]
}
