/* Integrity of preview functions */

import "../setup/CompleteSiloSetup.spec";
import "../setup/previewIntegrity_invariant.spec";
import "../setup/ERC20/erc20cvl.spec";
import "../setup/summaries/siloconfig_dispatchers.spec";



import "../simplifications/priceOracle_UNSAFE.spec";
import "../simplifications/ignore_hooks_simplification.spec";
import "../simplifications/SiloMathLib_SAFE.spec";
import "../simplifications/SiloMathLib_UNSAFE.spec";
import "../simplifications/zero_compound_interest.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";

import "unresolved.spec";

// ---- Methods and Invariants -------------------------------------------------

methods {
    function _.beforeAction(address, uint256, bytes) external => NONDET;
    function _.afterAction(address, uint256, bytes) external => NONDET;
}

// ---- Rules ------------------------------------------------------------------

/// @status Done
rule HLP_PreviewMintCorrectness_strict(address receiver)
{
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    totalSuppliesMoreThanBalances(receiver, silo0);
    
    requireInvariant assetsZeroInterestRateTimestampZero(e) ;

    uint256 shares;
    uint256 assetsReported = previewMint(e, shares);
    uint256 assetsPaid = mint(e, shares, receiver);

    assert assetsReported == assetsPaid;
}

/// @status Done
rule HLP_PreviewRedeemCorrectness(address receiver)
{
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    totalSuppliesMoreThanBalances(receiver, silo0);

    requireInvariant assetsZeroInterestRateTimestampZero(e) ;
    
    uint256 shares;
    uint256 assetsReported = previewRedeem(e, shares);
    uint256 assetsReceived = redeem(e, shares, receiver, e.msg.sender);

    assert assetsReported == assetsReceived;
}

/// @status Done
rule HLP_PreviewDepositCorrectness(address receiver)
{
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    totalSuppliesMoreThanBalances(receiver, silo0);

    requireInvariant assetsZeroInterestRateTimestampZero(e) ;
    
    uint256 assets;
    uint256 sharesReported = previewDeposit(e, assets);
    uint256 sharesReceived = deposit(e, assets, receiver);

    assert sharesReported == sharesReceived;
}

/// @status Done
rule HLP_PreviewWithdrawCorrectness_strict(address receiver)
{
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    totalSuppliesMoreThanBalances(receiver, silo0);

    requireInvariant assetsZeroInterestRateTimestampZero(e) ;
    
    uint256 assets;
    uint256 sharesReported = previewWithdraw(e, assets);
    uint256 sharesPaid = withdraw(e, assets, receiver, e.msg.sender);
    assert sharesPaid == sharesReported;
}

/// @status Done
rule HLP_PreviewBorrowCorrectness_strict(address receiver)
{
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    totalSuppliesMoreThanBalances(receiver, silo0);

    requireInvariant assetsZeroInterestRateTimestampZero(e) ;
    
    // bool sameAsset;
    uint256 assets;
    uint256 debtSharesReported = previewBorrow(e, assets);
    uint256 debtSharesReceived = borrow(e, assets, receiver, e.msg.sender); // , sameAsset);
    assert debtSharesReported == debtSharesReceived;
}

/// @status Done
rule HLP_PreviewBorrowSharesCorrectness(address receiver)
{
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    totalSuppliesMoreThanBalances(receiver, silo0);

    requireInvariant assetsZeroInterestRateTimestampZero(e) ;
    
    // bool sameAsset;
    uint256 shares;
    uint256 assetsReported = previewBorrowShares(e, shares);
    uint256 assetsReceived = borrowShares(e, shares, receiver, e.msg.sender); // , sameAsset);
    assert assetsReported == assetsReceived;
}

/// @status Done
rule HLP_PreviewRepaySharesCorrectness(address receiver)
{
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    totalSuppliesMoreThanBalances(receiver, silo0);

    requireInvariant assetsZeroInterestRateTimestampZero(e) ;
    
    uint256 shares;
    uint256 assetsReported = previewRepayShares(e, shares);
    uint256 assetsPaid = repayShares(e, shares, receiver);
    assert assetsReported >= assetsPaid;
}

/// @status Done
rule HLP_PreviewRepayCorrectness(address receiver)
{
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    totalSuppliesMoreThanBalances(receiver, silo0);

    requireInvariant assetsZeroInterestRateTimestampZero(e) ;
    
    uint256 assets;
    uint256 sharesReported = previewRepay(e, assets);
    uint256 sharesPaid = repay(e, assets, receiver);
    assert sharesReported >= sharesPaid;
}


/// @status Done
rule HLP_Preview_Deposit_ConvertToShares(address receiver)
{
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    totalSuppliesMoreThanBalances(receiver, silo0);

    requireInvariant assetsZeroInterestRateTimestampZero(e) ;
    
    uint256 assets;
    uint256 sharesReported = previewDeposit(e, assets);
    uint256 sharesReceived = deposit(e, assets, receiver);
    uint256 sharesCalculated = convertToShares(e,assets);

    assert ((sharesReported == sharesReceived) &&
     (sharesReported == sharesCalculated) && (sharesReceived == sharesCalculated));
}

/// @status Done
rule HLP_Preview_Mint_ConvertToAssets(address receiver)
{
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    totalSuppliesMoreThanBalances(receiver, silo0);
    
    requireInvariant assetsZeroInterestRateTimestampZero(e) ;

    uint256 shares;
    uint256 assetsReported = previewMint(e, shares);
    uint256 assetsPaid = mint(e, shares, receiver);
    uint256 assetsCalculated = convertToAssets(e,shares);


    assert assetsReported == assetsPaid &&
           assetsReported == assetsCalculated &&
           assetsPaid     == assetsCalculated;
}