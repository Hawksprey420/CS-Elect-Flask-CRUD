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
        print("\n[TEST] Creating Student...")
        student_data = {
            'student_id': 999,
            'student_name': 'Test Student',
            'year_level': 1,
            'gpa': 4.0,
            'dept_id': 1
        }
        print(f"   Sending: {student_data}")
        response = self.app.post('/students', headers=self.headers, json=student_data)
        print(f"   Response: {response.status_code} - {response.data.decode()}")
        self.assertEqual(response.status_code, 201)

    def test_2_get_students(self):
        print("\n[TEST] Getting All Students...")
        response = self.app.get('/students', headers=self.headers)
        print(f"   Response Status: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('students', data)

    def test_3_get_student(self):
        print("\n[TEST] Getting Single Student (ID: 999)...")
        response = self.app.get('/students/999', headers=self.headers)
        print(f"   Response: {response.data.decode()}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['student']['student_name'], 'Test Student')

    def test_4_update_student(self):
        print("\n[TEST] Updating Student (ID: 999)...")
        update_data = {'gpa': 3.9}
        print(f"   Sending Update: {update_data}")
        response = self.app.put('/students/999', headers=self.headers, json=update_data)
        print(f"   Response: {response.status_code} - {response.data.decode()}")
        self.assertEqual(response.status_code, 200)
        
        # Verify update
        response = self.app.get('/students/999', headers=self.headers)
        data = json.loads(response.data)
        self.assertEqual(float(data['student']['gpa']), 3.9)

    def test_5_search_student(self):
        print("\n[TEST] Searching Student (Query: 'Test')...")
        response = self.app.get('/students?search=Test', headers=self.headers)
        print(f"   Response: {response.data.decode()}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(len(data['students']) > 0)

    def test_6_xml_format(self):
        print("\n[TEST] Testing XML Format...")
        response = self.app.get('/students/999?format=xml', headers=self.headers)
        print(f"   Response Header: {response.headers['Content-Type']}")
        print(f"   Response Body Snippet: {response.data[:50]}...")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/xml')
        self.assertIn(b'<student>', response.data)

    def test_7_delete_student(self):
        print("\n[TEST] Deleting Student (ID: 999)...")
        response = self.app.delete('/students/999', headers=self.headers)
        print(f"   Response: {response.status_code} - {response.data.decode()}")
        self.assertEqual(response.status_code, 200)
        
        # Verify deletion
        response = self.app.get('/students/999', headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_8_edge_cases(self):
        print("\n[TEST] Testing Edge Cases...")
        
        # 1. Unauthorized Access
        print("   Testing Unauthorized Access...")
        response = self.app.get('/students')
        self.assertEqual(response.status_code, 401)

        # 2. Create with Missing Fields
        print("   Testing Create with Missing Fields...")
        response = self.app.post('/students', headers=self.headers, json={'student_name': 'Incomplete'})
        self.assertEqual(response.status_code, 400)

        # 3. Create with Invalid Data Types
        print("   Testing Create with Invalid Data Types...")
        invalid_data = {
            'student_id': 'abc', # Should be int
            'student_name': 'Test',
            'year_level': 1,
            'gpa': 4.0,
            'dept_id': 1
        }
        response = self.app.post('/students', headers=self.headers, json=invalid_data)
        self.assertEqual(response.status_code, 400)

        # 4. Get Non-Existent Student
        print("   Testing Get Non-Existent Student...")
        response = self.app.get('/students/99999', headers=self.headers)
        self.assertEqual(response.status_code, 404)

        # 5. Update Non-Existent Student
        print("   Testing Update Non-Existent Student...")
        response = self.app.put('/students/99999', headers=self.headers, json={'gpa': 4.0})
        self.assertEqual(response.status_code, 404)

        # 6. Delete Non-Existent Student
        print("   Testing Delete Non-Existent Student...")
        response = self.app.delete('/students/99999', headers=self.headers)
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()