from . import board as b

mysql = f'alter table {b} drop foreign key {b}_media_id_fk;'

sqlite = f''

postgresql = f"alter table {b} drop constraint {b}_media_id_fk;"
