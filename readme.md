## Description

This repository contains solutions to projects from [roadmap.sh/projects](https://roadmap.sh/projects).

---

### Project 1: [Task Tracker](https://roadmap.sh/projects/task-tracker)

A simple cli application that saves given description of a task into json.

#### Features

- Add, update, and delete tasks
- Mark tasks as **todo**, **in-progress** or **done**
- List all tasks
- List tasks by status:
    - Todo
    - Done
    - In progress

### Command Examples

- **Add a task:**
  ```sh
  python "Task Tracker\src\taski.py" add "Buy groceries"
  ```

- **List all tasks:**
  ```sh
  python "Task Tracker\src\taski.py" list
  ```

- **List tasks by status:**
  ```sh
  python "Task Tracker\src\taski.py" list --status todo
  python "Task Tracker\src\taski.py" list --status done
  python "Task Tracker\src\taski.py" list --status in-progress
  ```

- **Update a task:**
  ```sh
  python "Task Tracker\src\taski.py" update 1 --description "Buy groceries and cook dinner" --status in-progress
  ```

- **Delete a task:**
  ```sh
  python "Task Tracker\src\taski.py" delete 1
  ```

### Help

For more options, run:
```sh
python "Task Tracker\src\taski.py" --help
```

#### Implementation Overview

- `supported_queries()` — Returns supported query types
- `get_queries()` — Parses and retrieves user queries
- `create_db_dir` — Initializes the database directory
- `open_task_db` — Opens the task database
- `save_to_task_db` — Saves changes to the database
- `add_task` — Adds a new task
- `delete_task` — Removes a task
- `update_task` — Updates an existing task
- `list_tasks` — Lists tasks based on filters
- `main` — Entry point for the application

#### Tests

- Unit tests for core functionality (add, update, delete, list)
- Integration tests for file operations
- Validation tests
- Cli tests

---
