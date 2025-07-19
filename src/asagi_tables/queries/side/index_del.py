from . import (
	board as b,
	map_join_index,
)

mysql = map_join_index(
	lambda table, index: f'drop index `{index.name}` on `{b}_{table}`;'
)

sqlite = map_join_index(
	lambda table, index: f'drop index if exists `{b}_{table}_{index.name}`;'
)

postgresql = sqlite.replace('`', '"')
