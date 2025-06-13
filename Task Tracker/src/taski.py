import os
import json
from datetime import datetime
from argparse import ArgumentParser
from pprint import pprint
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
            required_fields = {'task_id', 'description', 'status', 'createdAt', 'updatedAt'}
            for task in task_tracker.values():
                if not required_fields.issubset(task):
                    raise ValueError(f"Missing required fields in task: {task}")
    except FileNotFoundError:
        task_tracker = {}
    return task_tracker


def save_to_task_db(task_tracker: Optional[dict[str, TaskProperties]] = None, file_name: str = 'tasks.json', folder_name: str='json_task_tracker') -> None:
    with open(f'{folder_name}/{file_name}', 'w', encoding='utf-8') as js_file:
        json.dump(task_tracker, js_file, indent=4)

def add_task(task_tracker: dict[str, TaskProperties], description: str) -> dict[str, TaskProperties]:
    if not isinstance(task_tracker, dict):
        raise TypeError("Task Tracker should not be empty and should be dict")
    if not description or not isinstance(description, str):
        raise TypeError("Description should not be empty and should be a string")
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
    if not task_tracker or not isinstance(task_tracker, dict):
        raise TypeError("Task Tracker should not be empty and should be dict")
    if not task_id or not isinstance(task_id, str):
        raise TypeError("Task id should not be be empty and should be a string")
    try:
        del task_tracker[task_id]
    except KeyError as exc:
        raise KeyError(f'Task id {task_id} not found') from exc
    return task_tracker


def update_task(task_tracker: dict[str, TaskProperties], task_id: str, description: Optional[str]='', status: Optional[STATUS]='todo') -> dict[str, TaskProperties]:
    try:
        if not task_tracker or not isinstance(task_tracker, dict):
            raise TypeError("Task Tracker should not be empty and should be dict")
        if not task_id or not isinstance(task_id, str):
            raise TypeError("Task id should not be be empty and should be a string")
        if not isinstance(description, str):
            raise TypeError("Description should not be empty and should be a string")
        if not status or not isinstance(status, str):
            raise TypeError('Status should not be empty and should be a string')
        if status not in get_args(STATUS):
            raise ValueError(f"Status only accepts following args -> {get_args(STATUS)}")

        if description is not None:
            task_tracker[task_id]['description'] = description
        if status:
            task_tracker[task_id]['status'] = status
        task_tracker[task_id]['updatedAt'] = datetime.now().isoformat()
    except KeyError as exc:
        raise KeyError(f'Task id {task_id} not found') from exc
    return task_tracker


def list_tasks(task_tracker: dict[str, TaskProperties], status: Optional[STATUS]=None) -> None:
    if isinstance(task_tracker, dict):
        if status in get_args(STATUS) or status is None:
            for _, task in task_tracker.items():
                if not status:
                    pprint(task, sort_dicts=False)
                elif task['status'] == status:
                    pprint(task, sort_dicts=False)
        else:
            raise ValueError(f"Status only accepts following args -> {get_args(STATUS)}")
    else:
        raise TypeError(f'List tasks accepts a dict got: {task_tracker}')


def main() -> None:

    task_manager = open_task_db()
    args, queries = get_queries(sup_queries=supported_queries())

    queries(task_manager, **args)

    save_to_task_db(task_manager)


if __name__ == '__main__':
    main()
