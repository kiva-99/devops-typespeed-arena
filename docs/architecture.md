TypeSpeed Arena - Architecture Overview

1. ЦЕЛЬ ПРОЕКТА

TypeSpeed Arena — дипломный DevOps-проект.

Цель:
- автоматизированное развертывание приложения в облаке;
- управление инфраструктурой через Terraform;
- настройка серверов через Ansible;
- CI/CD через GitHub Actions;
- мониторинг и логирование;
- резервное копирование данных;
- безопасная и воспроизводимая инфраструктура.

--------------------------------------------------

2. ТЕКУЩЕЕ СОСТОЯНИЕ

Развернуто 3 виртуальные машины в Yandex Cloud:

1. app-node
2. db-node
3. monitoring-node

Также используются:

- VPC
- Subnet
- Security Groups
- Container Registry
- Object Storage

--------------------------------------------------

3. APP NODE

Назначение:

- frontend
- backend
- прием пользовательского трафика
- выполнение деплоя

Текущее состояние:

- nginx frontend
- backend container
- Docker Compose
- образы берутся из Yandex Container Registry

Сейчас приложение работает именно через Docker Compose.

--------------------------------------------------

4. DB NODE

Назначение:

- PostgreSQL
- хранение данных приложения

Реализовано:

- PostgreSQL установлен через Ansible
- отдельная VM
- доступ по внутреннему IP
- резервное копирование в Object Storage

--------------------------------------------------

5. MONITORING NODE

Назначение:

- мониторинг
- визуализация
- алертинг

Развернуто:

- Prometheus
- Grafana
- Alertmanager
- Blackbox Exporter
- Node Exporter

Мониторятся:

- app-node
- db-node
- monitoring-node
- HTTP endpoint приложения

--------------------------------------------------

6. CI/CD

CI:

GitHub Actions выполняет:

- checkout
- python compile check
- dependency install
- docker compose build
- запуск приложения
- health check
- smoke tests

CD:

GitHub Actions выполняет:

- сборку Docker image
- push в Container Registry
- подключение к app-node
- docker compose pull
- docker compose up -d
- health check

--------------------------------------------------

7. TERRAFORM

Terraform создает:

- сеть
- подсеть
- security groups
- container registry
- object storage
- service accounts
- app-node
- db-node
- monitoring-node

Проблема:

Состояние Terraform пока локальное.

Необходимо:

- вынести state в Object Storage
- настроить remote backend

--------------------------------------------------

8. ANSIBLE

Используемые роли:

common
docker
postgres
backup
app
logging
monitoring
node_exporter

Ansible отвечает за настройку всей инфраструктуры после создания Terraform.

--------------------------------------------------

9. РЕЗЕРВНОЕ КОПИРОВАНИЕ

Реализовано:

- pg_dump
- gzip
- загрузка в Object Storage
- cron запуск

Требуется:

- контроль восстановления
- периодическая проверка backup

--------------------------------------------------

10. МОНИТОРИНГ

Реализовано:

- Prometheus
- Grafana
- Alertmanager
- Node Exporter
- Blackbox Exporter

Требуется:

- alert rules
- уведомления
- расширение dashboard

--------------------------------------------------

11. ЛОГИРОВАНИЕ

Сейчас:

- backend пишет логи
- настроен logrotate

Целевая схема:

- Loki
- Promtail или Grafana Alloy
- Grafana для просмотра логов

ELK использовать в дипломе не планируется из-за ресурсов.

--------------------------------------------------

12. БЕЗОПАСНОСТЬ

Уже реализовано:

- Security Groups
- ограничение SSH
- отдельная DB VM
- GitHub открывает SSH только на время деплоя

Необходимо:

- убрать публичный IP с db-node
- перейти на OIDC вместо постоянного ключа YC
- использовать Vault/Secrets
- настроить HTTPS

--------------------------------------------------

13. KUBERNETES

Сейчас:

Docker Compose

Планируется:

k3s на app-node

Будет использоваться:

- Deployment
- Service
- Ingress
- ConfigMap
- Secret
- Liveness Probe
- Readiness Probe

Причина:

- автоматические rollout
- rollback
- управление версиями
- более правильная production архитектура

--------------------------------------------------

14. КРИТИЧЕСКИЕ НЕЗАКРЫТЫЕ ЗАДАЧИ

1. Remote Terraform State
2. k3s
3. Deploy по git SHA
4. Rollback
5. Blue/Green или Rolling Update
6. Loki
7. Secrets Management
8. Закрытие db-node от интернета
9. HTTPS
10. Домен

--------------------------------------------------

15. ЦЕЛЕВАЯ АРХИТЕКТУРА

Developer
    |
GitHub
    |
GitHub Actions
    |
Container Registry
    |
app-node (k3s)
    |
    +-- frontend
    +-- backend

db-node
    |
    +-- PostgreSQL
    +-- backups

monitoring-node
    |
    +-- Prometheus
    +-- Grafana
    +-- Alertmanager
    +-- Loki

--------------------------------------------------

16. БЛИЖАЙШИЙ ПЛАН

1. Запустить VM.
2. Проверить инфраструктуру.
3. Настроить remote Terraform state.
4. Подготовить k3s.
5. Перенести приложение в Kubernetes.
6. Переделать CD на git SHA.
7. Реализовать rollback.
8. Добавить Loki.
9. Закрыть db-node от интернета.
10. Настроить HTTPS и домен.

После этого диплом можно будет считать практически завершённым.