// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.24;

import {ISilo} from "silo-core/contracts/interfaces/ISilo.sol";
import {ISiloConfig} from "silo-core/contracts/interfaces/ISiloConfig.sol";
import {IHookReceiver} from "silo-core/contracts/interfaces/IHookReceiver.sol";

library SiloStorageLib {
    // keccak256(abi.encode(uint256(keccak256("silo.storage.SiloVault")) - 1)) & ~bytes32(uint256(0xff));
    bytes32 private constant SiloStorageLocation = 0xd7513ffe3a01a9f6606089d1b67011bca35bec018ac0faa914e1c529408f8300;

    function getSiloStorage() internal pure returns (ISilo.SiloStorage storage $) {
        assembly {
            $.slot := SiloStorageLocation
        }
    }
}