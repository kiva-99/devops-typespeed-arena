resource "yandex_iam_service_account" "backup_sa" {
  name        = var.backup_sa_name
  description = "Service account for uploading PostgreSQL backups to Object Storage"
}

resource "yandex_resourcemanager_folder_iam_member" "backup_storage_editor" {
  folder_id = var.folder_id
  role      = "storage.editor"
  member    = "serviceAccount:${yandex_iam_service_account.backup_sa.id}"
}

resource "yandex_iam_service_account_static_access_key" "backup_sa_static_key" {
  service_account_id = yandex_iam_service_account.backup_sa.id
  description        = "Static access key for PostgreSQL backup uploads"
}

resource "yandex_storage_bucket" "backup_bucket" {
  bucket     = var.backup_bucket_name
  access_key = yandex_iam_service_account_static_access_key.backup_sa_static_key.access_key
  secret_key = yandex_iam_service_account_static_access_key.backup_sa_static_key.secret_key

  max_size = 1073741824

  anonymous_access_flags {
    read        = false
    list        = false
    config_read = false
  }
}
