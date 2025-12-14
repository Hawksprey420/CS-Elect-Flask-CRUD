# Enrollment System CRUD REST API (MySQL)

Final Project (CSE1): a CRUD REST API for an ultra-basic enrollment system using Flask + MySQL.

## Requirements Checklist (Assignment)
- CRUD operations with validations + error handling
- Tests covering CRUD + edge cases
- XML/JSON output option via `?format=xml|json`
- Search functionality
- Security (JWT)
- Documentation (this README)

## Features Implemented
- JWT-protected endpoints for Students
- Student CRUD + search (`student_name LIKE ...`)
- Response formatting: JSON (default) or XML (`?format=xml`)
- Local request logging to `logs/api.log`
- Local helper UI at `/ui` (for demo/testing)

## Prerequisites
- Python 3.x
- MySQL server running locally
- Database schema created (database `ucms_enrollment` and the tables in your SQL file)

## Installation

1. Create/activate a virtual environment.

2. Install dependencies:
	 ```bash
	 pip install -r requirements.txt
	 ```

## Configuration

Edit `config/config.py` OR set environment variables:
- `MYSQL_HOST`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DB`
- `MYSQL_PORT`
- `JWT_SECRET_KEY`
- `API_USERNAME`
- `API_PASSWORD`

## Run the API

```bash
python app.py
```

Open:
- API root: `http://localhost:5000/`
- Local test UI: `http://localhost:5000/ui`

## Authentication (JWT)

1. Get a JWT token:

`POST /login` using Basic Auth (username/password from `config/config.py`).

Example:
```bash
curl -X POST -u admin:password http://localhost:5000/login
```

2. Use it on API calls:

Header:
`Authorization: Bearer <token>`

## API Endpoints (Students)

All `/students*` endpoints require JWT.

### Create
- `POST /students`
	- JSON body: `student_id`, `student_name`, `year_level`, `gpa`, `dept_id`

### Read (list + search)
- `GET /students`
	- Optional query:
		- `search=<text>`
		- `format=json|xml`

### Read (single)
- `GET /students/<id>`
	- Optional: `format=json|xml`

### Update
- `PUT /students/<id>`
	- JSON body: any of `student_name`, `year_level`, `gpa`, `dept_id`

### Delete
- `DELETE /students/<id>`

## Seed Test Data (20+ records)

This generates and inserts sample data (departments/instructors/courses/students/enrollments):
```bash
python tests/insert_data.py
```

## Run Tests

```bash
python tests/test_api.py
```

## Local Test UI (`/ui`)

This is a simple HTML page intended for local testing/demo:
- Can run `tests/insert_data.py` and `tests/test_api.py`
	- Restricted to localhost
	- Requires Basic Auth
- Can login to get a JWT and then manually:
	- Create a Student
	- Search Students
	- Get Student by ID
