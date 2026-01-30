.PHONY: run cli test lint docker-up docker-down validate smoke help

# Default target
help:
	@echo "Available commands:"
	@echo "  make run          - Run Streamlit web interface"
	@echo "  make cli          - Run CLI interface"
	@echo "  make test         - Run all tests with pytest"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo "  make lint         - Check code with ruff"
	@echo "  make smoke        - Run smoke tests (imports only)"
	@echo "  make validate     - Validate interview log format"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make install      - Install all dependencies"

# Run Streamlit UI
run:
	streamlit run streamlit_app.py

# Run CLI version
cli:
	python main.py

# Run all tests
test:
	pytest tests/ -v --tb=short

# Run tests with coverage
test-cov:
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing
	@echo "Coverage report: htmlcov/index.html"

# Lint code with Ruff
lint:
	ruff check . --output-format=full
	ruff format --check .

# Format code
format:
	ruff format .
	ruff check --fix .

# Smoke test (imports only)
smoke:
	python smoke_test.py

# Validate log format
validate:
	python validate_logs.py interview_log_1.json

# Docker operations
docker-up:
	docker-compose up --build -d
	@echo "App available at http://localhost:8501"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Install dependencies
install:
	pip install -r requirements.txt
	@echo "Dependencies installed successfully!"

# Clean artifacts
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleaned up!"
