// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {SiloConfig} from "silo-core/contracts/SiloConfig.sol";
import {ISiloFactory} from "silo-core/contracts/interfaces/ISiloFactory.sol";
import {ISiloConfig} from "silo-core/contracts/interfaces/ISiloConfig.sol";
import {SiloSolvencyLib} from "silo-core/contracts/lib/SiloSolvencyLib.sol";
import {IShareToken} from "silo-core/contracts/interfaces/IShareToken.sol";
import {ISilo} from "silo-core/contracts/interfaces/ISilo.sol";
import {Views} from "silo-core/contracts/lib/Views.sol";
import {ShareTokenLib} from "silo-core/contracts//lib/ShareTokenLib.sol";

contract SiloConfigHarness is SiloConfig {
    constructor(uint256 _siloId,
        ISiloConfig.ConfigData memory _configData0,
        ISiloConfig.ConfigData memory _configData1) SiloConfig(_siloId,_configData0,_configData1) {}

    function getBorrowerCollateral(address borrower) external returns(address){
        return borrowerCollateralSilo[borrower];
    }
}
