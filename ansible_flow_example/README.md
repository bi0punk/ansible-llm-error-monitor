# Proyecto base Ansible para pruebas locales

Base mínima para probar ejecuciones Ansible en Linux sobre `localhost`.
Está pensada como punto de partida para luego integrar captura de errores y diagnóstico con LLM.

## Estructura

```text
ansible_llm_base/
├── ansible.cfg
├── inventory.ini
├── group_vars/
│   └── all.yml
├── playbooks/
│   └── site.yml
├── roles/
│   └── demo/
│       ├── defaults/
│       │   └── main.yml
│       └── tasks/
│           └── main.yml
├── callback_plugins/
├── scripts/
│   ├── check_prereqs.sh
│   ├── run_ok.sh
│   ├── run_fail_assert.sh
│   └── run_fail_command.sh
└── requirements.txt
```

## Requisitos

- Linux
- Python 3.10+ recomendado
- Ansible instalado

Instalación rápida con `pip`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## Verificar entorno

```bash
./scripts/check_prereqs.sh
```

## Ejecutar caso exitoso

```bash
./scripts/run_ok.sh
```

Eso debe:
- mostrar datos del host
- crear `/tmp/ansible_llm_base`
- crear `/tmp/ansible_llm_base/healthcheck.txt`
- terminar sin errores

## Ejecutar fallo controlado por comando

```bash
./scripts/run_fail_command.sh
```

Esto fuerza un fallo real con `/bin/false`.

## Ejecutar fallo controlado por assert

```bash
./scripts/run_fail_assert.sh
```

Esto fuerza un fallo lógico con `assert`.

## Ejecución manual

Caso OK:

```bash
ANSIBLE_CONFIG=./ansible.cfg ansible-playbook playbooks/site.yml
```

Caso con fallo:

```bash
ANSIBLE_CONFIG=./ansible.cfg ansible-playbook playbooks/site.yml -e simulate_failure=true -e failure_mode=command
```

## Variables principales

Definidas en `group_vars/all.yml`:

- `project_name`: nombre del proyecto
- `workspace_dir`: directorio de trabajo
- `simulate_failure`: activa o no el fallo controlado
- `failure_mode`: `command` o `assert`
- `sample_file_name`: archivo de prueba

## Siguiente fase sugerida

Cuando esta base ya esté corriendo, el siguiente paso natural es agregar un callback plugin en `callback_plugins/` para capturar `runner_on_failed` y `runner_on_unreachable`, y enviar el error a un servicio de diagnóstico LLM.
