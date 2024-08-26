// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.20;

import {ISiloConfig} from "../interfaces/ISiloConfig.sol";
import {ICrossReentrancyGuard} from "../interfaces/ICrossReentrancyGuard.sol";

library NonReentrantLib {
    function nonReentrant(ISiloConfig _config) internal view {
        if (_config.reentrancyGuardEntered()) revert ICrossReentrancyGuard.CrossReentrantCall();
    }
}