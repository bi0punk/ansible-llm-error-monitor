#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
ANSIBLE_CONFIG=./ansible.cfg ansible-playbook playbooks/site.yml
