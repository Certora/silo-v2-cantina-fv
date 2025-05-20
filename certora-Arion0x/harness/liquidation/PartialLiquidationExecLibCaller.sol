// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {PartialLiquidationExecLib} from "silo-core/contracts/utils/hook-receivers/liquidation/lib/PartialLiquidationExecLib.sol";
import {ISiloConfig} from "silo-core/contracts/interfaces/ISiloConfig.sol";


contract PartialLiquidationExecLibCaller {

    function getExactLiquidationAmounts(ISiloConfig.ConfigData memory _collateralConfig,
        ISiloConfig.ConfigData memory _debtConfig,
        address _user,
        uint256 _maxDebtToCover,
        uint256 _liquidationFee)
        external view returns (uint256 withdrawAssetsFromCollateral,
            uint256 withdrawAssetsFromProtected,
            uint256 repayDebtAssets,
            bytes4 customError)
    {
        return PartialLiquidationExecLib.getExactLiquidationAmounts(_collateralConfig, _debtConfig, _user,_maxDebtToCover,_liquidationFee);
    }

}
