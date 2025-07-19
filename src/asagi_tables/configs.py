from functools import cache
from os.path import exists as path_exists
import tomllib

conf_file = 'asagi.toml'
alt_conf_file = 'config.toml'


def load_config() -> dict:
	if path_exists(conf_file):
		return _load_config_toml(conf_file)
	elif path_exists(alt_conf_file):
		return _load_config_toml(alt_conf_file)
	raise FileNotFoundError("No config file found in current working directory")

@cache
def _load_config_toml(filename: str) -> dict:
	with open(filename, 'rb') as f:
		return tomllib.load(f)

conf = load_config()
db_conf = conf['db']
