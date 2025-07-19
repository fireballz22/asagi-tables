from dataclasses import dataclass

BOARD = '%%BOARD%%'
BACKUP_SUFFIX = 'bak'

entities = ('table', 'index', 'trigger', 'fk')
cmd_op_mapping = dict(
	add='add',
	drop='del',
	backup='bak',
	restore='res',
	update='upd',
	populate='populate', # validation only
)

tabletype_modules = dict(
	base=(
		'table_add',
		'table_del',
		'table_bak',
		'table_res',
		'table_upd',
		'index_add',
		'index_del',
		'trigger_add',
		'trigger_del',
	),
	side=(
		'table_add',
		'table_del',
		'table_bak',
		'table_res',
		'index_add',
		'index_del',
		'fk_add',
		'fk_del',
	)
)

@dataclass(slots=True) # frozen=True?
class TableIndex:
	name: str
	colummns: list[str]
	unique: bool = False
