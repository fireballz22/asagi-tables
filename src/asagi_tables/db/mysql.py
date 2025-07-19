from .base_db import BasePlaceHolderGen
from . import conn_details, echo

async def get_connection():
	if not hasattr(get_connection, 'pool'):
		from aiomysql import create_pool

		get_connection.pool = await create_pool(**conn_details, autocommit=True)
	return get_connection.pool

async def close_pool():
	if hasattr(get_connection, 'pool'):
		pool = await get_connection()
		pool.close()
		await pool.wait_closed()
		del get_connection.pool

async def query_tuple(query: str, params: tuple=None):
		pool = await get_connection()
		async with pool.acquire() as conn:
			async with conn.cursor() as cursor:
				if echo:
					final_sql = cursor.mogrify(query, params)
					print('::SQL::', final_sql, '')

				await cursor.execute(query, params)

				results = [await cursor.fetchall()]
				while await cursor.nextset():
					results.append(await cursor.fetchall())

				return results[0] if len(results) == 1 else results

async def run_script(sql: str):
	await query_tuple(sql)

def on_conflict(column: str):
	return f'as excluded on duplicate key update'

class Phg(BasePlaceHolderGen):
	__slots__ = ()

	def __call__(self) -> str:
		return '%s'
	
	def qty(self, count: int=1) -> str:
		return ','.join('%s' for _ in range(count))
