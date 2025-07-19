from . import queries as q
from queries.templates import (
	get_template,
	render_template,
)

def test_command_operations():
	assert 'backup' in q.cmd_op_mapping

def test_get_template():
	template = get_template('mysql', 'base', 'table_bak')
	assert template.startswith('rename table `')
	assert template.endswith('`;')

def test_render_template():
	t = get_template('mysql', 'base', 'table_bak')
	r = render_template(t, 'hi')
	assert r == 'rename table `hi` to `hi_bak`;'
