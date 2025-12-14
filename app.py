from flask import Flask, request, jsonify, make_response
from flask_mysqldb import MySQL
from config.config import SystemConfig
import jwt
import datetime
import dicttoxml
from functools import wraps
app = Flask(__name__)
app.config['MYSQL_HOST'] = SystemConfig.MYSQL_HOST


mysql = MySQL(app)
app.config.from_object(SystemConfig)

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
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
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

@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the Enrollment System API'})

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

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO student (student_id, student_name, year_level, gpa, dept_id) VALUES (%s, %s, %s, %s, %s)",
                    (data['student_id'], data['student_name'], data['year_level'], data['gpa'], data['dept_id']))
        mysql.connection.commit()
        cur.close()
        return format_response({'message': 'Student created successfully'}, 201)
    except Exception as e:
        return format_response({'message': str(e)}, 500)

@app.route('/students', methods=['GET'])
@token_required
def get_students():
    search_query = request.args.get('search')
    try:
        cur = mysql.connection.cursor()
        if search_query:
            query = "SELECT * FROM student WHERE student_name LIKE %s"
            cur.execute(query, ('%' + search_query + '%',))
        else:
            cur.execute("SELECT * FROM student")
        
        rows = cur.fetchall()
        columns = [col[0] for col in cur.description]
        students = []
        for row in rows:
            students.append(dict(zip(columns, row)))
        cur.close()
        return format_response({'students': students})
    except Exception as e:
        return format_response({'message': str(e)}, 500)

@app.route('/students/<int:student_id>', methods=['GET'])
@token_required
def get_student(student_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM student WHERE student_id = %s", (student_id,))
        row = cur.fetchone()
        cur.close()
        
        if row:
            columns = [col[0] for col in cur.description]
            student = dict(zip(columns, row))
            return format_response({'student': student})
        else:
            return format_response({'message': 'Student not found'}, 404)
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
        # Check if student exists
        cur.execute("SELECT * FROM student WHERE student_id = %s", (student_id,))
        if not cur.fetchone():
            cur.close()
            return format_response({'message': 'Student not found'}, 404)

        update_fields = []
        values = []
        if 'student_name' in data:
            update_fields.append("student_name = %s")
            values.append(data['student_name'])
        if 'year_level' in data:
            update_fields.append("year_level = %s")
            values.append(data['year_level'])
        if 'gpa' in data:
            update_fields.append("gpa = %s")
            values.append(data['gpa'])
        if 'dept_id' in data:
            update_fields.append("dept_id = %s")
            values.append(data['dept_id'])
            
        if not update_fields:
             return format_response({'message': 'No fields to update'}, 400)
             
        values.append(student_id)
        query = f"UPDATE student SET {', '.join(update_fields)} WHERE student_id = %s"
        cur.execute(query, tuple(values))
        mysql.connection.commit()
        cur.close()
        return format_response({'message': 'Student updated successfully'})
    except Exception as e:
        return format_response({'message': str(e)}, 500)

@app.route('/students/<int:student_id>', methods=['DELETE'])
@token_required
def delete_student(student_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM student WHERE student_id = %s", (student_id,))
        mysql.connection.commit()
        affected_rows = cur.rowcount
        cur.close()
        
        if affected_rows > 0:
            return format_response({'message': 'Student deleted successfully'})
        else:
            return format_response({'message': 'Student not found'}, 404)
    except Exception as e:
        return format_response({'message': str(e)}, 500)

if __name__ == '__main__':
    app.run(debug=True)

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
            current_user = data['user']
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated