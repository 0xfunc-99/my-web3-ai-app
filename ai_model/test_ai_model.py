import unittest
import json
import numpy as np
from datetime import datetime
import joblib
import os

class TestAIModel(unittest.TestCase):
    def setUp(self):
        # Load the model and vectorizer
        self.vectorizer = joblib.load('models/vectorizer.pkl')
        self.model = joblib.load('models/naive_bayes_model.pkl')
        self.test_results = []
        
    def test_xss_detection(self):
        """Test XSS attack detection capabilities"""
        test_cases = [
            {
                "input": "<script>alert('xss')</script>",
                "expected": "attack",
                "description": "Basic XSS script tag"
            },
            {
                "input": "John Doe",
                "expected": "normal",
                "description": "Normal name input"
            },
            {
                "input": "<img src=x onerror=alert('XSS')>",
                "expected": "attack",
                "description": "IMG tag with onerror XSS"
            },
            {
                "input": "123 Main Street, New York",
                "expected": "normal",
                "description": "Normal address input"
            },
            {
                "input": "javascript:alert(document.cookie)",
                "expected": "attack",
                "description": "JavaScript protocol handler"
            },
            {
                "input": "<div onmouseover='alert(1)'>hover me</div>",
                "expected": "attack",
                "description": "Event handler XSS"
            },
            {
                "input": "Downtown LA",
                "expected": "normal",
                "description": "Normal location input"
            },
            {
                "input": "'; DROP TABLE users--",
                "expected": "attack",
                "description": "SQL injection attempt"
            }
        ]
        
        results = []
        for case in test_cases:
            # Transform input using vectorizer
            X = self.vectorizer.transform([case['input']])
            
            # Get prediction and confidence
            prediction = self.model.predict(X)[0]
            confidence = float(np.max(self.model.predict_proba(X)[0]))  # Convert to native Python float
            
            # Determine if test passed
            passed = bool((prediction == case['expected']) and (confidence > 0.75 if prediction == 'attack' else True))
            
            result = {
                "test_case": case['description'],
                "input": case['input'],
                "expected": case['expected'],
                "actual": prediction,
                "confidence": confidence,
                "passed": passed
            }
            results.append(result)
            
            # Add to test results
            self.test_results.append(result)
            
            # Assert test case
            if case['expected'] == 'attack':
                self.assertTrue(prediction == 'attack' and confidence > 0.75,
                              f"Failed to detect XSS attack: {case['input']}")
            else:
                self.assertEqual(prediction, 'normal',
                               f"False positive on normal input: {case['input']}")
    
    def test_model_robustness(self):
        """Test model robustness with edge cases"""
        edge_cases = [
            {
                "input": "",
                "expected": "normal",
                "description": "Empty input"
            },
            {
                "input": "a" * 1000,
                "expected": "normal",
                "description": "Very long input"
            },
            {
                "input": "特殊字符测试",
                "expected": "normal",
                "description": "Non-ASCII characters"
            },
            {
                "input": "<scr<script>ipt>alert('nested')</scr</script>ipt>",
                "expected": "attack",
                "description": "Nested XSS attempt"
            }
        ]
        
        for case in edge_cases:
            X = self.vectorizer.transform([case['input']])
            prediction = self.model.predict(X)[0]
            confidence = float(np.max(self.model.predict_proba(X)[0]))  # Convert to native Python float
            
            result = {
                "test_case": case['description'],
                "input": case['input'],
                "expected": case['expected'],
                "actual": prediction,
                "confidence": confidence,
                "passed": bool(prediction == case['expected'])  # Convert to native Python boolean
            }
            self.test_results.append(result)
    
    def tearDown(self):
        """Save test results to a JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for r in self.test_results if r['passed']),
            "model_accuracy": float(sum(1 for r in self.test_results if r['passed'])) / len(self.test_results),
            "test_cases": self.test_results
        }
        
        filename = f'test_results_{timestamp}.json'
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nTest results saved to {filename}")
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed Tests: {results['passed_tests']}")
        print(f"Model Accuracy: {results['model_accuracy']:.2%}")

if __name__ == '__main__':
    unittest.main(verbosity=2) 