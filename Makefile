.PHONY: lint test test-cov clean help

help:
	@echo "Commandes disponibles:"
	@echo "  make lint       - Vérifier le code avec flake8"
	@echo "  make test       - Lancer tous les tests (pytest + unittest)"
	@echo "  make test-cov   - Lancer tests avec couverture"
	@echo "  make clean      - Nettoyer fichiers temporaires"

lint:
	@echo "Vérification PEP8 avec flake8..."
	flake8 banking_api/ tests/ tests_unittest/

test:
	@echo "Lancement des tests pytest..."
	pytest tests/ -v
	@echo "\nLancement des tests unittest..."
	python -m unittest discover tests_unittest -v

test-cov:
	@echo "Tests avec couverture de code..."
	pytest tests/ --cov=banking_api/services --cov-report=term --cov-report=html

clean:
	@echo "Nettoyage..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	@echo "Nettoyage terminé!"
