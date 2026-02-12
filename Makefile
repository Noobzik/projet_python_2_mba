# Configuration Makefile pour Windows PowerShell
# Utiliser avec: make <target>

.PHONY: help install install-dev test test-unit test-features lint format typecheck clean run build docker-build docker-run

help:
	@echo "Commandes disponibles:"
	@echo "  make install        - Installer les dépendances"
	@echo "  make install-dev    - Installer les dépendances de développement"
	@echo "  make test           - Exécuter tous les tests"
	@echo "  make test-unit      - Exécuter les tests pytest"
	@echo "  make test-features  - Exécuter les tests unittest"
	@echo "  make lint           - Vérifier le code avec flake8"
	@echo "  make format         - Formater le code avec black"
	@echo "  make typecheck      - Vérifier les types avec mypy"
	@echo "  make clean          - Nettoyer les fichiers temporaires"
	@echo "  make run            - Démarrer l'API"
	@echo "  make build          - Construire le package"
	@echo "  make docker-build   - Construire l'image Docker"
	@echo "  make docker-run     - Exécuter avec Docker"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

test:
	pytest --cov=banking_api --cov-report=term-missing --cov-report=html
	python -m unittest discover tests/features

test-unit:
	pytest --cov=banking_api --cov-report=term-missing

test-features:
	python -m unittest discover tests/features

lint:
	flake8 banking_api/ tests/

format:
	black banking_api/ tests/
	isort banking_api/ tests/

typecheck:
	mypy banking_api/

clean:
	Remove-Item -Recurse -Force __pycache__, .pytest_cache, .mypy_cache, htmlcov, dist, build, *.egg-info -ErrorAction SilentlyContinue
	Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
	Get-ChildItem -Recurse -Filter "*.pyo" | Remove-Item -Force

run:
	uvicorn banking_api.main:app --reload

build:
	python -m build

docker-build:
	docker build -t banking-api:latest .

docker-run:
	docker run -p 8000:8000 banking-api:latest

check:
	python check_setup.py
