# Makefile — Lint Markdown and Python

MARKDOWN_FILES = $(shell find . -name "*.md")
PYTHON_FILES = $(shell find . -name "*.py")
DOCKER_IMAGE = buibui-bot

.PHONY: lint lint-md lint-py format format-py docker-build docker-run-price docker-run-position

lint: lint-md lint-py

lint-md:
	@echo "🔍 Running markdownlint..."
	markdownlint $(MARKDOWN_FILES)

lint-py:
	@echo "🧹 Checking Python formatting with black..."
	black --check $(PYTHON_FILES)

format: format-py

format-py:
	@echo "🎨 Formatting Python code with black..."
	black $(PYTHON_FILES)

docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t $(DOCKER_IMAGE) .

docker-run-price:
	@echo "🐳 Running price_monitor in Docker..."
	docker run --env-file .env $(DOCKER_IMAGE) poetry run python buibui.py monitor price

docker-run-position:
	@echo "🐳 Running position_monitor in Docker..."
	docker run --env-file .env $(DOCKER_IMAGE) poetry run python buibui.py monitor position
