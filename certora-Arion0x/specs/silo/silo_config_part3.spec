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

// ---- Rules from the list ----------------------------------------------------

/// @dev rule 98:
//       `getConfigsForSolvency()` collateralConfig.silo is equal 
//       `borrowerCollateralSilo[_depositOwner]` if there is debt

/// @status inProgress

rule collateralSiloMatchesDebt_solvency(address borrower,method f,calldataarg args)filtered{
   f-> f.selector != sig:Silo0.initialize(address).selector && !ignoredFunction(f)
} {
    env e;
    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;

    // setThisSiloAsCollateralSilo(e,borrower);
    SafeAssumptionsEnv_withInvariants(e);
    synchronous_siloStorage_erc20cvl(e);
    nonSceneAddressRequirements(e.msg.sender);
    nonSceneAddressRequirements(borrower);

    //non zero collateral
    silo0.setSiloAsCollateral(e,borrower);
 
    f(e,args);

    collateralConfig,debtConfig = CVLGetConfigsForSolvency(borrower);
    address currentCollateral = getBorrowerCollateral(e,borrower);
    uint256 debtBalance =   balanceOfCVL(debtConfig.debtShareToken,borrower);
    //  debtConfig.debtShareToken.balanceOf(e,borrower);

    //if there is a debt the collateralSilo should be configured for the borrwer
    assert debtBalance != 0 => currentCollateral == collateralConfig.silo;
}