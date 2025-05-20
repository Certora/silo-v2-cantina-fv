
import "../setup/CompleteSiloSetup.spec";
import "../setup/summaries/siloconfig_dispatchers.spec";
import "../setup/StorageHooks/hook_all.spec"; 
import "../setup/ERC20/erc20cvl.spec";
import "../setup/Helpers.spec";

import "unresolved.spec";

import "../simplifications/SiloMathLib_SAFE.spec";
import "../simplifications/SiloMathLib_UNSAFE.spec";
import "../simplifications/SiloStdLib_UNSAFE.spec";
import "../simplifications/ignore_hooks_simplification.spec";
import "../simplifications/zero_compound_interest.spec";

// invariant maxRedeem_leq_balance(env e, address user)
//     silo0.maxRedeem(e,user) <= silo0.balanceOf(user)
//   { preserved
//         { 
//             configForEightTokensSetupRequirements();
//             nonSceneAddressRequirements(e.msg.sender);
//             silosTimestampSetupRequirements(e);
//         } 
// }

methods{
    function _.beforeAction(address, uint256, bytes) external => NONDET;
    function _.afterAction(address, uint256, bytes) external => NONDET;
    function _.isSolvent(address) external => DISPATCHER(true);

    function _.quote(address) external => NONDET;
    function _.quote(uint256 _baseAmount, address _baseToken) external => NONDET; 
}


// the maxQ_reverts rules check that
// the method Q always reverts when called with more than maxQ
rule HLP_MaxDeposit_reverts(env e, address receiver)
{
    SafeAssumptions_withInvariants(e, receiver);
    synchronous_siloStorage_erc20cvl(e);
    
    uint256 maxAssets = maxDeposit(e, receiver);
    uint256 assets;
    uint256 sharesReceived = deposit@withrevert(e, assets, receiver);
    assert  assets > maxAssets => lastReverted;
}

rule HLP_MaxMint_reverts(env e, address receiver)
{
    SafeAssumptions_withInvariants(e, receiver);
    synchronous_siloStorage_erc20cvl(e);
    
    uint256 maxShares = maxMint(e, receiver);
    uint256 shares;
    uint256 assetsReceived = mint@withrevert(e, shares, receiver);
    assert shares > maxShares => lastReverted;
}

// result of maxWithdraw() should never be more than liquidity of the Silo
rule maxWithdraw_noGreaterThanLiquidity(env e)
{
    SafeAssumptionsEnv_withInvariants(e);
    synchronous_siloStorage_erc20cvl(e);
    
    // uint totalCollateral = silo0.getTotalAssetsStorage(ISilo.AssetType.Collateral);
    // uint totalDebt = silo0.getTotalAssetsStorage(ISilo.AssetType.Debt);
    //mathint liquidity = max(0, totalCollateral - totalDebt);
    uint liquidity = getLiquidity(e);

    uint256 maxAssets = maxWithdraw(e, e.msg.sender);
    
    assert maxAssets <= liquidity;
}

/// @dev rule 86 :
//       `repay()` should not be able to repay more than `maxRepay()`
/// @status 
// rule HLP_MaxRepay_reverts(env e, address borrower)
// {
//     SafeAssumptions_withInvariants(e, borrower);
//     nonSceneAddressRequirements(borrower);
//     disableAccrueInterest(e);
//     synchronous_siloStorage_erc20cvl(e);

    
//     storage initState = lastStorage; // To Avoide the accruing interest between the two calls.

//     uint256 maxAssets = maxRepay(e, borrower);
//     uint256 assets;
//     require assets > maxAssets;
//     uint256 sharesReceived = repay@withrevert(e, assets, borrower);
//     assert lastReverted;
// }
/// @dev rule 84 :
//       `maxRepay()` should never return more than `totalAssets[AssetType.Debt]` plus interest
/// @status 
// rule maxRepay_noGreaterThanTotalDebt(env e, address borrower)
// {
//     SafeAssumptions_withInvariants(e, borrower);
//     nonSceneAddressRequirements(borrower);
//     disableAccrueInterest(e);
//     synchronous_siloStorage_erc20cvl(e);
//     //loadingThevalue into ghost 
//     silo0.getTotalAssetsStorage(ISilo.AssetType.Debt);

//     uint256 maxAssets = maxRepay(e, borrower);
//     uint256 totalDebtAssets  = require_uint256(ghostTotalAssets[silo0][DEBT_ASSET_TYPE()]);
//     //silo0.getDebtAssets(e);

//     assert maxAssets <= totalDebtAssets;
// }

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