const UserDataStorage = artifacts.require("UserDataStorage");

module.exports = function (deployer) {
  deployer.deploy(UserDataStorage);
};