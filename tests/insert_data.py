import sys
import os
import random
from faker import Faker

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from seed.db import connect_db
from seed import templates
from seed.generate import (
    generate_courses,
    generate_enrollments,
    generate_instructors,
    generate_students,
)

def insert_test_data():
    rng = random.Random(0)
    Faker.seed(0)
    fake = Faker()

    try:
        db = connect_db()
        cursor = db.cursor()
        try:
            departments = templates.departments()
            course_titles = templates.course_titles()

            print(f"Inserting {len(departments)} Departments...")
            cursor.executemany(
                "INSERT IGNORE INTO department (dept_id, dept_name) VALUES (%s, %s)",
                departments,
            )

            instructors = generate_instructors(cursor=cursor, departments=departments, count=15, faker=fake, rng=rng)
            print(f"Inserting {len(instructors)} Instructors...")
            cursor.executemany(
                "INSERT IGNORE INTO instructor (instr_id, instr_name, salary, dept_id) VALUES (%s, %s, %s, %s)",
                instructors,
            )

            courses = generate_courses(cursor=cursor, departments=departments, course_titles=course_titles, rng=rng)
            print(f"Inserting {len(courses)} Courses...")
            cursor.executemany(
                "INSERT IGNORE INTO course (course_id, course_code, title, credits, dept_id) VALUES (%s, %s, %s, %s, %s)",
                courses,
            )

            students = generate_students(cursor=cursor, departments=departments, count=50, faker=fake, rng=rng)
            print(f"Inserting {len(students)} Students...")
            cursor.executemany(
                "INSERT IGNORE INTO student (student_id, student_name, year_level, gpa, dept_id) VALUES (%s, %s, %s, %s, %s)",
                students,
            )

            enrollments = generate_enrollments(cursor=cursor, students=students, courses=courses, count=100, rng=rng)
            print(f"Inserting {len(enrollments)} Enrollments...")
            cursor.executemany(
                "INSERT IGNORE INTO enrollment (enroll_id, student_id, course_id, semester, grade) VALUES (%s, %s, %s, %s, %s)",
                enrollments,
            )

            db.commit()
            print("Data generation and insertion completed successfully!")
        finally:
            cursor.close()
            db.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    insert_test_data()