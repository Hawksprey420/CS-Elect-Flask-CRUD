from flask import Flask, request, jsonify, make_response, render_template, redirect
from flask_mysqldb import MySQL
import jwt
import datetime
from functools import wraps
from config.config import SystemConfig
import dicttoxml
import logging
from logging.handlers import RotatingFileHandler
import os
import subprocess
import sys
from pathlib import Path

app = Flask(__name__)
app.config.from_object(SystemConfig)

# Configure Logging
if not os.path.exists('logs'):
    os.mkdir('logs')

if not app.logger.hasHandlers():
    file_handler = RotatingFileHandler('logs/api.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Enrollment API startup')

@app.before_request
def log_request_info():
    app.logger.info(f"Request: {request.method} {request.url} - IP: {request.remote_addr}")

mysql = MySQL(app)


def _is_local_request() -> bool:
    return request.remote_addr in {"127.0.0.1", "::1"}


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not _is_local_request():
            return format_response({"message": "Forbidden"}, 403)

        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return make_response(
                "Admin credentials required",
                401,
                {"WWW-Authenticate": 'Basic realm="Admin"'},
            )

        if auth.username != app.config["API_USERNAME"] or auth.password != app.config["API_PASSWORD"]:
            return make_response(
                "Invalid admin credentials",
                401,
                {"WWW-Authenticate": 'Basic realm="Admin"'},
            )

        return f(*args, **kwargs)

    return decorated


def _run_python_script(relative_path: str, timeout_seconds: int = 180) -> dict:
    script_path = (Path(app.root_path) / relative_path).resolve()
    if not script_path.exists():
        return {"ok": False, "returncode": None, "output": f"Script not found: {script_path}"}

    try:
        completed = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(Path(app.root_path).resolve()),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        output = (completed.stdout or "") + ("\n" if completed.stderr else "") + (completed.stderr or "")
        output = output.strip()
        return {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "output": output if output else "(no output)",
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "returncode": None, "output": f"Timed out after {timeout_seconds}s"}
    except Exception as e:
        app.logger.exception("Failed to run script")
        return {"ok": False, "returncode": None, "output": str(e)}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            if token.startswith('Bearer '):
                token = token.split(" ")[1]
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            return jsonify({'message': f'Token error: {str(e)}'}), 401
        return f(*args, **kwargs)
    return decorated

def format_response(data, status_code=200):
    fmt = request.args.get('format', 'json')
    if fmt == 'xml':
        xml = dicttoxml.dicttoxml(data, custom_root='response', attr_type=False)
        response = make_response(xml)
        response.headers['Content-Type'] = 'application/xml'
    else:
        response = make_response(jsonify(data))
        response.headers['Content-Type'] = 'application/json'
    
    response.status_code = status_code
    return response

@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if auth.username == app.config['API_USERNAME'] and auth.password == app.config['API_PASSWORD']:
        token = jwt.encode({
            'user': auth.username,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
        }, app.config['JWT_SECRET_KEY'], algorithm="HS256")

        return jsonify({'token': token})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

@app.route('/')
def index():
    return redirect('/ui')

@app.route('/students', methods=['POST'])
@token_required
def create_student():
    data = request.get_json()
    if not data:
        return format_response({'message': 'No input data provided'}, 400)
    
    required_fields = ['student_id', 'student_name', 'year_level', 'gpa', 'dept_id']
    for field in required_fields:
        if field not in data:
            return format_response({'message': f'Missing field: {field}'}, 400)

    # Validation
    try:
        int(data['student_id'])
        int(data['year_level'])
        int(data['dept_id'])
        float(data['gpa'])
    except ValueError:
        return format_response({'message': 'Invalid data types'}, 400)

    try:
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO student (student_id, student_name, year_level, gpa, dept_id) VALUES (%s, %s, %s, %s, %s)",
                        (data['student_id'], data['student_name'], data['year_level'], data['gpa'], data['dept_id']))
            mysql.connection.commit()
            return format_response({'message': 'Student created successfully'}, 201)
        finally:
            cur.close()
    except Exception as e:
        if 'Duplicate entry' in str(e):
            return format_response({'message': 'Student ID already exists'}, 409)
        return format_response({'message': str(e)}, 500)

