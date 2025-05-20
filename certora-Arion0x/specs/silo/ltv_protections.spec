
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
    // function _.isBelowMaxLtv(ISiloConfig.ConfigData,ISiloConfig.ConfigData,address,ISilo.AccrueInterestInMemory) internal => DISPATCHER(true);

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

rule borrowingRespectLTV(env e,uint256 assets,uint256 shares, address _receiver, address _borrower, method f)
filtered{f-> !ignoredFunction(f)}{
    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // e.msg.sender is not one of the contracts in the scene
    nonSceneAddressRequirements(e.msg.sender);
    synchronous_siloStorage_erc20cvl(e);
    require e.msg.sender !=0;

    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;

    collateralConfig,debtConfig = CVLGetConfigsForBorrow(currentContract);

    mathint maxLTVCounterPre_collateral = maxLtvOracleGhost[collateralConfig.silo];
    mathint maxLTVCounterPre_debt = maxLtvOracleGhost[debtConfig.silo];

    if(f.selector == sig:borrow(uint256,address,address).selector){
        borrow(e,assets,_receiver,_borrower);
    }else{
        borrowShares(e,shares,_receiver,_borrower);
    }

    assert isBelowMaxLTVHarness(e,collateralConfig,debtConfig,_borrower,ISilo.AccrueInterestInMemory.No);
    //checking on triggering the oracle before quote
    assert (collateralConfig.silo != debtConfig.silo) => (
        maxLtvOracleGhost[collateralConfig.silo] == maxLTVCounterPre_collateral + 1 &&
        maxLtvOracleGhost[debtConfig.silo] == maxLTVCounterPre_debt +1
    );
}

rule borrowSameRespectLTV(env e,uint256 assets, address _receiver, address _borrower){
    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // e.msg.sender is not one of the contracts in the scene
    nonSceneAddressRequirements(e.msg.sender);
    synchronous_siloStorage_erc20cvl(e);
    require e.msg.sender !=0;

    ISiloConfig.ConfigData collateralConfig;

    collateralConfig = CVLGetConfig(currentContract);

    mathint maxLTVCounterPre_collateral = maxLtvOracleGhost[collateralConfig.silo];

    borrowSameAsset(e,assets,_receiver,_borrower);

    assert isBelowMaxLTVHarness(e,collateralConfig,collateralConfig,_borrower,ISilo.AccrueInterestInMemory.No);
    //borrow same shouldnt trigger oracles because collateralSilo == debtSilo
    assert maxLtvOracleGhost[collateralConfig.silo] == maxLTVCounterPre_collateral;
}