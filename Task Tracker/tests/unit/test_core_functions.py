import os
import sys
import shutil
from time import sleep
from typing import get_args
import pytest
from src.taski import create_db_dir, add_task, update_task, delete_task, list_tasks, supported_queries, get_queries, STATUS
from ..conftest import string_gen, make_task, make_task_tracker


@pytest.mark.parametrize('file_name', (
    'test_folder', 'test_folder_1', string_gen(50)
))
def test_create_db_dir(file_name):
    create_db_dir(file_name)
    assert os.path.exists(file_name)
    shutil.rmtree(file_name)

@pytest.mark.parametrize(
    ('task_tracker', 'description'),
    [
        ({}, 'first test task'),
        ({}, string_gen(1_000))
    ]
)
def test_add_task(task_tracker, description):
    task = add_task(task_tracker, description)
    assert len(task) == 1
    assert task['1']['description'] == description

def test_add_tasks():
    task_tracker = {}
    test_desc = [string_gen(15) for _ in range(15)]
    for desc in test_desc:
        task_tracker.update(add_task(task_tracker, desc))

    assert task_tracker['5']['description'] == test_desc[4]
    assert len(task_tracker) == 15


@pytest.mark.parametrize(
    'kwargs',
    [
        {'description': 'updated description', 'status': 'todo'},
        {'description': '', 'status': 'in-progress'},
        {'description': string_gen(15), 'status': 'done'},
        {'description': string_gen(15)},
        {'status': 'done'}
    ]
)
def test_update_task(kwargs):

    task_tracker = update_task(make_task(), '1', **kwargs)
    if 'description' in kwargs:
        assert task_tracker['1']['description'] == kwargs['description']
    if 'status' in kwargs:
        assert task_tracker['1']['status'] == kwargs['status']

def test_update_multiple():

    tasks = make_task_tracker()
    for i in ['1', '2', '8']:
        tasks = update_task(tasks, i, 'updated description')
        if i == '8':
            tasks = update_task(tasks, i, status='done')
    assert tasks['1']['description'] == 'updated description' and tasks['2']['description'] == 'updated description'
    assert tasks['8']['status'] == 'done'
    assert len(tasks) == 10

@pytest.mark.parametrize(['task_tracker', 'task_id'],
    [
        (make_task(), '1'),
        (make_task_tracker(), '2'),
    ]
)
def test_delete_task(task_tracker, task_id):
    res_length = len(task_tracker) - 1
    task_tracker = delete_task(task_tracker, task_id)
    assert len(task_tracker) == res_length

@pytest.mark.parametrize(['task_tracker', 'task_id_lst'],
    [
        (make_task_tracker(), ['1', '3', '6', '5', '2'])
    ]
)
def test_delete_task_multiple(task_tracker, task_id_lst):
    res_length = len(task_tracker) - len(task_id_lst)

    for del_id in task_id_lst:
        task_tracker = delete_task(task_tracker, del_id)

    assert len(task_tracker) == res_length

def test_list_tasks(capsys):
    task_tracker = make_task_tracker()
    list_tasks(task_tracker)
    out, _ = capsys.readouterr()
    assert task_tracker['1']['description'] in out


@pytest.mark.parametrize(
    ['tracker_len', 'status', 'rnd_status'],
    [
        (10, None, True),
        (10, 'todo', False),
        (10, 'in-progress', False),
        (10, 'done', False),
    ]
)
def test_list_tasks_status(capsys, tracker_len, status, rnd_status):
    task_tracker = make_task_tracker(length=tracker_len, status=status, rnd_status=rnd_status)
    list_tasks(task_tracker, status)
    out, _ = capsys.readouterr()

    if status:
        for s in get_args(STATUS):
            if s == status:
                assert s in out
            else:
                assert s not in out

    assert task_tracker['1']['status'] in out

def test_supported_queries():
    queries = supported_queries()

    assert set(queries.keys()) == {'add', 'delete', 'update', 'list'}

    add_query = queries['add']
    assert add_query['target'] == add_task
    assert isinstance(add_query['help'], str)
    assert isinstance(add_query['args'], list)
    assert add_query['args'][0]['name_or_flags'] == ['description']

    delete_query = queries['delete']
    assert delete_query['target'] == delete_task
    assert isinstance(delete_query['help'], str)
    assert isinstance(delete_query['args'], list)
    assert delete_query['args'][0]['name_or_flags'] == ['task_id']

    update_query = queries['update']
    assert update_query['target'] == update_task
    assert update_query['args'][0]['name_or_flags'] == ['task_id']
    assert any('--status' in arg['name_or_flags'] for arg in update_query['args'])
    assert any('--description' in arg['name_or_flags'] for arg in update_query['args'])

    list_query = queries['list']
    assert list_query['target'] == list_tasks
    assert any('--status' in arg['name_or_flags'] for arg in list_query['args'])

def test_get_queries_add(monkeypatch):
    test_args = ['taski.py', 'add', 'test']
    monkeypatch.setattr(sys, 'argv', test_args)
    args, func = get_queries(supported_queries())
    assert args['description'] == 'test'
    assert callable(func)

def test_get_queries_update(monkeypatch):
    test_args = ['taski.py', 'update', '1', '--status', 'done', '--description', 'end of a test']
    monkeypatch.setattr(sys, 'argv', test_args)
    args, func = get_queries(supported_queries())
    assert args['task_id'] == '1'
    assert args['status'] == 'done'
    assert args['description'] == 'end of a test'
    assert callable(func)

def test_update_updatedAt():
    task_tracker = make_task_tracker(10, rnd_desc=True, rnd_status=True)
    sleep(0.00001)
    task_tracker = update_task(task_tracker, '5', 'test', 'in-progress')
    assert task_tracker['4']['updatedAt'] != task_tracker['5']['updatedAt']

def test_task_sequence_delete():
    task_tracker = make_task_tracker(10, rnd_desc=True, rnd_status=True)
    keys = list(task_tracker.keys())
    for key in reversed(keys):
        task_tracker = delete_task(task_tracker, key)
        assert key not in task_tracker

def test_task_sequence_update():
    task_tracker = make_task_tracker(10, rnd_desc=True)
    before_update = task_tracker['5'].copy()
    task_tracker = update_task(task_tracker, '5', 'test', 'done')
    assert task_tracker['5']['description'] != before_update['description']
    assert task_tracker['5']['status'] != before_update['status']

def test_task_sequence_add():
    task_tracker = make_task_tracker(10, rnd_desc=True, rnd_status=True)
    before_add = task_tracker[list(task_tracker.keys())[-1]].copy()
    task_tracker = add_task(task_tracker, 'new_desc')
    assert task_tracker[list(task_tracker.keys())[-1]] != before_add