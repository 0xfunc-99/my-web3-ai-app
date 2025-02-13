import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
import joblib
import re

def create_training_data():
    # Training data with blockchain-specific patterns
    attack_patterns = [
        # Reentrancy Attacks
        "function withdraw() { msg.sender.call.value(balance)(); balance = 0; }",
        "msg.sender.call{value: amount}('')",
        "external call before state update",
        
        # Integer Overflow/Underflow
        "balance += amount",
        "totalSupply += amount",
        "balance -= amount without check",
        
        # Access Control
        "selfdestruct(target)",
        "delegatecall(",
        "suicide(",
        
        # Gas Manipulation
        "gasPrice = 0",
        "gasLimit = 999999999",
        "infinite loop in contract",
        
        # Malicious Addresses
        "0x0000000000000000000000000000000000000000",
        "0xdead000000000000000000000000000000000000",
        
        # Timestamp Manipulation
        "block.timestamp",
        "now >= deadline",
        
        # Function Selector Manipulation
        "0x4e487b71",
        "raw function selector manipulation",
        
        # Additional Attack Patterns
        "unchecked transfer",
        "arbitrary jump with function type variable",
        "uninitialized storage pointer",
        "floating pragma",
        "tx.origin for authentication"
    ]

    safe_patterns = [
        # Safe Transfer Patterns
        "transfer(100)",
        "safeTransfer(",
        "require(balance >= amount)",
        
        # Safe Contract Patterns
        "function deposit() public payable { balance += msg.value; }",
        "require(msg.sender == owner)",
        "onlyOwner modifier",
        
        # Safe Address Usage
        "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        "valid contract address",
        
        # Safe Function Calls
        "view function call",
        "pure function execution",
        
        # Safe State Updates
        "SafeMath.add(",
        "SafeMath.sub(",
        "checked arithmetic",
        
        # Access Control
        "Ownable contract",
        "role-based access control",
        
        # Input Validation
        "require(amount > 0)",
        "require(address != address(0))",
        
        # Event Emission
        "emit Transfer(",
        "emit Approval("
    ]

    # Create labels
    y = np.concatenate([
        np.array(['attack'] * len(attack_patterns)),
        np.array(['safe'] * len(safe_patterns))
    ])

    # Combine all patterns
    X = attack_patterns + safe_patterns

    return X, y

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove special characters but keep important symbols
    text = re.sub(r'[^\w\s(){}=;.]', '', text)
    return text

def train_model():
    print("Starting model training...")
    
    # Get training data
    X, y = create_training_data()
    
    # Preprocess the data
    X = [preprocess_text(x) for x in X]
    
    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create and train the vectorizer
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 3),
        analyzer='char_wb'
    )
    X_train_vectorized = vectorizer.fit_transform(X_train)
    
    # Train the model
    model = MultinomialNB(alpha=0.1)
    model.fit(X_train_vectorized, y_train)
    
    # Test the model
    X_test_vectorized = vectorizer.transform(X_test)
    accuracy = model.score(X_test_vectorized, y_test)
    print(f"Model accuracy: {accuracy * 100:.2f}%")
    
    # Save the model and vectorizer
    joblib.dump(vectorizer, 'models/vectorizer.pkl')
    joblib.dump(model, 'models/naive_bayes_model.pkl')
    print("Model and vectorizer saved successfully!")
    
    # Test some examples
    test_cases = [
        "function withdraw() { msg.sender.call.value(balance)(); balance = 0; }",
        "transfer(100)",
        "0x0000000000000000000000000000000000000000",
        "safeTransfer(recipient, amount)"
    ]
    
    print("\nTesting some examples:")
    for test in test_cases:
        test_vectorized = vectorizer.transform([preprocess_text(test)])
        prediction = model.predict(test_vectorized)[0]
        probability = model.predict_proba(test_vectorized)[0]
        confidence = max(probability)
        print(f"\nInput: {test}")
        print(f"Prediction: {prediction}")
        print(f"Confidence: {confidence:.2f}")

if __name__ == "__main__":
    train_model() 