# Makefile — Lint Markdown and Python

MARKDOWN_FILES = $(shell find . -name "*.md")
PYTHON_FILES = $(shell find . -name "*.py")

.PHONY: lint lint-md lint-py format format-py

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
