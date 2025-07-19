from . import (
	board as b,
	backup_suffix as suf,
)
mysql = f"rename table `{b}_{suf}` to `{b}`;"

sqlite = f"alter table `{b}_{suf}` rename to `{b}`;"

postgresql = f'alter table if exists "{b}_{suf}" rename to "{b}";'
