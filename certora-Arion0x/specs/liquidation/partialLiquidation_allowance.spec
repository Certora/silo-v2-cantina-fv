import "./partialLiquidation_functions.spec";
import "../setup/ERC20/erc20cvl.spec";
import "../setup/StorageHooks/hook_all.spec";
import "../setup/CompleteSiloSetup.spec";
import "../simplifications/SiloSolvencyLib_UNSAFE.spec";
import "../setup/summaries/siloconfig_summaries.spec";

// import "../setup/single_silo_tokens_requirements.spec";
// import "../setup/summaries/silo0_summaries.spec";
// import "../setup/summaries/siloconfig_summaries_for_two.spec";
// import "../setup/summaries/config_for_one_in_cvl.spec";
// import "../setup/summaries/safe-approximations.spec";

import "../simplifications/priceOracle_UNSAFE.spec";
import "../simplifications/SiloMathLib_SAFE.spec";
import "../simplifications/SiloMathLib_UNSAFE.spec";

import "../simplifications/SiloStdLib_UNSAFE.spec";
import "../simplifications/Silo_isSolvent_ghost_UNSAFE.spec";
import "../simplifications/PartialLiquidationExecLib.spec";

// import "../simplifications/PartialLiquidationLib_UNSAVE.spec";
// import "../silo/unresolved.spec";
 
// using PartialLiquidationExecLibCaller as PL_Lib;
methods {
    function PartialLiquidationHarness.liquidationPreviewHarness(uint256,uint256,uint256,uint256,uint256,PartialLiquidationLib.LiquidationPreviewParams)
    external returns(uint256,uint256,uint256) envfree;
    // function _.isSolvent(address) external => DISPATCHER(true) ;
    // Dispatchers to Silos
    function _.repay(uint256, address) external => NONDET;
    function _.callOnBehalfOfSilo(address, uint256, ISilo.CallType, bytes) external => NONDET;
    function _.redeem(uint256, address, address, ISilo.CollateralType) external => NONDET;
    function _.previewRedeem(uint256) external => NONDET;
    function _.previewRedeem(uint256, ISilo.CollateralType) external => NONDET;
    function _.getLiquidity() external => DISPATCHER(true);
    // function RevertLib.revertIfError(bytes4) internal => DISPATCHER(true);
    //function revertIfError(bytes4 _errorSelector) internal 
    function _._callShareTokenForwardTransferNoChecks(
        address,
        address,
        address,
        uint256,
        address,
        ISilo.AssetType
    ) internal => NONDET;
    function _.callSolvencyOracleBeforeQuote(ISiloConfig.ConfigData memory) internal => NONDET;
    function _.callMaxLtvOracleBeforeQuote(ISiloConfig.ConfigData memory) internal => NONDET;

    // unresolved external in PartialLiquidation.liquidationCall(address, address, address, uint256, bool) 
    //     => DISPATCH(use_fallback=true) [ silo0._ ] default NONDET;
    // unresolved external in PartialLiquidation.maxLiquidation(address) 
    //     => DISPATCH(use_fallback=true) [ silo0._ ] default NONDET;
}


rule allowanceAfterLiquidation(env e1,address collateralAsset,address debtAsset,
    address borrower,uint256 maxDebtToCover,bool receiveSToken){
    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;
    uint256 withdrawCollateral;
    uint256 repayDebtAssets;

    configForEightTokensSetupRequirements();
    nonSceneAddressRequirements(e1.msg.sender);
    nonSceneAddressRequirements(borrower);
    silosTimestampSetupRequirements(e1);
    synchronous_siloStorage_erc20cvl(silo0);
    synchronous_siloStorage_erc20cvl(silo1);

    require balanceOfCVL(shareDebtToken0, borrower) >0 ;
    mathint shareDebtTokenBefore = balanceOfCVL(shareDebtToken0,borrower);

    collateralConfig,debtConfig = CVLGetConfigsForSolvency(borrower);
    uint256 allowanceBefore = allowanceCVL(debtConfig.token,currentContract,debtConfig.silo);

    withdrawCollateral,repayDebtAssets = liquidationCall(e1,collateralAsset,debtAsset,borrower,maxDebtToCover,receiveSToken);

    // ignore change in assets amount while converting to shares in SiloLendingLib
    uint256 sharesCalculated = silo0.convertToShares(e1,repayDebtAssets);
    require sharesCalculated <= shareDebtTokenBefore;

    uint256 allowanceAfter = allowanceCVL(debtConfig.token,currentContract,debtConfig.silo);

    assert to_mathint(allowanceAfter) == allowanceBefore + repayDebtAssets;
}


