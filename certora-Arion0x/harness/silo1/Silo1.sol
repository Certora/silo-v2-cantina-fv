// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
import {ISiloConfig} from "silo-core/contracts/interfaces/ISiloConfig.sol";
import {SiloLendingLib} from "silo-core/contracts/lib/SiloLendingLib.sol";
import {ISilo} from "silo-core/contracts/interfaces/ISilo.sol";
import {SiloHarness} from "../SiloHarness.sol";
import {ISiloFactory} from "silo-core/contracts/interfaces/ISiloFactory.sol";

import {SiloSolvencyLib} from "silo-core/contracts/lib/SiloSolvencyLib.sol";
import {IShareToken} from "silo-core/contracts/interfaces/IShareToken.sol";
import {Views} from "silo-core/contracts/lib/Views.sol";
import {ShareTokenLib} from "silo-core/contracts//lib/ShareTokenLib.sol";
import {IERC20} from "openzeppelin5/token/ERC20/IERC20.sol";

contract Silo1 is SiloHarness {
    constructor(ISiloFactory _siloFactory) SiloHarness(_siloFactory) {}


}
