# TypeSpeed Arena — архитектура дипломного проекта

## 1. Цель проекта

TypeSpeed Arena — это веб-приложение для тренировки скорости печати.

Само приложение намеренно сделано достаточно простым. Основной фокус дипломного проекта — не сложная бизнес-логика, а демонстрация DevOps-практик:

- Git и ветвление;
- GitHub Actions;
- Docker;
- Docker Compose;
- Infrastructure as Code;
- Yandex Cloud;
- Terraform;
- Ansible;
- Kubernetes / k3s;
- резервное копирование;
- мониторинг;
- логирование;
- домен и HTTPS.

---

## 2. Принятое архитектурное решение

Для диплома выбран путь дешёвой, но достаточно взрослой архитектуры на двух виртуальных машинах.

Мы не используем fully managed-подход на первом этапе, потому что Managed Kubernetes и Managed PostgreSQL могут заметно увеличить стоимость проекта.

Вместо этого мы показываем больше самостоятельной DevOps-работы:

- сами создаём инфраструктуру через Terraform;
- сами настраиваем серверы через Ansible;
- сами поднимаем k3s;
- сами настраиваем PostgreSQL;
- сами настраиваем бэкапы;
- сами строим CI/CD.

---

## 3. Целевая схема

```text
Пользователь
    |
    v
typespeedarena.ru
    |
    v
app-node VM
    |
    +-- k3s
    +-- Ingress Nginx
    +-- frontend
    +-- backend
    |
    v
db-node VM
    |
    +-- PostgreSQL
    +-- backup scripts
    +-- cron
    |
    v
Yandex Object Storage
    |
    +-- database backups
4. Виртуальная машина app-node

Назначение:

запуск лёгкого Kubernetes-кластера k3s;
запуск frontend;
запуск backend;
приём входящего HTTP/HTTPS-трафика;
работа Ingress-контроллера;
публикация приложения наружу через домен.

Планируемая конфигурация:

2 vCPU
2 GB RAM
20 GB disk
preemptible = true
Ubuntu 22.04

Почему app-node может быть preemptible:

приложение в основном stateless;
frontend/backend можно пересоздать;
код хранится в GitHub;
Docker-образы будут храниться в Container Registry;
инфраструктура описана в Terraform;
настройка сервера будет автоматизирована через Ansible.
5. Виртуальная машина db-node

Назначение:

запуск PostgreSQL;
хранение результатов тестов;
хранение текстов для печати;
выполнение резервного копирования;
загрузка бэкапов в Object Storage.

Планируемая конфигурация:

2 vCPU
2 GB RAM
20-30 GB disk
отдельный data disk — желательно
preemptible = false — желательно
Ubuntu 22.04

Почему БД вынесена отдельно:

база данных является stateful-компонентом;
данные важнее, чем контейнеры приложения;
приложение и БД не мешают друг другу по ресурсам;
проще объяснить разделение stateless/stateful;
проще настроить отдельную стратегию бэкапов.
6. Почему не одна ВМ

Одна ВМ дешевле и проще, но для диплома хуже:

приложение и база данных смешаны;
хуже демонстрируется архитектурное мышление;
сложнее показать разделение ответственности;
сбой одной машины ломает сразу всё;
сложнее объяснить backup strategy.

Поэтому выбран компромисс: две минимальные ВМ.

7. Почему не полностью managed-сервисы

Managed Kubernetes и Managed PostgreSQL дают меньше ручной работы и лучше подходят для production.

Но для диплома у них есть минусы:

выше стоимость;
меньше демонстрации самостоятельной настройки;
меньше практики администрирования;
сложнее уложиться в бюджет.

Поэтому на первом этапе используем:

self-hosted k3s
self-hosted PostgreSQL
Object Storage для бэкапов
Container Registry для Docker-образов
Cloud DNS / домен для внешнего доступа
8. Git workflow

В проекте используются ветки:

main      — production/stable
develop   — dev/staging
feature/* — рабочие ветки под задачи

Текущая рабочая ветка:

feature/jenkins-setup

Логика движения изменений:

feature/* -> develop -> main
9. CI/CD

Сейчас уже настроен GitHub Actions CI.

Он проверяет:

синтаксис Python-кода;
установку backend-зависимостей;
сборку Docker-образа backend;
запуск Docker Compose;
доступность /health;
доступность /api/texts;
корректную остановку контейнеров.

Целевое состояние CI/CD:

push в feature/*
    -> CI проверки

merge/push в develop
    -> CI
    -> build Docker image
    -> push image в Yandex Container Registry
    -> deploy в dev/staging

merge/push в main
    -> CI
    -> build Docker image
    -> push image в Yandex Container Registry
    -> deploy в production
10. Terraform

Terraform будет управлять облачной инфраструктурой в Yandex Cloud.

Планируемые ресурсы:

сеть VPC;
подсеть;
security groups;
app-node VM;
db-node VM;
Container Registry;
Object Storage bucket для бэкапов;
сервисные аккаунты;
IAM-роли;
outputs для Ansible и CI/CD.
11. Ansible

Ansible будет настраивать созданные виртуальные машины.

app-node:

установка базовых пакетов;
установка k3s;
настройка kubectl;
установка Ingress Nginx;
подготовка окружения для деплоя приложения.

db-node:

установка PostgreSQL;
создание базы данных;
создание пользователя;
настройка доступа только с app-node;
настройка backup script;
настройка cron;
загрузка бэкапов в Object Storage.
12. Kubernetes / k3s

В Kubernetes будут описаны:

namespace;
backend Deployment;
frontend Deployment;
Services;
Ingress;
ConfigMap;
Secrets;
livenessProbe;
readinessProbe.
13. Backup strategy

Бэкапы PostgreSQL будут храниться вне db-node.

План:

pg_dump
    -> сжатый backup-файл
    -> загрузка в Yandex Object Storage
    -> хранение нескольких последних копий

Это нужно, чтобы восстановить данные даже при потере db-node.

14. Мониторинг и логирование

Планируемый мониторинг:

Prometheus;
Grafana;
node-exporter;
PostgreSQL exporter.

Минимальное логирование:

docker logs;
kubectl logs.

Расширенное логирование:

Loki;
Promtail;
Grafana.
15. Текущий статус

Уже сделано:

Flask backend;
HTML/JS frontend;
Nginx reverse proxy;
Docker Compose для локального запуска;
PostgreSQL контейнер локально;
backend Dockerfile;
.dockerignore;
внешний файл texts.json;
healthcheck /health;
API /api/texts;
GitHub Actions CI;
отдельный каталог Yandex Cloud для диплома.

Следующие шаги:

создать Terraform-структуру;
описать provider;
описать переменные;
создать Container Registry;
создать сеть;
создать подсеть;
создать security groups.