from asagi_tables.db import mysql, sqlite, postgresql

def test_phg_mysql():
	Phg = mysql.Phg
	phg = Phg()
	one = phg()
	four = phg.qty(4)
	three = phg.size((1,2,3))
	instant = Phg()()
	assert one == '%s'
	assert four == '%s,%s,%s,%s'
	assert three == '%s,%s,%s'
	assert instant == '%s'

def test_phg_sqlite():
	Phg = sqlite.Phg
	phg = Phg()
	one = phg()
	four = phg.qty(4)
	three = phg.size((1,2,3))
	instant = Phg()()
	assert one == '?'
	assert four == '?,?,?,?'
	assert three == '?,?,?'
	assert instant == '?'

def test_phg_postgresql():
	Phg = postgresql.Phg
	phg = Phg()
	one = phg()
	four = phg.qty(4)
	one_again = phg()
	three = phg.size((1,2,3))
	instant = Phg()()
	assert one == '$1'
	assert four == '$2,$3,$4,$5'
	assert one_again == '$6'
	assert three == '$7,$8,$9'
	assert instant == '$1'
