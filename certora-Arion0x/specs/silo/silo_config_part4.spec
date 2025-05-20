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
    function _.synchronizeHooks(uint24,uint24) external => DISPATCHER(true);
    function _.hookReceiverConfig(address) external => DISPATCHER(true);
    
    //------------NONDET-------------//
    function _.onFlashLoan(address _initiator, address _token, uint256 _amount, uint256 _fee, bytes _data) external => NONDET;
    function _.flashFee(address,address,uint256) internal => NONDET;
    function _.maxFlashLoan(address) internal => NONDET;
    function _.reentrancyGuardEntered()external => NONDET;
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

// ---- Rules from the list ----------------------------------------------------

rule borrowerShouldHasDebt(address borrower,method f, calldataarg args)
filtered{f-> f.contract != siloConfig && !ignoredFunction(f) && !UNNECESSARY_MINT_BORROW_REPAY_REDEEM_WITHDRAW_DEPOSIT(f) && f.selector != sig:silo0.switchCollateralToThisSilo().selector} {
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // e.msg.sender is not one of the contracts in the scene
    nonSceneAddressRequirements(borrower);
    totalSuppliesMoreThanBalances(borrower, silo0);
    synchronous_siloStorage_erc20cvl(e);

    // require ghostBorrowerCollateralSilo[borrower] == 0;
    address collateralSiloPre = ghostBorrowerCollateralSilo[borrower];


    f(e,args);

    address collateralSiloPost = ghostBorrowerCollateralSilo[borrower];

    ISiloConfig.ConfigData collateralConfig_0;
    ISiloConfig.ConfigData debtConfig_0;
    ISiloConfig.ConfigData collateralConfig_1;
    ISiloConfig.ConfigData debtConfig_1;
    collateralConfig_0,debtConfig_0 = CVLGetConfigsForSolvency(borrower);
    collateralConfig_1,debtConfig_1 = CVLGetConfigsForSolvency(borrower);
    uint256 debt0Balance =  balanceOfCVL(debtConfig_0.debtShareToken,borrower);
    // debtConfig_0.debtShareToken.balanceOf(e,borrower);
    uint256 debt1Balance =  balanceOfCVL(debtConfig_1.debtShareToken,borrower);
    // debtConfig_1.debtShareToken.balanceOf(e,borrower);

    // we can't set the collateralSilo to address zero if he wasn't zero address
    assert (collateralSiloPre ==0 && collateralSiloPost != 0) => (debt0Balance!= 0 || debt1Balance !=0);
}