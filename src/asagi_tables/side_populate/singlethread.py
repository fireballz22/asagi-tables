from typing import Iterable
from tqdm import tqdm
from tqdm.asyncio import tqdm as tqdm_a

from . import (
	RowProcessor,
	board_rows_gen,
	insert_sidetable_fresh,
	SideTable,
	media_row_gen,
	thread_row_gen,
	thread_columns,
	media_columns,
	BATCH_THREADS,
	BATCH_IMAGES,
)

def batch_total(collection: Iterable, batch_size: int) -> int:
	quotient, remainder = divmod(len(collection), batch_size)
	if remainder:
		quotient += 1
	return quotient

async def aggregate_posts(board: str, after_doc_id: int=0):
	row_processor = RowProcessor()
	async for row_batch in tqdm_a(board_rows_gen(board, after_doc_id), desc=f'load posts'):
		row_processor.process_rows(row_batch)
	return row_processor

async def populate_single_thread(boards: list[str]):
	if not boards:
		return
	for board in boards:
		print('Populating:', board)

		rp = await aggregate_posts(board)
		threads, medias = rp.threads, rp.medias

		for row_batch in tqdm(thread_row_gen(threads), desc=f'insert threads', total=batch_total(threads, BATCH_THREADS)):
			await insert_sidetable_fresh(SideTable.threads, thread_columns, board, row_batch)
		
		for row_batch in tqdm(media_row_gen(medias), desc=f'insert medias', total=batch_total(medias, BATCH_IMAGES)):
			await insert_sidetable_fresh(SideTable.media, media_columns, board, row_batch)
