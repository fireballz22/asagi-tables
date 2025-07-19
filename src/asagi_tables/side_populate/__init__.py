from collections import defaultdict
from itertools import batched
from typing import AsyncGenerator, Generator, Iterable
from dataclasses import dataclass
from enum import StrEnum

from ..db import Phg, on_conflict, query_tuple

BATCH_POSTS = 10000
BATCH_THREADS = 4000
BATCH_IMAGES = 5000 # can't go higher, sqlite3 limit 5000 * 6 => ~30000

post_columns = (
	'doc_id',
	'num',
	'subnum',
	'thread_num',
	'timestamp',
	'preview_orig',
	'media_hash',
	'media_orig',
	'sticky',
	'locked',
	'email',
)
thread_columns = (
	'thread_num',
	'time_op',
	'time_last',
	'time_bump',
	'time_ghost',
	'time_ghost_bump',
	'time_last_modified',
	'nreplies',
	'nimages',
)
media_columns = (
	'media_hash',
	'media',
	'preview_op',
	'preview_reply',
	'total',
	'banned',
)

class SideTable(StrEnum):
	threads = 'threads'
	media = 'images'
	users = 'users'
	daily = 'daily'
	deleted = 'deleted'

@dataclass(slots=True)
class Thread:
	replies: int = 0
	images: int = 0
	sticky: int = 0
	locked: int = 0
	time_bump: int = 0
	time_op: int = 0
	time_last_modified: int = 0
	time_last: int = 0
	time_ghost: int = 0
	time_ghost_bump: int = 0

	def get_row(self, thread_num: int) -> tuple[int|None, ...]:
		return (
			thread_num,
			self.time_op,
			self.time_last,
			self.time_bump,
			self.time_ghost or None,
			self.time_ghost_bump or None,
			self.time_last_modified,
			self.replies,
			self.images,
		)

@dataclass(slots=True)
class Media:
	total: int = 0
	banned: int = 0
	media: str|None = None
	preview_op: str|None = None
	preview_reply: str|None = None

	def get_row(self, media_hash: str) -> tuple[int|str|None, ...]:
		return (
			media_hash,
			self.media,
			self.preview_op,
			self.preview_reply,
			self.total,
			self.banned,
		)

def media_row_gen(medias: dict[str, Media]) -> Generator:
	for batch in batched(medias.items(), BATCH_IMAGES):
		yield [media.get_row(media_hash) for media_hash, media in batch]

def thread_row_gen(threads: dict[int, Thread]) -> Generator:
	for batch in batched(threads.items(), BATCH_THREADS):
		yield [thread.get_row(threadnum) for threadnum, thread in batch]

async def board_rows_gen(board: str, after_doc_id: int=0) -> AsyncGenerator:
	batch_size = BATCH_POSTS

	sql = f"""
	select {','.join(post_columns)}
	from {board}
	where doc_id > {Phg()()}
	order by doc_id asc
	limit {batch_size}
	;"""
	while True:
		rows = await query_tuple(sql, (after_doc_id,))
		if not rows:
			break

		yield rows
		if len(rows) < batch_size:
			break
		after_doc_id = rows[-1][0] # last doc_id


async def increment_threads(board: str, rows: list[tuple]):
	col_len = len(thread_columns)
	phg = Phg()
	ph = ','.join(
		f"({phg.qty(col_len)})"
		for _ in range(len(rows))
	)
	params = tuple(cell for row in rows for cell in row)
	sql = f"""insert into {board}_{SideTable.threads}({",".join(thread_columns)})
	values {ph}
	{on_conflict('thread_num')}
		nreplies = nreplies + excluded.nreplies,
		nimages = nimages + excluded.nimages,
		time_last = excluded.time_last,
		time_bump = excluded.time_bump,
		time_last_modified = excluded.time_last_modified
	;"""
	await query_tuple(sql, params)

async def insert_sidetable_fresh(sidetable: SideTable, columns: Iterable[str], board: str, rows: list[tuple]):
	col_len = len(columns)
	phg = Phg()
	ph = ','.join(
		f"({phg.qty(col_len)})"
		for _ in range(len(rows))
	)
	params = tuple(cell for row in rows for cell in row)
	sql = f'insert into {board}_{sidetable}({",".join(columns)}) values {ph};'
	await query_tuple(sql, params)

NO_BUMP = 'sage'
class RowProcessor:
	"""Reimplements the insert trigger logic in batch mode"""
	def __init__(self):
		self.threads: dict[int, Thread] = defaultdict(Thread)
		self.medias: dict[str, Media] = defaultdict(Media)

	def process_rows(self, rows: Iterable[tuple]):
		threads = self.threads
		medias = self.medias

		for _, num, snum, thread_num, time, p_orig, m_hash, m_orig, sticky, locked, email in rows:
			thread = threads[thread_num]
			is_op = num == thread_num # is_op db field wrongly set in corrupted datasets

			if is_op:
				thread.time_op = time
				thread.locked = locked
				thread.sticky = sticky
			else:
				thread.replies += 1

			if time > thread.time_last_modified:
				thread.time_last_modified = time
			if snum: # ghost post
				if time > thread.time_ghost:
					thread.time_ghost = time
				if email != NO_BUMP and time > thread.time_ghost_bump:
					thread.time_ghost_bump = time
			else: # not ghost post
				if time > thread.time_last:
					thread.time_last = time
				if email != NO_BUMP and time > thread.time_bump:
					thread.time_bump = time
			
			if m_hash:
				media = medias[m_hash]
				thread.images += 1
				media.total += 1
				media.media = m_orig
				if is_op:
					media.preview_op = p_orig
				else:
					media.preview_reply = p_orig
