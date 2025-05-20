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

// ---- Transition -------------------------------------------------------------

/// @title Transitioning collateral between protected an borrowable doesn't affect others
/// @property third-party
/// @status done
rule HLP_transitionCollateralDoesntAffectOthers(
    address receiver,
    address other,
    uint256 shares,
    ISilo.CollateralType anyType
) {
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

    mathint assets = transitionCollateral(e, shares, e.msg.sender, anyType);

    mathint balanceTokenAfter = token0.balanceOf(other);
    mathint balanceSharesAfter = shareDebtToken0.balanceOf(other);
    mathint balanceCollateralAfter = silo0.balanceOf(other);
    mathint balanceProtectedCollateralAfter = shareProtectedCollateralToken0.balanceOf(other);

    assert balanceTokenBefore == balanceTokenAfter;
    assert balanceSharesBefore == balanceSharesAfter;
    assert balanceCollateralBefore == balanceCollateralAfter;
    assert balanceProtectedCollateralBefore == balanceProtectedCollateralAfter;
}

// ---- Borrow -----------------------------------------------------------------

/// @title Borrow doesn't affect others
/// @property third-party
/// @status done
rule HLP_borrowDoesntAffectOthers(address receiver, address other, uint256 assets) {
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

    mathint shares = borrow(e, assets, receiver, e.msg.sender);

    mathint balanceTokenAfter = token0.balanceOf(other);
    mathint balanceSharesAfter = shareDebtToken0.balanceOf(other);
    mathint balanceCollateralAfter = silo0.balanceOf(other);
    mathint balanceProtectedCollateralAfter = shareProtectedCollateralToken0.balanceOf(other);

    assert balanceTokenBefore == balanceTokenAfter;
    assert balanceSharesBefore == balanceSharesAfter;
    assert balanceCollateralBefore == balanceCollateralAfter;
    assert balanceProtectedCollateralBefore == balanceProtectedCollateralAfter;
}


/// @title Borrow same asset doesn't affect others
/// @property third-party
/// @status done
rule HLP_borrowSameAssetDoesntAffectOthers(address receiver, address other, uint256 assets) {
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

    mathint shares = borrowSameAsset(e, assets, receiver, e.msg.sender);

    mathint balanceTokenAfter = token0.balanceOf(other);
    mathint balanceSharesAfter = shareDebtToken0.balanceOf(other);
    mathint balanceCollateralAfter = silo0.balanceOf(other);
    mathint balanceProtectedCollateralAfter = shareProtectedCollateralToken0.balanceOf(other);

    assert balanceTokenBefore == balanceTokenAfter;
    assert balanceSharesBefore == balanceSharesAfter;
    assert balanceCollateralBefore == balanceCollateralAfter;
    assert balanceProtectedCollateralBefore == balanceProtectedCollateralAfter;
}


/// @title Borrow shares doesn't affect others
/// @property third-party
/// @status done
rule HLP_borrowSharesDoesntAffectOthers(address receiver, address other, uint256 shares) {

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

    mathint assets = borrowShares(e, shares, receiver, e.msg.sender);

    mathint balanceTokenAfter = token0.balanceOf(other);
    mathint balanceSharesAfter = shareDebtToken0.balanceOf(other);
    mathint balanceCollateralAfter = silo0.balanceOf(other);
    mathint balanceProtectedCollateralAfter = shareProtectedCollateralToken0.balanceOf(other);

    assert balanceTokenBefore == balanceTokenAfter;
    assert balanceSharesBefore == balanceSharesAfter;
    assert balanceCollateralBefore == balanceCollateralAfter;
    assert balanceProtectedCollateralBefore == balanceProtectedCollateralAfter;
}


/// @title Withdraw doesn't affect others
/// @property third-party
/// @status done
rule HLP_WithdrawDoesntAffectOthers(address receiver, address other, uint256 assets) {
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

    mathint shares = withdraw(e, assets, receiver, e.msg.sender);

    mathint balanceTokenAfter = token0.balanceOf(other);
    mathint balanceSharesAfter = shareDebtToken0.balanceOf(other);
    mathint balanceCollateralAfter = silo0.balanceOf(other);
    mathint balanceProtectedCollateralAfter = shareProtectedCollateralToken0.balanceOf(other);

    assert balanceTokenBefore == balanceTokenAfter;
    assert balanceSharesBefore == balanceSharesAfter;
    assert balanceCollateralBefore == balanceCollateralAfter;
    assert balanceProtectedCollateralBefore == balanceProtectedCollateralAfter;
}
