// SPDX-License-Identifier: BUSL-1.1
pragma solidity >=0.5.0;

import {IERC20} from "openzeppelin-contracts/token/ERC20/IERC20.sol";

interface IWrappedNativeToken is IERC20 {
    function deposit() external payable;
    function withdraw(uint256 amount) external;
}