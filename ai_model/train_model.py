import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
import joblib
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Extended training data with more XSS patterns
training_data = [
    # Attack patterns
    ("<script>alert('xss')</script>", "attack"),
    ("<img src=x onerror=alert('XSS')>", "attack"),
    ("<svg onload=alert(1)>", "attack"),
    ("javascript:alert(document.cookie)", "attack"),
    ("'; DROP TABLE users--", "attack"),
    ("<div onmouseover='alert(1)'>", "attack"),
    ("<scr<script>ipt>alert('nested')</scr</script>ipt>", "attack"),
    ("<img src='javascript:alert(\"XSS\")'/>", "attack"),
    ("<a href='javascript:alert(1)'>click me</a>", "attack"),
    ("'-prompt(8)-'", "attack"),
    ("<IMG SRC=javascript:alert('XSS')>", "attack"),
    ("<IMG SRC=JaVaScRiPt:alert('XSS')>", "attack"),
    ("<<SCRIPT>alert('XSS');//<</SCRIPT>", "attack"),
    ("<SCRIPT SRC=http://xss.rocks/xss.js></SCRIPT>", "attack"),
    ("<META HTTP-EQUIV=\"refresh\" CONTENT=\"0;url=javascript:alert('XSS');\">", "attack"),
    
    # Normal inputs
    ("John Doe", "normal"),
    ("123 Main Street", "normal"),
    ("New York, NY", "normal"),
    ("Downtown LA", "normal"),
    ("user@example.com", "normal"),
    ("555-123-4567", "normal"),
    ("https://example.com", "normal"),
    ("Alice Smith", "normal"),
    ("San Francisco, CA 94105", "normal"),
    ("42 Wallaby Way, Sydney", "normal"),
    ("特殊字符测试", "normal"),
    ("", "normal"),
    ("a" * 1000, "normal"),
    ("Mr. & Mrs. Smith", "normal"),
    ("O'Connor Street", "normal")
]

# Separate features and labels
X = [x[0] for x in training_data]
y = [x[1] for x in training_data]

# Create and fit the vectorizer
vectorizer = TfidfVectorizer(
    analyzer='char',
    ngram_range=(1, 4),
    min_df=0.0,
    max_df=1.0
)

# Transform the training data
X = vectorizer.fit_transform(X)

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = MultinomialNB()
model.fit(X_train, y_train)

# Evaluate the model
train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)

print(f"Training accuracy: {train_score:.2%}")
print(f"Testing accuracy: {test_score:.2%}")

# Save the model and vectorizer
joblib.dump(vectorizer, 'models/vectorizer.pkl')
joblib.dump(model, 'models/naive_bayes_model.pkl')

print("Model and vectorizer saved successfully")

if __name__ == "__main__":
    train_model() 