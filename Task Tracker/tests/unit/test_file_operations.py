import os
import sys
import shutil
import pytest
from src.taski import save_to_task_db, open_task_db
from ..conftest import make_task, make_task_tracker, TEST_FILE_PATH

@pytest.mark.parametrize('task', (
    {}, make_task()
))
def test_save_to_task_db(tmpdir, task):

    test_folder = tmpdir.mkdir('test_save_to_task')
    test_file_path = test_folder.join(TEST_FILE_PATH)

    save_to_task_db(task, TEST_FILE_PATH, str(test_folder))
    assert test_file_path.check(file=1)

def test_open_task_db_very_large_json(tmp_path):
    folder = tmp_path / 'very_large_json'
    folder.mkdir()
    file = folder / 'test_very_large_json.json'
    task_tracker = make_task_tracker(1_000)
    save_to_task_db(task_tracker, file.name, str(folder))
    assert len(open_task_db(file.name, str(folder))) == 1_000

def test_open_task_db_exists(tmpdir):

    tmp = tmpdir.mkdir('json_task_tracker')
    save_to_task_db(make_task(), TEST_FILE_PATH, tmp)
    task = open_task_db(TEST_FILE_PATH, tmp)
    assert task['1']['description'] == 'that is a test description'
    assert len(task) == 1

def test_open_task_db_not_exsists():
    if os.path.exists('json_task_tracker'):
        shutil.rmtree('json_task_tracker')
    open_task_db()
    assert os.path.exists('json_task_tracker')