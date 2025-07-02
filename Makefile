# Makefile — Lint Markdown using markdownlint-cli

MARKDOWN_FILES = $(shell find . -name "*.md")

.PHONY: lint

lint:
	@echo "🔍 Running markdownlint..."
	markdownlint $(MARKDOWN_FILES)