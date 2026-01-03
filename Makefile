.PHONY: default check test doc publish

default:
	@echo "Usage: make [check|test|doc|publish]"
	@exit 1

check:
	uvx ruff@0.14.10 check .
	uvx ruff@0.14.10 format --check .
	uvx mypy@1.19.1

test:
	source ./.venv/bin/activate && pytest

doc:
	source ./.venv/bin/activate && uv run sphinx-apidoc -o docs/source/references aztec_tool
	source ./.venv/bin/activate && cd ./docs && make html

publish:
	rm -rf dist/ aztec_tool.egg-info/
	uv build
	uvx twine check dist/*
	uv publish
