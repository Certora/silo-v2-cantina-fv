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
