// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Silo} from "silo-core/contracts/Silo.sol";
import {ISiloFactory} from "silo-core/contracts/interfaces/ISiloFactory.sol";
import {ISiloConfig} from "silo-core/contracts/interfaces/ISiloConfig.sol";
import {SiloSolvencyLib} from "silo-core/contracts/lib/SiloSolvencyLib.sol";
import {SiloStdLib} from "silo-core/contracts/lib/SiloStdLib.sol";
import {IShareToken} from "silo-core/contracts/interfaces/IShareToken.sol";
import {ISilo} from "silo-core/contracts/interfaces/ISilo.sol";
import {Views} from "silo-core/contracts/lib/Views.sol";
import {ShareTokenLib} from "silo-core/contracts//lib/ShareTokenLib.sol";
import {IERC20} from "openzeppelin5/token/ERC20/IERC20.sol";


contract SiloHarness is Silo {
    bytes32 public constant FLASHLOAN_CALLBACK_HARNESS = keccak256("ERC3156FlashBorrower.onFlashLoan");
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
    // function getFeesWithAssetHarness()external view returns (uint256 daoFee, uint256 deployerFee, uint256 flashloanFee, address assetToken){
    //     (daoFee,deployerFee,flashloanFee,assetToken) = ShareTokenLib.siloConfig().getFeesWithAsset(address(this));;
    // }

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
    function isBelowMaxLTVHarness(ISiloConfig.ConfigData memory collateralConfig,ISiloConfig.ConfigData memory debtConfig,address borrower,ISilo.AccrueInterestInMemory accrueInMemory)external view returns (bool) {
        return SiloSolvencyLib.isBelowMaxLtv(collateralConfig, debtConfig, borrower, accrueInMemory);
    }

    function getConfigsForSolvencyHarness(address borrower) external view returns (ISiloConfig.ConfigData memory collateralConfig,ISiloConfig.ConfigData memory debtConfig) {
        (
            ISiloConfig.ConfigData memory collateralConfig,
            ISiloConfig.ConfigData memory debtConfig
        ) = ShareTokenLib.siloConfig().getConfigsForSolvency(borrower);
        
        return (collateralConfig,debtConfig);
    }
    function getConfigsForWithdrawHarness(address borrower) external view returns (ISiloConfig.DepositConfig memory depositConfig,ISiloConfig.ConfigData memory collateralConfig,ISiloConfig.ConfigData memory debtConfig) {
        (
        ISiloConfig.DepositConfig memory depositConfig,
        ISiloConfig.ConfigData memory collateralConfig,
        ISiloConfig.ConfigData memory debtConfig
        ) = ShareTokenLib.siloConfig().getConfigsForWithdraw(address(this), borrower);
        
        // return (depositConfig,collateralConfig,debtConfig);
    }
    function getDebtConfigTokenBalance(ISiloConfig.ConfigData memory debtConfig,address user) external view returns (uint256) {
        return  IShareToken(debtConfig.token).balanceOf(user);
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

    function getHookSetup() external view returns (IShareToken.HookSetup memory) {
        IShareToken.ShareTokenStorage storage $ = ShareTokenLib.getShareTokenStorage();
        return $.hookSetup;
    }
    


    function getSiloFromStorage() external view returns (ISilo) {
        IShareToken.ShareTokenStorage storage $ = ShareTokenLib.getShareTokenStorage();
        return $.silo;
    }
    function getConfig()external view returns(ISiloConfig.ConfigData memory) {
        return ShareTokenLib.getConfig();
    }
    function setSiloAsCollateral(address borrower)external {
        
        ISiloConfig siloConfig = ShareTokenLib.siloConfig();
        siloConfig.setThisSiloAsCollateralSilo(borrower);
    }

    function getFlashFee(ISiloConfig siloConfig,address token,uint256 amount) external returns(uint256){
        return SiloStdLib.flashFee(siloConfig, token, amount);
    }
    
}
