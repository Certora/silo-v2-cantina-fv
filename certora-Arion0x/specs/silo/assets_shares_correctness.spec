/* 
 * Verifies properties releated to the totalShares-totalAssets
 */

import "../setup/CompleteSiloSetup.spec";
import "../setup/ERC20/erc20cvl.spec";
import "../setup/StorageHooks/hook_all.spec";
// import "../setup/summaries/siloconfig_dispatchers.spec";
// import "../setup/summaries/tokens_dispatchers.spec";
// import "unresolved.spec";

import "../simplifications/priceOracle_UNSAFE.spec";
import "../simplifications/SiloMathLib_SAFE.spec";
import "../simplifications/SiloMathLib_UNSAFE.spec";
import "../simplifications/SiloStdLib_UNSAFE.spec";
import "../simplifications/ignore_hooks_simplification.spec";
//ignore interest for this rules
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";
import "../simplifications/zero_compound_interest.spec";

methods{
    function getSiloStorage() external returns (uint192, uint64, uint256, uint256, uint256) envfree;

    function _.getConfigsForWithdraw(address,address) external => DISPATCHER(true);
    function _.getConfigsForBorrow(address) external  => DISPATCHER(true);
    function _.getConfigsForSolvency(address) external  => DISPATCHER(true);

    function _.setThisSiloAsCollateralSilo(address) external  => DISPATCHER(true);
    function _.setOtherSiloAsCollateralSilo(address) external  => DISPATCHER(true);
    function _.borrowerCollateralSilo(address) external  => DISPATCHER(true);
    function _.onDebtTransfer(address,address) external  => DISPATCHER(true);
    function _.hasDebtInOtherSilo(address,address) external => DISPATCHER(true);
    function _.hookReceiverConfig(address) external => DISPATCHER(true);

    function _.reentrancyGuardEntered()external => NONDET;
    function _.onFlashLoan(address _initiator, address _token, uint256 _amount, uint256 _fee, bytes _data) external => NONDET;
    function _.flashFee(address,address,uint256) internal => NONDET;
    function _.maxFlashLoan(address) internal => NONDET;
    function _.synchronizeHooks(uint24,uint24) external => NONDET;
    function _.matchAction(uint256 _action, uint256 _expectedHook) internal => ALWAYS(false);
    function _.beforeAction(address, uint256, bytes) external => NONDET;
    function _.afterAction(address, uint256, bytes) external => NONDET;
    function _.accrueInterestForSilo(address) external => NONDET;
    function _.accrueInterestForBothSilos() external => NONDET;
    function _.turnOnReentrancyProtection() external => NONDET;
    function _.turnOffReentrancyProtection() external => NONDET;

    // function _.getFeeReceivers(
    //     address _silo
    // ) external => NONDET;
}

// ---- Rules ------------------------------------------------------------------

rule functionsCanDecrease_shares(env e,method f,calldataarg args)
filtered{f-> !ignoredFunction(f) && f.selector !=sig:flashLoan(address,address,uint256,bytes).selector}{

    SafeAssumptionsEnv_withInvariants(e);
    synchronous_siloStorage_erc20cvl(e);
    require ghostInterestRateTimestamp[silo0] == e.block.timestamp;


    mathint totalSharesBefore = totalSupplyCVL(silo0);
    mathint totalProtectedAssetsBefore;
    totalProtectedAssetsBefore = totalSupplyCVL(shareProtectedCollateralToken0);
    mathint totalDebtBefore;
    totalDebtBefore = totalSupplyCVL(shareDebtToken0);

    f(e,args);

    mathint totalSharesAfter = totalSupplyCVL(silo0);
    mathint totalProtectedAssetsAfter;
    totalProtectedAssetsAfter = totalSupplyCVL(shareProtectedCollateralToken0);
    mathint totalDebtAfter;
    totalDebtAfter = totalSupplyCVL(shareDebtToken0);

    assert totalSharesAfter < totalSharesBefore => canDecreaseSharesBalance(f);
    assert totalProtectedAssetsAfter < totalProtectedAssetsBefore => canDecreaseProtectedAssets(f);
    assert totalDebtAfter < totalDebtBefore => canDecreaseTotalDebt(f);
}

rule functionsCanIncrease_shares(env e,method f,calldataarg args)filtered{f-> !ignoredFunction(f) && f.selector !=sig:flashLoan(address,address,uint256,bytes).selector}{

    SafeAssumptionsEnv_withInvariants(e);
    synchronous_siloStorage_erc20cvl(e);
    require ghostInterestRateTimestamp[silo0] == e.block.timestamp;

    mathint totalSharesBefore = totalSupplyCVL(silo0);
    mathint totalProtectedAssetsBefore;
    totalProtectedAssetsBefore = totalSupplyCVL(shareProtectedCollateralToken0);
    mathint totalCollateralAssetsBefore;
    totalCollateralAssetsBefore = totalSupplyCVL(silo0);
    mathint totalDebtBefore;
    totalDebtBefore = totalSupplyCVL(shareDebtToken0);

    f(e,args);

    mathint totalSharesAfter = totalSupplyCVL(silo0);
    mathint totalProtectedAssetsAfter;
    totalProtectedAssetsAfter = totalSupplyCVL(shareProtectedCollateralToken0);

    mathint totalCollateralAssetsAfter;
    totalCollateralAssetsAfter = totalSupplyCVL(silo0);
    mathint totalDebtAfter;
    totalDebtAfter = totalSupplyCVL(shareDebtToken0);

    assert totalSharesAfter > totalSharesBefore => canIncreaseSharesBalance(f);
    assert totalProtectedAssetsAfter > totalProtectedAssetsBefore => canIncreaseProtectedAssets(f);
    assert totalCollateralAssetsAfter > totalCollateralAssetsBefore => canIncreaseTotalCollateral(f);
    assert totalDebtAfter > totalDebtBefore => canIncreaseTotalDebt(f);
}

