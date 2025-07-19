from typing import Callable
from . import (
	board as b,
)

def nl_map(keys: tuple[str], fn: Callable):
	return '\n'.join(fn(k) for k in keys)

mysql_triggers = (
	'before_ins',
	'after_ins',
	'after_del',
)
mysql_functions = (
	'create_thread',
	'delete_thread',
	'update_thread',
	'insert_image',
	'delete_image',
)
mysql =	nl_map(mysql_triggers,
	lambda t: f'drop trigger if exists `{t}_{b}`;'
) + '\n' + nl_map(mysql_functions,
	lambda f: f'drop procedure if exists `{f}_{b}`;'
)

sqlite_triggers = (
	'before_ins_media_op',
	'before_ins_media_reply',
	'after_ins_media',
	'after_ins_op',
	'after_ins_reply',
	'after_ins_reply_ghost',
	'after_del_media',
	'after_del_op',
	'after_del_reply',
	'after_del_reply_ghost',
)
sqlite = nl_map(sqlite_triggers, lambda t: f'drop trigger if exists `{b}_{t}`;')

postgresql_triggers = (
	'after_delete',
	'before_insert',
	'after_insert',
)
postgresql_functions = (
	'update_thread',
	'create_thread',
	'delete_thread',
	'insert_image',
	'delete_image',
	'insert_post',
	'delete_post',
	'before_insert',
	'after_insert',
	'after_del',
)
postgresql = nl_map(postgresql_triggers,
	lambda t: f'drop trigger if exists {b}_{t} on {b};'
) + '\n' + nl_map(postgresql_functions,
	lambda f: f'drop function if exists {b}_{f};'
)
