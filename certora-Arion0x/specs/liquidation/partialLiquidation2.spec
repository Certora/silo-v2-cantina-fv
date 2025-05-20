import "./partialLiquidation_functions.spec";

import "../setup/ERC20/erc20cvl.spec";
import "../setup/StorageHooks/hook_all.spec";
import "../setup/CompleteSiloSetup.spec";

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
import "../simplifications/SiloSolvencyLib_UNSAFE.spec";
import "../simplifications/PartialLiquidationExecLib.spec";
// import "../simplifications/PartialLiquidationLib_UNSAVE.spec";

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
    function _.forwardTransferFromNoChecks(address _from, address _to, uint256 _amount) external => DISPATCHER(true);
    // function _._callShareTokenForwardTransferNoChecks(
    //     address,
    //     address,
    //     address,
    //     uint256,
    //     address,
    //     ISilo.AssetType
    // ) internal => NONDET;
    function _.callSolvencyOracleBeforeQuote(ISiloConfig.ConfigData memory config) internal => CVLCallSolvencyOracle(config) expect void;
    function _.callMaxLtvOracleBeforeQuote(ISiloConfig.ConfigData memory config) internal => CVLCallMaxLtvOracle(config) expect void;

    // unresolved external in PartialLiquidation.liquidationCall(address, address, address, uint256, bool) 
    //     => DISPATCH(use_fallback=true) [ silo0._ ] default NONDET;
    // unresolved external in PartialLiquidation.maxLiquidation(address) 
    //     => DISPATCH(use_fallback=true) [ silo0._ ] default NONDET;
}

persistent ghost mapping(address => mathint) solvencyOracleGhost{
    init_state axiom forall address i. solvencyOracleGhost[i] == 0;
}
persistent ghost mapping(address => mathint) maxLtvOracleGhost{
    init_state axiom forall address i. maxLtvOracleGhost[i] == 0;
}

function CVLCallSolvencyOracle(ISiloConfig.ConfigData config){
    solvencyOracleGhost[config.silo]= solvencyOracleGhost[config.silo] + 1;
}
function CVLCallMaxLtvOracle(ISiloConfig.ConfigData config){
    maxLtvOracleGhost[config.silo] = maxLtvOracleGhost[config.silo] + 1;
}

rule liquidationBalances(env e,address collateralAsset,address debtAsset,
    address borrower,uint256 maxDebtToCover,bool receiveSToken){
    configForEightTokensSetupRequirements();
    nonSceneAddressRequirements(e.msg.sender);
    silosTimestampSetupRequirements(e);
    synchronous_siloStorage_erc20cvl(silo0);
    synchronous_siloStorage_erc20cvl(silo1);
    require balanceOfCVL(shareDebtToken0, borrower) >0 ;

    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;

    collateralConfig,debtConfig = CVLGetConfigsForSolvency(borrower);
    PartialLiquidation.LiquidationCallParams params;
    uint256 withdrawAssetsFromCollateral;uint256 withdrawAssetsFromProtected; uint256 repayDebtAssets;bytes4 customError;
    withdrawAssetsFromCollateral, withdrawAssetsFromProtected, repayDebtAssets,customError
    = CVLGetExactLiquidationAmounts(collateralConfig,debtConfig,borrower,maxDebtToCover,collateralConfig.liquidationFee); 
    uint256 collateralShares;
    uint256 protectedShares;
    collateralShares = assetsToSharesApprox(withdrawAssetsFromCollateral, require_uint256(ghostTotalAssets[collateralConfig.silo][COLLATERAL_ASSET_TYPE()]),
     totalSupplyCVL(collateralConfig.collateralShareToken), Math.Rounding.Floor, ISilo.AssetType.Collateral);
    protectedShares = assetsToSharesApprox(withdrawAssetsFromProtected, require_uint256(ghostTotalAssets[collateralConfig.silo][PROTECTED_ASSET_TYPE()]),
     totalSupplyCVL(collateralConfig.protectedShareToken), Math.Rounding.Floor, ISilo.AssetType.Protected);

    address receiver;
    if(receiveSToken){receiver = e.msg.sender;}else{receiver = currentContract;}
    require borrower != receiver;
    mathint receiverCollateralBalancePre = balanceOfCVL(collateralConfig.collateralShareToken,receiver);
    mathint receiverProtectedBalancePre = balanceOfCVL(collateralConfig.protectedShareToken,receiver);
    mathint borrowerCollateralBalancePre = balanceOfCVL(collateralConfig.collateralShareToken,borrower);
    mathint borrowerProtectedBalancePre = balanceOfCVL(collateralConfig.protectedShareToken,borrower);

    liquidationCall(e,collateralAsset,debtAsset,borrower,maxDebtToCover,receiveSToken);

    mathint receiverCollateralBalancePost = balanceOfCVL(collateralConfig.collateralShareToken,receiver);
    mathint receiverProtectedBalancePost = balanceOfCVL(collateralConfig.protectedShareToken,receiver);
    mathint borrowerCollateralBalancePost = balanceOfCVL(collateralConfig.collateralShareToken,borrower);
    mathint borrowerProtectedBalancePost = balanceOfCVL(collateralConfig.protectedShareToken,borrower);

    // assert (
    //     collateralSh
    // )
    assert receiverCollateralBalancePost == receiverCollateralBalancePre + collateralShares;
    assert receiverProtectedBalancePost  == receiverProtectedBalancePre  + protectedShares;

    assert borrowerCollateralBalancePost == borrowerCollateralBalancePre - collateralShares;
    assert borrowerProtectedBalancePost  == borrowerProtectedBalancePre  - protectedShares;
}

