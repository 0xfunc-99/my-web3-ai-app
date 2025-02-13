const { ethers } = require('ethers');
const UserAuthenticationAbi = require('../client/src/abis/UserAuthentication.json');

// Replace with your local Ganache or other testnet RPC
const provider = new ethers.providers.JsonRpcProvider('http://127.0.0.1:8545');

// TODO: Replace with your deployed contract address
const contractAddress = '0x1234567890abcdef1234567890abcdef12345678';

const contract = new ethers.Contract(contractAddress, UserAuthenticationAbi.abi, provider);

// Example function that might call an AI service
async function callAIForAnalysis(eventName, data) {
  console.log(`AI Service Called for ${eventName}`, data);
  // e.g., fetch('http://localhost:5000/analyze', { method: 'POST', body: JSON.stringify(data) })
}

function startMonitor() {
  console.log('Starting contract event monitor...');

  contract.on('UserRegistered', (userAddress, username) => {
    console.log(`UserRegistered - Address: ${userAddress} / Username: ${username}`);
    callAIForAnalysis('UserRegistered', { userAddress, username });
  });

  contract.on('UserLoginAttempt', (userAddress, success) => {
    console.log(`UserLoginAttempt - Address: ${userAddress} / Success: ${success}`);
    callAIForAnalysis('UserLoginAttempt', { userAddress, success });
  });
}

startMonitor();