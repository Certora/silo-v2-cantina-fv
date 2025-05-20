// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IERC3156FlashBorrower} from "silo-core/contracts/interfaces/IERC3156FlashBorrower.sol";
import {IERC20} from "openzeppelin5/token/ERC20/ERC20.sol";

contract EmptyFlashBorrower is IERC3156FlashBorrower {
   uint256 public balanceAfterFlashLoan;
   address public initiator;
   address public token;
   uint256 public amount;
   uint256 public fee;

   constructor() {}

   function onFlashLoan(address _initiator, address _token, uint256 _amount, uint256 _fee, bytes calldata _data)
   external
   returns (bytes32) {
      balanceAfterFlashLoan = IERC20(_token).balanceOf(address(this));
      initiator = _initiator;
      token = _token;
      amount = _amount;
      fee = _fee;
      return keccak256("ERC3156FlashBorrower.onFlashLoan");
   }

   function getRecordedParams() public view returns(uint256, address, address, uint256, uint256) {
      return (balanceAfterFlashLoan, initiator, token, amount, fee);
   }
}

