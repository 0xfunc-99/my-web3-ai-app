import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import logging
from web3 import Web3

class BlockchainSecurityModel:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
        
    def extract_features(self, transaction_data):
        """Extract features from blockchain transaction data"""
        features = []
        try:
            # Gas price ratio to network average
            avg_gas_price = self.w3.eth.gas_price
            gas_price_ratio = transaction_data.get('gasPrice', avg_gas_price) / avg_gas_price
            features.append(gas_price_ratio)
            
            # Transaction value in ETH
            value_in_eth = self.w3.from_wei(transaction_data.get('value', 0), 'ether')
            features.append(float(value_in_eth))
            
            # Number of recent transactions from this address
            recent_blocks = [self.w3.eth.get_block('latest', full_transactions=True) for _ in range(5)]
            recent_txs = sum(1 for block in recent_blocks for tx in block['transactions'] 
                           if tx['from'] == transaction_data.get('from'))
            features.append(recent_txs)
            
            # Gas limit ratio to block gas limit
            block_gas_limit = self.w3.eth.get_block('latest')['gasLimit']
            gas_limit_ratio = transaction_data.get('gas', 21000) / block_gas_limit
            features.append(gas_limit_ratio)
            
            # Account balance ratio to transaction value
            if transaction_data.get('from'):
                balance = self.w3.eth.get_balance(transaction_data['from'])
                value = transaction_data.get('value', 0)
                balance_ratio = value / balance if balance > 0 else 1
                features.append(balance_ratio)
            else:
                features.append(0)
            
            return np.array(features).reshape(1, -1)
        except Exception as e:
            logging.error(f"Error extracting features: {str(e)}")
            return np.zeros((1, 5))  # Return zero features on error
    
    def generate_training_data(self):
        """Generate training data from blockchain history"""
        X = []
        y = []
        
        try:
            # Get recent blocks
            latest_block = self.w3.eth.block_number
            for block_num in range(max(0, latest_block - 1000), latest_block):
                block = self.w3.eth.get_block(block_num, full_transactions=True)
                
                for tx in block['transactions']:
                    features = self.extract_features(tx)
                    X.append(features[0])
                    
                    # Label transaction as suspicious if it meets certain criteria
                    is_suspicious = (
                        tx.get('value', 0) > self.w3.to_wei(100, 'ether') or  # High value
                        tx.get('gasPrice', 0) > self.w3.eth.gas_price * 2 or  # High gas price
                        len([t for t in block['transactions'] if t['from'] == tx['from']]) > 5  # Many transactions
                    )
                    y.append(1 if is_suspicious else 0)
            
            return np.array(X), np.array(y)
        except Exception as e:
            logging.error(f"Error generating training data: {str(e)}")
            return np.array([]), np.array([])
    
    def train(self):
        """Train the blockchain security model"""
        X, y = self.generate_training_data()
        
        if len(X) == 0 or len(y) == 0:
            logging.error("No training data available")
            return False
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        logging.info(f"Training accuracy: {train_score:.2%}")
        logging.info(f"Testing accuracy: {test_score:.2%}")
        
        # Save model
        joblib.dump(self.model, 'models/blockchain_security_model.pkl')
        return True
    
    def predict(self, transaction_data):
        """Predict if a transaction is suspicious"""
        features = self.extract_features(transaction_data)
        if features.size == 0:
            return True  # Consider suspicious if feature extraction fails
        
        prediction = self.model.predict(features)[0]
        probability = self.model.predict_proba(features)[0][1]  # Probability of being suspicious
        
        return {
            'is_suspicious': bool(prediction),
            'confidence': float(probability),
            'features': {
                'gas_price_ratio': float(features[0][0]),
                'value_in_eth': float(features[0][1]),
                'recent_transactions': int(features[0][2]),
                'gas_limit_ratio': float(features[0][3]),
                'balance_ratio': float(features[0][4])
            }
        }

if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize and train model
    model = BlockchainSecurityModel()
    if model.train():
        logging.info("Model trained and saved successfully")
    else:
        logging.error("Failed to train model") 