from . import (
	board as b,
	map_join_table,
)

mysql = map_join_table(
	lambda table: f'drop table if exists `{b}_{table}`;'
)

sqlite = mysql

postgresql = mysql.replace('`', '"')
