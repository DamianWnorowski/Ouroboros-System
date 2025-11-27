# Ouroboros System - Makefile
# Common tasks and operations

.PHONY: help install test verify generate start stop clean deploy

help: ## Show this help message
	@echo "Ouroboros System - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install --upgrade pip
	pip install -r requirements.txt
	pre-commit install

test: ## Run tests
	pytest tests/ -v --cov=core --cov=agents --cov-report=term-missing

test-watch: ## Run tests in watch mode
	pytest-watch tests/

verify: ## Run Oracle verification
	python -m core.verification.cli --level 6

verify-quick: ## Quick verification (L0-L2)
	python -m core.verification.cli --level 2

generate: ## Generate from example DNA
	python -m core.generators.cli --dna examples/generator-dna-example.yaml --output ./generated

start: ## Start orchestrator
	python -m core.orchestrator

start-api: ## Start REST API server
	python -m core.api

start-docker: ## Start with Docker Compose
	docker-compose up -d

stop: ## Stop Docker Compose
	docker-compose down

clean: ## Clean generated files and caches
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf generated
	rm -rf dist
	rm -rf build

lint: ## Run linters
	flake8 core agents tests --count --select=E9,F63,F7,F82 --show-source --statistics
	black --check core agents tests
	isort --check-only core agents tests
	mypy core agents

format: ## Format code
	black core agents tests
	isort core agents tests

deploy: ## Deploy to Kubernetes
	kubectl apply -f deployment/kubernetes/

deploy-dev: ## Deploy to development
	./scripts/deploy.sh development

deploy-prod: ## Deploy to production
	./scripts/deploy.sh production

docker-build: ## Build Docker image
	docker build -t ouroboros/orchestrator:latest .

docker-push: ## Push Docker image (requires registry)
	docker tag ouroboros/orchestrator:latest registry.example.com/ouroboros/orchestrator:latest
	docker push registry.example.com/ouroboros/orchestrator:latest

setup: install ## Full setup (install + pre-commit)
	@echo "Setup complete!"

ci: lint test verify ## Run CI checks locally

chain-all: ## Run full command chain (all phases)
	@echo "Running full command chain..."
	@if [ -f scripts/chain-all.sh ]; then \
		chmod +x scripts/chain-all.sh && ./scripts/chain-all.sh; \
	else \
		python scripts/auto-chain.py; \
	fi

auto-chain: ## Run auto-recursive chain AI
	python scripts/auto-chain.py

onboard: ## Complete onboarding setup
	@if [ -f scripts/onboard.sh ]; then \
		chmod +x scripts/onboard.sh && ./scripts/onboard.sh; \
	else \
		echo "Onboarding script not found"; \
	fi

health: ## Quick health check
	@if [ -f scripts/health-check.sh ]; then \
		chmod +x scripts/health-check.sh && ./scripts/health-check.sh; \
	else \
		python -c "from core.orchestrator import DynamicOrchestrator; print('OK')"; \
	fi

all: clean install test verify ## Clean, install, test, and verify

