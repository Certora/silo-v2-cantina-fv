
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

    //------------NONDET-------------//
    function _.callSolvencyOracleBeforeQuote(ISiloConfig.ConfigData memory config) internal => CVLCallSolvencyOracle(config) expect void;
    function _.callMaxLtvOracleBeforeQuote(ISiloConfig.ConfigData memory config) internal => CVLCallMaxLtvOracle(config) expect void;
    function _.beforeAction(address, uint256, bytes) external => NONDET;
    function _.afterAction(address, uint256, bytes) external => NONDET;
    function _.onFlashLoan(address _initiator, address _token, uint256 _amount, uint256 _fee, bytes _data) external => NONDET;
    function _.flashFee(address,address,uint256) internal => NONDET;
    function _.maxFlashLoan(address) internal => NONDET;
    function _.synchronizeHooks(uint24,uint24) external => NONDET;
    function _.accrueInterestForSilo() external => NONDET;
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

// invariant SolventAccrossSilos(env e,address owner)
//     silo0.isSolvent(e,owner) <=> silo1.isSolvent(e,owner);


// ---- Rules from the list ----------------------------------------------------


/// @dev rule 59:
//          if user is NOT solvent `transitionCollateral()`
//          must always reverts
/// @status inProgress

rule switchCollateralRequireSolvency(env e) {

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // e.msg.sender is not one of the contracts in the scene
    nonSceneAddressRequirements(e.msg.sender);
    synchronous_siloStorage_erc20cvl(e);
    require e.msg.sender !=0;

    ISiloConfig.ConfigData debtConfig;

    // transitions collateral

    silo0.switchCollateralToThisSilo@withrevert(e);
    bool lastRevertedBool = lastReverted;

    _,debtConfig= CVLGetConfigsForSolvency(e.msg.sender);
    bool isSolvent = silo0.isSolvent(e,e.msg.sender);

    // should revert if not solvent
    assert (!isSolvent && debtConfig.silo != 0) => lastRevertedBool;
}


// ---- Rules from properties-draft ----------------------------------------------------

/// @dev rule 59:
//          if user is NOT solvent `transitionCollateral()`
//          must always reverts
/// @dev rule 52:
//          if user is solvent transitionCollateral() for
//          _transitionFrom == CollateralType.Protected should never revert
/// @status inProgress

rule transitionRequireSolvency(uint256 _shares,address _owner,ISilo.CollateralType _transitionFrom) {
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // e.msg.sender is not one of the contracts in the scene
    nonSceneAddressRequirements(_owner);
    totalSuppliesMoreThanBalances(_owner, silo0);
    synchronous_siloStorage_erc20cvl(e);
    ISiloConfig.DepositConfig depositConfig;
    ISiloConfig.ConfigData collateralConfig;

    // transitions collateral

    silo0.transitionCollateral@withrevert(e,_shares,_owner,_transitionFrom);
    bool lastRevertedBool = lastReverted;

    depositConfig,collateralConfig,_ = CVLGetConfigsForWithdraw(silo0,_owner);
    bool isSolvent = silo0.isSolvent(e,_owner);

    // should revert if not solvent
    assert (!isSolvent && depositConfig.silo == collateralConfig.silo) => lastRevertedBool;
}


/// @dev rule 10:
//          user is always solvent after `withdraw()`
/// @status inProgress

rule solventAfterWithdraw(uint256 assets,address receiver) {
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // e.msg.sender is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    totalSuppliesMoreThanBalances(receiver, silo0);
    synchronous_siloStorage_erc20cvl(e);

    ISiloConfig.DepositConfig depositConfig;
    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;

    depositConfig,collateralConfig,debtConfig = CVLGetConfigsForWithdraw(silo0,receiver);

    mathint solvencyCounterPre_collateral = solvencyOracleGhost[collateralConfig.silo];
    mathint solvencyCounterPre_debt = solvencyOracleGhost[debtConfig.silo];

    // withdrawing collateral
    silo0.withdraw(e, assets, receiver, receiver);

    // should revert if not solvent
    assert ((depositConfig.silo == collateralConfig.silo)) => (silo0.isSolvent(e,receiver));
    assert (
        (depositConfig.silo == collateralConfig.silo && debtConfig.silo != collateralConfig.silo)
        => (solvencyOracleGhost[collateralConfig.silo] == solvencyCounterPre_collateral + 1 &&
            solvencyOracleGhost[debtConfig.silo] == solvencyCounterPre_debt + 1 )
    );
}

