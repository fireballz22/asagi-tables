from importlib import import_module
from os.path import (
	dirname,
	normpath,
	sep as path_sep,
)

from . import (
	tabletype_modules,
	BOARD,
)

ROOT_NESTING = 2
def get_package_path() -> str:
	parent_path = dirname(__file__)
	parts = normpath(parent_path).split(path_sep)
	levels = parts[-ROOT_NESTING:]
	return '.'.join(levels)

PKG_NAME = get_package_path()
def get_template(db_type: str, table_type: str, module_name: str) -> str:
	mod_path = f'{PKG_NAME}.{table_type}.{module_name}'
	try:
		module = import_module(mod_path)
		template = getattr(module, db_type).strip()
	except Exception as e:
		print(e)
		template = ''
	return template

# not used anywhere
def load_all_templates(db_type: str) -> dict:
	template_d = {}
	for table_type, modules in tabletype_modules.items():
		for mod_name in modules:
			key = f'{table_type}_{mod_name}'
			template_d[key] = get_template(db_type, table_type, mod_name)	

	return template_d

def render_template(template: str, board: str):
	return template.replace(BOARD, board)

def render_template_many(template: str, boards: list[str]):
	return '\n'.join(
		template.replace(BOARD, board)
		for board in boards	
	)
