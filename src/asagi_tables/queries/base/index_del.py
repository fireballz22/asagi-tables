from . import (
	board as b,
	map_join_index,
)

mysql = map_join_index(
	lambda index: f"drop index {index.name} on `{b}`;"	
)

sqlite = map_join_index(
	lambda index: f"drop index if exists `{b}_{index.name}`;"
)

postgresql = sqlite.replace('`', '"')
