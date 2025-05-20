/* Verifies the protocol allows anyone user access 
 * This setup is for a single silo - `Silo0`
 */

import "../setup/single_silo_tokens_requirements.spec";
import "../setup/summaries/silo0_summaries.spec";
import "../setup/summaries/siloconfig_dispatchers.spec";
import "../setup/summaries/config_for_one_in_cvl.spec";
import "../setup/summaries/safe-approximations.spec";
import "../setup/summaries/tokens_dispatchers.spec";


methods {
    // ---- `SiloConfig` -------------------------------------------------------
    // `envfree`
    function SiloConfigHarness.accrueInterestForSilo(address) external envfree;
    function SiloConfigHarness.getCollateralShareTokenAndAsset(
        address,
        ISilo.CollateralType
    ) external returns (address, address) envfree;

    function _.isSolvent(address) external => DISPATCHER(true) ;
    
    // ---- `IInterestRateModel` -----------------------------------------------
    // Since `getCompoundInterestRateAndUpdate` is not *pure*, this is not strictly sound.
    function _.getCompoundInterestRateAndUpdate(
        uint256 _collateralAssets,
        uint256 _debtAssets,
        uint256 _interestRateTimestamp
    ) external =>  CVLGetCompoundInterestRate(
        _collateralAssets,
        _debtAssets,
        _interestRateTimestamp
    ) expect (uint256);
    
    // TODO: Is this sound?
    function _.getCompoundInterestRate(
        address _silo,
        uint256 _blockTimestamp
    ) external => CVLGetCompoundInterestRateForSilo(_silo, _blockTimestamp) expect (uint256);

    // ---- `ISiloOracle` ------------------------------------------------------
    // NOTE: Since `beforeQuote` is not a view function, strictly speaking this is unsound.
    function _.beforeQuote(address) external => NONDET DELETE;

    function _.beforeAction(address, uint256, bytes) external => NONDET;
    function _.afterAction(address, uint256, bytes) external => NONDET;
    function _.quote(address) external => NONDET;
    function _.quote(uint256 _baseAmount, address _baseToken) external => NONDET; 
}

// ---- Functions and ghosts ---------------------------------------------------

ghost mapping(uint256 => mapping(uint256 => mapping(uint256 => uint256))) interestGhost;

// @title An arbitrary (pure) function for the interest rate
function CVLGetCompoundInterestRate(
    uint256 _collateralAssets,
    uint256 _debtAssets,
    uint256 _interestRateTimestamp
) returns uint256 {
    return interestGhost[_collateralAssets][_debtAssets][_interestRateTimestamp];
}


ghost mapping(address => mapping(uint256 => uint256)) interestGhostSilo;

// @title An arbitrary (pure) function for the interest rate 
function CVLGetCompoundInterestRateForSilo(
    address _silo,
    uint256 _blockTimestamp
) returns uint256 {
    return interestGhostSilo[_silo][_blockTimestamp];
}


// @title Require that the second env has at least as much allowance and balance as first
function requireSecondEnvAtLeastAsFirst(env e1, env e2) {
    /// At least as much allowance as first `env`
    require (
        token0.allowance(e2, e2.msg.sender, silo0) >=
        token0.allowance(e1, e1.msg.sender, silo0)
    );
    /// At least as much balance as first `env`
    require token0.balanceOf(e2, e2.msg.sender) >= token0.balanceOf(e1, e1.msg.sender);
}

// ---- Rules ------------------------------------------------------------------
// use builtin rule sanity;

/// @title For testing the setup
rule sanityWithSetup_borrow() {
    calldataarg args;
    env e; 
    configForEightTokensSetupRequirements();
    nonSceneAddressRequirements(e.msg.sender);
    silosTimestampSetupRequirements(e);
    silo0.borrow(e, args);
    satisfy true;
}

/// @title If a user may deposit some amount, any other user also may
/// @property user-access
rule RA_anyone_may_deposit(env e1, env e2, address recipient, uint256 amount) {
    /// Assuming same context (time and value).
    require e1.block.timestamp == e2.block.timestamp;
    require e1.msg.value == e2.msg.value;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e1);
    silosTimestampSetupRequirements(e2);
    configForEightTokensSetupRequirements();
    nonSceneAddressRequirements(e1.msg.sender);
    nonSceneAddressRequirements(e2.msg.sender);
    totalSuppliesMoreThanBalances(e1.msg.sender,e2.msg.sender);
    require to_mathint(silo0.totalSupply()) > amount; 

    // Conditions necessary that `e2` will not revert if `e1` did not
    requireSecondEnvAtLeastAsFirst(e1, e2);

    storage initState = lastStorage;
    deposit(e1, amount, recipient);
    deposit@withrevert(e2, amount, recipient) at initState;

    assert e2.msg.sender != 0 => !lastReverted;
}

/// @title If one user can repay some borrower's debt, any other user also can
/// @property user-access
rule RA_anyone_may_repay(env e1, env e2, uint256 amount, address borrower) {
    /// Assuming same context (time and value).
    require e1.block.timestamp == e2.block.timestamp;
    require e1.msg.value == e2.msg.value;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e1);
    silosTimestampSetupRequirements(e2);

    // Conditions necessary that `e2` will not revert if `e1` did not
    requireSecondEnvAtLeastAsFirst(e1, e2);

    storage initState = lastStorage;
    repay(e1, amount, borrower);
    repay@withrevert(e2, amount, borrower) at initState;

    assert e2.msg.sender != 0 => !lastReverted;
}


/// @title The deposit recipient is not discriminated
/// @property user-access
rule RA_deposit_recipient_is_not_restricted(address user1, address user2, uint256 amount) {
    env e;

    storage initState = lastStorage;
    deposit(e, amount, user1);
    deposit@withrevert(e, amount, user2) at initState;

    assert user2 !=0 => !lastReverted;
}
