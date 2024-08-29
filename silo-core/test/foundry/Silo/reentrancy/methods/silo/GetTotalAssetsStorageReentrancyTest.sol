// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.20;

import {ISilo} from "silo-core/contracts/interfaces/ISilo.sol";
import {MethodReentrancyTest} from "../MethodReentrancyTest.sol";
import {TestStateLib} from "../../TestState.sol";

contract GetTotalAssetsStorageReentrancyTest is MethodReentrancyTest {
    function callMethod() external {
        emit log_string("\tEnsure it will not revert");
        _ensureItWillNotRevert();
    }

    function verifyReentrancy() external view {
        _ensureItWillNotRevert();
    }

    function methodDescription() external pure returns (string memory description) {
        description = "getTotalAssetsStorage(uint256)";
    }

    function _ensureItWillNotRevert() internal view {
        TestStateLib.silo0().getTotalAssetsStorage(uint256(ISilo.AssetType.Collateral));
        TestStateLib.silo1().getTotalAssetsStorage(uint256(ISilo.AssetType.Collateral));

        TestStateLib.silo0().getTotalAssetsStorage(uint256(ISilo.AssetType.Protected));
        TestStateLib.silo1().getTotalAssetsStorage(uint256(ISilo.AssetType.Protected));

        TestStateLib.silo0().getTotalAssetsStorage(uint256(ISilo.AssetType.Debt));
        TestStateLib.silo1().getTotalAssetsStorage(uint256(ISilo.AssetType.Debt));
    }
}