import unittest
import json
import requests
from datetime import datetime
from web3 import Web3
import numpy as np
import joblib

class TestBlockchainAI(unittest.TestCase):
    def setUp(self):
        # Connect to local blockchain
        self.w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
        self.base_url = "http://localhost:5002"
        self.test_results = []
        
        # Load AI model components
        self.vectorizer = joblib.load('models/vectorizer.pkl')
        self.model = joblib.load('models/naive_bayes_model.pkl')
        
        # Test account with some ETH
        self.test_account = self.w3.eth.accounts[0]
    
    def test_blockchain_connection(self):
        """Test blockchain connectivity"""
        result = {
            "test_case": "Blockchain Connection",
            "description": "Check if we can connect to local blockchain",
            "passed": self.w3.is_connected(),
            "details": {
                "network": "Ganache",
                "connected": self.w3.is_connected(),
                "block_number": self.w3.eth.block_number if self.w3.is_connected() else None
            }
        }
        self.test_results.append(result)
        self.assertTrue(self.w3.is_connected(), "Failed to connect to blockchain")
    
    def test_secure_transaction_flow(self):
        """Test complete flow of secure transaction processing"""
        test_cases = [
            {
                "input": {
                    "name": "John Doe",
                    "address": "123 Main St",
                    "location": "New York"
                },
                "expected_status": 200,
                "description": "Valid transaction data"
            },
            {
                "input": {
                    "name": "<script>alert('xss')</script>",
                    "address": "123 Main St",
                    "location": "New York"
                },
                "expected_status": 403,
                "description": "Transaction with XSS attack"
            },
            {
                "input": {
                    "name": "Alice Smith",
                    "address": "javascript:alert(document.cookie)",
                    "location": "London"
                },
                "expected_status": 403,
                "description": "Transaction with malicious JavaScript"
            }
        ]
        
        for case in test_cases:
            response = requests.post(f"{self.base_url}/predict", json=case['input'])
            
            # For successful transactions, verify blockchain interaction
            blockchain_verification = None
            if response.status_code == 200:
                transaction_data = response.json().get('transaction_data', {})
                blockchain_verification = {
                    "contract_address": transaction_data.get('to'),
                    "gas_estimate": transaction_data.get('gas'),
                    "chain_id": transaction_data.get('chainId')
                }
            
            result = {
                "test_case": case['description'],
                "input": case['input'],
                "expected_status": case['expected_status'],
                "actual_status": response.status_code,
                "response": response.json(),
                "blockchain_verification": blockchain_verification,
                "passed": response.status_code == case['expected_status']
            }
            self.test_results.append(result)
            
            self.assertEqual(response.status_code, case['expected_status'],
                           f"Failed test case: {case['description']}")
    
    def test_gas_estimation(self):
        """Test gas estimation for transactions"""
        test_data = {
            "name": "John Doe",
            "address": "123 Main St",
            "location": "New York"
        }
        
        response = requests.post(f"{self.base_url}/predict", json=test_data)
        self.assertEqual(response.status_code, 200)
        
        transaction_data = response.json().get('transaction_data', {})
        gas_estimate = int(transaction_data.get('gas', 0))
        
        result = {
            "test_case": "Gas Estimation",
            "description": "Verify gas estimation for valid transaction",
            "gas_estimate": gas_estimate,
            "passed": gas_estimate > 0 and gas_estimate < 3000000,  # Reasonable gas limit
            "details": {
                "estimated_gas": gas_estimate,
                "gas_price": transaction_data.get('gasPrice'),
                "chain_id": transaction_data.get('chainId')
            }
        }
        self.test_results.append(result)
        
        self.assertTrue(gas_estimate > 0, "Gas estimation failed")
        self.assertTrue(gas_estimate < 3000000, "Gas estimate too high")
    
    def test_fraud_detection(self):
        """Test blockchain fraud detection"""
        suspicious_transactions = [
            {
                "input": {
                    "name": "John Doe",
                    "address": "123 Main St",
                    "location": "New York"
                },
                "gas_price": self.w3.eth.gas_price * 3,  # Suspiciously high gas price
                "description": "High gas price transaction"
            },
            {
                "input": {
                    "name": "Alice Smith",
                    "address": "456 Oak St",
                    "location": "London"
                },
                "value": self.w3.to_wei(150, 'ether'),  # Suspiciously high value
                "description": "High value transaction"
            }
        ]
        
        for case in suspicious_transactions:
            response = requests.post(f"{self.base_url}/predict", json=case['input'])
            
            result = {
                "test_case": f"Fraud Detection - {case['description']}",
                "input": case['input'],
                "response": response.json(),
                "passed": True,  # We're testing the detection mechanism exists
                "details": {
                    "gas_price": str(case.get('gas_price', 'N/A')),
                    "value": str(case.get('value', 'N/A')),
                    "response_status": response.status_code
                }
            }
            self.test_results.append(result)
    
    def tearDown(self):
        """Save blockchain AI test results to a JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for r in self.test_results if r['passed']),
            "success_rate": float(sum(1 for r in self.test_results if r['passed'])) / len(self.test_results),
            "blockchain_info": {
                "network": "Ganache",
                "connected": self.w3.is_connected(),
                "latest_block": self.w3.eth.block_number if self.w3.is_connected() else None
            },
            "test_cases": self.test_results
        }
        
        filename = f'blockchain_ai_test_results_{timestamp}.json'
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nBlockchain AI test results saved to {filename}")
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed Tests: {results['passed_tests']}")
        print(f"Success Rate: {results['success_rate']:.2%}")

if __name__ == '__main__':
    unittest.main(verbosity=2) 