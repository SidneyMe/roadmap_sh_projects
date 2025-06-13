# from src.taski import get_queries, get_args, add_task, update_task, delete_task, list_tasks, open_task_db, save_to_task_db, create_db_dir, STATUS, TaskProperties, supported_queries
# import pytest
# import random
# import os
# import shutil
# import string
# import json
# import sys
# import subprocess
# from time import sleep
# from typing import Optional, get_args
# from pathlib import Path
# from datetime import datetime


# TEST_FOLDER = 'test_folder'
# TEST_FILE = 'test_db.json'
# TEST_DB_PATH = Path(f'{TEST_FOLDER}/{TEST_FILE}')


# @pytest.fixture(autouse=True)
# def create_test_folder():
#     if not os.path.exists(TEST_FOLDER):
#         os.makedirs(TEST_FOLDER, exist_ok=True)

# @pytest.fixture(autouse=True)
# def del_test_folder():
#     yield
#     if os.path.exists(TEST_FOLDER):
#         shutil.rmtree(TEST_FOLDER)

# def string_gen(length: int= 15) -> str:
#     return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# def make_task(status: Optional[STATUS]= None,
#               rnd_status: bool=False) -> dict[str, dict[str, str]]:

#     test_time = datetime.now().isoformat()
#     test_task = {
#         '1': {
#             'task_id': '1',
#             'description': 'that is a test description',
#             'status': random.choice(get_args(STATUS)) if rnd_status else (status or 'todo'),
#             'createdAt': test_time,
#             'updatedAt': test_time
#         }
#     }
#     return test_task

# def make_task_tracker(length: int=10,
#                       rnd_desc: bool= False,
#                       status: Optional[STATUS]=None,
#                       rnd_status: bool=False,
#                       fields_to_miss: Optional[list]= None,
#                       rnd_missing_fields: bool= False,
#                       ) -> dict[str, dict[str, str]]:

#     def _rnd_missing_fields(task_tracker_fields: list[str]) -> list[str]:
#         return random.choices(task_tracker_fields, k=random.randint(1, len(task_tracker_fields)))

#     task_tracker = {}

#     test_time = datetime.now().isoformat()
#     test_task = {
#             'task_id': '1',
#             'description': 'that is a test description',
#             'status': random.choice(get_args(STATUS)) if rnd_status else (status or 'todo'),
#             'createdAt': test_time,
#             'updatedAt': test_time
#         }

#     task_tracker_fields = [field for field in test_task]

#     if rnd_missing_fields:
#         fields_to_miss = None

#     if fields_to_miss:
#         for field_to_miss in fields_to_miss:
#             try:
#                 test_task.pop(field_to_miss)
#             except KeyError:
#                 continue
    
#     for i in range(0, length):
#         task = test_task.copy()
#         task_id = str(i)
#         task['id'] = task_id
#         if rnd_missing_fields:
#             for field_to_miss in _rnd_missing_fields(task_tracker_fields):
#                 try:
#                     task.pop(field_to_miss)
#                 except KeyError:
#                     continue
#         if rnd_desc:
#             task['description'] = string_gen()
#         task_tracker[task_id] = task

#     return task_tracker


# @pytest.mark.parametrize('file_name', (
#     'test_folder', 'test_folder_1', string_gen(50)
# ))
# def test_create_db_dir(file_name):
#     create_db_dir(file_name)
#     assert os.path.exists(file_name)
#     shutil.rmtree(file_name)

# @pytest.mark.parametrize('file_name', (
#     None, False, 13, 0.44
# ))
# def test_create_db_dir_exceptions(file_name):
#     with pytest.raises(TypeError):
#         create_db_dir(file_name)

# @pytest.mark.parametrize('task', (
#     {}, make_task()
# ))
# def test_save_to_task_db(tmpdir, task):

#     test_folder = tmpdir.mkdir('test_save_to_task')
#     test_file_path = test_folder.join(TEST_FILE)

#     save_to_task_db(task, TEST_FILE, str(test_folder))
#     assert test_file_path.check(file=1)

# def test_open_task_db_exists(tmpdir):

#     tmp = tmpdir.mkdir('json_task_tracker')
#     save_to_task_db(make_task(), TEST_FILE, tmp)
#     task = open_task_db(TEST_FILE, tmp)
#     assert task['1']['description'] == 'that is a test description'
#     assert len(task) == 1

# def test_open_task_db_not_exsists():
#     if os.path.exists('json_task_tracker'):
#         shutil.rmtree('json_task_tracker')
#     open_task_db()
#     assert os.path.exists('json_task_tracker')

