from typing import Callable

from .. import (
	BOARD, BACKUP_SUFFIX,
	TableIndex as TI,
)

board = BOARD
backup_suffix = BACKUP_SUFFIX

table_indexes = [
	TI('num_subnum_index', ['num', 'subnum'], True),
	TI('thread_num_subnum_index', ['thread_num', 'num', 'subnum']),
	TI('subnum_index', ['subnum']),
	TI('op_index', ['op']),
	TI('media_id_index', ['media_id']),
	TI('media_hash_index', ['media_hash']),
	TI('media_orig_index', ['media_orig']),
	TI('name_trip_index', ['name', 'trip']),
	TI('trip_index', ['trip']),
	TI('email_index', ['email']),
	TI('poster_ip_index', ['poster_ip']),
	TI('timestamp_index', ['timestamp']),
]

def map_join_index(fn: Callable):
	return '\n'.join(
		fn(index)
		for index in table_indexes
	)
