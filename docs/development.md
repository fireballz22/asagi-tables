# Development
- Trying out `uv`

## Setup
```sh
uv venv # 3.12+

# activate your venv

uv pip install -r pyproject.toml --all-extras # all optional dependencies
uv pip install -e .
```

## Running
- Cli
```sh
asagi base|side ENTITY OPERATION BOARD1 [BOARD2 [BOARD3]...]
```

- Tests
```sh
pytest
```

- Lint
```sh
ruff check --fix
```

## Wheel
- Build
```sh
uv build --wheel # wheel in dist/
```

- Install
```sh
pip install dist/asagi_tables-0.1.0-py3-none-any.whl[sqlite] # change db and version as needed
```

## Cleanup
```sh
rm -rf dist build .pytest_cache .ruff_cache src/*.egg-info
fd -I __pycache__ . -x rm -r # fd installed
find . -type d -name __pycache__ -exec rm -r {} + # fd not installed
```
