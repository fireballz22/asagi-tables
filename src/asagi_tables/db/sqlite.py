from .base_db import BasePlaceHolderGen
from . import conn_details, echo

async def get_connection():
	if not hasattr(get_connection, 'pool'):
		import aiosqlite
		pool = await aiosqlite.connect(conn_details.get('database'))
		get_connection.pool = pool
	return get_connection.pool

async def close_pool():
	if hasattr(get_connection, 'pool'):
		await get_connection.pool.close()
		del get_connection.pool

async def query_tuple(query: str, params: tuple=None):
		pool = await get_connection()
		if echo:
			print('::SQL::', query)
			print('::PARAMS::', params)

		async with pool.execute(query, params) as cursor:
			results = await cursor.fetchall()
			await pool.commit()
			return results

async def run_script(query: str):
		pool = await get_connection()
		if echo:
			print('::SQL::', query)

		await pool.executescript(query)
		await pool.commit()

def on_conflict(column: str):
	return f'on conflict({column}) do update'

class Phg(BasePlaceHolderGen):
	__slots__ = ()

	def __call__(self) -> str:
		return '?'
	
	def qty(self, count: int=1) -> str:
		return ','.join('?' for _ in range(count))
