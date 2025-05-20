/* Integrity of main methods */

import "../setup/summaries/siloconfig_dispatchers.spec";
import "../setup/CompleteSiloSetup.spec";
import "../setup/ERC20/erc20cvl.spec";


import "../simplifications/priceOracle_UNSAFE.spec";
import "../simplifications/SiloMathLib_SAFE.spec";
import "../simplifications/SiloMathLib_UNSAFE.spec";
import "../simplifications/ignore_hooks_simplification.spec";
import "../simplifications/zero_compound_interest.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";
import "../simplifications/Silo_isSolvent_ghost_UNSAFE.spec";

import "unresolved.spec";


methods {
    function _.isSolvent(address) external => DISPATCHER(true);
    function _.matchAction(uint256 _action, uint256 _expectedHook) internal => ALWAYS(false);
    function _.beforeAction(address, uint256, bytes) external => NONDET;
    function _.afterAction(address, uint256, bytes) external => NONDET;
}



// ---- Deposit/Redeem -Rounding-------------------------------------------------------

rule HLP_RedeemAfterDeposit(address receiver,uint256 assets){
    env e;
    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver and msg.sender is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    nonSceneAddressRequirements(e.msg.sender);

    totalSuppliesMoreThanBalances(receiver, silo0);

    SafeAssumptions_withInvariants(e,receiver);
    synchronous_siloStorage_erc20cvl(e);

    mathint shares = deposit(e, assets, receiver);
    mathint assets_redeem = redeem(e, require_uint256(shares), receiver, receiver);

    assert assets_redeem <= to_mathint(assets);

}

rule HLP_DepositAfterRedeem(address receiver,uint256 shares){
    env e;
    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver and msg.sender is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    nonSceneAddressRequirements(e.msg.sender);

    totalSuppliesMoreThanBalances(receiver, silo0);

    SafeAssumptions_withInvariants(e,receiver);
    synchronous_siloStorage_erc20cvl(e);

    mathint assets = redeem(e, shares, receiver, receiver);
    mathint shares_deposit = deposit(e, require_uint256(assets), receiver);

    assert shares_deposit <= to_mathint(shares);
}


// ---- Withdraw/Mint -Rounding----------------------------------------------------------

rule HLP_MintAfterWithdraw(address receiver,uint256 assets){
    env e;
    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);

    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    nonSceneAddressRequirements(e.msg.sender);

    totalSuppliesMoreThanBalances(receiver, silo0);

    SafeAssumptions_withInvariants(e,receiver);
    synchronous_siloStorage_erc20cvl(e);

    uint256 shares = withdraw(e, assets, receiver, receiver);
    uint256 assets_mint = mint(e, require_uint256(shares), receiver);

    assert assets_mint <= assets;

}

rule HLP_WithdrawAfterMint(address receiver,uint256 shares){
    env e;
    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    nonSceneAddressRequirements(e.msg.sender);

    totalSuppliesMoreThanBalances(receiver, silo0);

    SafeAssumptions_withInvariants(e,receiver);
    synchronous_siloStorage_erc20cvl(e);

    uint256 assets = mint(e, shares, receiver);
    uint256 shares_withdraw = withdraw(e, require_uint256(assets), receiver, receiver);

    assert shares_withdraw <= shares;

}

// ---- Withdraw/Deposit -Rounding----------------------------------------------------------

// rule HLP_WithdrawAfterDeposit(address receiver,uint256 assets){
//     // Block time-stamp >= interest rate time-stamp
//     silosTimestampSetupRequirements(e);

//     // receiver is not one of the contracts in the scene
//     nonSceneAddressRequirements(receiver);
//     totalSuppliesMoreThanBalances(receiver, silo0);

//     mathint shares = deposit(e, assets, receiver);

//     mathint shares = withdraw(e, assets, receiver, receiver);

//     assert assets_mint >= assets;

// }

// ---- Redeem/Mint -Rounding----------------------------------------------------------


rule HLP_RedeemAfterMint(address receiver,uint256 shares){
    env e;
    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver and msg.sender is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    nonSceneAddressRequirements(e.msg.sender);

    totalSuppliesMoreThanBalances(receiver, silo0);

    SafeAssumptions_withInvariants(e,receiver);
    synchronous_siloStorage_erc20cvl(e);

    mathint assets = mint(e, shares, receiver);
    mathint assets_redeem = redeem(e, require_uint256(assets), receiver, receiver);

    assert assets >= assets_redeem;

}

rule HLP_MintAfterRedeem(address receiver,uint256 assets){
    env e;
    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver and msg.sender is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    nonSceneAddressRequirements(e.msg.sender);
    totalSuppliesMoreThanBalances(receiver, silo0);

    SafeAssumptions_withInvariants(e,receiver);
    synchronous_siloStorage_erc20cvl(e);

    mathint assets_redeem = redeem(e, assets, receiver, receiver);
    uint256 shares_redeem = convertToShares(e,require_uint256(assets_redeem));
    mathint assets_mint = mint(e,shares_redeem, receiver);

    assert assets_mint <= assets;

}

// ---- borrow/repay -Rounding----------------------------------------------------------

//timeout
// rule userDontGainAssetAfterBorrowing(env e,uint256 _assets, address _receiver){
    
//     nonSceneAddressRequirements(_receiver);
//     nonSceneAddressRequirements(e.msg.sender);
//     configForEightTokensSetupRequirements();
//     SafeAssumptions_withInvariants(e,_receiver);
//     synchronous_siloStorage_erc20cvl(e);

//     uint256 debtBefore = balanceOfCVL(shareDebtToken0,_receiver);
//     uint256 balanceBefore = balanceOfCVL(token0,_receiver);
    
//     uint256 borrowShares = borrow(e,_assets,_receiver,_receiver);

//     uint256 repayShares = repay(e,_assets,_receiver);
//     // uint256 repayAssets = convertToAssets(e,repayShares);

//     uint256 debtAfter = balanceOfCVL(shareDebtToken0,_receiver);
//     uint256 balanceAfter = balanceOfCVL(token0,_receiver);

//     // assert repayAssets <= _assets;
//     assert  debtAfter > debtBefore => balanceBefore >= balanceAfter;
// }

rule userDontGainAssetAfterBorrowing2(env e,uint256 _assets, address _receiver){
    
    nonSceneAddressRequirements(_receiver);
    nonSceneAddressRequirements(e.msg.sender);
    SafeAssumptions_withInvariants(e,_receiver);
    synchronous_siloStorage_erc20cvl(e);

    uint256 debtBefore = balanceOfCVL(shareDebtToken0,_receiver);
    uint256 balanceBefore = balanceOfCVL(token0,_receiver);
    
    uint256 borrowShares = borrow(e,_assets,_receiver,_receiver);

    uint256 repayAssets = repayShares(e,borrowShares,_receiver);

    uint256 debtAfter = balanceOfCVL(shareDebtToken0,_receiver);
    uint256 balanceAfter = balanceOfCVL(token0,_receiver);

    assert repayAssets <= _assets;
    // assert debtBefore <= debtAfter => balanceBefore >= balanceAfter;
}

function synchronous_siloStorage_erc20cvl(env e){
    mathint totalDebt;
    mathint totalCollateral;
    mathint totalProtected;
    totalDebt = silo0.getTotalAssetsStorage(ISilo.AssetType.Debt); 
    totalCollateral,totalProtected = silo0.getCollateralAndProtectedTotalsStorage(e); 
    require totalDebt == totalSupplyCVL(shareDebtToken0);
    require totalCollateral == totalSupplyCVL(silo0);
    require totalProtected  == totalSupplyCVL(shareProtectedCollateralToken0);
}