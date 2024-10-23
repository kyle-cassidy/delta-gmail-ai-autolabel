# Project Name

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
make setup
```

3. Run tests:
```bash
make test
```

## Development

- Format code: `make format`
- Run linters: `make lint`
- Run tests: `make test`

## Project Structure

```
.
├── config/          # Configuration files
├── docs/           # Documentation
├── notebooks/      # Jupyter notebooks
├── output/         # Generated files
├── src/            # Source code
├── tests/          # Test files
└── requirements/   # Dependencies
```
