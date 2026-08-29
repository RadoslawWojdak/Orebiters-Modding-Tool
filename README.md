# Orebiters Modding Tool

A prototype modding tool for Orebiters built with Python and PySide6.

## Requirements

- Python 3.14
- uv

## Installation

Clone the repository and install the project dependencies:

```bash
uv sync
```

Install the Git hooks:

```bash
uv run pre-commit install
```

## Running the Application

```bash
uv run orebiters-modding-tool
```

## Development

Pre-commit hooks automatically run code quality checks before each commit.

To manually run all hooks:

```bash
uv run pre-commit run --all-files
```
