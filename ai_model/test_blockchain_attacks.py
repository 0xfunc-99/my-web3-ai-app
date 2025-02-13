import requests
import json
from datetime import datetime

def test_blockchain_attacks():
    test_cases = [
        # Real-world Attack Scenarios
        {
            "name": "TheDAO Reentrancy Attack",
            "data": {
                "data": "function withdraw() { msg.sender.call.value(balance)(); balance = 0; }",
                "name": "DAO Attack",
                "address": "0x0",
                "location": "test"
            },
            "expected": "attack"
        },
        {
            "name": "Parity Wallet Hack",
            "data": {
                "data": "function initWallet(address _owner) public { require(owner == address(0)); owner = _owner; }",
                "name": "Parity Init",
                "address": "0x0",
                "location": "test"
            },
            "expected": "attack"
        },
        {
            "name": "Integer Overflow Token",
            "data": {
                "data": "function transfer(address to, uint256 amount) { balances[msg.sender] -= amount; balances[to] += amount; }",
                "name": "Overflow",
                "address": "0x0",
                "location": "test"
            },
            "expected": "attack"
        },
        
        # Smart Contract Vulnerabilities
        {
            "name": "Unchecked External Call",
            "data": {
                "data": "addr.call(abi.encodeWithSignature('transfer(address,uint256)', to, amount));",
                "name": "External Call",
                "address": "0x0",
                "location": "test"
            },
            "expected": "attack"
        },
        {
            "name": "Timestamp Dependence",
            "data": {
                "data": "require(block.timestamp >= deadline);",
                "name": "Time Lock",
                "address": "0x0",
                "location": "test"
            },
            "expected": "attack"
        },

        # Safe Transactions (Should Pass)
        {
            "name": "Safe Transfer with Check",
            "data": {
                "data": "require(balance >= amount); balance -= amount; emit Transfer(msg.sender, to, amount);",
                "name": "Safe Transfer",
                "address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
                "location": "test"
            },
            "expected": "safe"
        },
        {
            "name": "OpenZeppelin SafeMath",
            "data": {
                "data": "using SafeMath for uint256; balance = balance.add(amount);",
                "name": "Safe Math",
                "address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
                "location": "test"
            },
            "expected": "safe"
        }
    ]

    print(f"\nStarting Blockchain Security Tests at {datetime.now()}")
    print("=" * 60)

    results = {
        "total": len(test_cases),
        "passed": 0,
        "failed": 0,
        "details": []
    }

    for test in test_cases:
        try:
            print(f"\nTesting: {test['name']}")
            print("-" * 40)
            
            response = requests.post(
                'http://localhost:5002/predict',
                json=test['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                prediction = result.get('prediction', '').lower()
                confidence = result.get('confidence', 0)
                patterns = result.get('detected_patterns', [])
                
                test_passed = prediction == test['expected']
                
                if test_passed:
                    results['passed'] += 1
                    status = '✅ PASSED'
                else:
                    results['failed'] += 1
                    status = '❌ FAILED'
                
                print(f"Status: {status}")
                print(f"Input: {test['data']['data'][:100]}...")
                print(f"Expected: {test['expected']}")
                print(f"Got: {prediction}")
                print(f"Confidence: {confidence:.2f}")
                if patterns:
                    print(f"Detected Patterns: {', '.join(patterns)}")
                
                results['details'].append({
                    'name': test['name'],
                    'status': status,
                    'expected': test['expected'],
                    'got': prediction,
                    'confidence': confidence,
                    'patterns': patterns
                })
                
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                results['failed'] += 1
                
        except Exception as e:
            print(f"❌ Error running test: {str(e)}")
            results['failed'] += 1

    print("\n" + "=" * 60)
    print("\nTest Summary:")
    print(f"Total Tests: {results['total']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Success Rate: {(results['passed']/results['total'] * 100):.2f}%")

    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"blockchain_test_results_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to {filename}")

if __name__ == "__main__":
    test_blockchain_attacks() 