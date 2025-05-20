/* Third party protection rules (i.e. unrelated addresses are not affected)  */

import "../setup/CompleteSiloSetup.spec";
import "../setup/summaries/tokens_dispatchers.spec";
import "../setup/summaries/siloconfig_dispatchers.spec";

import "../simplifications/ignore_hooks_simplification.spec";
import "../simplifications/zero_compound_interest.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";

methods {
    // ---- `ISiloOracle` ------------------------------------------------------
    // NOTE: Since `beforeQuote` is not a view function, strictly speaking this is unsound.
    function _.beforeQuote(address) external => NONDET DELETE;
    function _.beforeAction(address, uint256, bytes) external => NONDET;
    function _.afterAction(address, uint256, bytes) external => NONDET;
}

// ---- Rules ------------------------------------------------------------------

// ---- Deposit/Mint -----------------------------------------------------------

/// @title Deposit doesn't affect others
/// @property third-party
/// @status done
rule HLP_DepositDoesntAffectOthers(address receiver, address other, uint256 assets) {

    env e;
    require other != receiver && other != e.msg.sender;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // `other` is not one of the contracts in the scene
    nonSceneAddressRequirements(other);

    mathint balanceTokenBefore = token0.balanceOf(other);
    mathint balanceSharesBefore = shareDebtToken0.balanceOf(other);
    mathint balanceCollateralBefore = silo0.balanceOf(other);
    mathint balanceProtectedCollateralBefore = shareProtectedCollateralToken0.balanceOf(other);

    mathint shares = deposit(e, assets, receiver);

    mathint balanceTokenAfter = token0.balanceOf(other);
    mathint balanceSharesAfter = shareDebtToken0.balanceOf(other);
    mathint balanceCollateralAfter = silo0.balanceOf(other);
    mathint balanceProtectedCollateralAfter = shareProtectedCollateralToken0.balanceOf(other);

    assert balanceTokenBefore == balanceTokenAfter;
    assert balanceSharesBefore == balanceSharesAfter;
    assert balanceCollateralBefore == balanceCollateralAfter;
    assert balanceProtectedCollateralBefore == balanceProtectedCollateralAfter;
}


/// @title Mint doesn't affect others
/// @property third-party
/// @status done
rule HLP_MintDoesntAffectOthers(address receiver, address other, uint256 shares) {

    env e;
    require other != receiver && other != e.msg.sender;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // `other` is not one of the contracts in the scene
    nonSceneAddressRequirements(other);

    mathint balanceTokenBefore = token0.balanceOf(other);
    mathint balanceSharesBefore = shareDebtToken0.balanceOf(other);
    mathint balanceCollateralBefore = silo0.balanceOf(other);
    mathint balanceProtectedCollateralBefore = shareProtectedCollateralToken0.balanceOf(other);

    mathint assets = mint(e, shares, receiver);

    mathint balanceTokenAfter = token0.balanceOf(other);
    mathint balanceSharesAfter = shareDebtToken0.balanceOf(other);
    mathint balanceCollateralAfter = silo0.balanceOf(other);
    mathint balanceProtectedCollateralAfter = shareProtectedCollateralToken0.balanceOf(other);

    assert balanceTokenBefore == balanceTokenAfter;
    assert balanceSharesBefore == balanceSharesAfter;
    assert balanceCollateralBefore == balanceCollateralAfter;
    assert balanceProtectedCollateralBefore == balanceProtectedCollateralAfter;
}

// ---- Redeem/Withdraw --------------------------------------------------------

/// @title Redeem doesn't affect others
/// @property third-party
/// @status done
rule HLP_RedeemDoesntAffectOthers(address receiver, address other, uint256 shares) {

    env e;
    require other != receiver && other != e.msg.sender;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // `other` is not one of the contracts in the scene
    nonSceneAddressRequirements(other);

    mathint balanceTokenBefore = token0.balanceOf(other);
    mathint balanceSharesBefore = shareDebtToken0.balanceOf(other);
    mathint balanceCollateralBefore = silo0.balanceOf(other);
    mathint balanceProtectedCollateralBefore = shareProtectedCollateralToken0.balanceOf(other);

    mathint assets = redeem(e, shares, receiver, e.msg.sender);

    mathint balanceTokenAfter = token0.balanceOf(other);
    mathint balanceSharesAfter = shareDebtToken0.balanceOf(other);
    mathint balanceCollateralAfter = silo0.balanceOf(other);
    mathint balanceProtectedCollateralAfter = shareProtectedCollateralToken0.balanceOf(other);

    assert balanceTokenBefore == balanceTokenAfter;
    assert balanceSharesBefore == balanceSharesAfter;
    assert balanceCollateralBefore == balanceCollateralAfter;
    assert balanceProtectedCollateralBefore == balanceProtectedCollateralAfter;
}


// ---- Repay ------------------------------------------------------------------

/// @title Repay doesn't affect others
/// @property third-party
/// @status done
rule HLP_repayDoesntAffectOthers(address receiver, address other, uint256 assets) {
    env e;
    require other != receiver && other != e.msg.sender;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // `other` is not one of the contracts in the scene
    nonSceneAddressRequirements(other);

    mathint balanceTokenBefore = token0.balanceOf(other);
    mathint balanceSharesBefore = shareDebtToken0.balanceOf(other);
    mathint balanceCollateralBefore = silo0.balanceOf(other);
    mathint balanceProtectedCollateralBefore = shareProtectedCollateralToken0.balanceOf(other);

    mathint shares = repay(e, assets, e.msg.sender);

    mathint balanceTokenAfter = token0.balanceOf(other);
    mathint balanceSharesAfter = shareDebtToken0.balanceOf(other);
    mathint balanceCollateralAfter = silo0.balanceOf(other);
    mathint balanceProtectedCollateralAfter = shareProtectedCollateralToken0.balanceOf(other);

    assert balanceTokenBefore == balanceTokenAfter;
    assert balanceSharesBefore == balanceSharesAfter;
    assert balanceCollateralBefore == balanceCollateralAfter;
    assert balanceProtectedCollateralBefore == balanceProtectedCollateralAfter;
}


/// @title Repay shares doesn't affect others
/// @property third-party
/// @status done
rule HLP_repaySharesDoesntAffectOthers(address receiver, address other, uint256 shares) {

    env e;
    require other != receiver && other != e.msg.sender;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // `other` is not one of the contracts in the scene
    nonSceneAddressRequirements(other);

    mathint balanceTokenBefore = token0.balanceOf(other);
    mathint balanceSharesBefore = shareDebtToken0.balanceOf(other);
    mathint balanceCollateralBefore = silo0.balanceOf(other);
    mathint balanceProtectedCollateralBefore = shareProtectedCollateralToken0.balanceOf(other);

    mathint assets = repayShares(e, shares, e.msg.sender);

    mathint balanceTokenAfter = token0.balanceOf(other);
    mathint balanceSharesAfter = shareDebtToken0.balanceOf(other);
    mathint balanceCollateralAfter = silo0.balanceOf(other);
    mathint balanceProtectedCollateralAfter = shareProtectedCollateralToken0.balanceOf(other);

    assert balanceTokenBefore == balanceTokenAfter;
    assert balanceSharesBefore == balanceSharesAfter;
    assert balanceCollateralBefore == balanceCollateralAfter;
    assert balanceProtectedCollateralBefore == balanceProtectedCollateralAfter;
}
