from typing import Callable

from .. import (
	BOARD, BACKUP_SUFFIX,
	TableIndex as TI,
)

board = BOARD
backup_suffix = BACKUP_SUFFIX
sidetables = ('daily', 'deleted', 'images', 'threads', 'users')

table_indexes = dict(
	threads=(
		TI('time_op_index', ['time_op']),
		TI('time_bump_index', ['time_bump']),
		TI('time_ghost_bump_index', ['time_ghost_bump']),
		TI('time_last_modified_index', ['time_last_modified']),
		TI('sticky_index', ['sticky']),
		TI('locked_index', ['locked']),
	),
	images=(
		TI('media_hash_index', ['media_hash'], True),
		TI('total_index', ['total']),
		TI('banned_index', ['banned']),
	),
	users=(
		TI('name_trip_index', ['name', 'trip'], True),
		TI('firstseen_index', ['firstseen']),
		TI('postcount_index', ['postcount']),
	),
)

def map_join_table(fn: Callable[[str], str]):
	return '\n'.join(
		fn(st) for st in sidetables
	)

def map_join_index(fn: Callable[[str, TI], str]):
	return '\n'.join(
		fn(table, index)
		for table, indices in table_indexes.items()
		for index in indices
	)
