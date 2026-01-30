# Makefile for Multi-Agent Interview Coach

.PHONY: install run validate test help

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies from requirements.txt"
	@echo "  make run      - Start the main application"
	@echo "  make validate - Validate the structure of interview_log.json"
	@echo "  make test     - Run a simple smoke test"

install:
	pip install -r requirements.txt

run:
	python main.py

validate:
	python validate_logs.py

test:
	@echo "Running smoke test..."
	python -c "import graph; print('✅ Graph compiled successfully'); import main; print('✅ Main logic loaded')"
