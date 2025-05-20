// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Silo} from "silo-core/contracts/Silo.sol";

import {ISiloFactory} from "silo-core/contracts/interfaces/ISiloFactory.sol";
import {IShareToken} from "silo-core/contracts/interfaces/IShareToken.sol";

import {Hook} from "silo-core/contracts/lib/Hook.sol";
import {ShareTokenLib} from "silo-core/contracts/lib/ShareTokenLib.sol";

contract ExampleHarness is Silo {
    using Hook for uint24;

    constructor(ISiloFactory _siloFactory) Silo(_siloFactory) {}


    function afterTokenTransfer(address _sender, address _recipient, uint256 _amount) external {
        _afterTokenTransfer(_sender, _recipient, _amount);
    }

    function getHooksAfter() external view returns (uint24) {
        IShareToken.ShareTokenStorage storage _shareStorage = ShareTokenLib.getShareTokenStorage();
        return _shareStorage.hookSetup.hooksAfter;
    }
    function getHooksBefore() external view returns (uint24) {
        IShareToken.ShareTokenStorage storage _shareStorage = ShareTokenLib.getShareTokenStorage();
        return _shareStorage.hookSetup.hooksBefore;
    }
    function getStoredTokenType() external view returns (uint24) {
        IShareToken.ShareTokenStorage storage _shareStorage = ShareTokenLib.getShareTokenStorage();
        return _shareStorage.hookSetup.tokenType;
    }

}