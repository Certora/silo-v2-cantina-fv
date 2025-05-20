// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Silo} from "silo-core/contracts/Silo.sol";
import {ISiloFactory} from "silo-core/contracts/interfaces/ISiloFactory.sol";
import {ISiloConfig} from "silo-core/contracts/interfaces/ISiloConfig.sol";
import {SiloSolvencyLib} from "silo-core/contracts/lib/SiloSolvencyLib.sol";
import {SiloMathLib} from "silo-core/contracts/lib/SiloMathLib.sol";
import {SiloStdLib} from "silo-core/contracts/lib/SiloStdLib.sol";
import {IShareToken} from "silo-core/contracts/interfaces/IShareToken.sol";
import {ISilo} from "silo-core/contracts/interfaces/ISilo.sol";
import {Views} from "silo-core/contracts/lib/Views.sol";
import {ShareTokenLib} from "silo-core/contracts//lib/ShareTokenLib.sol";
import "silo-core/contracts/lib/SiloStorageLib.sol";
import {Rounding} from "silo-core/contracts/lib/Rounding.sol";
import {Math} from "gitmodules/openzeppelin-contracts-5/contracts/utils/math/Math.sol";

contract SiloHarness is Silo {
    constructor(ISiloFactory _siloFactory) Silo(_siloFactory) {}

    // TODO: this function is no longer needed
    function getSiloDataInterestRateTimestamp() external view returns (
        uint64 interestRateTimestamp
    ) {
        (, interestRateTimestamp, , , ) = Views.getSiloStorage();
    }

    // TODO: this function is no longer needed
    // TODO: verify that daoAndDeployerRevenue is the same as the old daoAndDeployerFee!
    function getSiloDataDaoAndDeployerRevenue() external view returns (
        uint192 daoAndDeployerRevenue
    ) {
        (daoAndDeployerRevenue, , , , ) = Views.getSiloStorage();
    }

    // TODO: this function is no longer needed
    function getFlashloanFee0() external view returns (uint256) {
        (,, uint256 flashloanFee, ) = ShareTokenLib.siloConfig().getFeesWithAsset(address(this));
        return flashloanFee;
    }

    // TODO: this function is no longer needed
    function reentrancyGuardEntered() external view returns (bool) {
        return ShareTokenLib.siloConfig().reentrancyGuardEntered();
    }

    // TODO: this function is no longer needed
    function getDaoFee() external view returns (uint256) {
        (uint256 daoFee,,, ) = ShareTokenLib.siloConfig().getFeesWithAsset(address(this));
        return daoFee;
    }

    // TODO: this function is no longer needed
    function getDeployerFee() external view returns (uint256) {
        (, uint256 deployerFee,, ) = ShareTokenLib.siloConfig().getFeesWithAsset(address(this));
        return deployerFee;
    }

    function getLTV(address borrower) external view returns (uint256) {
        (
            ISiloConfig.ConfigData memory collateralConfig,
            ISiloConfig.ConfigData memory debtConfig
        ) = ShareTokenLib.siloConfig().getConfigsForSolvency(borrower);
        // SiloSolvencyLib.getOrderedConfigs(this, config, borrower);
        
        uint256 debtShareBalance = IShareToken(debtConfig.debtShareToken).balanceOf(borrower);
        
        return SiloSolvencyLib.getLtv(
            collateralConfig,
            debtConfig,
            borrower,
            ISilo.OracleType.MaxLtv,
            AccrueInterestInMemory.Yes,
            debtShareBalance
        );
    }

    function getAssetsDataForLtvCalculations(
        address borrower
    ) external view returns (SiloSolvencyLib.LtvData memory) {
        uint256 action;
        (
            ISiloConfig.ConfigData memory collateralConfig,
            ISiloConfig.ConfigData memory debtConfig
        ) = ShareTokenLib.siloConfig().getConfigsForSolvency(borrower);
        
        uint256 debtShareBalance = IShareToken(debtConfig.debtShareToken).balanceOf(borrower);
        
        return SiloSolvencyLib.getAssetsDataForLtvCalculations(
            collateralConfig,
            debtConfig,
            borrower,
            ISilo.OracleType.MaxLtv,
            AccrueInterestInMemory.Yes,
            debtShareBalance
        );
    }
    
    function getTransferWithChecks() external view returns (bool) {
        IShareToken.ShareTokenStorage storage $ = ShareTokenLib.getShareTokenStorage();
        return $.transferWithChecks;
    }

    
    function getSiloFromStorage() external view returns (ISilo) {
        IShareToken.ShareTokenStorage storage $ = ShareTokenLib.getShareTokenStorage();
        return $.silo;
    }

    function totalAssetsHarness() external view returns (uint256 protectedAssets, uint256 collateralAssets, uint256 debtAssets) {
        ISilo.SiloStorage storage $ = SiloStorageLib.getSiloStorage();
        protectedAssets = $.totalAssets[ISilo.AssetType.Protected];
        collateralAssets = $.totalAssets[ISilo.AssetType.Collateral];
        debtAssets = $.totalAssets[ISilo.AssetType.Debt];
    }

    function totalProtectedAssetsHarness() external view returns (uint256 protectedAssets) {
        ISilo.SiloStorage storage $ = SiloStorageLib.getSiloStorage();
        protectedAssets = $.totalAssets[ISilo.AssetType.Protected];
    }

    function totalDebtAssetsHarness() external view returns (uint256 debtAssets) {
        ISilo.SiloStorage storage $ = SiloStorageLib.getSiloStorage();
        debtAssets = $.totalAssets[ISilo.AssetType.Debt];
    }

    function totalCollateralAssetsHarness() external view returns (uint256 collateralAssets) {
        ISilo.SiloStorage storage $ = SiloStorageLib.getSiloStorage();
        collateralAssets = $.totalAssets[ISilo.AssetType.Collateral];
    }

    function borrowerCollateralSiloHarness(address borrower) external view returns (address collateralSilo){
        ISiloConfig siloConfig = ShareTokenLib.siloConfig();
        return siloConfig.borrowerCollateralSilo(borrower);
    }
     

    function ltvBelowMaxLtvHarness(address borrower) external view returns (bool borrowerIsBelowMaxLtv) {
        ISiloConfig siloConfig = ShareTokenLib.siloConfig();

        ISiloConfig.ConfigData memory collateralConfig;
        ISiloConfig.ConfigData memory debtConfig;

        bool borrowerIsBelowMaxLtv = SiloSolvencyLib.isBelowMaxLtv(
            collateralConfig, debtConfig, borrower, ISilo.AccrueInterestInMemory.No
        );

    }

    function getUserAssetsHarness(address user) external view 
            returns (uint256 protectedAssets, uint256 collateralAssets, uint256 debtAssets) {
        //get siloConfig
        ISiloConfig siloConfig = ShareTokenLib.siloConfig();

        //get deposit config to know the addresses of the tokens
        ISiloConfig.ConfigData memory silo0Config = siloConfig.getConfig(address(this));

        //get balance of tokens of the user and convert them to assets
        uint256 protectedShares = IShareToken(silo0Config.protectedShareToken).balanceOf(user);
        protectedAssets = convertToAssetsHarness(protectedShares, AssetType.Protected);

        uint256 collateralShares = IShareToken(silo0Config.collateralShareToken).balanceOf(user);
        collateralAssets = convertToAssetsHarness(collateralShares, AssetType.Collateral);

        uint256 debtShares = IShareToken(silo0Config.debtShareToken).balanceOf(user);
        debtAssets = convertToAssetsHarness(debtShares, AssetType.Debt);
    }

    function convertToAssetsHarness(uint256 _shares, AssetType _assetType) public view returns (uint256 assets) {
        (
            uint256 totalSiloAssets, uint256 totalShares
        ) = SiloStdLib.getTotalAssetsAndTotalSharesWithInterest(ShareTokenLib.getConfig(), _assetType);

        assets = SiloMathLib.convertToAssets(
            _shares,
            totalSiloAssets,
            totalShares,
            _assetType == AssetType.Debt ? Rounding.REPAY_TO_ASSETS : Rounding.WITHDRAW_TO_ASSETS, 
            _assetType
        );
    }

    function repayHarness(
        IShareToken _debtShareToken,
        uint256 _assets,
        uint256 _shares,
        address _borrower
    ) external returns (uint256 assets, uint256 shares) {
        ISilo.SiloStorage storage $ = SiloStorageLib.getSiloStorage();

        uint256 totalDebtAssets = $.totalAssets[ISilo.AssetType.Debt];
        (uint256 debtSharesBalance, uint256 totalDebtShares) = _debtShareToken.balanceOfAndTotalSupply(_borrower);

        (assets, shares) = SiloMathLib.convertToAssetsOrToShares({
            _assets: _assets,
            _shares: _shares,
            _totalAssets: totalDebtAssets,
            _totalShares: totalDebtShares,
            _roundingToAssets: Rounding.REPAY_TO_ASSETS,
            _roundingToShares: Rounding.REPAY_TO_SHARES,
            _assetType: ISilo.AssetType.Debt
        });

        if (shares > debtSharesBalance) {
            shares = debtSharesBalance;

            (assets, shares) = SiloMathLib.convertToAssetsOrToShares({
                _assets: 0,
                _shares: shares,
                _totalAssets: totalDebtAssets,
                _totalShares: totalDebtShares,
                _roundingToAssets: Rounding.REPAY_TO_ASSETS,
                _roundingToShares: Rounding.REPAY_TO_SHARES,
                _assetType: ISilo.AssetType.Debt
            });
        }
    }

    function flashFeeHarness(address token, uint256 amount) external view returns (uint256) {
        IShareToken.ShareTokenStorage storage _shareStorage = ShareTokenLib.getShareTokenStorage();

        // flashFee will revert for wrong token
        return SiloStdLib.flashFee(_shareStorage.siloConfig, token, amount);
    }

        //check if hook is activated
        //token: 0 = no token; 1 = protected; 2 = collateral; 3 = debt
    function hookCallActivatedHarness(uint256 action, bool before) public view returns (bool) {


        IShareToken.ShareTokenStorage storage _shareStorage = ShareTokenLib.getShareTokenStorage();
        if (before) {
            uint256 hooksBefore = _shareStorage.hookSetup.hooksBefore;
            return hooksBefore & action == action;
        } else {
            uint256 hooksAfter = _shareStorage.hookSetup.hooksAfter;
            return hooksAfter & action == action;
        }
    }

    function hookReceiverHarness(address silo) external view returns (address) {
        ISiloConfig siloConfig = ShareTokenLib.siloConfig();
        return siloConfig.getConfig(silo).hookReceiver;
    }

    function getTokenAndAssetsDataHarness(ISilo.AssetType assetType) public view returns (
        address token,
        uint256 totalAssets
    ) {
        if (assetType == ISilo.AssetType.Protected) {
            token = ShareTokenLib.siloConfig().getConfig(address(this)).protectedShareToken;
            (, , totalAssets, , ) = getSiloStorageHarness();
        } else if (assetType == ISilo.AssetType.Collateral) {
            token = ShareTokenLib.siloConfig().getConfig(address(this)).collateralShareToken;
            (, , , totalAssets, ) = getSiloStorageHarness();
        } else if (assetType == ISilo.AssetType.Debt) {
            token = ShareTokenLib.siloConfig().getConfig(address(this)).debtShareToken;
            (, , , , totalAssets) = getSiloStorageHarness();
        }
    }

    function getSiloStorageHarness()
        public
        view
        virtual
        returns (
            uint192 daoAndDeployerRevenue,
            uint64 interestRateTimestamp,
            uint256 protectedAssets,
            uint256 collateralAssets,
            uint256 debtAssets
        )
    {
        return Views.getSiloStorage();
    }

    function assetsBorrowerForLTVHarness(
        ISiloConfig.ConfigData memory _collateralConfig,
        ISiloConfig.ConfigData memory _debtConfig,
        address _borrower,
        ISilo.OracleType _oracleType,
        ISilo.AccrueInterestInMemory _accrueInMemory
    ) public returns (uint256 protectedAssets, uint256 collateralAssets, uint256 debtAssets) {
            SiloSolvencyLib.LtvData memory ltvData = SiloSolvencyLib.getAssetsDataForLtvCalculations(
                _collateralConfig, _debtConfig, _borrower, _oracleType, _accrueInMemory, 0
            );
            protectedAssets = ltvData.borrowerProtectedAssets;
            collateralAssets = ltvData.borrowerCollateralAssets;
            debtAssets = ltvData.borrowerDebtAssets;
    }

    function isSolventHarness(
        address _borrower,
        ISilo.AccrueInterestInMemory _accrueInMemory
    ) public returns (bool isSolvent) {
        address collateralSilo = ShareTokenLib.siloConfig().borrowerCollateralSilo(_borrower);
        address debtSilo = ShareTokenLib.siloConfig().getDebtSilo(_borrower);
        ISiloConfig.ConfigData memory _collateralConfig = ShareTokenLib.siloConfig().getConfig(collateralSilo);
        ISiloConfig.ConfigData memory _debtConfig = ShareTokenLib.siloConfig().getConfig(debtSilo);
        isSolvent = SiloSolvencyLib.isSolvent(
            _collateralConfig, _debtConfig, _borrower, _accrueInMemory
        );
    }

    function userLTVHarness(uint256 debtAssets, uint256 collateralAssets) public view returns (uint256 ltv) {
        return SiloSolvencyLib.ltvMath(debtAssets, collateralAssets);
    }

    function sumHarness(uint256 a, uint256 b) public view returns (uint256) {
        return a + b;
    }

    function hooksBeforeHarness() public view returns (uint256) {
        return ShareTokenLib.getShareTokenStorage().hookSetup.hooksBefore;
    }

    function hooksAfterHarness() public view returns (uint256) {
        return ShareTokenLib.getShareTokenStorage().hookSetup.hooksAfter;
    }

    

}