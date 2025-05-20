// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Actions} from "silo-core/contracts/lib/Actions.sol";
import {ISiloConfig} from "silo-core/contracts/interfaces/ISiloConfig.sol";

contract A_Caller {
    function initialize(ISiloConfig _siloConfig) external returns (address hookReceiver) {
        return Actions.initialize(_siloConfig);
    }
}
