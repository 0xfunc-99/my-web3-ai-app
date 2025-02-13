import requests
import json
from datetime import datetime

def test_blockchain_security_model():
    # Test cases for blockchain security
    test_cases = [
        # Smart Contract Vulnerabilities
        {
            "name": "Reentrancy Attack",
            "data": {
                "data": "function withdraw() { msg.sender.call.value(balance)(); balance = 0; }",
                "name": "Malicious Contract",
                "address": "0x0",
                "location": "test"
            },
            "expected": "attack"
        },
        {
            "name": "Integer Overflow",
            "data": {
                "data": "function transfer(uint256 amount) { balances[msg.sender] += amount; }",
                "name": "Overflow Test",
                "address": "0x0",
                "location": "test"
            },
            "expected": "attack"
        },
        
        # Malicious Transaction Patterns
        {
            "name": "Gas Manipulation",
            "data": {
                "data": "gasPrice = 0; gasLimit = 999999999",
                "name": "Gas Attack",
                "address": "0x0",
                "location": "test"
            },
            "expected": "attack"
        },
        
        # Suspicious Addresses
        {
            "name": "Zero Address",
            "data": {
                "data": "transfer to 0x0000000000000000000000000000000000000000",
                "name": "Zero Address Test",
                "address": "0x0000000000000000000000000000000000000000",
                "location": "test"
            },
            "expected": "attack"
        },
        
        # Function Call Manipulation
        {
            "name": "Malicious Function Call",
            "data": {
                "data": "selfdestruct(target); // Destructive operation",
                "name": "Destruct Test",
                "address": "0x0",
                "location": "test"
            },
            "expected": "attack"
        },
        
        # Safe Cases
        {
            "name": "Normal Transfer",
            "data": {
                "data": "transfer(100 ETH)",
                "name": "Valid Transfer",
                "address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
                "location": "test"
            },
            "expected": "safe"
        },
        {
            "name": "Normal Contract Interaction",
            "data": {
                "data": "function deposit() public payable { balance += msg.value; }",
                "name": "Valid Contract",
                "address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
                "location": "test"
            },
            "expected": "safe"
        }
    ]

    # Test results
    results = {
        "total": len(test_cases),
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "details": []
    }

    print(f"Starting Blockchain Security Model Tests at {datetime.now()}\n")
    print("=" * 50)

    # Run tests
    for test in test_cases:
        try:
            print(f"\nTesting: {test['name']}")
            print("-" * 30)
            
            # Send request to your AI model endpoint
            response = requests.post(
                'http://localhost:5002/predict',
                json=test['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 200:
                print(f"❌ Error: HTTP {response.status_code}")
                results["errors"] += 1
                continue

            result = response.json()
            prediction = result.get('prediction', '').lower()
            
            # Compare prediction with expected result
            test_passed = prediction == test['expected']
            
            # Store test details
            test_result = {
                "name": test['name'],
                "input": test['data']['data'],
                "expected": test['expected'],
                "got": prediction,
                "passed": test_passed
            }
            
            results["details"].append(test_result)
            
            if test_passed:
                results["passed"] += 1
                print(f"✅ Test Passed")
            else:
                results["failed"] += 1
                print(f"❌ Test Failed")
                print(f"Expected: {test['expected']}")
                print(f"Got: {prediction}")
            
            # Print confidence score if available
            if 'confidence' in result:
                print(f"Confidence: {result['confidence']:.2f}")
                
        except Exception as e:
            print(f"❌ Error running test: {str(e)}")
            results["errors"] += 1
            results["details"].append({
                "name": test['name'],
                "error": str(e)
            })

    # Print summary
    print("\n" + "=" * 50)
    print("\nTest Summary:")
    print(f"Total Tests: {results['total']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Errors: {results['errors']}")
    print(f"Success Rate: {(results['passed']/results['total'] * 100):.2f}%")

    # Save detailed results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to {filename}")

if __name__ == "__main__":
    test_blockchain_security_model() 