rule liquidationShouldRevert(env e,address collateralAsset,address debtAsset,
    address borrower,uint256 maxDebtToCover,bool receiveSToken){
    configForEightTokensSetupRequirements();
    nonSceneAddressRequirements(e.msg.sender);
    nonSceneAddressRequirements(borrower);
    silosTimestampSetupRequirements(e);
    synchronous_siloStorage_erc20cvl(silo0);
    synchronous_siloStorage_erc20cvl(silo1);
    require balanceOfCVL(shareDebtToken0, borrower) >0 ;

    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;

    collateralConfig,debtConfig = CVLGetConfigsForSolvency(borrower);
    uint256 withdrawAssetsFromCollateral;uint256 withdrawAssetsFromProtected;
    uint256 repayDebtAssets; bytes4 customError;
    withdrawAssetsFromCollateral, withdrawAssetsFromProtected,repayDebtAssets,customError
    = CVLGetExactLiquidationAmounts(collateralConfig,debtConfig,borrower,maxDebtToCover,collateralConfig.liquidationFee); 

    liquidationCall@withrevert(e,collateralAsset,debtAsset,borrower,maxDebtToCover,receiveSToken);

    bool shouldRevert = isKnownError(customErrorGhost);

    assert shouldRevert => lastReverted;
}

/// @notice Definition for the EmptySiloConfig error selector
definition EMPTY_SILO_CONFIG_SELECTOR() returns bytes4 = to_bytes4(0xa58a2b1b);

/// @notice Definition for the AlreadyConfigured error selector
definition ALREADY_CONFIGURED_SELECTOR() returns bytes4 = to_bytes4(0x7f289930);

/// @notice Definition for the UnexpectedCollateralToken error selector
definition UNEXPECTED_COLLATERAL_TOKEN_SELECTOR() returns bytes4 = to_bytes4(0xbb1d067c);

/// @notice Definition for the UnexpectedDebtToken error selector
definition UNEXPECTED_DEBT_TOKEN_SELECTOR() returns bytes4 = to_bytes4(0x509f0487);

/// @notice Definition for the NoDebtToCover error selector
definition NO_DEBT_TO_COVER_SELECTOR() returns bytes4 = to_bytes4(0xf8d88654);

/// @notice Definition for the FullLiquidationRequired error selector
definition FULL_LIQUIDATION_REQUIRED_SELECTOR() returns bytes4 = to_bytes4(0x2b82b8ec);

/// @notice Definition for the UserIsSolvent error selector
definition USER_IS_SOLVENT_SELECTOR() returns bytes4 = to_bytes4(0x92b6d91c);

/// @notice Definition for the UnknownRatio error selector
definition UNKNOWN_RATIO_SELECTOR() returns bytes4 = to_bytes4(0x67005018);

/// @notice Definition for the NoRepayAssets error selector
definition NO_REPAY_ASSETS_SELECTOR() returns bytes4 = to_bytes4(0x4a02eecb);

function isKnownError(bytes4 selector) returns bool {
    return selector == EMPTY_SILO_CONFIG_SELECTOR() ||
           selector == ALREADY_CONFIGURED_SELECTOR() ||
           selector == UNEXPECTED_COLLATERAL_TOKEN_SELECTOR() ||
           selector == UNEXPECTED_DEBT_TOKEN_SELECTOR() ||
           selector == NO_DEBT_TO_COVER_SELECTOR() ||
           selector == FULL_LIQUIDATION_REQUIRED_SELECTOR() ||
           selector == USER_IS_SOLVENT_SELECTOR() ||
           selector == UNKNOWN_RATIO_SELECTOR() ||
           selector == NO_REPAY_ASSETS_SELECTOR();
}