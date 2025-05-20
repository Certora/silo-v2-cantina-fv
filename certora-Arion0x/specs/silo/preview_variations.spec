/* Integrity of preview functions */

import "../setup/CompleteSiloSetup.spec";
import "../setup/summaries/tokens_dispatchers.spec";
import "../setup/summaries/siloconfig_dispatchers.spec";

import "unresolved.spec";

import "../simplifications/SiloMathLib_SAFE.spec";
import "../simplifications/SiloMathLib_UNSAFE.spec";
import "../simplifications/priceOracle_UNSAFE.spec";
import "../simplifications/ignore_hooks_simplification.spec";
import "../simplifications/zero_compound_interest.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";

// ---- Methods and Invariants -------------------------------------------------

methods{
    function _.beforeAction(address, uint256, bytes) external => NONDET;
    function _.afterAction(address, uint256, bytes) external => NONDET;
}

// ---- Rules ------------------------------------------------------------------


rule HLP_PreviewMintCallerVariation()
{
    env e1;
    env e2;
    require e1.block.timestamp == e2.block.timestamp;
    require e1.msg.sender != e2.msg.sender;

    storage initial = lastStorage;


    uint256 shares;
    uint256 assetsReported1 = previewMint(e1, shares) at initial;
    uint256 assetsReported2 = previewMint(e2, shares) at initial;

    assert assetsReported1 == assetsReported2;
}


rule HLP_PreviewRedeemCallerVariation(address receiver)
{
    env e1;
    env e2;
    require e1.block.timestamp == e2.block.timestamp;
    require e1.msg.sender != e2.msg.sender;

    storage initial = lastStorage;
    
    uint256 shares;
    uint256 assetsReported1 = previewRedeem(e1, shares) at initial;
    uint256 assetsReported2 = previewRedeem(e2, shares) at initial;

    assert assetsReported1 == assetsReported2;
}


rule HLP_PreviewDepositCallerVariation()
{
    env e1;
    env e2;
    require e1.block.timestamp == e2.block.timestamp;
    require e1.msg.sender != e2.msg.sender;

    storage initial = lastStorage;
    
    uint256 assets;
    uint256 sharesReported1 = previewDeposit(e1, assets) at initial;
    uint256 sharesReported2 = previewDeposit(e2, assets) at initial;

    assert sharesReported1 == sharesReported2;
}

rule HLP_PreviewWithdrawCallerVariation()
{
    env e1;
    env e2;
    require e1.block.timestamp == e2.block.timestamp;
    require e1.msg.sender != e2.msg.sender;

    storage initial = lastStorage;
    
    uint256 assets;
    uint256 sharesReported1 = previewWithdraw(e1, assets) at initial;
    uint256 sharesReported2 = previewWithdraw(e2, assets) at initial;

    assert sharesReported1 == sharesReported2;
}


rule HLP_PreviewBorrowCallerVariation()
{
    env e1;
    env e2;
    require e1.block.timestamp == e2.block.timestamp;
    require e1.msg.sender != e2.msg.sender;

    storage initial = lastStorage;
    
    uint256 assets;
    uint256 debtSharesReported1 = previewBorrow(e1, assets) at initial;
    uint256 debtSharesReported2 = previewBorrow(e2, assets) at initial;

    assert debtSharesReported1 == debtSharesReported2;
}


rule HLP_PreviewBorrowSharesCallerVariation()
{
    env e1;
    env e2;
    require e1.block.timestamp == e2.block.timestamp;
    require e1.msg.sender != e2.msg.sender;

    storage initial = lastStorage;
    
    uint256 shares;
    uint256 assetsReported1 = previewBorrowShares(e1, shares) at initial;
    uint256 assetsReported2 = previewBorrowShares(e2, shares) at initial;

    assert assetsReported1 == assetsReported2;
}

rule HLP_PreviewRepaySharesCallerVariation()
{
    env e1;
    env e2;
    require e1.block.timestamp == e2.block.timestamp;
    require e1.msg.sender != e2.msg.sender;

    storage initial = lastStorage;
    
    uint256 shares;
    uint256 assetsReported1 = previewRepayShares(e1, shares) at initial;
    uint256 assetsReported2 = previewRepayShares(e2, shares) at initial;

    assert assetsReported1 == assetsReported2;
}