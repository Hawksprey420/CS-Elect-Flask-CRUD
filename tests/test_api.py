import unittest
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
from config.config import SystemConfig
import base64


class TestEnrollmentAPI(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        # Get Token
        credentials = f"{SystemConfig.API_USERNAME}:{SystemConfig.API_PASSWORD}"
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(credentials.encode()).decode('utf-8')
        }
        response = self.app.post('/login', headers=headers)
        data = json.loads(response.data)
        self.token = data['token']
        self.headers = {'Authorization': f'Bearer {self.token}'}

    def test_1_create_student(self):
        student_data = {
            'student_id': 999,
            'student_name': 'Test Student',
            'year_level': 1,
            'gpa': 4.0,
            'dept_id': 1
        }
        response = self.app.post('/students', headers=self.headers, json=student_data)
        self.assertEqual(response.status_code, 201)

    def test_2_get_students(self):
        response = self.app.get('/students', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('students', data)

    def test_3_get_student(self):
        response = self.app.get('/students/999', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['student']['student_name'], 'Test Student')

    def test_4_update_student(self):
        update_data = {'gpa': 3.9}
        response = self.app.put('/students/999', headers=self.headers, json=update_data)
        self.assertEqual(response.status_code, 200)
        
        # Verify update
        response = self.app.get('/students/999', headers=self.headers)
        data = json.loads(response.data)
        self.assertEqual(float(data['student']['gpa']), 3.9)

    def test_5_search_student(self):
        response = self.app.get('/students?search=Test', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(len(data['students']) > 0)

    def test_6_xml_format(self):
        response = self.app.get('/students/999?format=xml', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/xml')
        self.assertIn(b'<student>', response.data)

    def test_7_delete_student(self):
        response = self.app.delete('/students/999', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        
        # Verify deletion
        response = self.app.get('/students/999', headers=self.headers)
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()