@app.route('/students', methods=['GET'])
@token_required
def get_students():
    search_query = request.args.get('search')
    try:
        cur = mysql.connection.cursor()
        try:
            if search_query:
                query = "SELECT * FROM student WHERE student_name LIKE %s"
                cur.execute(query, ('%' + search_query + '%',))
            else:
                cur.execute("SELECT * FROM student")
            
            rows = cur.fetchall()
            students = []
            if rows:
                columns = [col[0] for col in cur.description]
                for row in rows:
                    students.append(dict(zip(columns, row)))
            return format_response({'students': students})
        finally:
            cur.close()
    except Exception as e:
        return format_response({'message': str(e)}, 500)

@app.route('/students/<int:student_id>', methods=['GET'])
@token_required
def get_student(student_id):
    try:
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT * FROM student WHERE student_id = %s", (student_id,))
            row = cur.fetchone()
            
            if row:
                columns = [col[0] for col in cur.description]
                student = dict(zip(columns, row))
                return format_response({'student': student})
            else:
                return format_response({'message': 'Student not found'}, 404)
        finally:
            cur.close()
    except Exception as e:
        return format_response({'message': str(e)}, 500)

@app.route('/students/<int:student_id>', methods=['PUT'])
@token_required
def update_student(student_id):
    data = request.get_json()
    if not data:
        return format_response({'message': 'No input data provided'}, 400)
    
    try:
        cur = mysql.connection.cursor()
        try:
            # Check if student exists
            cur.execute("SELECT * FROM student WHERE student_id = %s", (student_id,))
            if not cur.fetchone():
                return format_response({'message': 'Student not found'}, 404)

            update_fields = []
            values = []
            if 'student_name' in data:
                update_fields.append("student_name = %s")
                values.append(data['student_name'])
            if 'year_level' in data:
                try:
                    values.append(int(data['year_level']))
                    update_fields.append("year_level = %s")
                except ValueError:
                    return format_response({'message': 'Invalid year_level'}, 400)
            if 'gpa' in data:
                try:
                    values.append(float(data['gpa']))
                    update_fields.append("gpa = %s")
                except ValueError:
                    return format_response({'message': 'Invalid gpa'}, 400)
            if 'dept_id' in data:
                try:
                    values.append(int(data['dept_id']))
                    update_fields.append("dept_id = %s")
                except ValueError:
                    return format_response({'message': 'Invalid dept_id'}, 400)
                
            if not update_fields:
                 return format_response({'message': 'No fields to update'}, 400)
                 
            values.append(student_id)
            query = f"UPDATE student SET {', '.join(update_fields)} WHERE student_id = %s"
            cur.execute(query, tuple(values))
            mysql.connection.commit()
            return format_response({'message': 'Student updated successfully'})
        finally:
            cur.close()
    except Exception as e:
        return format_response({'message': str(e)}, 500)

@app.route('/students/<int:student_id>', methods=['DELETE'])
@token_required
def delete_student(student_id):
    try:
        cur = mysql.connection.cursor()
        try:
            cur.execute("DELETE FROM student WHERE student_id = %s", (student_id,))
            mysql.connection.commit()
            affected_rows = cur.rowcount
            
            if affected_rows > 0:
                return format_response({'message': 'Student deleted successfully'})
            else:
                return format_response({'message': 'Student not found'}, 404)
        finally:
            cur.close()
    except Exception as e:
        return format_response({'message': str(e)}, 500)


@app.route('/ui', methods=['GET'])
def ui_home():
    # This UI is intended for local development/testing only.
    return render_template('test.html')


@app.route('/admin/seed', methods=['POST'])
@admin_required
def admin_seed_database():
    result = _run_python_script('tests/insert_data.py')
    status = 200 if result.get('ok') else 500
    return jsonify(result), status


@app.route('/admin/run-tests', methods=['POST'])
@admin_required
def admin_run_tests():
    result = _run_python_script('tests/test_api.py')
    status = 200 if result.get('ok') else 500
    return jsonify(result), status

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)