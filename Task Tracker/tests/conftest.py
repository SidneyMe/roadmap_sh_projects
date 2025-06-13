from src.taski import STATUS
import os
import random
import string
import pytest
import shutil
from pathlib import Path
from typing import Optional, get_args
from datetime import datetime

TEST_FOLDER_PATH= 'test_folder'
TEST_FILE_PATH = 'test_db.json'
TEST_DB_PATH = Path(f'{TEST_FOLDER_PATH}/{TEST_FILE_PATH}')

@pytest.fixture(autouse=True)
def create_test_folder():
    if not os.path.exists(TEST_FOLDER_PATH):
        os.makedirs(TEST_FOLDER_PATH, exist_ok=True)

@pytest.fixture(autouse=True)
def del_test_folder():
    yield
    if os.path.exists(TEST_FOLDER_PATH):
        shutil.rmtree(TEST_FOLDER_PATH)

def string_gen(length: int= 15) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def make_task(status: Optional[STATUS]= None,
              rnd_status: bool=False) -> dict[str, dict[str, str]]:

    test_time = datetime.now().isoformat()
    test_task = {
        '1': {
            'task_id': '1',
            'description': 'that is a test description',
            'status': random.choice(get_args(STATUS)) if rnd_status else (status or 'todo'),
            'createdAt': test_time,
            'updatedAt': test_time
        }
    }
    return test_task

def make_task_tracker(length: int=10,
                      rnd_desc: bool= False,
                      status: Optional[STATUS]=None,
                      rnd_status: bool=False,
                      fields_to_miss: Optional[list]= None,
                      rnd_missing_fields: bool= False,
                      ) -> dict[str, dict[str, str]]:

    def _rnd_missing_fields(task_tracker_fields: list[str]) -> list[str]:
        return random.choices(task_tracker_fields, k=random.randint(1, len(task_tracker_fields)))

    task_tracker = {}

    test_time = datetime.now().isoformat()
    test_task = {
            'task_id': '1',
            'description': 'that is a test description',
            'status': random.choice(get_args(STATUS)) if rnd_status else (status or 'todo'),
            'createdAt': test_time,
            'updatedAt': test_time
        }

    task_tracker_fields = [field for field in test_task]

    if rnd_missing_fields:
        fields_to_miss = None

    if fields_to_miss:
        for field_to_miss in fields_to_miss:
            try:
                test_task.pop(field_to_miss)
            except KeyError:
                continue
    
    for i in range(0, length):
        task = test_task.copy()
        task_id = str(i)
        task['id'] = task_id
        if rnd_missing_fields:
            for field_to_miss in _rnd_missing_fields(task_tracker_fields):
                try:
                    task.pop(field_to_miss)
                except KeyError:
                    continue
        if rnd_desc:
            task['description'] = string_gen()
        task_tracker[task_id] = task

    return task_tracker