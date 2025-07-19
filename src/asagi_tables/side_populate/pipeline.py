from asyncio import (
	Queue as QueueA,
	create_task,
	CancelledError,
	sleep,
)
from itertools import batched

from tqdm import tqdm
from tqdm.asyncio import tqdm as tqdm_a

from . import (
	BATCH_POSTS,
	RowProcessor,
	board_rows_gen,
	insert_sidetable_fresh,
	SideTable,
	media_row_gen,
	thread_row_gen,
	thread_columns,
	media_columns,
)

# stolen from ayase-quart loader, gave up retrofitting, don't use
# wait for free threading to become default in python
# processpool not worth the copy overhead
class PopulatePipeline:
	def __init__(self, board: str):
		self.board = board

	async def run(self):
		print('Populating:', self.board)
		self.row_queue = QueueA(maxsize=200)
		wait_thread_workers = self.threads_worker()
		transform_task = create_task(self.transform_worker())
		await wait_thread_workers
		await self.row_queue.join()
		transform_task.cancel()
		row_processor = await transform_task
		insert_task = create_task(self.insert_worker(row_processor))
		insert_task.cancel()
		await insert_task

	async def threads_worker(self):
		total = 0
		async for thread_nums in tqdm_a(board_rows_gen(self.board), desc='get thread_nums', leave=False):
			for batch in batched(thread_nums, BATCH_POSTS):
				await self.row_queue.put(batch)
				total += 1
			self.thread_nums_p.total = total
			self.thread_nums_p.refresh()

	async def transform_worker(self):
		row_processor = RowProcessor()
		while True:
			try:
				rows = await self.row_queue.get()
			except CancelledError:
				return row_processor
			await sleep(0)
			row_processor.process_rows(rows)
			await sleep(0)
			self.row_queue.task_done()
			self.rows_batch_p.update(-1)

	async def insert_worker(self, row_processor: RowProcessor):
		for row_batch in tqdm(thread_row_gen(row_processor.threads), desc=f'insert threads'):
			await insert_sidetable_fresh(SideTable.threads, thread_columns, self.board, row_batch)
		
		for row_batch in tqdm(media_row_gen(row_processor.medias), desc=f'insert medias'):
			await insert_sidetable_fresh(SideTable.media, media_columns, self.board, row_batch)

async def populate_pipeline(boards: list[str]):
	if not boards:
		return
	# don't use
	# for board in boards:
	# 	pipeline = PopulatePipeline(board)
	# 	await pipeline.run()
