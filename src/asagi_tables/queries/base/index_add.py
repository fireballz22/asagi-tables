from . import (
	board as b,
	TI,
	map_join_index,
)

def mysql_t(ti: TI):
	unique = ' unique' if ti.unique else ''
	columns = ', '.join(f'`{col}`' for col in ti.colummns)
	return f'alter table `{b}` add{unique} index {ti.name} ({columns});'
mysql = map_join_index(mysql_t)


def sqlite_t(ti: TI):
	unique = 'unique ' if ti.unique else ''
	columns = ', '.join(f'`{col}`' for col in ti.colummns)
	return f'create {unique}index if not exists `{b}_{ti.name}` on `{b}`({columns});'
sqlite = map_join_index(sqlite_t)


def postgresql_t(ti: TI):
	return f'create index if not exists {b}_{ti.name} on {b} ({ti.colummns[0]});'
postgresql = map_join_index(postgresql_t)
