import json
import pytest
from src.taski import create_db_dir, add_task, update_task, delete_task, list_tasks, open_task_db, save_to_task_db
from ..conftest import string_gen, make_task, make_task_tracker

@pytest.mark.parametrize('file_name', (
    None, False, 13, 0.44
))
def test_create_db_dir_exceptions(file_name):
    with pytest.raises(TypeError):
        create_db_dir(file_name)

@pytest.mark.parametrize('task',
    ('', [], 1, False, None, (), 0.323)
)
def test_update_task_invalid_task(task):
    with pytest.raises(TypeError):
        update_task(task, '1', 'updated description', 'done')


def test_update_task_invalid_id():
    with pytest.raises(KeyError):
        update_task(make_task(), '2', 'updated description', 'done' )
    
@pytest.mark.parametrize('description',
    (1, [], (), {}, 0.33, False, None),
)
def test_update_task_invalid_description(description):
    with pytest.raises(TypeError):
        update_task(make_task(), '1', description, 'done')

@pytest.mark.parametrize('status',
    (string_gen(), '1'),
)
def test_update_task_invalid_status_value(status):
    with pytest.raises(ValueError):
        update_task(make_task(), '1', 'updated_description', status)

@pytest.mark.parametrize('status',
    ('', {}, [], (), None, False)
)
def test_update_task_empty_status(status):
    with pytest.raises(TypeError):
        update_task(make_task(), '1', 'updated_description', status)

@pytest.mark.parametrize('status',
    (1, True, 0.33)
)
def test_update_task_invalid_status_not_string(status):
    with pytest.raises(TypeError):
        update_task(make_task(), '1', 'updated_description', status)

@pytest.mark.parametrize(['task_tracker', 'task_id'],
    [
        (make_task_tracker(), '11'),
        (make_task(), '2')
    ]
)
def test_delete_task_invalid_id(task_tracker, task_id):
    with pytest.raises(KeyError):
        delete_task(task_tracker, task_id)

def test_delete_task_not_existent_key():
    with pytest.raises(KeyError):
        delete_task(make_task_tracker(10), '11')

def test_delete_task_wrong_type():
    with pytest.raises(TypeError):
        delete_task([], '1')

def test_list_tasks_type_error():
    with pytest.raises(TypeError):
        list_tasks([], 'done')

def test_list_tasks_value_error():
    with pytest.raises(ValueError):
        list_tasks({}, 'test')

def test_open_task_db_corrupted_json(tmp_path):
    folder = tmp_path / 'corrupted_json'
    folder.mkdir()
    file = folder / 'test_corrupted_json.json'
    file.write_text("{ not valid json }")
    with pytest.raises(json.JSONDecodeError):
        open_task_db(file.name, str(folder))


def test_open_task_db_permission_denied_makedirs(mocker, tmp_path):
    folder = tmp_path / 'test_permission_denied'
    folder.mkdir()
    file = folder / 'test_permission_denied_file.json'

    mock_makedirs = mocker.patch('src.taski.os.makedirs', autospec=True)
    mock_makedirs.side_effect = PermissionError('Simulated permission error for a directory')

    with pytest.raises(PermissionError):
        open_task_db(file.name, str(folder))

def test_open_task_db_locked_file_by_another_process(mocker, tmp_path):
    folder = tmp_path / 'locked_file_by_another_process'
    folder.mkdir()
    file = folder / 'test_locked_file_by_another_process.json'

    mock_access = mocker.patch('builtins.open', autospec=True)
    mock_access.side_effect = PermissionError('Locked by another process')

    with pytest.raises(PermissionError):
        open_task_db(file.name, str(folder))

@pytest.mark.parametrize(
    ['fields_to_miss', 'rnd_missing_fields'],
    [
        (['task_id'], False),
        (['description', 'status'], False),
        (['description', 'status', 'createdAt'], False),
        (['createdAt', 'updatedAt', 'task_id'], False),
        (['description', 'status', 'createdAt', 'updatedAt'], False),
        (['description', 'status', 'createdAt', 'updatedAt', 'task_id'], False),
        (None, True)
    ]
)
def test_open_task_db_missing_fields(tmp_path, fields_to_miss, rnd_missing_fields):
    folder = tmp_path / 'missing_fields'
    folder.mkdir()
    file = folder / 'test_missing_fields'

    task_tracker = make_task_tracker(length=20, fields_to_miss=fields_to_miss, rnd_missing_fields=rnd_missing_fields)
    save_to_task_db(task_tracker, file.name, str(folder))
    with pytest.raises(ValueError):
        open_task_db(file.name, str(folder))

@pytest.mark.parametrize(
    ['task_tracker', 'description'],
    [
        ({}, None),
        (None, 'test_description'),
        (None, None)
    ]
)
def test_missing_required_arguments_add_task(task_tracker, description):
    with pytest.raises(TypeError):
        add_task(task_tracker, description)

@pytest.mark.parametrize(
    ['task_tracker', 'task_id', 'description', 'status'],
    [
        (make_task_tracker(1), '1', 'test', None),
        (make_task_tracker(1), '1', None, 'todo'),
        (make_task_tracker(1), None, 'test', 'todo'),
        (None, '1', 'test', 'todo'),
        (None, None, None, None)
    ]
)
def test_missing_required_arguments_update_task(task_tracker, task_id, description, status):
    with pytest.raises(TypeError):
        update_task(task_tracker, task_id, description, status)

@pytest.mark.parametrize(['task_tracker', 'task_id'],
    [
        (None, '1'),
        (make_task(), None),
        (None, None)
    ]
)
def test_missing_required_arguments_delete_task(task_tracker, task_id):
    with pytest.raises(TypeError):
        delete_task(task_tracker, task_id)

def test_missing_required_arguments_list_task():
    with pytest.raises(TypeError):
        list_tasks(None, None)
