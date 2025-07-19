import sys
import asyncio

from .queries import (
	cmd_op_mapping,
	entities,
	tabletype_modules,
)
from .db import db_type, close_pool, run_script
from .side_populate.singlethread import populate_single_thread
from .queries.templates import (
	get_template,
	render_template,
)

populate_action = 'table_populate'

async def execute_action(table_type: str, action: str, boards: list[str]):
	if table_type == 'side' and action == populate_action:
		await populate_single_thread(boards)
		return
	if not (template := get_template(db_type, table_type, action)):
		print(f'Empty template for {table_type} {action} {db_type}')
		return
	for board in boards:
		queries = render_template(template, board)
		print('Executing:', table_type, action, board)
		# print(queries)
		await run_script(queries)

def get_args():
	if len(args := sys.argv[1:]) < 4:
		return None
	table_type, entity, command, *boards = args
	if table_type not in tabletype_modules:
		table_types = list(tabletype_modules.key())
		raise KeyError(f'Invalid table type: {table_type}', table_types)
	if entity not in entities:
		raise KeyError(f'Invalid entity: {entity}', entities)
	if not (op := cmd_op_mapping.get(command)):
		commands = list(cmd_op_mapping.keys())
		raise KeyError( f'Invalid command: {command}', commands )
	action = f'{entity}_{op}'
	if action not in tabletype_modules[table_type] and action != populate_action:
		raise KeyError(f'{entity} {command} not defined for {table_type}')
	return table_type, action, boards

async def main():
	if not (args := get_args()):
		print('Invalid or not enough arguments (min 4)')
		# figure out how to print help menu
		return
	table_type, action, boards = args
	await execute_action(table_type, action, boards)

def run():
	loop = asyncio.new_event_loop()
	loop.set_task_factory(asyncio.eager_task_factory)
	try:
		loop.run_until_complete(main())
	except Exception as e:
		raise e
	except KeyboardInterrupt: pass
	finally:
		loop.run_until_complete(close_pool())
		loop.close()
