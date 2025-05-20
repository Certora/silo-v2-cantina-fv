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

// ---- Borrow ----------------------------------------------------------------- 

//done-proved
rule cantBorrowFromTwoSilos(env e,uint256 assets,address receiver){
    
    SafeAssumptionsEnv_withInvariants(e);
    nonSceneAddressRequirements(receiver);
    require receiver != 0;
    synchronous_siloStorage_erc20cvl(e);

    silo0.borrowSameAsset(e, assets, receiver, receiver);
    silo1.borrowSameAsset@withrevert(e,assets,receiver,receiver);

    assert lastReverted;
}

// ---- Rules from the list ----------------------------------------------------

/// @dev rule 104:
//       `getConfigsForWithdraw()` collateralConfig.silo is equal
//       `borrowerCollateralSilo[_depositOwner]` if there is debt

/// @status inProgress

rule collateralSiloMatchesDebt_withdraw(address borrower,method f,calldataarg args)filtered{
  f->  f.selector != sig:Silo0.initialize(address).selector && !ignoredFunction(f)
}{
    env e;
    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;

    SafeAssumptionsEnv_withInvariants(e);
    synchronous_siloStorage_erc20cvl(e);
    nonSceneAddressRequirements(e.msg.sender);
    nonSceneAddressRequirements(borrower);

    silo0.setSiloAsCollateral(e,borrower);

    f(e,args);

    _,collateralConfig,debtConfig = CVLGetConfigsForWithdraw(silo0,borrower);
    address currentCollateral = getBorrowerCollateral(e,borrower);
    uint256 debtBalance = balanceOfCVL(debtConfig.debtShareToken,borrower);
    // debtConfig.debtShareToken.balanceOf(e,borrower);

    //if there is a debt the collateralSilo should be configured for the borrwer
    assert debtBalance != 0 =>  currentCollateral == collateralConfig.silo;
}

/// @dev rule 89:
//       if `borrowerCollateralSilo[user]` is set from zero to non-zero value,
//       it never goes back to zero

/// @status Done-proved

rule collateralSiloMatchesDebt(address user,method f, calldataarg args)
filtered{f-> f.contract != siloConfig && f.selector != sig:Silo0.initialize(address).selector && !ignoredFunction(f) && !UNNECESSARY_MINT_BORROW_REPAY_REDEEM_WITHDRAW_DEPOSIT(f)} {
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // e.msg.sender is not one of the contracts in the scene
    nonSceneAddressRequirements(user);
    totalSuppliesMoreThanBalances(user, silo0);
    synchronous_siloStorage_erc20cvl(e);

    address collateralSilo = ghostBorrowerCollateralSilo[user];
    f(e,args);

    // we can't set the collateralSilo to address zero if he wasn't zero address
    assert collateralSilo != 0 => ghostBorrowerCollateralSilo[user] != 0;
}

//done-proved
rule switchCollateralToThisSiloIntegrity(env e,address borrower){
    require e.msg.sender == borrower;

    getBorrowerCollateral(borrower);
    address collateralSiloPre = ghostBorrowerCollateralSilo[borrower];

    silo0.switchCollateralToThisSilo(e);

    address collateralSiloPost = ghostBorrowerCollateralSilo[borrower];

    assert collateralSiloPre != silo0 => collateralSiloPost == silo0;
}

// 16* if user has debt, `borrowerCollateralSilo[user]` should be silo0 or silo1 and one of shares tokens balances should not be 0
// 58* `borrowerCollateralSilo[user]` should be set to "this" Silo address. No other state should be changed in either Silo. ?
// 91* if `borrowerCollateralSilo[user]` is set from zero to non-zero value, one of the debt share token `totalSupply()` increases and `totalAssets[AssetType.Debt]` increases for one of the silos - excluding `switchCollateralToThisSilo()` method