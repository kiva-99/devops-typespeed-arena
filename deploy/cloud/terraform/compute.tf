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

  service_account_id = yandex_iam_service_account.registry_pull_sa.id

  metadata = {
    ssh-keys = "ubuntu:${var.ssh_public_key}"

    user-data = <<-EOF
#cloud-config
package_update: true

packages:
  - curl
  - ca-certificates
  - gnupg
  - lsb-release

runcmd:
  - curl -fsSL https://get.docker.com | sh
  - usermod -aG docker ubuntu
  - curl -sSL https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash -s -- -i /opt/yandex-cloud -n
  - ln -sf /opt/yandex-cloud/bin/yc /usr/local/bin/yc
  - yc config profile create registry-pull || true
  - yc config set cloud-id ${var.cloud_id}
  - yc config set folder-id ${var.folder_id}
  - yc container registry configure-docker
  - mkdir -p /opt/typespeed-arena
  - chown -R ubuntu:ubuntu /opt/typespeed-arena
EOF
  }

  depends_on = [
    yandex_resourcemanager_folder_iam_member.registry_pull_images_puller
  ]

  scheduling_policy {
    preemptible = true
  }

  lifecycle {
    ignore_changes = [
      boot_disk[0].initialize_params[0].image_id
    ]
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

  lifecycle {
    ignore_changes = [
      boot_disk[0].initialize_params[0].image_id
    ]
  }
}

resource "yandex_compute_instance" "monitoring_node" {
  name        = "typespeed-monitoring-node"
  hostname    = "typespeed-monitoring-node"
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
    security_group_ids = [yandex_vpc_security_group.monitoring_sg.id]
  }

  metadata = {
    ssh-keys = "ubuntu:${var.ssh_public_key}"

    user-data = <<-EOF
#cloud-config
package_update: true

packages:
  - curl
  - ca-certificates
  - gnupg
  - lsb-release

runcmd:
  - curl -fsSL https://get.docker.com | sh
  - usermod -aG docker ubuntu
  - mkdir -p /opt/typespeed-monitoring
  - chown -R ubuntu:ubuntu /opt/typespeed-monitoring
EOF
  }

  scheduling_policy {
    preemptible = true
  }
}
