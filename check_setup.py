#!/usr/bin/env python3
"""
Verifica se a estrutura essencial do projeto está presente.
Execute com: python check_setup.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent


def check(path: str, description: str) -> bool:
    exists = (ROOT / path).exists()
    print(f"{'OK' if exists else 'MISSING'} {description}")
    return exists


def main() -> int:
    print("=" * 60)
    print("Verificando estrutura do projeto")
    print("=" * 60)
    print()

    required = [
        ("app.py", "Entry point"),
        ("app/factory.py", "Factory Flask"),
        ("app/config.py", "Configurações"),
        ("app/models.py", "Modelos"),
        ("requirements.txt", "Dependências"),
        (".env.example", "Template de variáveis"),
        ("Dockerfile", "Container"),
        ("docker-compose.yml", "Orquestração local"),
        ("seed.py", "Seed do banco"),
        ("manage_db.py", "CLI do banco"),
        ("tests/test_api.py", "Testes da API"),
        ("README.md", "Documentação principal"),
        ("docs/QUICKSTART.md", "Guia rápido"),
        ("docs/BACKEND.md", "Documentação da API"),
        ("scripts/setup-cloud-sql.sh", "Setup GCP (Unix)"),
        ("scripts/setup-cloud-sql.ps1", "Setup GCP (Windows)"),
    ]

    found = sum(check(path, desc) for path, desc in required)

    print()
    print("=" * 60)
    print(f"Resumo: {found}/{len(required)} itens encontrados")
    print("=" * 60)

    if found == len(required):
        print()
        print("Projeto OK. Próximo passo: docker-compose up")
        return 0

    print()
    print(f"Faltam {len(required) - found} item(ns).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
