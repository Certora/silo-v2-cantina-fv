// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {PartialLiquidation} from "silo-core/contracts/utils/hook-receivers/liquidation/PartialLiquidation.sol";
import {PartialLiquidationLib} from "silo-core/contracts/utils/hook-receivers/liquidation/lib/PartialLiquidationLib.sol";
import {PartialLiquidationExecLib} from "silo-core/contracts/utils/hook-receivers/liquidation/lib/PartialLiquidationExecLib.sol";
import {SiloSolvencyLib} from "silo-core/contracts/lib/SiloSolvencyLib.sol";
import {ISiloConfig} from "silo-core/contracts/interfaces/ISiloConfig.sol";
import {ISilo} from "silo-core/contracts/interfaces/ISilo.sol";


contract PartialLiquidationHarness is PartialLiquidation {

    function estimateMaxRepayValueHarness(
        uint256 _totalBorrowerDebtValue, 
        uint256 _totalBorrowerCollateralValue,
        uint256 _ltvAfterLiquidation, //i: liquidationTargetLtv from collateralConfig
        uint256 _liquidationFee 
    ) external view returns (uint256) {
        return PartialLiquidationLib.estimateMaxRepayValue(_totalBorrowerDebtValue, _totalBorrowerCollateralValue, _ltvAfterLiquidation, _liquidationFee);
    }

    function valueToAssetsByRatioHarness(
        uint256 _value, //i: debtToRepay in USD
        uint256 _totalAssets, //i: _borrowerDebtValue in USD (TOTAL)
        uint256 _totalValue //i: _borrowerDebtAssets (TOTAL)
    ) external view returns (uint256) {
        return PartialLiquidationLib.valueToAssetsByRatio(_value, _totalAssets, _totalValue);
    }
   
    function calculateCollateralToLiquidateHarness(uint256 _maxDebtToCover, uint256 _sumOfCollateral, uint256 _liquidationFee) public pure returns (uint256 toLiquidate){
        return PartialLiquidationLib.calculateCollateralToLiquidate(_maxDebtToCover, _sumOfCollateral, _liquidationFee);
    }

    function liquidationPreviewHarness(
        uint256 _ltvBefore,
        uint256 _sumOfCollateralAssets,
        uint256 _sumOfCollateralValue,
        uint256 _borrowerDebtAssets,
        uint256 _borrowerDebtValue,
        PartialLiquidationLib.LiquidationPreviewParams memory _params
    )
    public
    pure
    returns (uint256 collateralToLiquidate, uint256 debtToRepay, uint256 ltvAfter){
        return PartialLiquidationLib.liquidationPreview(_ltvBefore, _sumOfCollateralAssets, _sumOfCollateralValue, _borrowerDebtAssets, _borrowerDebtValue, _params);
    }

    function calculateLtvAfterHarness(
        uint256 _sumOfCollateralValue,
        uint256 _totalDebtValue,
        uint256 _collateralValueToLiquidate,
        uint256 _debtValueToCover
    )
        public pure returns (uint256 ltvAfter)
    {
        if (_sumOfCollateralValue <= _collateralValueToLiquidate || _totalDebtValue <= _debtValueToCover) {
            return 0;
        }

        ltvAfter = (_totalDebtValue - _debtValueToCover) * 1e18;
        ltvAfter = ceilDiv(ltvAfter, _sumOfCollateralValue - _collateralValueToLiquidate);
    }

    function ceilDiv(uint256 a, uint256 b) internal pure returns (uint256) {
    require (b != 0);

    unchecked {
        return a == 0 ? 0 : (a - 1) / b + 1;
    }
    }

    function liquidationPreviewExecHarness(
        SiloSolvencyLib.LtvData memory _ltvData,
        PartialLiquidationLib.LiquidationPreviewParams memory _params
    )
        public
        view
        returns (uint256 collateralToLiquidate, uint256 debtToRepay, bytes4 customError)
    {
        return PartialLiquidationExecLib.liquidationPreview(_ltvData, _params);
    }

    function splitReceiveCollateralToLiquidateHarness(uint256 _collateralToLiquidate, uint256 _borrowerProtectedAssets) public pure
    returns (uint256 withdrawAssetsFromCollateral, uint256 withdrawAssetsFromProtected){
        return PartialLiquidationLib.splitReceiveCollateralToLiquidate(_collateralToLiquidate, _borrowerProtectedAssets);
    }

    function _fetchConfigsHarness(
        ISiloConfig _siloConfigCached,
        address _collateralAsset,
        address _debtAsset,
        address _borrower
    )
        public
        virtual
    returns (
        ISiloConfig.ConfigData memory collateralConfig,
        ISiloConfig.ConfigData memory debtConfig
    ){
        return _fetchConfigs(_siloConfigCached, _collateralAsset, _debtAsset, _borrower);
    }

    function _callShareTokenForwardTransferNoChecksHarness(
        address _silo,
        address _borrower,
        address _receiver,
        uint256 _withdrawAssets,
        address _shareToken,
        ISilo.AssetType _assetType
    ) public virtual returns (uint256 shares) {
        return _callShareTokenForwardTransferNoChecks(_silo, _borrower, _receiver, _withdrawAssets, _shareToken, _assetType);
    }

    function getExactLiquidationAmountsHarness(
        ISiloConfig.ConfigData memory _collateralConfig,
        ISiloConfig.ConfigData memory _debtConfig, address _user,
        uint256 _maxDebtToCover,
        uint256 _liquidationFee
    )
        external
        view
        returns (
            uint256 withdrawAssetsFromCollateral,
            uint256 withdrawAssetsFromProtected,
            uint256 repayDebtAssets,
            bytes4 customError
        )
    {
        return PartialLiquidationExecLib.getExactLiquidationAmounts(_collateralConfig, _debtConfig, _user, _maxDebtToCover, _liquidationFee);
    }




    



}