.PHONY: setup lint format test

setup:
	git config core.hooksPath .githooks
	@echo "Git hooks configured."

lint:
	python3 -m ruff check .

format:
	python3 -m ruff format --check .

test:
	python3 -m pytest tests/ -v --cov=scripts --cov-report=term-missing --cov-fail-under=90
