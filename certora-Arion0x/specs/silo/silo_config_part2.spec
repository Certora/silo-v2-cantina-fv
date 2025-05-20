/* The specification of the Silo configs */

import "../setup/CompleteSiloSetup.spec";
import "../setup/summaries/siloconfig_summaries.spec";
import "../setup/StorageHooks/siloConfig.spec";
import "../setup/StorageHooks/hook_all.spec";
import "../setup/ERC20/erc20cvl.spec";

import "../simplifications/priceOracle_UNSAFE.spec";
import "../simplifications/ignore_hooks_simplification.spec";
import "../simplifications/SiloMathLib_SAFE.spec";
import "../simplifications/SiloMathLib_UNSAFE.spec";
import "../simplifications/SiloStdLib_UNSAFE.spec";
import "../simplifications/zero_compound_interest.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";

methods{
    function ShareTokenLib.siloConfig() internal returns(address) => SiloConfigCVL();
    
    //ignore calling hooks 
    function _.matchAction(uint256 _action, uint256 _expectedHook) internal => ALWAYS(false);

    //------------DISPATCHERS-------------//
    function _.isSolvent(address) external => DISPATCHER(true);

    //------------NONDET-------------//
    function _.onFlashLoan(address _initiator, address _token, uint256 _amount, uint256 _fee, bytes _data) external => NONDET;
    function _.flashFee(address,address,uint256) internal => NONDET;
    function _.maxFlashLoan(address) internal => NONDET;
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
// ---- Rules and Invariants ----------------------------------------------------


// use builtin rule sanity;

// ---- Borrow ----------------------------------------------------------------- 

//done-proved
rule cantBorrowFromTwoSilos_2(env e,uint256 assets,address receiver){
    
    // ISiloConfig.ConfigData config = siloConfig.getConfig(silo1);
    bool hasDebtInOtherSilo = siloConfig.hasDebtInOtherSilo(e,silo1,e.msg.sender);
    synchronous_siloStorage_erc20cvl(e);

    silo1.borrow@withrevert(e,assets,receiver,e.msg.sender);

    assert hasDebtInOtherSilo => lastReverted;
}

//done-proved
rule siloMarkedAsHasDebtAfterBorrow(env e,uint256 assets,address receiver){
    
    SafeAssumptionsEnv_withInvariants(e);
    nonSceneAddressRequirements(e.msg.sender);
    synchronous_siloStorage_erc20cvl(e);

    silo1.borrow(e,assets,receiver,receiver);

    bool SilohasDebt = siloConfig.hasDebtInOtherSilo(e,silo0,receiver);

    assert SilohasDebt;
}

/**
@title the siloConfig cant updated  //done-proved
*/
rule siloConfigIntegrity(env e,method f, calldataarg args)
filtered{f-> !ignoredFunction(f) && f.selector != sig:Silo0.initialize(address).selector}{
    
    synchronous_siloStorage_erc20cvl(e);
    address configBefore = silo0.config(e);

    f(e,args);
    address configAfter = silo0.config(e);

    assert configBefore == configAfter;
}

// ---- Rules from the list ----------------------------------------------------

//done-proved
rule switchCollateralToThisSiloRevert(env e,address borrower){
    require e.msg.sender == borrower;

    getBorrowerCollateral(borrower);

    address collateralSiloPre = ghostBorrowerCollateralSilo[borrower];


    silo0.switchCollateralToThisSilo@withrevert(e);


    address collateralSiloPost = ghostBorrowerCollateralSilo[borrower];

    assert collateralSiloPre == silo0 => lastReverted;
}
// 16* if user has debt, `borrowerCollateralSilo[user]` should be silo0 or silo1 and one of shares tokens balances should not be 0
// 58* `borrowerCollateralSilo[user]` should be set to "this" Silo address. No other state should be changed in either Silo. ?
// 91* if `borrowerCollateralSilo[user]` is set from zero to non-zero value, one of the debt share token `totalSupply()` increases and `totalAssets[AssetType.Debt]` increases for one of the silos - excluding `switchCollateralToThisSilo()` method