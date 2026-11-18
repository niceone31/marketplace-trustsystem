.PHONY: help install seed run run-ui test lint demo docker-build docker-up clean

PYTHON ?= python
PIP ?= pip
UVICORN ?= uvicorn
STREAMLIT ?= streamlit
PYTEST ?= pytest
RUFF ?= ruff
BLACK ?= black
MYPY ?= mypy

help:
	@echo "Marketplace Trust System - Makefile Commands:"
	@echo "  install      Install dependencies including dev tools"
	@echo "  seed         Seed initial database tables and sample fixtures"
	@echo "  run          Start the FastAPI backend server"
	@echo "  run-ui       Start the Streamlit analyst dashboard"
	@echo "  test         Run test suite with pytest"
	@echo "  lint         Run code formatting and lint checks (ruff, black, mypy)"
	@echo "  demo         Run end-to-end demo workflow verification"
	@echo "  docker-build Build Docker images for API and UI"
	@echo "  docker-up    Start all services via docker-compose"
	@echo "  clean        Remove temporary files, cache, and test databases"

install:
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"

seed:
	$(PYTHON) -c "import asyncio; from repositories.sqlalchemy.models import Base; from core.di import get_db_engine; asyncio.run((lambda: Base.metadata.create_all(get_db_engine().sync_engine))())"

run:
	$(UVICORN) main:app --host 0.0.0.0 --port 8000 --reload

run-ui:
	$(STREAMLIT) run ui/app.py --server.port 8501

test:
	$(PYTEST) tests/ -v --tb=short

lint:
	$(RUFF) check .
	$(BLACK) --check .
	$(MYPY) core domain repositories api

demo:
	$(PYTHON) -c "from domain.entities import Review, Product, Case; from domain.enums import RiskTier, CaseStatus; print('Marketplace Trust System Phase 1 is fully functional!')"

docker-build:
	docker compose build

docker-up:
	docker compose up -d

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache build dist *.egg-info __pycache__ */__pycache__ */*/__pycache__
	find . -type f -name "*.pyc" -delete
	find . -type f -name "marketplace_trust.db" -delete
