resource "yandex_vpc_network" "typespeed_network" {
  name = var.network_name
}

resource "yandex_vpc_subnet" "typespeed_subnet" {
  name           = var.subnet_name
  zone           = var.zone
  network_id     = yandex_vpc_network.typespeed_network.id
  v4_cidr_blocks = [var.subnet_cidr]
}

resource "yandex_container_registry" "typespeed_registry" {
  name = var.registry_name
}

resource "yandex_vpc_security_group" "app_sg" {
  name       = "typespeed-app-sg"
  network_id = yandex_vpc_network.typespeed_network.id

  ingress {
    protocol       = "TCP"
    description    = "HTTP public access"
    port           = 80
    v4_cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    protocol       = "TCP"
    description    = "HTTPS public access"
    port           = 443
    v4_cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    protocol       = "TCP"
    description    = "SSH from trusted IP"
    port           = 22
    v4_cidr_blocks = [var.my_ip_cidr]
  }

  ingress {
    protocol          = "TCP"
    description       = "Node Exporter access from monitoring node"
    port              = 9100
    security_group_id = yandex_vpc_security_group.monitoring_sg.id
  }

  ingress {
    protocol          = "TCP"
    description       = "cAdvisor access from monitoring node"
    port              = 8080
    security_group_id = yandex_vpc_security_group.monitoring_sg.id
  }

  egress {
    protocol       = "ANY"
    description    = "Allow all outbound traffic"
    v4_cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "yandex_vpc_security_group" "db_sg" {
  name       = "typespeed-db-sg"
  network_id = yandex_vpc_network.typespeed_network.id

  ingress {
    protocol          = "TCP"
    description       = "PostgreSQL from app security group"
    port              = 5432
    security_group_id = yandex_vpc_security_group.app_sg.id
  }

  ingress {
    protocol       = "TCP"
    description    = "SSH from trusted IP"
    port           = 22
    v4_cidr_blocks = [var.my_ip_cidr]
  }

  ingress {
    protocol          = "TCP"
    description       = "Node Exporter access from monitoring node"
    port              = 9100
    security_group_id = yandex_vpc_security_group.monitoring_sg.id
  }

  egress {
    protocol       = "ANY"
    description    = "Allow all outbound traffic"
    v4_cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "yandex_vpc_security_group" "monitoring_sg" {
  name       = "typespeed-monitoring-sg"
  network_id = yandex_vpc_network.typespeed_network.id

  ingress {
    protocol       = "TCP"
    description    = "SSH from trusted IP"
    port           = 22
    v4_cidr_blocks = [var.my_ip_cidr]
  }

  ingress {
    protocol       = "TCP"
    description    = "Grafana from trusted IP"
    port           = 3000
    v4_cidr_blocks = [var.my_ip_cidr]
  }

  ingress {
    protocol       = "TCP"
    description    = "Prometheus from trusted IP"
    port           = 9090
    v4_cidr_blocks = [var.my_ip_cidr]
  }

  ingress {
    protocol       = "TCP"
    description    = "Alertmanager from trusted IP"
    port           = 9093
    v4_cidr_blocks = [var.my_ip_cidr]
  }

  ingress {
    protocol          = "TCP"
    description       = "Loki push from app security group"
    port              = 3100
    v4_cidr_blocks    = ["10.10.10.35/32"]
  }

  egress {
    protocol       = "ANY"
    description    = "Allow all outbound traffic"
    v4_cidr_blocks = ["0.0.0.0/0"]
  }
}



