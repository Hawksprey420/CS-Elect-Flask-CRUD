insert_data.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import MySQLdb
from config.config import SystemConfig

def insert_test_data():
    try:
        db = MySQLdb.connect(
            host=SystemConfig.MYSQL_HOST,
            user=SystemConfig.MYSQL_USER,
            passwd=SystemConfig.MYSQL_PASSWORD,
            db=SystemConfig.MYSQL_DB,
            port=SystemConfig.MYSQL_PORT
        )
        cursor = db.cursor()

        # Insert Departments
        departments = [
            (1, 'Computer Science'),
            (2, 'Engineering'),
            (3, 'Mathematics'),
            (4, 'Physics'),
            (5, 'Biology')
        ]
        print("Inserting Departments...")
        cursor.executemany("INSERT IGNORE INTO department (dept_id, dept_name) VALUES (%s, %s)", departments)

        # Insert Students (20 records)
        students = [
            (101, 'Alice Johnson', 1, 3.5, 1),
            (102, 'Bob Smith', 2, 3.2, 1),
            (103, 'Charlie Brown', 1, 3.8, 2),
            (104, 'David Lee', 3, 2.9, 2),
            (105, 'Eva Garcia', 4, 3.9, 3),
            (106, 'Frank White', 2, 3.0, 3),
            (107, 'Grace Miller', 1, 3.6, 4),
            (108, 'Henry Wilson', 3, 3.1, 4),
            (109, 'Ivy Thomas', 4, 3.7, 5),
            (110, 'Jack Taylor', 2, 2.8, 5),
            (111, 'Kevin Anderson', 1, 3.4, 1),
            (112, 'Laura Martinez', 3, 3.3, 1),
            (113, 'Mike Robinson', 2, 3.5, 2),
            (114, 'Nina Clark', 4, 3.8, 2),
            (115, 'Oscar Rodriguez', 1, 3.0, 3),
            (116, 'Paul Lewis', 3, 3.2, 3),
            (117, 'Quinn Walker', 2, 3.6, 4),
            (118, 'Rachel Hall', 4, 3.9, 4),
            (119, 'Sam Allen', 1, 2.7, 5),
            (120, 'Tina Young', 3, 3.4, 5)
        ]
        print("Inserting Students...")
        cursor.executemany("INSERT IGNORE INTO student (student_id, student_name, year_level, gpa, dept_id) VALUES (%s, %s, %s, %s, %s)", students)

        db.commit()
        print("Data inserted successfully!")
        cursor.close()
        db.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    insert_test_data()