rule getTotalAssetsStorageCorrectness(env e){
    uint256 totalDebtStorage;
    uint256 totalCollateralStorage;
    uint256 totalProtectedStorage;
    totalDebtStorage = silo0.getTotalAssetsStorage(ISilo.AssetType.Debt);
    totalCollateralStorage = silo0.getTotalAssetsStorage(ISilo.AssetType.Collateral);
    totalProtectedStorage = silo0.getTotalAssetsStorage(ISilo.AssetType.Protected);

    mathint totalDebt;
    mathint totalCollateral;
    mathint totalProtected;
    totalProtected =  ghostTotalAssets[silo0][PROTECTED_ASSET_TYPE()];
    totalCollateral = ghostTotalAssets[silo0][COLLATERAL_ASSET_TYPE()];
    totalDebt = ghostTotalAssets[silo0][DEBT_ASSET_TYPE()]; 

    assert totalDebtStorage == totalDebt;
    assert totalCollateralStorage == totalCollateral;
    assert totalProtectedStorage  ==  totalProtected;
}

rule revenueAndTimestampCorrectness(){
    uint192 daoAndDeployerStorage;
    uint64 interestRateTimeStampStorage;
    daoAndDeployerStorage,interestRateTimeStampStorage,_
    ,_,_ = getSiloStorage();


    mathint daoAndDeployerGhost;
    mathint interestRateTimestampGhost;
    daoAndDeployerGhost = ghostDaoAndDeployerRevenue[silo0];
    interestRateTimestampGhost = ghostInterestRateTimestamp[silo0];

    assert daoAndDeployerStorage == daoAndDeployerGhost;
    assert interestRateTimeStampStorage == interestRateTimestampGhost;
}


rule getSiloStorageCorrectness(env e){

    uint192 daoAndDeployerStorage;
    uint64 interestRateTimeStampStorage;
    uint256 totalDebtStorage;
    uint256 totalCollateralStorage;
    uint256 totalProtectedStorage;
    daoAndDeployerStorage,interestRateTimeStampStorage,totalProtectedStorage
    ,totalCollateralStorage,totalDebtStorage = getSiloStorage();

    uint256 totalDebt;
    uint256 totalCollateral;
    uint256 totalProtected;
    totalDebt = silo0.getTotalAssetsStorage(ISilo.AssetType.Debt);
    totalCollateral = silo0.getTotalAssetsStorage(ISilo.AssetType.Collateral);
    totalProtected = silo0.getTotalAssetsStorage(ISilo.AssetType.Protected);

    assert totalDebtStorage == totalDebt;
    assert totalCollateralStorage == totalCollateral;
    assert totalProtectedStorage == totalProtected;
}

rule getCollateralAndProtectedCorrectness(env e){
    mathint totalCollateralStorage; mathint totalProtectedStorage;
    totalCollateralStorage, totalProtectedStorage = silo0.getCollateralAndProtectedTotalsStorage(e);

    mathint totalCollateral;
    mathint totalProtected;
    totalProtected =  ghostTotalAssets[silo0][PROTECTED_ASSET_TYPE()];
    totalCollateral = ghostTotalAssets[silo0][COLLATERAL_ASSET_TYPE()];
    
    assert totalCollateralStorage == totalCollateral;
    assert totalProtectedStorage == totalProtected;
}

rule getCollateralAndDebtCorrectness(env e){
    mathint totalCollateralStorage; mathint totalDebtStorage;
    totalCollateralStorage, totalDebtStorage = silo0.getCollateralAndDebtTotalsStorage(e);

    mathint totalCollateral;
    mathint totalDebt;
    totalCollateral = ghostTotalAssets[silo0][COLLATERAL_ASSET_TYPE()];
    totalDebt = ghostTotalAssets[silo0][DEBT_ASSET_TYPE()]; 
    
    assert totalCollateralStorage == totalCollateral;
    assert totalDebtStorage == totalDebt;
}

function synchronous_siloStorage_erc20cvl(env e){
    mathint totalDebt;
    mathint totalCollateral;
    mathint totalProtected;
    totalProtected =  ghostTotalAssets[silo0][PROTECTED_ASSET_TYPE()];
    totalCollateral = ghostTotalAssets[silo0][COLLATERAL_ASSET_TYPE()];
    totalDebt = ghostTotalAssets[silo0][DEBT_ASSET_TYPE()]; 
    require totalProtected  == totalSupplyCVL(shareProtectedCollateralToken0);
    require totalCollateral == totalSupplyCVL(silo0);
    require totalDebt == totalSupplyCVL(shareDebtToken0);
}