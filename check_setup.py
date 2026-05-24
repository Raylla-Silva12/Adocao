#!/usr/bin/env python3
"""
Script para verificar se o projeto está corretamente configurado.
Execute com: python check_setup.py
"""

import os
import sys
from pathlib import Path

def check_file(path, description):
    """Verifica se um arquivo existe."""
    exists = Path(path).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}")
    return exists

def check_directory(path, description):
    """Verifica se um diretório existe."""
    exists = Path(path).is_dir()
    status = "✅" if exists else "⚠️"
    print(f"{status} {description}")
    return exists

def main():
    """Executa todas as verificações."""
    print("=" * 60)
    print("🔍 Verificando Configuração do Projeto")
    print("=" * 60)
    print()
    
    checks = {
        "files": [
            ("app.py", "Entry point da aplicação"),
            ("seed.py", "Script de inicialização do banco"),
            ("manage_db.py", "CLI para gerenciar banco de dados"),
            ("requirements.txt", "Dependências Python"),
            (".env.example", "Template de variáveis"),
            (".gitignore", "Arquivos ignorados pelo Git"),
            ("Dockerfile", "Container para Cloud Run"),
            ("docker-compose.yml", "Orquestração local"),
            ("cloudbuild.yaml", "CI/CD do Google Cloud"),
            ("app.yaml", "Configuração do App Engine"),
            ("Makefile", "Comandos úteis"),
            ("gunicorn_config.py", "Configuração do Gunicorn"),
            ("deploy.sh", "Script de deploy (Unix)"),
            ("deploy.bat", "Script de deploy (Windows)"),
            ("insomnia_collection.json", "Collection para API"),
            ("README_NEW.md", "Documentação principal"),
            ("QUICKSTART.md", "Guia rápido"),
            ("BACKEND.md", "Documentação completa"),
            ("ARCHITECTURE.md", "Padrões e design"),
            ("CLOUD_SQL.md", "Guia do Cloud SQL"),
            ("SUMMARY.md", "Resumo da implementação"),
        ],
        "directories": [
            ("app", "Código principal da aplicação"),
            ("app/api", "Blueprints com rotas"),
            ("app/utils", "Utilitários e validação"),
            ("tests", "Testes unitários"),
        ],
        "python_files": [
            ("app/__init__.py", "Inicializador do pacote app"),
            ("app/config.py", "Configurações por ambiente"),
            ("app/extensions.py", "Extensões do Flask"),
            ("app/models.py", "Modelos SQLAlchemy"),
            ("app/auth.py", "Lógica de autenticação"),
            ("app/api/__init__.py", "Inicializador de blueprints"),
            ("app/api/auth.py", "Endpoints de autenticação"),
            ("app/api/pets.py", "Endpoints de CRUD"),
            ("app/utils/__init__.py", "Inicializador de utils"),
            ("app/utils/errors.py", "Classes de erro"),
            ("app/utils/uploads.py", "Gerenciamento de uploads"),
            ("app/utils/validators.py", "Validação de dados"),
            ("tests/__init__.py", "Inicializador de testes"),
            ("tests/test_api.py", "Testes de endpoints"),
        ]
    }
    
    results = {
        "files": 0,
        "directories": 0,
        "python_files": 0,
    }
    
    print("📁 Arquivos de Configuração e Documentação")
    print("-" * 60)
    for filepath, desc in checks["files"]:
        if check_file(filepath, desc):
            results["files"] += 1
    print()
    
    print("📂 Diretórios")
    print("-" * 60)
    for dirpath, desc in checks["directories"]:
        if check_directory(dirpath, desc):
            results["directories"] += 1
    print()
    
    print("🐍 Arquivos Python")
    print("-" * 60)
    for filepath, desc in checks["python_files"]:
        if check_file(filepath, desc):
            results["python_files"] += 1
    print()
    
    # Resumo
    total_expected = len(checks["files"]) + len(checks["directories"]) + len(checks["python_files"])
    total_found = results["files"] + results["directories"] + results["python_files"]
    
    print("=" * 60)
    print(f"📊 Resumo: {total_found}/{total_expected} itens encontrados")
    print("=" * 60)
    print()
    
    if total_found == total_expected:
        print("✅ PROJETO COMPLETO! Tudo pronto para começar.")
        print()
        print("🚀 Próximos passos:")
        print("   1. Leia QUICKSTART.md para começar em 5 minutos")
        print("   2. Execute: docker-compose up")
        print("   3. Acesse: http://localhost:8080")
        print()
        return 0
    else:
        print(f"⚠️  Faltam {total_expected - total_found} arquivos/diretórios")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
