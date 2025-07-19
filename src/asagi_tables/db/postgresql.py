from .base_db import BasePlaceHolderGen
from . import conn_details, echo

async def get_connection():
	if not hasattr(get_connection, 'pool'):
		from asyncpg import create_pool
		get_connection.pool = await create_pool(**conn_details)
	return get_connection.pool

async def close_pool():
	if hasattr(get_connection, 'pool'):
		await get_connection.pool.close()
		del get_connection.pool

async def query_tuple(query: str, params: tuple=None):
		pool = await get_connection()

		async with pool.acquire() as conn:
			if echo:
				print('::SQL::', query)
				print('::PARAMS::', params)

			async with conn.transaction():
				await conn.execute(query, *params if params else [])

			# Record objects always returned
			# https://magicstack.github.io/asyncpg/current/api/index.html#record-objects
			# if dict_row:
			#     results = await conn.fetch(query, *params if params else [])
			#     return [dict(result) for result in results]
			return await conn.fetch(query, *params if params else [])

async def run_script(sql: str):
	await query_tuple(sql)

def on_conflict(column: str):
	return f'on conflict({column}) do update set'

class Phg(BasePlaceHolderGen):
	__slots__ = ('counter')

	def __init__(self):
		self.counter = 0

	def __call__(self) -> str:
		self.counter += 1
		return f'${self.counter}'

	def qty(self, count: int=1) -> str:
		start = self.counter + 1
		self.counter += count
		return ','.join(f'${i}' for i in range(start, start+count))
