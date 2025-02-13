import React, { useState, useEffect } from 'react';
import { BrowserProvider, Contract } from 'ethers';
import UserDataStorageAbi from '../abis/UserDataStorage.json';
import './FetchUserData.css';

const FetchUserData = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [account, setAccount] = useState('');
  const [searchAddress, setSearchAddress] = useState('');
  const [userData, setUserData] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [entriesPerPage, setEntriesPerPage] = useState(5);
  const [status, setStatus] = useState({ type: '', message: '' });
  const [isLoading, setIsLoading] = useState(false);
  const contractAddress = '0x7635615a00cbC897Bd020468C4338B194C8CC948';

  useEffect(() => {
    checkIfWalletIsConnected();
    window.ethereum.on('accountsChanged', handleAccountsChanged);
    return () => {
      window.ethereum.removeListener('accountsChanged', handleAccountsChanged);
    };
  }, []);

  const checkIfWalletIsConnected = async () => {
    try {
      if (window.ethereum) {
        const accounts = await window.ethereum.request({ method: 'eth_accounts' });
        if (accounts.length > 0) {
          setAccount(accounts[0]);
          setIsConnected(true);
        }
      }
    } catch (error) {
      console.error('Error checking wallet connection:', error);
    }
  };

  const handleAccountsChanged = (accounts) => {
    if (accounts.length > 0) {
      setAccount(accounts[0]);
      setIsConnected(true);
    } else {
      setIsConnected(false);
      setAccount('');
    }
  };

  const connectWallet = async () => {
    try {
      if (window.ethereum) {
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        setAccount(accounts[0]);
        setIsConnected(true);
        setStatus({ type: 'success', message: 'Wallet connected successfully! ✅' });
      } else {
        setStatus({ type: 'error', message: 'Please install MetaMask! ❌' });
      }
    } catch (error) {
      setStatus({ type: 'error', message: 'Error connecting wallet: ' + error.message });
    }
  };

  const copyAddress = (address) => {
    navigator.clipboard.writeText(address);
    setStatus({ type: 'info', message: 'Address copied to clipboard! 📋' });
    setTimeout(() => setStatus({ type: '', message: '' }), 3000);
  };

  const useCurrentAddress = () => {
    setSearchAddress(account);
  };

  const fetchDataFromBlockchain = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setStatus({ type: '', message: '' });
    setUserData([]);

    try {
      if (!window.ethereum) throw new Error('Please install MetaMask');
      
      const provider = new BrowserProvider(window.ethereum);
      const contract = new Contract(contractAddress, UserDataStorageAbi, provider);

      let data;
      if (searchAddress) {
        console.log('Fetching data for address:', searchAddress);
        data = await contract.getUserDataByAddress(searchAddress);
      } else {
        console.log('Fetching all user data');
        data = await contract.getUserData();
      }

      console.log('Fetched data:', data);

      if (Array.isArray(data) && data.length > 0) {
        setUserData(data);
        setStatus({ type: 'success', message: 'Data fetched successfully! ✅' });
      } else {
        setStatus({ type: 'info', message: 'No data found for this address.' });
      }
    } catch (error) {
      console.error('Error:', error);
      setStatus({ type: 'error', message: 'Error fetching data: ' + error.message + ' ❌' });
    } finally {
      setIsLoading(false);
    }
  };

  const indexOfLastEntry = currentPage * entriesPerPage;
  const indexOfFirstEntry = indexOfLastEntry - entriesPerPage;
  const currentEntries = userData.slice(indexOfFirstEntry, indexOfLastEntry);
  const totalPages = Math.ceil(userData.length / entriesPerPage);

  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  return (
    <div className="fetch-data-container">
      <div className="fetch-data-card">
        <div className="card-header">
          <h2>
            <i className="fas fa-database"></i>
            Fetch User Data
          </h2>
          {isConnected && (
            <div className="wallet-info">
              <i className="fas fa-circle connected-icon"></i>
              <span>Connected: {account.substring(0, 6)}...{account.substring(38)}</span>
            </div>
          )}
        </div>

        {!isConnected ? (
          <div className="connect-wallet-section">
            <p>Please connect your wallet to fetch data</p>
            <button onClick={connectWallet} className="connect-wallet-btn">
              <i className="fas fa-wallet"></i>
              Connect Wallet
            </button>
          </div>
        ) : (
          <>
            <form onSubmit={fetchDataFromBlockchain} className="fetch-form">
              <div className="search-group">
                <label>
                  <i className="fas fa-search"></i>
                  Search by Address (Optional)
                </label>
                <div className="search-input-wrapper">
                  <input
                    type="text"
                    value={searchAddress}
                    onChange={(e) => setSearchAddress(e.target.value)}
                    placeholder="Enter Ethereum address or leave empty to fetch all"
                  />
                  <button
                    type="button"
                    onClick={useCurrentAddress}
                    className="use-current-btn"
                    title="Use connected wallet address"
                  >
                    📋
                  </button>
                </div>
              </div>

              <button 
                type="submit" 
                className={`submit-btn ${isLoading ? 'loading' : ''}`}
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <div className="loader"></div>
                    Fetching Data...
                  </>
                ) : (
                  <>
                    <i className="fas fa-search"></i>
                    Fetch Data
                  </>
                )}
              </button>
            </form>

            {status.message && (
              <div className={`status-message ${status.type}`}>
                {status.message}
              </div>
            )}

            {userData.length > 0 && (
              <div className="data-results">
                <div className="table-controls">
                  <div className="entries-control">
                    <select
                      value={entriesPerPage}
                      onChange={(e) => {
                        setEntriesPerPage(Number(e.target.value));
                        setCurrentPage(1);
                      }}
                      className="entries-select"
                    >
                      <option value={5}>5</option>
                      <option value={10}>10</option>
                      <option value={25}>25</option>
                      <option value={50}>50</option>
                    </select>
                    <span>entries per page</span>
                  </div>
                  <div className="search-control">
                    <input
                      type="text"
                      placeholder="Search in results..."
                      className="search-input"
                    />
                  </div>
                </div>

                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Address</th>
                        <th>Location</th>
                      </tr>
                    </thead>
                    <tbody>
                      {currentEntries.map((item, index) => (
                        <tr key={index}>
                          <td>{item.name}</td>
                          <td className="address-cell" onClick={() => copyAddress(item.userAddress)} title="Click to copy">
                            <span>{item.userAddress.substring(0, 6)}...{item.userAddress.substring(38)}</span>
                            <i className="fas fa-copy copy-icon"></i>
                          </td>
                          <td>{item.location}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="table-footer">
                  <div className="entries-info">
                    Showing {indexOfFirstEntry + 1} to {Math.min(indexOfLastEntry, userData.length)} of {userData.length} entries
                  </div>
                  <div className="pagination">
                    <button
                      onClick={() => paginate(1)}
                      disabled={currentPage === 1}
                      className="page-btn"
                    >
                      First
                    </button>
                    <button
                      onClick={() => paginate(currentPage - 1)}
                      disabled={currentPage === 1}
                      className="page-btn"
                    >
                      Previous
                    </button>
                    {(() => {
                      let pages = [];
                      let startPage = Math.max(1, currentPage - 2);
                      let endPage = Math.min(totalPages, startPage + 4);
                      
                      // Adjust startPage if endPage is maxed out
                      if (endPage === totalPages) {
                        startPage = Math.max(1, endPage - 4);
                      }

                      for (let i = startPage; i <= endPage; i++) {
                        pages.push(
                          <button
                            key={i}
                            onClick={() => paginate(i)}
                            className={`page-btn ${currentPage === i ? 'active' : ''}`}
                          >
                            {i}
                          </button>
                        );
                      }
                      return pages;
                    })()}
                    <button
                      onClick={() => paginate(currentPage + 1)}
                      disabled={currentPage === totalPages}
                      className="page-btn"
                    >
                      Next
                    </button>
                    <button
                      onClick={() => paginate(totalPages)}
                      disabled={currentPage === totalPages}
                      className="page-btn"
                    >
                      Last
                    </button>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default FetchUserData;