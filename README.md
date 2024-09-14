# TaskFlow

TaskFlow is a simplified task tracker similar to Trello or Jira, implemented using FastAPI. The application allows for creating, editing, and deleting tasks, and it features a role-based authorization system. The project supports pagination functionality for convenient work with large task lists.

## Features

### 1. Task Management
- **Create, edit, and delete tasks.**
  - Each task contains the following fields:
    - **Title**
    - **Description**
    - **Responsible Person**
    - **Executors**
    - **Status**: `TODO`, `In Progress`, `Done`
    - **Priority**: `Low`, `Medium`, `High`
- **Assign a responsible person and executors.**
- **Mock email notification sending to the responsible person when the task status is updated.**

### 2. Authorization and Role System
- The authorization system is based on tokens (Bearer tokens).
- Supports different roles:
  - **Admin** — full access to all operations.
  - **Manager** — same access level as Admin.
  - **User** — view-only access to tasks.
- User authorization via token, with the ability to log out (Logout).

### 3. Pagination and Sorting
- Pagination support for task lists.
  - Parameters:
    - `page` — the page number (starts from 1).
    - `page_size` — the number of tasks per page.
  - Response headers:
    - `X-Total-Count` — total number of tasks.
    - `X-Total-Pages` — total number of pages.
    - `X-Current-Page` — the current page number.
    - `X-Page-Size` — the number of tasks per page.
- Sorting support for tasks using the `order_by` parameter (e.g., by `title`).

## How to Run the Project

### 1. Clone the Repository
Clone this repository to your computer:
```bash
git clone https://github.com/mhvozdesky/task_flow.git
cd task_flow
```

### 2. Set Up Virtual Environment
Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # for Linux/Mac
# or
.venv\Scripts\activate  # for Windows
```

### 3. Install Dependencies
Install the required dependencies using pip:
```bash
pip install -r requirements.txt
```

Make sure you have a file with the environment variables:
```bash
DB_HOST=
DB_PORT=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
```

### 4. Set Up the Database
Start the database.

The project has been tested on PostgreSQL.

### 5. Apply Database Migrations
Apply the migrations to set up the database structure:
```bash
alembic upgrade head
```

### 6. Run the Server
Run the FastAPI server:
```bash
uvicorn task_flow_backend.main:app --reload
```

### 7. Test the Project
To ensure everything works, you can run the tests:
```bash
pytest
```

### The project will be available at:
```bash
http://127.0.0.1:8000
```

## User Registration and Task Creation
After launching the server, you can register a user at the following address:

127.0.0.1:8000/accounts/register

### Example data for registration:
```json
{
    "email": "user@example.com",
    "password": "password123",
    "phone": "0123456789",
    "first_name": "John",
    "last_name": "Doe"
}
```

You will receive a token in response:

```json
{
    "token": "947fc71f528b94151358ac09bbe8f85c"
}
```

After registration, a new user will be created, but they won't have the rights to create tasks. Since the project does not have an admin panel yet, it's recommended to manually change the user role for testing.

### Setting Up Permissions via Console:
The new user will most likely be created in the database with id = 1. You can connect to your database through the console and run the following query to grant admin rights:

```sql
UPDATE user_roles
SET role_id = 1
WHERE user_id = 1;
```
This query will give the user admin rights.

### Task Creation:
Now you can create a new task using the following endpoint:
```bash
127.0.0.1:8000/taskboard/tasks
```

Example data for task creation:
```json
{
    "title": "title",
    "description": "description",
    "status": "TODO",
    "priority": "High",
    "responsible_id": 1,
    "executor_ids": [1]
}
```

Don't forget to include the obtained token in the request headers for authorization.

### Other possible endpoints can be found at:
```bash
http://127.0.0.1:8000/docs
```
