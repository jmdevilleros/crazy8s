#!/bin/bash
# run.sh - Ejecuta Crazy8s usando el entorno virtual local (.venv)
# No utiliza Python global.

cd "$(dirname "$0")" || exit 1

if [ ! -d ".venv" ]; then
    echo "❌ Error: No se encontró el entorno virtual .venv"
    echo "   Ejecuta primero:"
    echo "   python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt"
    exit 1
fi

echo "🎮 Ejecutando Crazy8s (usando .venv local)..."
./.venv/bin/python main.py