# @pytest.mark.parametrize(
#     ('task_tracker', 'description'),
#     [
#         ({}, 'first test task'),
#         ({}, string_gen(1_000))
#     ]
# )
# def test_add_task(task_tracker, description):
#     task = add_task(task_tracker, description)
#     assert len(task) == 1
#     assert task['1']['description'] == description

# def test_add_tasks():
#     task_tracker = {}
#     test_desc = [string_gen(15) for _ in range(15)]
#     for desc in test_desc:
#         task_tracker.update(add_task(task_tracker, desc))

#     assert task_tracker['5']['description'] == test_desc[4]
#     assert len(task_tracker) == 15


# @pytest.mark.parametrize(
#     'kwargs',
#     [
#         {'description': 'updated description', 'status': 'todo'},
#         {'description': '', 'status': 'in-progress'},
#         {'description': string_gen(15), 'status': 'done'},
#         {'description': string_gen(15)},
#         {'status': 'done'}
#     ]
# )
# def test_update_task(kwargs):

#     task_tracker = update_task(make_task(), '1', **kwargs)
#     if 'description' in kwargs:
#         assert task_tracker['1']['description'] == kwargs['description']
#     if 'status' in kwargs:
#         assert task_tracker['1']['status'] == kwargs['status']

# @pytest.mark.parametrize('task',
#     ('', [], 1, False, None, (), 0.323)
# )
# def test_update_task_invalid_task(task):
#     with pytest.raises(TypeError):
#         update_task(task, '1', 'updated description', 'done')

# def test_update_task_invalid_id():
#     with pytest.raises(KeyError):
#         update_task(make_task(), '2', 'updated description', 'done' )
    
# @pytest.mark.parametrize('description',
#     (1, [], (), {}, 0.33, False, None),
# )
# def test_update_task_invalid_description(description):
#     with pytest.raises(TypeError):
#         update_task(make_task(), '1', description, 'done')

# @pytest.mark.parametrize('status',
#     (string_gen(), '1'),
# )
# def test_update_task_invalid_status_value(status):
#     with pytest.raises(ValueError):
#         update_task(make_task(), '1', 'updated_description', status)

# @pytest.mark.parametrize('status',
#     ('', {}, [], (), None, False)
# )
# def test_update_task_empty_status(status):
#     with pytest.raises(TypeError):
#         update_task(make_task(), '1', 'updated_description', status)

# @pytest.mark.parametrize('status',
#     (1, True, 0.33)
# )
# def test_update_task_invalid_status_not_string(status):
#     with pytest.raises(TypeError):
#         update_task(make_task(), '1', 'updated_description', status)

# def test_update_multiple():

#     tasks = make_task_tracker()
#     for i in ['1', '2', '8']:
#         tasks = update_task(tasks, i, 'updated description')
#         if i == '8':
#             tasks = update_task(tasks, i, status='done')
#     assert tasks['1']['description'] == 'updated description' and tasks['2']['description'] == 'updated description'
#     assert tasks['8']['status'] == 'done'
#     assert len(tasks) == 10

# @pytest.mark.parametrize(['task_tracker', 'task_id'],
#     [
#         (make_task(), '1'),
#         (make_task_tracker(), '2'),
#     ]
# )
# def test_delete_task(task_tracker, task_id):
#     res_length = len(task_tracker) - 1
#     task_tracker = delete_task(task_tracker, task_id)
#     assert len(task_tracker) == res_length

# @pytest.mark.parametrize(['task_tracker', 'task_id'],
#     [
#         (make_task_tracker(), '11'),
#         (make_task(), '2')
#     ]
# )
# def test_delete_task_invalid_id(task_tracker, task_id):
#     with pytest.raises(KeyError):
#         delete_task(task_tracker, task_id)

# @pytest.mark.parametrize(['task_tracker', 'task_id_lst'],
#     [
#         (make_task_tracker(), ['1', '3', '6', '5', '2'])
#     ]
# )
# def test_delete_task_multiple(task_tracker, task_id_lst):
#     res_length = len(task_tracker) - len(task_id_lst)

#     for del_id in task_id_lst:
#         task_tracker = delete_task(task_tracker, del_id)

#     assert len(task_tracker) == res_length

# def test_delete_task_not_existent_key():
#     with pytest.raises(KeyError):
#         delete_task(make_task_tracker(10), '11')

# def test_delete_task_wrong_type():
#     with pytest.raises(TypeError):
#         delete_task([], '1')

