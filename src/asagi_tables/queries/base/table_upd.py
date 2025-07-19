from . import board as b

mysql = f"""
update `{b}`
inner join `{b}_images` using(media_hash)
set
	`{b}`.media_id = `{b}_images`.media_id
where
	`{b}`.media_hash is not null
	and `{b}`.media_id = 0;
"""

sqlite = f"""
update `{b}` set
	media_id = images.media_id
from (
	select media_hash, media_id
	from `{b}_images`
) as images
where
	`{b}`.media_hash is not null
	and `{b}`.media_id = 0
	and images.media_hash = `{b}`.media_hash;
"""

postgresql = f'''
update {b} set
	media_id = {b}_images.media_id
from {b}_images where
	{b}.media_hash is not null
	and {b}.media_id = 0
	and images.media_hash = {b}.media_hash;
'''