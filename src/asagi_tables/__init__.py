from .queries import (
	cmd_op_mapping as _cmd_ops,
	tabletype_modules as _modules_by_tt
)
from .queries.templates import (
	get_template as _get_template,
	render_template_many as _render_template,
)

__all__ = ['get_template', 'render_templates']

def get_template(db_type: str, table_type: str, entity: str, operation: str) -> str:
	if not (op := _cmd_ops.get(operation)):
		return ''
	if table_type not in _modules_by_tt:
		return ''
	module_name = f'{entity}_{op}'
	return _get_template(db_type, table_type, module_name)

def render_templates(template: str, boards: str|list[str]) -> str:
	if type(boards) is str:
		boards = [boards]
	return _render_template(template, boards)
