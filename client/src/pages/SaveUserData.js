import React, { useState, useEffect } from 'react';
import { ethers } from 'ethers';
import UserDataStorageAbi from '../abis/UserDataStorage.json';
import axios from 'axios';

function SaveUserData() {
  const [name, setName] = useState('');
  const [userAddress, setUserAddress] = useState('');
  const [location, setLocation] = useState('');
  const [status, setStatus] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [account, setAccount] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [transactionHash, setTransactionHash] = useState('');

  const contractAddress = '0x7635615a00cbC897Bd020468C4338B194C8CC948';

  // Check if wallet is connected on component mount
  useEffect(() => {
    checkIfWalletIsConnected();
    // Add listener for account changes
    if (window.ethereum) {
      window.ethereum.on('accountsChanged', handleAccountsChanged);
      window.ethereum.on('chainChanged', () => window.location.reload());
    }
    return () => {
      if (window.ethereum) {
        window.ethereum.removeListener('accountsChanged', handleAccountsChanged);
      }
    };
  }, []);

  const handleAccountsChanged = (accounts) => {
    if (accounts.length > 0) {
      setAccount(accounts[0]);
      setIsConnected(true);
    } else {
      setAccount('');
      setIsConnected(false);
    }
  };

  const checkIfWalletIsConnected = async () => {
    try {
      if (!window.ethereum) {
        setStatus('Please install MetaMask!');
        return;
      }

      const accounts = await window.ethereum.request({ method: 'eth_accounts' });
      if (accounts.length > 0) {
        setAccount(accounts[0]);
        setIsConnected(true);
      }
    } catch (error) {
      console.error('Error checking wallet connection:', error);
    }
  };

  const connectWallet = async () => {
    try {
      if (!window.ethereum) {
        alert('Please install MetaMask!');
        return;
      }

      setStatus('Connecting to MetaMask...');
      const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
      setAccount(accounts[0]);
      setIsConnected(true);
      setStatus('Wallet connected successfully!');
    } catch (error) {
      console.error('Error connecting wallet:', error);
      setStatus('Error connecting wallet. Please try again.');
    }
  };

  const saveDataToBlockchain = async () => {
    if (!isConnected) {
      setStatus('Please connect your wallet first!');
      return;
    }

    try {
      setStatus('Saving data to blockchain...');
      
      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const signerAddress = await signer.getAddress();
      
      console.log('Connected with address:', signerAddress);
      
      const contract = new ethers.Contract(
        contractAddress,
        UserDataStorageAbi,
        signer
      );

      console.log('Saving data:', { name, userAddress, location });

      // Create transaction with simplified parameters
      const tx = await contract.saveUserData(
        name,
        userAddress,
        location,
        {
          from: signerAddress,
          gasLimit: ethers.parseUnits("300000", "wei") // Fixed gas limit
        }
      );

      console.log('Transaction hash:', tx.hash);
      setStatus('Transaction sent! Waiting for confirmation...');

      // Wait for transaction confirmation
      const receipt = await tx.wait();
      console.log('Transaction confirmed:', receipt);

      if (receipt.status === 1) {
        setStatus('Data saved successfully!');
        // Clear form after successful save
        setName('');
        setUserAddress('');
        setLocation('');
      } else {
        setStatus('Transaction failed. Please try again.');
      }

    } catch (error) {
      console.error('Save error:', error);
      if (error.code === 'ACTION_REJECTED') {
        setStatus('Transaction was rejected by user.');
      } else if (error.code === 'INSUFFICIENT_FUNDS') {
        setStatus('Error: Insufficient funds for gas. Please check your balance.');
      } else {
        setStatus('Error saving data: ' + (error.message || 'Unknown error'));
      }
    }
  };

  async function checkTransaction(txData) {
    try {
      const response = await fetch('/api/analyze-transaction', {
        method: 'POST',
        body: JSON.stringify(txData)
      });
      
      const analysis = await response.json();
      
      if (analysis.is_suspicious) {
        displayWarning({
          riskLevel: analysis.risk_level,
          score: analysis.risk_score,
          details: analysis.risk_factors
        });
      }
      
    } catch (error) {
      console.error('Error analyzing transaction:', error);
    }
  }

  // Add server health check and better error handling
  const checkServerHealth = async () => {
    try {
      const response = await axios.get('http://localhost:5002/health');
      return response.status === 200;
    } catch (error) {
      console.error('Server health check failed:', error);
      return false;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setStatusMessage('');
    setTransactionHash('');

    try {
      // Check if server is available
      const isServerHealthy = await checkServerHealth();
      if (!isServerHealthy) {
        setStatusMessage('Error: Server is not available. Please try again later.');
        setIsLoading(false);
        return;
      }

      // Check if wallet is connected
      if (!isConnected) {
        setStatusMessage('Please connect your wallet first.');
        setIsLoading(false);
        return;
      }

      // Get the signer
      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const signerAddress = await signer.getAddress();

      // Proceed with data submission for security check
      const response = await axios.post('http://localhost:5002/predict', {
        name,
        address: userAddress,
        location
      });

      if (response.data.status === 'pending') {
        // Get transaction data from response
        const txData = response.data.transaction_data;

        // Prepare transaction
        const contract = new ethers.Contract(
          contractAddress,
          UserDataStorageAbi,
          signer
        );

        // Send transaction through MetaMask
        const tx = await contract.saveUserData(
          name,
          userAddress,
          location,
          {
            gasLimit: txData.gas,  // Use gas from backend
            gasPrice: BigInt(txData.gasPrice),  // Convert string to BigInt
            chainId: txData.chainId  // Use chainId from backend
          }
        );

        setStatusMessage('Transaction sent! Waiting for confirmation...');
        console.log('Transaction hash:', tx.hash);

        // Wait for transaction confirmation
        const receipt = await tx.wait();
        
        if (receipt.status === 1) {
          setStatusMessage('Data saved successfully!');
          setTransactionHash(tx.hash);
          // Clear form
          setName('');
          setUserAddress('');
          setLocation('');
        } else {
          setStatusMessage('Transaction failed. Please try again.');
        }
      } else {
        setStatusMessage(`Error: ${response.data.error}`);
      }
    } catch (error) {
      console.error('Error:', error);
      if (error.code === 'ACTION_REJECTED') {
        setStatusMessage('Transaction was rejected in MetaMask.');
      } else if (error.code === 'INSUFFICIENT_FUNDS') {
        setStatusMessage('Error: Insufficient funds for gas.');
      } else if (!error.response) {
        setStatusMessage('Error: Cannot connect to server. Please ensure the server is running.');
      } else {
        setStatusMessage(`Error: ${error.response?.data?.error || 'Something went wrong'}`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.formContainer}>
      <h2 style={styles.title}>Save User Data</h2>
      
      {!isConnected ? (
        <div style={styles.connectContainer}>
          <p style={styles.description}>Please connect your wallet to save data.</p>
          <button onClick={connectWallet} style={styles.connectButton}>
            Connect Wallet
          </button>
        </div>
      ) : (
        <>
          <div style={styles.connectedStatus}>
            <span style={styles.connectedIcon}></span>
            Connected: {account.slice(0, 6)}...{account.slice(-4)}
          </div>
          
          <p style={styles.description}>Enter your details to save them to the blockchain.</p>
          
          <div style={styles.inputGroup}>
            <label style={styles.label}>Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter your name"
              style={styles.input}
            />
          </div>
          
          <div style={styles.inputGroup}>
            <label style={styles.label}>Address</label>
            <input
              type="text"
              value={userAddress}
              onChange={(e) => setUserAddress(e.target.value)}
              placeholder="Enter your Ethereum address"
              style={styles.input}
            />
          </div>
          
          <div style={styles.inputGroup}>
            <label style={styles.label}>Location</label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Enter your location"
              style={styles.input}
            />
          </div>
          
          <button onClick={handleSubmit} style={styles.button}>
            Save Data
          </button>
        </>
      )}
      
      {statusMessage && <p style={styles.status}>{statusMessage}</p>}
    </div>
  );
}

const styles = {
  formContainer: {
    maxWidth: '600px',
    margin: '40px auto',
    padding: '30px',
    borderRadius: '16px',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
    backgroundColor: '#fff',
    transition: 'all 0.3s ease',
  },
  title: {
    fontSize: '32px',
    marginBottom: '24px',
    color: '#2C3E50',
    fontWeight: '600',
    textAlign: 'center',
  },
  inputGroup: {
    marginBottom: '20px',
  },
  label: {
    display: 'block',
    marginBottom: '8px',
    fontWeight: '500',
    color: '#34495E',
    fontSize: '16px',
  },
  input: {
    width: '100%',
    padding: '12px 16px',
    borderRadius: '8px',
    border: '2px solid #E0E7FF',
    fontSize: '16px',
    transition: 'all 0.3s ease',
    outline: 'none',
    '&:focus': {
      borderColor: '#4F46E5',
      boxShadow: '0 0 0 3px rgba(79, 70, 229, 0.1)',
    },
  },
  button: {
    width: '100%',
    padding: '14px',
    backgroundColor: '#4F46E5',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: '500',
    transition: 'all 0.3s ease',
    marginTop: '10px',
    '&:hover': {
      backgroundColor: '#4338CA',
      transform: 'translateY(-1px)',
    },
    '&:active': {
      transform: 'translateY(1px)',
    },
  },
  status: {
    marginTop: '20px',
    padding: '12px',
    borderRadius: '8px',
    backgroundColor: '#F8FAFC',
    color: '#64748B',
    textAlign: 'center',
    fontSize: '14px',
  },
  connectContainer: {
    textAlign: 'center',
    marginBottom: '30px',
    padding: '20px',
  },
  connectButton: {
    backgroundColor: '#10B981',
    color: 'white',
    border: 'none',
    padding: '14px 28px',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: '500',
    transition: 'all 0.3s ease',
    '&:hover': {
      backgroundColor: '#059669',
      transform: 'translateY(-1px)',
    },
  },
  connectedStatus: {
    color: '#10B981',
    fontWeight: '500',
    marginBottom: '24px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
  },
  connectedIcon: {
    width: '8px',
    height: '8px',
    backgroundColor: '#10B981',
    borderRadius: '50%',
    display: 'inline-block',
    marginRight: '8px',
  },
  description: {
    textAlign: 'center',
    color: '#64748B',
    marginBottom: '24px',
    fontSize: '16px',
    lineHeight: '1.5',
  },
};

export default SaveUserData;