# def test_list_tasks(capsys):
#     task_tracker = make_task_tracker()
#     list_tasks(task_tracker)
#     out, _ = capsys.readouterr()
#     assert task_tracker['1']['description'] in out


# @pytest.mark.parametrize(
#     ['tracker_len', 'status', 'rnd_status'],
#     [
#         (10, None, True),
#         (10, 'todo', False),
#         (10, 'in-progress', False),
#         (10, 'done', False),
#     ]
# )
# def test_list_tasks_status(capsys, tracker_len, status, rnd_status):
#     task_tracker = make_task_tracker(length=tracker_len, status=status, rnd_status=rnd_status)
#     list_tasks(task_tracker, status)
#     out, _ = capsys.readouterr()

#     if status:
#         for s in get_args(STATUS):
#             if s == status:
#                 assert s in out
#             else:
#                 assert s not in out

#     assert task_tracker['1']['status'] in out


# def test_list_tasks_type_error():
#     with pytest.raises(TypeError):
#         list_tasks([], 'done')

# def test_list_tasks_value_error():
#     with pytest.raises(ValueError):
#         list_tasks({}, 'test')


# def test_supported_queries():
#     queries = supported_queries()

#     assert set(queries.keys()) == {'add', 'delete', 'update', 'list'}

#     add_query = queries['add']
#     assert add_query['target'] == add_task
#     assert isinstance(add_query['help'], str)
#     assert isinstance(add_query['args'], list)
#     assert add_query['args'][0]['name_or_flags'] == ['description']

#     delete_query = queries['delete']
#     assert delete_query['target'] == delete_task
#     assert isinstance(delete_query['help'], str)
#     assert isinstance(delete_query['args'], list)
#     assert delete_query['args'][0]['name_or_flags'] == ['task_id']

#     update_query = queries['update']
#     assert update_query['target'] == update_task
#     assert update_query['args'][0]['name_or_flags'] == ['task_id']
#     assert any('--status' in arg['name_or_flags'] for arg in update_query['args'])
#     assert any('--description' in arg['name_or_flags'] for arg in update_query['args'])

#     list_query = queries['list']
#     assert list_query['target'] == list_tasks
#     assert any('--status' in arg['name_or_flags'] for arg in list_query['args'])

# def test_get_queries_add(monkeypatch):
#     test_args = ['taski.py', 'add', 'test']
#     monkeypatch.setattr(sys, 'argv', test_args)
#     args, func = get_queries(supported_queries())
#     assert args['description'] == 'test'
#     assert callable(func)

# def test_get_queries_update(monkeypatch):
#     test_args = ['taski.py', 'update', '1', '--status', 'done', '--description', 'end of a test']
#     monkeypatch.setattr(sys, 'argv', test_args)
#     args, func = get_queries(supported_queries())
#     assert args['task_id'] == '1'
#     assert args['status'] == 'done'
#     assert args['description'] == 'end of a test'
#     assert callable(func)

# def test_open_task_db_corrupted_json(tmp_path):
#     folder = tmp_path / 'corrupted_json'
#     folder.mkdir()
#     file = folder / 'test_corrupted_json.json'
#     file.write_text("{ not valid json }")
#     with pytest.raises(json.JSONDecodeError):
#         open_task_db(file.name, str(folder))


# def test_open_task_db_permission_denied_makedirs(mocker, tmp_path):
#     folder = tmp_path / 'test_permission_denied'
#     folder.mkdir()
#     file = folder / 'test_permission_denied_file.json'

#     mock_makedirs = mocker.patch('src.taski.os.makedirs', autospec=True)
#     mock_makedirs.side_effect = PermissionError('Simulated permission error for a directory')

#     with pytest.raises(PermissionError):
#         open_task_db(file.name, str(folder))

# def test_open_task_db_locked_file_by_another_process(mocker, tmp_path):
#     folder = tmp_path / 'locked_file_by_another_process'
#     folder.mkdir()
#     file = folder / 'test_locked_file_by_another_process.json'

#     mock_access = mocker.patch('builtins.open', autospec=True)
#     mock_access.side_effect = PermissionError('Locked by another process')

#     with pytest.raises(PermissionError):
#         open_task_db(file.name, str(folder))

# def test_open_task_db_very_large_json(tmp_path):
#     folder = tmp_path / 'very_large_json'
#     folder.mkdir()
#     file = folder / 'test_very_large_json.json'
#     task_tracker = make_task_tracker(1_000)
#     save_to_task_db(task_tracker, file.name, str(folder))
#     assert len(open_task_db(file.name, str(folder))) == 1_000

