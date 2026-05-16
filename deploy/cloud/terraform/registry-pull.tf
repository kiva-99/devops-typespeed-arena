resource "yandex_iam_service_account" "registry_pull_sa" {
  name        = var.registry_pull_sa_name
  description = "Service account for pulling TypeSpeed images from Container Registry"
}

resource "yandex_resourcemanager_folder_iam_member" "registry_pull_images_puller" {
  folder_id = var.folder_id
  role      = "container-registry.images.puller"
  member    = "serviceAccount:${yandex_iam_service_account.registry_pull_sa.id}"
}

resource "yandex_iam_service_account_static_access_key" "registry_pull_static_key" {
  service_account_id = yandex_iam_service_account.registry_pull_sa.id
  description        = "Static access key for Docker login on app-node"
}

resource "yandex_iam_service_account_key" "registry_pull_authorized_key" {
  service_account_id = yandex_iam_service_account.registry_pull_sa.id
  description        = "Authorized key for yc CLI Docker credential helper on app-node"
}

output "registry_pull_authorized_key_json" {
  value = jsonencode({
    id                 = yandex_iam_service_account_key.registry_pull_authorized_key.id
    service_account_id = yandex_iam_service_account.registry_pull_sa.id
    created_at         = yandex_iam_service_account_key.registry_pull_authorized_key.created_at
    key_algorithm      = yandex_iam_service_account_key.registry_pull_authorized_key.key_algorithm
    public_key         = yandex_iam_service_account_key.registry_pull_authorized_key.public_key
    private_key        = yandex_iam_service_account_key.registry_pull_authorized_key.private_key
  })
  sensitive = true
}
