// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UserDataStorage {
    // Struct to hold user data
    struct UserData {
        string name; // User's name
        string userAddress; // User's physical address (as a string)
        string location; // User's location
    }

    // Mapping from Ethereum address to an array of UserData structs
    mapping(address => UserData[]) private userDataMapping;

    // Event to notify when data is saved
    event UserDataSaved(
        address indexed userAccount,
        string name,
        string userAddress,
        string location
    );

    // Function to save user data (allows multiple entries for the same address)
    function saveUserData(
        string memory _name,
        string memory _userAddress,
        string memory _location
    ) external {
        // Create a new UserData struct and push it into the user's data array
        UserData memory newUserData = UserData({
            name: _name,
            userAddress: _userAddress,
            location: _location
        });
        userDataMapping[msg.sender].push(newUserData);

        // Emit an event to notify that new data has been saved
        emit UserDataSaved(msg.sender, _name, _userAddress, _location);
    }

    // Function to retrieve all user data for the caller's address
    function getUserData() external view returns (UserData[] memory) {
        return userDataMapping[msg.sender];
    }

    // Function to retrieve user data for a specific address (optional)
    function getUserDataByAddress(
        address _userAddress
    ) external view returns (UserData[] memory) {
        return userDataMapping[_userAddress];
    }
}
