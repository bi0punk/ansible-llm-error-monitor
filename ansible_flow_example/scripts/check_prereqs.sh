#!/usr/bin/env bash
set -euo pipefail

echo "[INFO] Verificando entorno..."
command -v python3 >/dev/null 2>&1 || { echo "[ERROR] python3 no está instalado"; exit 1; }
command -v ansible-playbook >/dev/null 2>&1 || { echo "[ERROR] ansible-playbook no está instalado"; exit 1; }

echo "[OK] python3: $(python3 --version 2>&1)"
echo "[OK] ansible-playbook: $(ansible-playbook --version | head -n 1)"
