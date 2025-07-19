# Asagi Tables
- Python cli/lib to manage [Asagi schema](https://github.com/bibanon/asagi_schema) tables
- Supports mysql/mariadb, sqlite and postgresql(untested)

## Install
- Requires Python 3.12+
```bash
# from git
pip install "asagi-tables[sqlite] @ git+https://github.com/bibanon/asagi-tables.git"
pip install "asagi-tables[mysql] @ git+https://github.com/bibanon/asagi-tables.git@master"

# from release wheel
version="0.1.0"
pip install "asagi-tables[postgresql] @ https://github.com/bibanon/asagi-tables/releases/download/v$version/asagi_tables-$version-py3-none-any.whl"

# with uv
uv add git+https://github.com/bibanon/asagi-tables.git
uv add asagi-tables --optional mysql
```

## Cli
### Config file
- Copy `asagi.tpl.toml` to `asagi.toml` and adapt contents as needed
- If `asagi.toml` is not found in the current working directory, `config.toml` will be tried
	- Same keys used as in [Ayase-Quart](https://github.com/sky-cake/ayase-quart)

### Available commands
- `BOARD` is one or more boards
```sh
asagi base table add BOARD
asagi base table drop BOARD
asagi base table backup BOARD
asagi base table restore BOARD
asagi base table update BOARD
asagi base index add BOARD
asagi base index drop BOARD
asagi base trigger add BOARD
asagi base trigger drop BOARD
asagi side table add BOARD
asagi side table drop BOARD
asagi side table backup BOARD
asagi side table restore BOARD
asagi side table populate BOARD
asagi side index add BOARD
asagi side index drop BOARD
```

## Library
- No side table populating from here
- Use your own database connection to execute the rendered templates

```python
from asagi_tables import get_template, render_templates

template = get_template('mysql', 'side', 'table', 'backup')

rendered = render_templates(template, 'news')
print(rendered)

rendered_many = render_templates(template, ['g', 'ck', 'news'])
print(rendered_many)
```

## Development
- See [development.md](./docs/development.md)
