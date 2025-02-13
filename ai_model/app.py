from flask import Flask, request, jsonify
import logging
import os
from datetime import datetime
from flask_cors import CORS
import joblib
from web3 import Web3
import re
import numpy as np
from collections import Counter
from datetime import datetime, timedelta
import json
import traceback
import sys
from admin_auth import verify_admin_credentials, generate_token, admin_required

app = Flask(__name__)
CORS(app)

# Ensure logs directory exists
current_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(current_dir, 'logs')
os.makedirs(log_dir, exist_ok=True)

# Define log file paths
app_log_file = os.path.join(log_dir, 'app.log')
security_log_file = os.path.join(log_dir, 'security.log')

# Create log files if they don't exist, but don't clear existing content
if not os.path.exists(app_log_file):
    with open(app_log_file, 'w', encoding='utf-8') as f:
        f.write('')
if not os.path.exists(security_log_file):
    with open(security_log_file, 'w', encoding='utf-8') as f:
        f.write('')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler(app_log_file, mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Configure werkzeug logger
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.INFO)

# Function to write logs
def write_log(message):
    """Write log message to file and console"""
    logging.info(message)

# Function to write security logs
def write_security_log(message):
    """Write security log message to both files"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(security_log_file, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} - {message}\n")
    write_log(f"{timestamp} - {message}")

# Test logging
write_log("Server starting...")

# Load vectorizer and model using joblib
try:
    vectorizer = joblib.load('models/vectorizer.pkl')
    model = joblib.load('models/naive_bayes_model.pkl')
    write_log(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Successfully loaded ML models")
except Exception as e:
    write_log(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error loading models: {str(e)}")
    raise

# Connect to Ganache blockchain
GANACHE_URL = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(GANACHE_URL))

# Remove automatic account setting
# web3.eth.default_account = web3.eth.accounts[0]  # Remove this line

if not web3.is_connected():
    write_log("Cannot connect to blockchain!")
    raise Exception("Blockchain connection failed")

write_log(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Connected to blockchain network")

# Contract configuration
CONTRACT_ADDRESS = "0x7635615a00cbC897Bd020468C4338B194C8CC948"
CONTRACT_ABI = [
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "userAccount",
        "type": "address"
      },
      {
        "indexed": False,
        "internalType": "string",
        "name": "name",
        "type": "string"
      },
      {
        "indexed": False,
        "internalType": "string",
        "name": "userAddress",
        "type": "string"
      },
      {
        "indexed": False,
        "internalType": "string",
        "name": "location",
        "type": "string"
      }
    ],
    "name": "UserDataSaved",
    "type": "event"
  },
  {
    "inputs": [
      {
        "internalType": "string",
        "name": "_name",
        "type": "string"
      },
      {
        "internalType": "string",
        "name": "_userAddress",
        "type": "string"
      },
      {
        "internalType": "string",
        "name": "_location",
        "type": "string"
      }
    ],
    "name": "saveUserData",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getUserData",
    "outputs": [
      {
        "components": [
          {
            "internalType": "string",
            "name": "name",
            "type": "string"
          },
          {
            "internalType": "string",
            "name": "userAddress",
            "type": "string"
          },
          {
            "internalType": "string",
            "name": "location",
            "type": "string"
          }
        ],
        "internalType": "struct UserDataStorage.UserData[]",
        "name": "",
        "type": "tuple[]"
      }
    ],
    "stateMutability": "view",
    "type": "function",
    "constant": True
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_userAddress",
        "type": "address"
      }
    ],
    "name": "getUserDataByAddress",
    "outputs": [
      {
        "components": [
          {
            "internalType": "string",
            "name": "name",
            "type": "string"
          },
          {
            "internalType": "string",
            "name": "userAddress",
            "type": "string"
          },
          {
            "internalType": "string",
            "name": "location",
            "type": "string"
          }
        ],
        "internalType": "struct UserDataStorage.UserData[]",
        "name": "",
        "type": "tuple[]"
      }
    ],
    "stateMutability": "view",
    "type": "function",
    "constant": True
  }
]

# Load the smart contract
contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
write_log("Smart contract loaded successfully")

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    return request.remote_addr

def check_blockchain_fraud(transaction_data):
    """Check for potential blockchain fraud indicators"""
    fraud_indicators = {
        'high_gas_price': False,
        'suspicious_value': False,
        'rapid_transactions': False
    }
    
    try:
        # Check gas price against network average
        avg_gas_price = web3.eth.gas_price
        if transaction_data.get('gasPrice', 0) > avg_gas_price * 2:
            fraud_indicators['high_gas_price'] = True
            
        # Check for suspicious transaction value
        if transaction_data.get('value', 0) > web3.to_wei(100, 'ether'):
            fraud_indicators['suspicious_value'] = True
            
        # Check for rapid transactions from same address
        recent_blocks = [web3.eth.get_block('latest', full_transactions=True) for _ in range(5)]
        sender_txs = sum(1 for block in recent_blocks for tx in block['transactions'] 
                        if tx['from'] == transaction_data.get('from'))
        if sender_txs > 10:  # More than 10 transactions in last 5 blocks
            fraud_indicators['rapid_transactions'] = True
            
        return fraud_indicators
        
    except Exception as e:
        write_log(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error in blockchain fraud check: {str(e)}")
        return fraud_indicators

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Log request details
        client_ip = request.remote_addr
        timestamp = datetime.now().strftime('%d/%b/%Y %H:%M:%S')
        
        # Log OPTIONS request
        if request.method == 'OPTIONS':
            write_log(f"{client_ip} - - [{timestamp}] \"OPTIONS /predict HTTP/1.1\" 200 -")
            return jsonify({"status": "ok"}), 200

        data = request.json
        if not data:
            write_log(f"{client_ip} - - [{timestamp}] \"POST /predict HTTP/1.1\" 400 -")
            return jsonify({"error": "No data provided"}), 400

        # Extract fields
        name = data.get('name', '')
        user_address = data.get('address', '')
        location = data.get('location', '')
        
        # Check each field for XSS
        fields_to_check = {
            'name': name,
            'address': user_address,
            'location': location
        }
        
        for field_name, field_value in fields_to_check.items():
            if not field_value:
                continue
            
            # Transform input using vectorizer
            X = vectorizer.transform([field_value])
            
            # Get prediction and confidence
            prediction = model.predict(X)[0]
            confidence = np.max(model.predict_proba(X)[0])
            
            # If ML model detects attack with high confidence
            if prediction == 'attack' and confidence > 0.75:
                write_log(f"{client_ip} - - [{timestamp}] \"POST /predict HTTP/1.1\" 403 -")
                return jsonify({
                    "error": "Security threat detected - Transaction blocked",
                    "status": "blocked",
                    "field": field_name,
                    "confidence": float(confidence)
                }), 403

        try:
            # Build transaction for MetaMask
            transaction = contract.functions.saveUserData(
                name,
                user_address,
                location
            ).build_transaction({
                'gas': 2000000,
                'gasPrice': web3.eth.gas_price,
                'nonce': 0,  # This will be set by MetaMask
                'chainId': 1337  # Ganache chain ID
            })
            
            write_log(f"{client_ip} - - [{timestamp}] \"POST /predict HTTP/1.1\" 200 -")
            
            return jsonify({
                "status": "pending",
                "message": "Please confirm the transaction in MetaMask",
                "transaction_data": {
                    "to": CONTRACT_ADDRESS,
                    "data": transaction['data'],
                    "gas": str(transaction['gas']),
                    "gasPrice": str(transaction['gasPrice']),
                    "chainId": transaction['chainId']
                }
            })
            
        except Exception as e:
            write_log(f"{client_ip} - - [{timestamp}] \"POST /predict HTTP/1.1\" 500 -")
            return jsonify({"error": f"Blockchain error: {str(e)}"}), 500

    except Exception as e:
        write_log(f"{client_ip} - - [{timestamp}] \"POST /predict HTTP/1.1\" 500 -")
        return jsonify({"error": f"Error in /predict endpoint: {str(e)}"}), 500

@app.route('/admin/logs', methods=['GET'])
def get_logs():
    try:
        with open(app_log_file, 'r') as f:
            logs = f.readlines()
        
        # Parse and format logs
        parsed_logs = []
        for log in logs:
            try:
                # Only process logs that contain actual transactions
                if "POST /predict" in log:
                    # Extract timestamp if it exists in the log
                    timestamp_match = re.search(r'\[(.*?)\]', log)
                    if timestamp_match:
                        timestamp = timestamp_match.group(1)
                    else:
                        # If log starts with timestamp in different format
                        timestamp_parts = log.split(' - ', 1)
                        if len(timestamp_parts) > 1:
                            timestamp = timestamp_parts[0]
                        else:
                            continue

                    # Determine status and type based on response code
                    if '403' in log:
                        status = 'Blocked'
                        log_type = 'Security Alert'
                        message = 'Security threat detected - Transaction blocked'
                    elif '200' in log:
                        status = 'Success'
                        log_type = 'Transaction'
                        message = 'New blockchain transaction processed'
                    else:
                        status = 'Failed'
                        log_type = 'Transaction'
                        message = 'Transaction failed to process'

                    parsed_logs.append({
                        'timestamp': timestamp,
                        'type': log_type,
                        'message': message,
                        'status': status
                    })
            except:
                continue
        
        return jsonify({
            'logs': parsed_logs,
            'stats': {
                'total_transactions': len(parsed_logs),
                'successful_transactions': sum(1 for log in parsed_logs if log['status'] == 'Success'),
                'blocked_transactions': sum(1 for log in parsed_logs if log['status'] == 'Blocked'),
                'failed_transactions': sum(1 for log in parsed_logs if log['status'] == 'Failed')
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint to verify server is running and healthy"""
    try:
        # Check if ML models are loaded
        if not (vectorizer and model):
            return jsonify({"status": "error", "message": "ML models not loaded"}), 503
        
        # Check blockchain connection
        if not web3.is_connected():
            return jsonify({"status": "error", "message": "Blockchain not connected"}), 503
            
        return jsonify({
            "status": "healthy",
            "message": "Server is running and all components are healthy",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        write_log(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Health check failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }), 500

@app.route('/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
            
        if verify_admin_credentials(username, password):
            token = generate_token(username)
            if token:
                return jsonify({
                    'token': token,
                    'username': username,
                    'message': 'Login successful'
                })
            else:
                return jsonify({'error': 'Error generating token'}), 500
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Server is running on http://0.0.0.0:5002")
    app.run(host='0.0.0.0', port=5002)