rule liquidationCallShoulCallOracle(env e,address collateralAsset,address debtAsset,
    address borrower,uint256 maxDebtToCover,bool receiveSToken){

    configForEightTokensSetupRequirements();
    nonSceneAddressRequirements(e.msg.sender);
    silosTimestampSetupRequirements(e);
    synchronous_siloStorage_erc20cvl(silo0);
    synchronous_siloStorage_erc20cvl(silo1);
    require balanceOfCVL(shareDebtToken0, borrower) >0 ;

    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;

    collateralConfig,debtConfig = CVLGetConfigsForSolvency(borrower);

    mathint solvencyCounterPre_collateral = solvencyOracleGhost[collateralConfig.silo];
    mathint solvencyCounterPre_debt = solvencyOracleGhost[debtConfig.silo];
    // mathint maxLtvCounterPre = maxLtvOracleGhost[collateralConfig];

    liquidationCall(e,collateralAsset,debtAsset,borrower,maxDebtToCover,receiveSToken);

    mathint solvencyCounterPost_collateral = solvencyOracleGhost[collateralConfig.silo];
    mathint solvencyCounterPost_debt = solvencyOracleGhost[debtConfig.silo];
    // mathint maxLtvCounterPost = maxLtvOracleGhost[collateralConfig];

    assert (
        debtConfig.silo != collateralConfig.silo <=> 
        solvencyOracleGhost[collateralConfig.silo] == solvencyCounterPre_collateral + 1
    );
    assert (
        debtConfig.silo != collateralConfig.silo <=> 
        solvencyOracleGhost[debtConfig.silo] == solvencyCounterPre_debt + 1
    );
}


rule maxLiquidationIntegrity(env e,address borrower){

    nonSceneAddressRequirements(borrower);
    SiloSolvencyLib.LtvData ltvData;
    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;

    collateralConfig,debtConfig = CVLGetConfigsForSolvency(borrower);
    ltvData = calculateAssetsDataCVL(collateralConfig.silo,debtConfig.silo,borrower,0);

    uint256 collateralToLiquidate;
    uint256 deptToRepay;
    bool sTokenRequired;
    collateralToLiquidate,deptToRepay,sTokenRequired = maxLiquidation(e,borrower);

    assert debtConfig.silo == 0 => (collateralToLiquidate == 0 && deptToRepay == 0);
    assert ltvData.borrowerDebtAssets == 0 => (collateralToLiquidate == 0 && deptToRepay == 0);
}