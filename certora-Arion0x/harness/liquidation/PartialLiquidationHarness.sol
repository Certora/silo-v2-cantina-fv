// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ISiloConfig} from "silo-core/contracts/interfaces/ISiloConfig.sol";
import {PartialLiquidationExecLib} from "silo-core/contracts/utils/hook-receivers/liquidation/lib/PartialLiquidationExecLib.sol";
import {PartialLiquidationLib} from "silo-core/contracts/utils/hook-receivers/liquidation/lib/PartialLiquidationLib.sol";
import {SiloSolvencyLib} from "silo-core/contracts/lib/SiloSolvencyLib.sol";
import {PartialLiquidation} from "silo-core/contracts/utils/hook-receivers/liquidation/PartialLiquidation.sol";
import {Math} from "openzeppelin5/utils/math/Math.sol";

import {RevertLib} from "silo-core/contracts/lib/RevertLib.sol";
contract PartialLiquidationHarness is PartialLiquidation {
    constructor() PartialLiquidation() {}

    function liquidationPreviewHarness(uint256 _ltvBefore,
        uint256 _sumOfCollateralAssets,
        uint256 _sumOfCollateralValue,
        uint256 _borrowerDebtAssets,
        uint256 _borrowerDebtValue,
        PartialLiquidationLib.LiquidationPreviewParams memory _params) external pure returns(uint256 collateralToLiquidate, uint256 debtToRepay, uint256 ltvAfter){
            return PartialLiquidationLib.liquidationPreview(_ltvBefore,_sumOfCollateralAssets,_sumOfCollateralValue,_borrowerDebtAssets,_borrowerDebtValue,_params);

        }
}