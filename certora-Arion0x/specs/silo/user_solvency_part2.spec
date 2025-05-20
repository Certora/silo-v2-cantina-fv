
import "../setup/CompleteSiloSetup.spec";
import "../setup/summaries/siloconfig_summaries.spec";
import "../setup/ERC20/erc20cvl.spec";
import "../setup/StorageHooks/hook_all.spec";

import "../simplifications/priceOracle_UNSAFE.spec";
import "../simplifications/ignore_hooks_simplification.spec";
import "../simplifications/SiloMathLib_SAFE.spec";
import "../simplifications/SiloMathLib_UNSAFE.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";
import "../simplifications/zero_compound_interest.spec";
import "../simplifications/SiloStdLib_UNSAFE.spec";



// ---- Methods and Invariants -------------------------------------------------

methods{
    //ignore calling hooks 
    function _.matchAction(uint256 _action, uint256 _expectedHook) internal => ALWAYS(false);

    //------------DISPATCHERS-------------//
    function _.isSolvent(address) external => DISPATCHER(true);

    //-------------NONDET-----------------//
    function _.beforeAction(address, uint256, bytes) external => NONDET;
    function _.afterAction(address, uint256, bytes) external => NONDET;
    function _.onFlashLoan(address _initiator, address _token, uint256 _amount, uint256 _fee, bytes _data) external => NONDET;
    function _.flashFee(address,address,uint256) internal => NONDET;
    function _.maxFlashLoan(address) internal => NONDET;
    function _.synchronizeHooks(uint24,uint24) external => NONDET;
    function _.accrueInterestForSilo() external => NONDET;
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


// ---- Rules from the list ----------------------------------------------------

/// @dev rule 57:
//  user must be solvent after switchCollateralToThisSilo()

/// @status done-proved

rule solventAfterSwitch() {
    env e;
    
    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // e.msg.sender is not one of the contracts in the scene
    nonSceneAddressRequirements(e.msg.sender);
    totalSuppliesMoreThanBalances(e.msg.sender, silo0);
    synchronous_siloStorage_erc20cvl(e);

    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;
    collateralConfig, debtConfig = CVLGetConfigsForSolvency(e.msg.sender);

    silo0.switchCollateralToThisSilo(e);

    assert debtConfig.silo != 0 =>  silo0.isSolvent(e,e.msg.sender);
}

/// @dev rule 112 && 33:
//          if user is insolvent, it must have debt shares
//          if user has no debt, should always be solvent and ltv == 0
/// @status done-proved

rule insolventHasDebt(address borrower) {
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // e.msg.sender is not one of the contracts in the scene
    nonSceneAddressRequirements(borrower);
    totalSuppliesMoreThanBalances(borrower, silo0);
    synchronous_siloStorage_erc20cvl(e);

    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;
    collateralConfig,debtConfig = CVLGetConfigsForSolvency(borrower);

    uint256 debtBalance = balanceOfCVL(debtConfig.debtShareToken,borrower);
    // debtConfig.debtShareToken.balanceOf(e,borrower);
    uint256 ltv = getLTV(e,borrower);

    // borrower has debt if inslovent
    assert !silo0.isSolvent(e,borrower) => debtBalance > 0;
    assert debtBalance == 0 => (silo0.isSolvent(e,borrower) && ltv == 0);
}


rule FunctionsRequiresSolvency(method f,calldataarg args,uint256 assets,address owner,ISilo.CollateralType type)
filtered{f -> REQUIRE_SOLVENCY_WITHDRAW_METHODS(f)}{
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // e.msg.sender is not one of the contracts in the scene
    nonSceneAddressRequirements(owner);
    totalSuppliesMoreThanBalances(owner, silo0);
    synchronous_siloStorage_erc20cvl(e);


    ISiloConfig.DepositConfig depositConfig;
    ISiloConfig.ConfigData collateralConfig;

    if(f.selector == sig:withdraw(uint256,address,address).selector) {
        silo0.withdraw(e,assets,owner, owner);
    } else if(f.selector == sig:withdraw(uint256,address,address,ISilo.CollateralType).selector) {
        silo0.withdraw(e,assets,owner, owner,type);
    } else if(f.selector == sig:transitionCollateral(uint256,address,ISilo.CollateralType).selector) {
        silo0.transitionCollateral(e, assets, owner, type);
    }
    depositConfig,collateralConfig,_ = CVLGetConfigsForWithdraw(silo0,owner);

    assert collateralConfig.silo == depositConfig.silo => silo0.isSolvent(e,owner);
}

/// @dev rule 99:
//       `getConfigsForSolvency()` debtConfig.silo is always the silo 
//        that debt share token balance is not equal 0 or zero address otherwise
//       
/// @status Done-proved

rule CorrectSiloDebt(address borrower) {
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // e.msg.sender is not one of the contracts in the scene
    nonSceneAddressRequirements(borrower);
    totalSuppliesMoreThanBalances(borrower, silo0);
    synchronous_siloStorage_erc20cvl(e);

    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;
    collateralConfig,debtConfig = CVLGetConfigsForSolvency(borrower);
    address siloDebt = siloConfig.getDebtSilo(e,borrower);

    assert debtConfig.silo == siloDebt;
}

/// @dev rule 100:
//       `getConfigsForSolvency()` if no debt, both configs
//       (collateralConfig, debtConfig) are zero
//       
/// @status Done-proved

rule noDebt_noSolvencyConfig(address borrower) {
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // e.msg.sender is not one of the contracts in the scene
    nonSceneAddressRequirements(borrower);
    totalSuppliesMoreThanBalances(borrower, silo0);
    synchronous_siloStorage_erc20cvl(e);

    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;
    collateralConfig,debtConfig = CVLGetConfigsForSolvency(borrower);
    address siloDebt = siloConfig.getDebtSilo(e,borrower);

    assert siloDebt == 0 => (collateralConfig.debtShareToken == 0 && debtConfig.debtShareToken == 0);
}