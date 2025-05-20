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

// import "../simplifications/PartialLiquidationExecLib.spec";
// import "../simplifications/PartialLiquidationLib_UNSAVE.spec";
// import "../silo/unresolved.spec";
 
// using PartialLiquidationExecLibCaller as PL_Lib;
methods {
    function PartialLiquidationHarness.liquidationPreviewHarness(uint256,uint256,uint256,uint256,uint256,PartialLiquidationLib.LiquidationPreviewParams)
    external returns(uint256,uint256,uint256) envfree;
    // function _.isSolvent(address) external => DISPATCHER(true) ;
    // Dispatchers to Silos
    function _.repay(uint256, address) external => DISPATCHER(true) ;
    function _.callOnBehalfOfSilo(address, uint256, ISilo.CallType, bytes) external => NONDET;
    function _.redeem(uint256, address, address, ISilo.CollateralType) external => NONDET;
    function _.previewRedeem(uint256) external => NONDET;
    function _.previewRedeem(uint256, ISilo.CollateralType) external => NONDET;
    function _.getLiquidity() external => DISPATCHER(true);
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


rule check_sanity(method f)
{
    // setup requirements 
    env e;
    configForEightTokensSetupRequirements();
    nonSceneAddressRequirements(e.msg.sender);
    silosTimestampSetupRequirements(e);
    synchronous_siloStorage_erc20cvl(silo0);
    synchronous_siloStorage_erc20cvl(silo1);
    calldataarg args;
    f(e,args);
    satisfy true;
}


rule debtBalanceAfterLiquidation(env e1,address collateralAsset,address debtAsset,
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
    uint256 debtBalanceBefore = balanceOfCVL(debtConfig.token,e1.msg.sender);

    withdrawCollateral,repayDebtAssets = liquidationCall(e1,collateralAsset,debtAsset,borrower,maxDebtToCover,receiveSToken);

    // ignore change in assets amount while converting to shares in SiloLendingLib
    uint256 sharesCalculated = silo0.convertToShares(e1,repayDebtAssets);
    require sharesCalculated <= shareDebtTokenBefore;

    mathint shareDebtTokenAfter = balanceOfCVL(shareDebtToken0,borrower);
    uint256 debtBalanceAfter = balanceOfCVL(debtConfig.token,e1.msg.sender);

    assert to_mathint(debtBalanceAfter) == debtBalanceBefore - repayDebtAssets ;
    assert shareDebtTokenAfter == shareDebtTokenBefore - repayDebtAssets;

}

rule cantExceedMaxDebtToCover(env e,address collateralAsset,address debtAsset,
    address borrower,uint256 maxDebtToCover,bool receiveSToken){
    uint256 withdrawCollateral;
    uint256 repayDebtAssets;

    configForEightTokensSetupRequirements();
    // nonSceneAddressRequirements(e1.msg.sender);
    silosTimestampSetupRequirements(e);
    synchronous_siloStorage_erc20cvl(silo0);
    synchronous_siloStorage_erc20cvl(silo1);

    withdrawCollateral,repayDebtAssets = liquidationCall@withrevert(e,collateralAsset,debtAsset,borrower,maxDebtToCover,receiveSToken);
    assert !lastReverted => repayDebtAssets <= maxDebtToCover;
    }


rule invalidLiquidation(env e,address collateralAsset,address debtAsset,
    address borrower,uint256 maxDebtToCover,bool receiveSToken){
    configForEightTokensSetupRequirements();
    nonSceneAddressRequirements(e.msg.sender);
    silosTimestampSetupRequirements(e);
    synchronous_siloStorage_erc20cvl(silo0);
    synchronous_siloStorage_erc20cvl(silo1);
    require balanceOfCVL(shareDebtToken0, borrower) >0 ;

    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;
    address SiloConfigCVL = siloConfig(e);
    collateralConfig,debtConfig = CVLGetConfigsForSolvency(borrower);

    liquidationCall@withrevert(e,collateralAsset,debtAsset,borrower,maxDebtToCover,receiveSToken);

    assert (maxDebtToCover ==0 || SiloConfigCVL ==0 || debtConfig.silo ==0 ||
             debtConfig.token != debtAsset || collateralConfig.token != collateralAsset) => lastReverted;
}


/// @title If one user can repay some borrower's debt, any other user also can
/// @property user-access
rule RA_anyone_may_liquidate(env e1, env e2,address collateralAsset,
        address debtAsset,
        address borrower,
        uint256 maxDebtToCover,
        bool receiveSToken) {

    /// Assuming same context (time and value).
    require e1.block.timestamp == e2.block.timestamp;
    require e1.msg.value == e2.msg.value;

    synchronous_siloStorage_erc20cvl(silo0);
    synchronous_siloStorage_erc20cvl(silo1);
    
    require balanceOfCVL(shareDebtToken0, borrower) >0 ;

    storage initState = lastStorage;
    liquidationCall(e1,collateralAsset,debtAsset,borrower,maxDebtToCover,receiveSToken);
    liquidationCall@withrevert(e2,collateralAsset,debtAsset,borrower,maxDebtToCover,receiveSToken) at initState;

    assert e2.msg.sender != 0 => !lastReverted;
}

rule unConfiguredHooks(env e){
    address add; uint256 hooks; bytes data;
    
    configForEightTokensSetupRequirements();
    nonSceneAddressRequirements(e.msg.sender);
    silosTimestampSetupRequirements(e);
    synchronous_siloStorage_erc20cvl(silo0);
    synchronous_siloStorage_erc20cvl(silo1);

    storage initState = lastStorage;
    
    afterAction(e,add,hooks,data);

    storage afterActionState = lastStorage;

    beforeAction(e,add,hooks,data);

    storage beforeActionState = lastStorage;

    assert (
        afterActionState == initState &&
        afterActionState == beforeActionState &&
        beforeActionState == initState
    );
}

rule unConfiguredHookReceiver(env e){
    address add;
    
    configForEightTokensSetupRequirements();
    nonSceneAddressRequirements(e.msg.sender);
    silosTimestampSetupRequirements(e);
    synchronous_siloStorage_erc20cvl(silo0);
    synchronous_siloStorage_erc20cvl(silo1);
    uint256 hooksBefore;
    uint256 hooksAfter;
    hooksBefore,hooksAfter = hookReceiverConfig(e,add);

    assert hooksBefore == 0 && hooksAfter == 0;
}

/**
@title initialize partialLiquidation that already has config configured will revert
*/
rule initializePartialLiquidationTwice(env e){
    
    address config;
    bytes data;
    initialize@withrevert(e,config,data);
    bool firstCall = lastReverted;
    initialize@withrevert(e,config,data);
    bool secondCall = lastReverted;
    assert !firstCall => secondCall;
}

/**
@title initialize partialLiquidation with invalid config will revert
*/
rule invalidSiloConfig(env e){
    address currentConfig = siloConfig(e);
    address config;
    bytes data;
    initialize@withrevert(e,config,data);
    assert currentConfig != 0 => lastReverted;
    assert config == 0 => lastReverted;
}

/**
@title initialize partialLiquidation with invalid config will revert
*/
rule intializeOnlyChangeSiloConfig(env e){
    address configPre = siloConfig(e);
    address config; bytes data;

    storage initState = lastStorage;

    initialize@withrevert(e,config,data);

    storage afterInitialize = lastStorage;

    address configPost = siloConfig(e);


    assert configPre == configPost => initState == afterInitialize;
}


rule FunctionsModifyState(env e, method f, calldataarg args) 
{
    require e.msg.value ==0;
    
    storage before = lastStorage;

    f(e, args);

    storage after = lastStorage;

    assert(before[currentContract] != after[currentContract] => MODIFY_STATE_METHODS(f));
}


definition MODIFY_STATE_METHODS(method f) returns bool = 
    f.selector == sig:initialize(address,bytes).selector||
    f.selector == sig:liquidationCall(address,address,address,uint256,bool).selector;