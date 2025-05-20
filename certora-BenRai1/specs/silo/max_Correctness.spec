import "../setup/CompleteSiloSetup.spec";
import "unresolved.spec";
//import "../simplifications/SiloMathLib_SAFE.spec";
//import "../simplifications/Oracle_quote_one_UNSAFE.spec";
import "../simplifications/SimplifiedGetCompoundInterestRateAndUpdate_SAFE.spec";

// the maxQ_reverts rules check that
// the method Q always reverts when called with more than maxQ
rule HLP_MaxDeposit_reverts(env e, address receiver)
{
    SafeAssumptions_withInvariants(e, receiver);
    
    uint256 maxAssets = maxDeposit(e, receiver);
    uint256 assets;
    require assets > maxAssets;
    uint256 sharesReceived = deposit@withrevert(e, assets, receiver);
    assert lastReverted;
}

// rule HLP_MaxRepayShares_reverts(env e, address borrower)
// {
//     SafeAssumptions_withInvariants(e, borrower);
    
//     uint maxShares = maxRepayShares(e, borrower);
//     uint256 shares;
//     require shares > maxShares;
//     mathint assets = repayShares@withrevert(e, shares, borrower);

//     assert lastReverted;
// }

// repaying with maxRepay() value should burn all user share debt token balance
rule maxRepay_burnsAllDebt(env e, address user)
{
    SafeAssumptions_withInvariants(e, user);

    uint maxAssets = maxRepay(e, user);
    uint256 shares = repay(e, maxAssets, user);    // this did not revert
    uint debtAfter = shareDebtToken0.balanceOf(user);

    assert debtAfter == 0;
}

// result of maxWithdraw() should never be more than liquidity of the Silo
rule maxWithdraw_noGreaterThanLiquidity(env e)
{
    SafeAssumptionsEnv_withInvariants(e);
    
    uint totalCollateral = silo0.getTotalAssetsStorage(ISilo.AssetType.Collateral);
    uint totalDebt = silo0.getTotalAssetsStorage(ISilo.AssetType.Debt);
    //mathint liquidity = max(0, totalCollateral - totalDebt);
    uint liquidity = getLiquidity(e);

    uint256 maxAssets = maxWithdraw(e, e.msg.sender);
    
    assert maxAssets <= liquidity;
}
