from . import board as b

mysql = f'alter table {b} add constraint {b}_media_id_fk foreign key (media_id) references {b}_images(media_id);'

sqlite = f''

postgresql = f"alter table {b} add constraint {b}_media_id_fk foreign key (media_id) references {b}_images(media_id);"
