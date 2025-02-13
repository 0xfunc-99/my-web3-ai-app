# Web3 AI Application Deployment Guide

## Prerequisites

- Node.js and npm installed
- Python 3.x installed
- Ganache CLI installed globally (`npm install -g ganache-cli`)
- MetaMask browser extension installed
- Git (optional)

## Step 1: Clone and Setup

1. Clone the repository (if using Git):

   ```bash
   git clone <repository-url>
   cd my-web3-ai-app
   ```

2. Install frontend dependencies:

   ```bash
   cd client
   npm install
   ```

3. Install backend dependencies:
   ```bash
   cd ../ai_model
   pip install -r requirements.txt
   ```

## Step 2: Deploy Smart Contract

1. Start Ganache:

   ```bash
   ganache-cli
   ```

   Keep this terminal window open.

2. Note down the following from Ganache output:

   - RPC Server URL (default: http://127.0.0.1:8545)
   - Available Accounts (first address)
   - Private Keys (corresponding to the first address)

3. Deploy the smart contract:

   ```bash
   # In a new terminal, from the project root
   truffle migrate --reset
   ```

4. Copy the deployed contract address from the migration output
   - Look for "contract address:" in the output
   - Save this address for later use

## Step 3: Configure MetaMask

1. Open MetaMask in your browser
2. Add Ganache Network:

   - Click Network dropdown -> Add Network -> Add Network Manually
   - Network Name: Ganache
   - RPC URL: http://127.0.0.1:8545
   - Chain ID: 1337
   - Currency Symbol: ETH

3. Import Ganache Account:
   - Click account icon -> Import Account
   - Paste the private key from Ganache
   - You should see a balance of 100 ETH

## Step 4: Update Contract Address

1. Update the contract address in frontend files:

   ```javascript
   // client/src/pages/SaveUserData.js
   // client/src/pages/FetchUserData.js
   const contractAddress = "YOUR_CONTRACT_ADDRESS";
   ```

2. Update the contract address in backend:
   ```python
   # ai_model/app.py
   CONTRACT_ADDRESS = "YOUR_CONTRACT_ADDRESS"
   ```

## Step 5: Update Contract ABI

1. Run the ABI update script:
   ```bash
   cd ai_model
   python sceipt.py
   ```
   This will copy the contract ABI to the necessary locations.

## Step 6: Start the Application

1. Start the AI backend server:

   ```bash
   # In ai_model directory
   python app.py
   ```

   The server will run on http://localhost:5002

2. Start the React frontend:
   ```bash
   # In a new terminal, in client directory
   npm start
   ```
   The application will open at http://localhost:3000

## Step 7: Verify Setup

1. Connect MetaMask to the application:

   - Click "Connect Wallet" in the application
   - Approve the connection in MetaMask

2. Test the application:
   - Try saving some data
   - Verify data can be fetched
   - Check the Admin Portal at http://localhost:3000/admin

## Troubleshooting

- If you restart Ganache:

  1. Reset your MetaMask account (Settings -> Advanced -> Reset Account)
  2. Redeploy the contract (`truffle migrate --reset`)
  3. Update the new contract address in all files
  4. Run the ABI update script again

- Common Issues:
  - "Internal JSON-RPC error": Make sure you're connected to Ganache in MetaMask
  - "Contract not found": Verify contract address is updated in all files
  - "MetaMask not connected": Reset connection and reconnect wallet
  - "Transaction failed": Ensure sufficient ETH in MetaMask account

## Additional Notes

- The AI model runs on port 5002
- The frontend runs on port 3000
- Ganache runs on port 8545
- Make sure all these ports are available
- Keep your private keys secure and never share them
- For development, use Ganache's test ETH only
