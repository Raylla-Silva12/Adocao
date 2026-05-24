.PHONY: help install dev test lint format clean deploy-local deploy-gcp

help:
	@echo "Adoção de Pets - Backend Flask"
	@echo ""
	@echo "Comandos disponíveis:"
	@echo "  make install         - Instala as dependências"
	@echo "  make dev             - Inicia servidor de desenvolvimento com Docker Compose"
	@echo "  make dev-local       - Inicia servidor sem Docker (requer PostgreSQL local)"
	@echo "  make test            - Executa os testes"
	@echo "  make test-cov        - Executa testes com cobertura"
	@echo "  make lint            - Valida o código com flake8"
	@echo "  make format          - Formata o código com black"
	@echo "  make clean           - Remove arquivos temporários"
	@echo "  make db-init         - Inicializa o banco de dados"
	@echo "  make db-seed         - Popula o banco com dados iniciais"
	@echo "  make db-reset        - Reseta o banco de dados"
	@echo "  make docker-build    - Faz build da imagem Docker"
	@echo "  make docker-run      - Executa a imagem Docker"
	@echo "  make deploy-gcp      - Faz deploy no Google Cloud Run"

install:
	pip install -r requirements.txt

dev:
	docker-compose up

dev-down:
	docker-compose down

dev-local:
	FLASK_ENV=development flask --app app run --host 0.0.0.0 --port 8080

test:
	pytest

test-cov:
	pytest --cov=app --cov-report=html

lint:
	flake8 app tests

format:
	black app tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov .tox dist build *.egg-info

db-init:
	python manage_db.py init-db

db-seed:
	python seed.py

db-reset:
	python manage_db.py reset-db

docker-build:
	docker build -t adocao-gatos:latest .

docker-run:
	docker run -p 8080:8080 \
		-e DB_HOST=localhost \
		-e DB_USER=postgres \
		-e DB_PASSWORD=postgres \
		-e DB_NAME=adocao_gatos \
		-e JWT_SECRET_KEY=sua-chave-secreta \
		adocao-gatos:latest

deploy-gcp:
	@read -p "Enter GCP Project ID: " PROJECT_ID; \
	./deploy.sh $$PROJECT_ID

logs:
	docker-compose logs -f app

shell:
	docker-compose exec app /bin/bash

# Alias úteis
build: docker-build
run: docker-run
up: dev
down: dev-down
serve: dev-local
t: test
l: lint
f: format
