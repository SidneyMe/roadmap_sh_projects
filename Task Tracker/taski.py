import os
import json
from datetime import datetime
from argparse import ArgumentParser
from pprint import pprint
import sys
from typing import Optional, Literal, Callable, TypedDict, get_args

STATUS = Literal['todo', 'in-progress', 'done']

class TaskProperties(TypedDict):
    task_id: str
    description: Optional[str]
    status: STATUS
    createdAt: str
    updatedAt: str

class SupportedQueryArgs(TypedDict, total=False):
    name_or_flags: list[str]
    help: str
    nargs: str

class SupportedQueryProperties(TypedDict):
    target: Callable
    help: str
    args: list[SupportedQueryArgs]


def supported_queries() -> dict[str, SupportedQueryProperties]:
    return {
        'add': {
            'target': add_task,
            'help': 'Add a new task',
            'args': [
                {
                    'name_or_flags': ['description'],
                    'help': 'Description of a task'
                }
            ]
        },
        'delete': {
            'target': delete_task,
            'help': 'Delete a task',
            'args': [
                {
                    'name_or_flags': ['task_id'],
                    'help': 'id of a task you want to delete'
                }
            ]
        },
        'update': {
            'target': update_task,
            'help': 'Updates a task',
            'args': [
                {
                    'name_or_flags': ['task_id'],
                    'help': 'id of a task you want to update'
                },
                {
                    'name_or_flags': ['--status'],
                    'help': 'Update status of a task',
                    'nargs': '?'
                },
                {
                    'name_or_flags': ['--description'],
                    'help': 'Update description of a task',
                    'nargs': '?'
                },
            ]
        },
        'list': {
            'target': list_tasks,
            'help': 'Lists tasks by status or all',
            'args': [
                {
                    'name_or_flags': ['--status'],
                    'help': 'status of tasks you want to see',
                    'nargs': '?'
                }
            ]
        }
    }


def get_queries(sup_queries: dict[str, SupportedQueryProperties]) -> tuple[dict, Callable]:
    parser = ArgumentParser(
        prog='taski',
        description='Handy tool for handling tasks'
    )

    sub_parser = parser.add_subparsers(title='commands', dest='command', required=True)

    for name, prop in sup_queries.items():
        s_pars = sub_parser.add_parser(name, help=prop['help'])
        for arg in prop['args']:
            kwargs = {'help' : arg['help']}
            if 'nargs' in arg:
                kwargs['nargs'] = arg['nargs']
            s_pars.add_argument(*arg['name_or_flags'], **kwargs)

    args = vars(parser.parse_args())
    queries = sup_queries[args.pop('command')]['target']

    return args, queries


def create_db_dir(folder_name: str='json_task_tracker') -> None:
    os.makedirs(folder_name, exist_ok=True)


def open_task_db(file_name: str = 'tasks.json', folder_name: str='json_task_tracker') -> dict[str, TaskProperties]:
    create_db_dir(folder_name)
    try:
        with open(f'{folder_name}/{file_name}', 'r', encoding='utf-8') as js_file:
            task_tracker = json.load(js_file)
    except FileNotFoundError:
        task_tracker = {}
    return task_tracker


def save_to_task_db(task_tracker: Optional[dict[str, TaskProperties]] = None, file_name: str = 'tasks.json', folder_name: str='json_task_tracker') -> None:
    with open(f'{folder_name}/{file_name}', 'w', encoding='utf-8') as js_file:
        json.dump(task_tracker, js_file, indent=4)


def add_task(task_tracker: dict[str, TaskProperties], description: str) -> dict[str, TaskProperties]:
    creation_date = datetime.now().isoformat()
    task_id = str(max(map(int, task_tracker.keys()), default=0) + 1)
    task_tracker[task_id] ={
        'task_id': task_id,
        'description': description,
        'status': 'todo',
        'createdAt': creation_date,
        'updatedAt': creation_date
    }
    return task_tracker


def delete_task(task_tracker: dict[str, TaskProperties], task_id: str) -> dict[str, TaskProperties]:
    try:
        del task_tracker[task_id]
    except KeyError:
        print(f'Task id {task_id} not found')
    return task_tracker


def update_task(task_tracker: dict[str, TaskProperties], task_id: str, description: Optional[str]=None, status: Optional[STATUS]=None) -> dict[str, TaskProperties]:
    try:
        if status not in get_args(STATUS) and status is not None:
            raise ValueError(f"Status only accepts following args -> {get_args(STATUS)}")

        if description:
            task_tracker[task_id]['description'] = description
        if status:
            task_tracker[task_id]['status'] = status
        task_tracker[task_id]['updatedAt'] = datetime.now().isoformat()
    except KeyError:
        print(f'Task id {task_id} not found')
    return task_tracker


def list_tasks(task_tracker: dict[str, TaskProperties], status: Optional[STATUS]=None) -> None:
    for _, task in task_tracker.items():
        if not status:
            pprint(task, sort_dicts=False)
        elif task['status'] == status:
            pprint(task, sort_dicts=False)


def main() -> None:

    task_manager = open_task_db()
    args, queries = get_queries(sup_queries=supported_queries())

    try:
        queries(task_manager, **args)
    except KeyError:
        sys.exit('No task found with the provided ID')

    save_to_task_db(task_manager)


if __name__ == '__main__':
    main()