# @pytest.mark.parametrize(
#     ['fields_to_miss', 'rnd_missing_fields'],
#     [
#         (['task_id'], False),
#         (['description', 'status'], False),
#         (['description', 'status', 'createdAt'], False),
#         (['createdAt', 'updatedAt', 'task_id'], False),
#         (['description', 'status', 'createdAt', 'updatedAt'], False),
#         (['description', 'status', 'createdAt', 'updatedAt', 'task_id'], False),
#         (None, True)
#     ]
# )
# def test_open_task_db_missing_fields(tmp_path, fields_to_miss, rnd_missing_fields):
#     folder = tmp_path / 'missing_fields'
#     folder.mkdir()
#     file = folder / 'test_missing_fields'

#     task_tracker = make_task_tracker(length=20, fields_to_miss=fields_to_miss, rnd_missing_fields=rnd_missing_fields)
#     save_to_task_db(task_tracker, file.name, str(folder))
#     with pytest.raises(ValueError):
#         open_task_db(file.name, str(folder))

# @pytest.mark.parametrize(
#     ['task_tracker', 'description'],
#     [
#         ({}, None),
#         (None, 'test_description'),
#         (None, None)
#     ]
# )
# def test_missing_required_arguments_add_task(task_tracker, description):
#     with pytest.raises(TypeError):
#         add_task(task_tracker, description)

# @pytest.mark.parametrize(
#     ['task_tracker', 'task_id', 'description', 'status'],
#     [
#         (make_task_tracker(1), '1', 'test', None),
#         (make_task_tracker(1), '1', None, 'todo'),
#         (make_task_tracker(1), None, 'test', 'todo'),
#         (None, '1', 'test', 'todo'),
#         (None, None, None, None)
#     ]
# )
# def test_missing_required_arguments_update_task(task_tracker, task_id, description, status):
#     with pytest.raises(TypeError):
#         update_task(task_tracker, task_id, description, status)

# @pytest.mark.parametrize(['task_tracker', 'task_id'],
#     [
#         (None, '1'),
#         (make_task(), None),
#         (None, None)
#     ]
# )
# def test_missing_required_arguments_delete_task(task_tracker, task_id):
#     with pytest.raises(TypeError):
#         delete_task(task_tracker, task_id)

# def test_missing_required_arguments_list_task():
#     with pytest.raises(TypeError):
#         list_tasks(None, None)

# def test_special_characters_in_add_task():
#     test_str = '\n\b\r\\l239984#(*@$_!(*$5))'
#     subprocess.run(
#         [
#             'python', 'Task Tracker/src/taski.py', 'add', test_str
#         ],
#         check=True
#     )
#     assert open_task_db()['1']['description'] == test_str

# @pytest.mark.parametrize(
#     'query',
#     ('add', 'update', 'delete')
# )
# def test_cli_missing_argument(query):
#     result = subprocess.run(
#         ['python', 'Task Tracker/src/taski.py', query],
#         capture_output=True,
#         text=True,
#         check=False
#     )
#     assert result.returncode != 0
#     assert "the following arguments are required" in result.stderr

# def test_update_updatedAt():
#     task_tracker = make_task_tracker(10, rnd_desc=True, rnd_status=True)
#     sleep(0.00001)
#     task_tracker = update_task(task_tracker, '5', 'test', 'in-progress')
#     assert task_tracker['4']['updatedAt'] != task_tracker['5']['updatedAt']

# def test_task_sequence_delete():
#     task_tracker = make_task_tracker(10, rnd_desc=True, rnd_status=True)
#     keys = list(task_tracker.keys())
#     for key in reversed(keys):
#         task_tracker = delete_task(task_tracker, key)
#         assert key not in task_tracker

# def test_task_sequence_update():
#     task_tracker = make_task_tracker(10, rnd_desc=True)
#     before_update = task_tracker['5'].copy()
#     task_tracker = update_task(task_tracker, '5', 'test', 'done')
#     assert task_tracker['5']['description'] != before_update['description']
#     assert task_tracker['5']['status'] != before_update['status']

# def test_task_sequence_add():
#     task_tracker = make_task_tracker(10, rnd_desc=True, rnd_status=True)
#     before_add = task_tracker[list(task_tracker.keys())[-1]].copy()
#     task_tracker = add_task(task_tracker, 'new_desc')
#     assert task_tracker[list(task_tracker.keys())[-1]] != before_add