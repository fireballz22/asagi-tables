from ..configs import db_conf

db_type = db_conf['db_type']
conn_details = db_conf[db_type]
echo = db_conf.get('echo', False)

def get_db_module():
	match db_type:
		case 'mysql':
			from . import mysql as db_mod
		case 'sqlite':
			from . import sqlite as db_mod
		case 'postgresql':
			from . import postgresql as db_mod
		case _:
			raise ValueError(f'Invalid db_type: {db_type}')
	return db_mod

_db_mod = get_db_module()

run_script = _db_mod.run_script
Phg = _db_mod.Phg
on_conflict = _db_mod.on_conflict
query_tuple = _db_mod.query_tuple
close_pool = _db_mod.close_pool
