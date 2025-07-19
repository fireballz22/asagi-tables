from . import (
	board as b,
	map_join_table,
	backup_suffix as suf,
)

mysql = map_join_table(
	lambda st: f"rename table `{b}_{st}` to `{b}_{st}_{suf}`;"
)

sqlite = map_join_table(
	lambda st: f"alter table `{b}_{st}` rename to `{b}_{st}_{suf}`;"
)

postgresql = map_join_table(
	lambda st: f'alter table if exists "{b}_{st}" rename to "{b}_{st}_{suf}";'
)
