from . import board as b

mysql = f"drop table if exists `{b}`;"

sqlite = mysql

postgresql = mysql.replace('`', '"')
