from . import (
	board as b,
	TI,
	map_join_index,
)

def st(table: str):
	return f'{b}_{table}'

def mysql_t(table: str, ti: TI):
	unique = ' unique' if ti.unique else ''
	columns = ', '.join(f'`{col}`' for col in ti.colummns)
	return f'alter table `{st(table)}` add{unique} index `{ti.name}` ({columns});'
mysql = map_join_index(mysql_t)

def sqlite_t(table: str, ti: TI):
	unique = 'unique ' if ti.unique else ''
	index = f'{b}_{table}_{ti.name}'
	columns = ', '.join(f'`{col}`' for col in ti.colummns)
	return f'create {unique}index if not exists `{index}` on `{b}_{table}`({columns});'
sqlite = map_join_index(sqlite_t)

def postgresql_t(table: str, ti: TI):
	t = st(table)
	index = f'{t}_{ti.name}'
	return f'create index if not exists {index} on {t} ({ti.colummns[0]});'
postgresql = map_join_index(postgresql_t)
