#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ANSIBLE_ROLES_PATH=./roles ansible-playbook -i inventory.ini -u ubuntu --private-key ~/.ssh/id_ed25519 playbooks/site.yml
