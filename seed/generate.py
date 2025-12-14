from __future__ import annotations

import random
from faker import Faker

from seed.db import next_id


def generate_instructors(*, cursor, departments, count: int, faker: Faker, rng: random.Random):
    instructors = []
    start_id = next_id(cursor, 'instructor', 'instr_id')
    for offset in range(count):
        instr_id = start_id + offset
        instr_name = faker.name()
        salary = round(rng.uniform(50000, 120000), 2)
        dept_id = rng.choice(departments)[0]
        instructors.append((instr_id, instr_name, salary, dept_id))
    return instructors


def generate_courses(*, cursor, departments, course_titles, rng: random.Random):
    courses = []
    start_id = next_id(cursor, 'course', 'course_id')
    for offset, (code, title) in enumerate(course_titles):
        course_id = start_id + offset
        credits = rng.choice([3, 4])
        dept_id = rng.choice(departments)[0]
        courses.append((course_id, code, title, credits, dept_id))
    return courses


def generate_students(*, cursor, departments, count: int, faker: Faker, rng: random.Random):
    students = []
    start_id = next_id(cursor, 'student', 'student_id')
    for offset in range(count):
        student_id = start_id + offset
        student_name = faker.name()
        year_level = rng.randint(1, 4)
        gpa = round(rng.uniform(1.0, 4.0), 2)
        dept_id = rng.choice(departments)[0]
        students.append((student_id, student_name, year_level, gpa, dept_id))
    return students


def generate_enrollments(*, cursor, students, courses, count: int, rng: random.Random):
    enrollments = []
    start_id = next_id(cursor, 'enrollment', 'enroll_id')
    for offset in range(count):
        enroll_id = start_id + offset
        student_id = rng.choice(students)[0]
        course_id = rng.choice(courses)[0]
        semester = rng.choice(['2023-1', '2023-2', '2024-1'])
        grade = round(rng.uniform(1.0, 4.0), 2)
        enrollments.append((enroll_id, student_id, course_id, semester, grade))
    return enrollments
