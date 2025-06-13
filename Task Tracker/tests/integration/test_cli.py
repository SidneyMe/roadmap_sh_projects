from src.taski import open_task_db
import subprocess
import pytest

def test_special_characters_in_add_task():
    test_str = '\n\b\r\\l239984#(*@$_!(*$5))'
    subprocess.run(
        [
            'python', 'Task Tracker/src/taski.py', 'add', test_str
        ],
        check=True
    )
    assert open_task_db()['1']['description'] == test_str

@pytest.mark.parametrize(
    'query',
    ('add', 'update', 'delete')
)
def test_cli_missing_argument(query):
    result = subprocess.run(
        ['python', 'Task Tracker/src/taski.py', query],
        capture_output=True,
        text=True,
        check=False
    )
    assert result.returncode != 0
    assert "the following arguments are required" in result.stderr