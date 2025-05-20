/* Integrity of main methods */

import "../setup/CompleteSiloSetup.spec";
import "../setup/ERC20/erc20cvl.spec";
import "../setup/StorageHooks/hook_all.spec";
import "../setup/summaries/siloconfig_dispatchers.spec";

import "../simplifications/priceOracle_UNSAFE.spec";
import "../simplifications/SiloMathLib_SAFE.spec";
import "../simplifications/SiloMathLib_UNSAFE.spec";
import "../simplifications/SiloStdLib_UNSAFE.spec";
import "../simplifications/zero_compound_interest.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";

methods {

    function _.beforeAction(address, uint256, bytes) external => NONDET;
    function _.afterAction(address, uint256, bytes) external => NONDET;
    // ---- `ISiloOracle` ------------------------------------------------------
    // NOTE: Since `beforeQuote` is not a view function, strictly speaking this is unsound.
    // function _.beforeQuote(address) external => NONDET DELETE;
}


rule previewRedeemEquivalence(){
    env e;
    
    uint256 shares;
    uint256 previewERC4625 = previewRedeem(e, shares);
    uint256 previewISilo = previewRedeem(e,shares,ISilo.CollateralType.Collateral);

    assert previewERC4625 == previewISilo;
}

rule previewDepositEquivalence(){
    env e;

    uint256 assets;
    uint256 previewERC4625 = previewDeposit(e, assets);
    uint256 previewISilo = previewDeposit(e,assets,ISilo.CollateralType.Collateral);

    assert previewERC4625 == previewISilo;
}

rule previewMintEquivalence(){
    env e;
    
    uint256 shares;
    uint256 previewERC4625 = previewMint(e, shares);
    uint256 previewISilo = previewMint(e,shares,ISilo.CollateralType.Collateral);

    assert previewERC4625 == previewISilo;
}

rule previewWithdrawEquivalence(){
    env e;
    
    uint256 assets;
    uint256 previewERC4625 = previewWithdraw(e, assets);
    uint256 previewISilo = previewWithdraw(e,assets,ISilo.CollateralType.Collateral);

    assert previewERC4625 == previewISilo;
}

rule maxRedeemEquivalence(){
    env e;
    
    address owner;
    uint256 maxERC4625 = maxRedeem(e,owner);
    uint256 maxISilo = maxRedeem(e,owner,ISilo.CollateralType.Collateral);

    assert maxERC4625 == maxISilo;
}

rule maxWithdrawEquivalence(){
    env e;
    
    address owner;
    uint256 maxERC4625 = maxWithdraw(e,owner);
    uint256 maxISilo = maxWithdraw(e,owner,ISilo.CollateralType.Collateral);

    assert maxERC4625 == maxISilo;
}


rule depositEquivalence(uint256 assets,address receiver){
    env e;

    storage initState = lastStorage;

    mathint shares_ERC4626 = deposit(e, assets, receiver);

    storage deposit_ERC4626_state = lastStorage;

    mathint shares_ISilo = deposit(e, assets, receiver,ISilo.CollateralType.Collateral) at initState;

    storage deposit_ISilo_state = lastStorage;

    assert deposit_ERC4626_state[currentContract] == deposit_ISilo_state[currentContract];
    assert shares_ERC4626 == shares_ISilo; 
}

rule mintEquivalence(uint256 shares,address receiver){
    env e;

    storage initState = lastStorage;

    mathint assets_ERC4626 = mint(e, shares, receiver);

    storage mint_ERC4626_state = lastStorage;

    mathint assets_ISilo = mint(e, shares, receiver,ISilo.CollateralType.Collateral) at initState;

    storage mint_ISilo_state = lastStorage;

    assert mint_ERC4626_state[currentContract] == mint_ISilo_state[currentContract];
    assert assets_ERC4626 == assets_ISilo; 
}

rule withdrawEquivalence(uint256 assets,address receiver,address owner){
    env e;

    storage initState = lastStorage;

    mathint shares_ERC4626 = withdraw(e, assets, receiver,owner);

    storage withdraw_ERC4626_state = lastStorage;

    mathint shares_ISilo = withdraw(e, assets, receiver,owner,ISilo.CollateralType.Collateral) at initState;

    storage withdraw_ISilo_state = lastStorage;

    assert withdraw_ERC4626_state[currentContract] == withdraw_ISilo_state[currentContract];
    assert shares_ERC4626 == shares_ISilo; 
}

rule redeemEquivalence(uint256 shares,address receiver,address owner){
    env e;

    storage initState = lastStorage;

    mathint assets_ERC4626 = redeem(e, shares, receiver,owner);

    storage redeem_ERC4626_state = lastStorage;

    mathint assets_ISilo = redeem(e, shares, receiver,owner,ISilo.CollateralType.Collateral) at initState;

    storage redeem_ISilo_state = lastStorage;

    assert redeem_ERC4626_state[currentContract] == redeem_ISilo_state[currentContract];
    assert assets_ERC4626 == assets_ISilo; 
}
