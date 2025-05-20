// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract EmptyFlashloanReceiver  {
    bytes32 _returnValue = keccak256("ERC3156FlashBorrower.onFlashLoan");


    function onFlashLoan(address sender, address token, uint256 amount, uint256 fee, bytes calldata data) external view  returns (bytes32) {
        return _returnValue;
    }
}