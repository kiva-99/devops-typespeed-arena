data "yandex_compute_image" "ubuntu" {
  family = var.vm_image_family
}

resource "yandex_compute_instance" "app_node" {
  name        = "typespeed-app-node"
  hostname    = "typespeed-app-node"
  platform_id = var.vm_platform_id
  zone        = var.zone

  allow_stopping_for_update = true

  resources {
    cores         = 2
    memory        = 2
    core_fraction = 20
  }

  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.ubuntu.id
      size     = 20
      type     = "network-hdd"
    }
  }

  network_interface {
    subnet_id          = yandex_vpc_subnet.typespeed_subnet.id
    nat                = true
    security_group_ids = [yandex_vpc_security_group.app_sg.id]
  }

  metadata = {
    ssh-keys = "ubuntu:${var.ssh_public_key}"
  }

  scheduling_policy {
    preemptible = true
  }
}

resource "yandex_compute_instance" "db_node" {
  name        = "typespeed-db-node"
  hostname    = "typespeed-db-node"
  platform_id = var.vm_platform_id
  zone        = var.zone

  allow_stopping_for_update = true

  resources {
    cores         = 2
    memory        = 2
    core_fraction = 20
  }

  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.ubuntu.id
      size     = 30
      type     = "network-hdd"
    }
  }

  network_interface {
    subnet_id          = yandex_vpc_subnet.typespeed_subnet.id
    nat                = true
    security_group_ids = [yandex_vpc_security_group.db_sg.id]
  }

  metadata = {
    ssh-keys = "ubuntu:${var.ssh_public_key}"
  }

  scheduling_policy {
    preemptible = false
  }
}
