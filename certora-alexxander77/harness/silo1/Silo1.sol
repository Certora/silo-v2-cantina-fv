// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
import {ISiloConfig} from "silo-core/contracts/interfaces/ISiloConfig.sol";
import {SiloLendingLib} from "silo-core/contracts/lib/SiloLendingLib.sol";
import {ISilo} from "silo-core/contracts/interfaces/ISilo.sol";
import {SiloHarnessLiq} from "../SiloHarnessLiq.sol";
import {ISiloFactory} from "silo-core/contracts/interfaces/ISiloFactory.sol";

contract Silo1 is SiloHarnessLiq {
    constructor(ISiloFactory _siloFactory) SiloHarnessLiq(_siloFactory) {}


}
