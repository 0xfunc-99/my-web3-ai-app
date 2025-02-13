import unittest
import requests
import json
from datetime import datetime

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:5002"
        self.test_results = []
        
    def test_predict_endpoint(self):
        """Test the /predict endpoint with various inputs"""
        test_cases = [
            {
                "input": {
                    "name": "John Doe",
                    "address": "123 Main St",
                    "location": "New York"
                },
                "expected_status": 200,
                "description": "Valid normal input"
            },
            {
                "input": {
                    "name": "<script>alert('xss')</script>",
                    "address": "123 Main St",
                    "location": "New York"
                },
                "expected_status": 403,
                "description": "XSS attack in name field"
            },
            {
                "input": {
                    "name": "John Doe",
                    "address": "<img src=x onerror=alert('XSS')>",
                    "location": "New York"
                },
                "expected_status": 403,
                "description": "XSS attack in address field"
            },
            {
                "input": {},
                "expected_status": 400,
                "description": "Empty request body"
            }
        ]
        
        for case in test_cases:
            response = requests.post(f"{self.base_url}/predict", json=case['input'])
            
            result = {
                "test_case": case['description'],
                "input": case['input'],
                "expected_status": case['expected_status'],
                "actual_status": response.status_code,
                "response": response.json(),
                "passed": response.status_code == case['expected_status']
            }
            self.test_results.append(result)
            
            self.assertEqual(response.status_code, case['expected_status'],
                           f"Failed test case: {case['description']}")
    
    def test_admin_login(self):
        """Test the /admin/login endpoint"""
        test_cases = [
            {
                "input": {
                    "username": "admin",
                    "password": "admin123"
                },
                "expected_status": 200,
                "description": "Valid admin credentials"
            },
            {
                "input": {
                    "username": "admin",
                    "password": "wrongpass"
                },
                "expected_status": 401,
                "description": "Invalid password"
            },
            {
                "input": {
                    "username": "nonexistent",
                    "password": "password"
                },
                "expected_status": 401,
                "description": "Non-existent user"
            },
            {
                "input": {},
                "expected_status": 400,
                "description": "Missing credentials"
            }
        ]
        
        for case in test_cases:
            response = requests.post(f"{self.base_url}/admin/login", json=case['input'])
            
            result = {
                "test_case": case['description'],
                "input": case['input'],
                "expected_status": case['expected_status'],
                "actual_status": response.status_code,
                "response": response.json(),
                "passed": response.status_code == case['expected_status']
            }
            self.test_results.append(result)
            
            self.assertEqual(response.status_code, case['expected_status'],
                           f"Failed test case: {case['description']}")
    
    def test_health_check(self):
        """Test the /health endpoint"""
        response = requests.get(f"{self.base_url}/health")
        
        result = {
            "test_case": "Health check endpoint",
            "expected_status": 200,
            "actual_status": response.status_code,
            "response": response.json(),
            "passed": response.status_code == 200
        }
        self.test_results.append(result)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'healthy')
    
    def tearDown(self):
        """Save API test results to a JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for r in self.test_results if r['passed']),
            "api_success_rate": float(sum(1 for r in self.test_results if r['passed'])) / len(self.test_results),
            "test_cases": self.test_results
        }
        
        filename = f'api_test_results_{timestamp}.json'
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nAPI test results saved to {filename}")
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed Tests: {results['passed_tests']}")
        print(f"API Success Rate: {results['api_success_rate']:.2%}")

if __name__ == '__main__':
    unittest.main(verbosity=2) 