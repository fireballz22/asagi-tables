from . import (
	board as b,
	backup_suffix as suf,
)

mysql = f"rename table `{b}` to `{b}_{suf}`;"

sqlite = f"alter table `{b}` rename to `{b}_{suf}`;"

postgresql = f'alter table if exists "{b}" rename to "{b}_{suf}";'
