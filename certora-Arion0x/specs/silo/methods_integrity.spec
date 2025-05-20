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

// ---- Borrow/Repay -----------------------------------------------------------------

/// @title Integrity of borrow
/// @property borrow-integrity
/// @status Done: https://vaas-stg.certora.com/output/39601/a92223ffd54b428bbc75fbbf76deaa91?anonymousKey=f962f690a342ccff3b3843c47f2d310b98d355f6
// TODO add check for decrease of silo's balance
rule HLP_integrityOfBorrow(address receiver, uint256 assets) {
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    totalSuppliesMoreThanBalances(receiver, silo0);
    synchronous_siloStorage_erc20cvl(e);

    mathint balanceTokenBefore = balanceOfCVL(token0,receiver);
    mathint siloBalanceBefore  = balanceOfCVL(token0,silo0);
    mathint shareDebtTokenBefore = balanceOfCVL(shareDebtToken0,receiver);
       
    mathint shares = borrow(e, assets, receiver, receiver);

    mathint balanceTokenAfter = balanceOfCVL(token0,receiver);
    mathint siloBalanceAfter  = balanceOfCVL(token0,silo0);
    mathint shareDebtTokenAfter = balanceOfCVL(shareDebtToken0,receiver);
   
    assert (
        balanceTokenAfter == balanceTokenBefore + assets,
        "token balance increased appropriately"
    );
    assert (
        siloBalanceAfter == siloBalanceBefore - assets,
        "silo balance of token decreased appropriately"
    );
    assert (
        shareDebtTokenAfter == shareDebtTokenBefore + shares,
        "debt share increased appropriately"
    );
}


/// @title Integrity of `borrowSameAsset`
/// @property borrow-integrity
/// @status Done: https://vaas-stg.certora.com/output/39601/0c5fdd83985f4cff92e256770d4a2146?anonymousKey=3d525a9323f55a52a02015eef18222af0a30e531
rule HLP_integrityOfBorrowSame(address receiver, uint256 assets) {
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    totalSuppliesMoreThanBalances(receiver, silo0);
    synchronous_siloStorage_erc20cvl(e);

    mathint balanceTokenBefore = balanceOfCVL(token0,receiver);
    mathint siloBalanceBefore  = balanceOfCVL(token0,silo0);
    mathint shareDebtTokenBefore = balanceOfCVL(shareDebtToken0,receiver);
       
    mathint shares = borrowSameAsset(e, assets, receiver, receiver);

    mathint balanceTokenAfter = balanceOfCVL(token0,receiver);
    mathint siloBalanceAfter  = balanceOfCVL(token0,silo0);
    mathint shareDebtTokenAfter = balanceOfCVL(shareDebtToken0,receiver);

    assert (
        balanceTokenAfter == balanceTokenBefore + assets,
        "token balance increased appropriately"
    );
    assert (
        siloBalanceAfter == siloBalanceBefore - assets,
        "silo balance of token decreased appropriately"
    );
    assert (
        shareDebtTokenAfter == shareDebtTokenBefore + shares,
        "debt share increased appropriately"
    );
}


/// @title Integrity of `borrowShares`
/// @property borrowShares-integrity
/// @status Done: https://vaas-stg.certora.com/output/39601/ba5142728e9e4089a74f3a448e4df9fa?anonymousKey=c6c5cca56df4b25896022089b307da711046c6c8
rule HLP_integrityOfBorrowShares(address receiver, uint256 shares) {
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    totalSuppliesMoreThanBalances(receiver, silo0);
    synchronous_siloStorage_erc20cvl(e);
    
    mathint balanceTokenBefore = balanceOfCVL(token0,receiver);
    mathint siloBalanceBefore  = balanceOfCVL(token0,silo0);
    mathint shareDebtTokenBefore = balanceOfCVL(shareDebtToken0,receiver);
       
    mathint assets = borrowShares(e, shares, receiver, receiver);

    mathint balanceTokenAfter = balanceOfCVL(token0,receiver);
    mathint siloBalanceAfter  = balanceOfCVL(token0,silo0);
    mathint shareDebtTokenAfter = balanceOfCVL(shareDebtToken0,receiver);

    assert (
        balanceTokenAfter == balanceTokenBefore + assets,
        "token balance increased appropriately"
    );
    assert (
        siloBalanceAfter == siloBalanceBefore - assets,
        "silo balance of token decreased appropriately"
    );
    assert (
        shareDebtTokenAfter == shareDebtTokenBefore + shares,
        "debt share increased appropriately"
    );
}

/// @title Integrity of `borrowShares`
/// @property borrowShares-integrity
/// @status Done: https://vaas-stg.certora.com/output/39601/ba5142728e9e4089a74f3a448e4df9fa?anonymousKey=c6c5cca56df4b25896022089b307da711046c6c8
rule HLP_integrityOfRepay(uint256 assets,address borrower) {
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // borrower is not one of the contracts in the scene
    nonSceneAddressRequirements(borrower);
    nonSceneAddressRequirements(e.msg.sender);
    totalSuppliesMoreThanBalances(borrower, silo0);
    synchronous_siloStorage_erc20cvl(e);
    
    mathint repayerBalanceBefore = balanceOfCVL(token0,e.msg.sender);
    mathint siloBalanceBefore  = balanceOfCVL(token0,silo0);
    mathint shareDebtTokenBefore = balanceOfCVL(shareDebtToken0,borrower);
    uint256 sharesCalculated = convertToShares(e,assets);
    require sharesCalculated <= shareDebtTokenBefore;
       
    mathint shares = repay(e, assets, borrower);

    mathint repayerBalanceAfter = balanceOfCVL(token0,e.msg.sender);
    mathint siloBalanceAfter  = balanceOfCVL(token0,silo0);
    mathint shareDebtTokenAfter = balanceOfCVL(shareDebtToken0,borrower);

    assert (
        repayerBalanceAfter == repayerBalanceBefore - assets,
        "token balance increased appropriately"
    );
    assert (
        siloBalanceAfter == siloBalanceBefore + assets,
        "silo balance of token decreased appropriately"
    );
    assert (
        shareDebtTokenAfter == shareDebtTokenBefore - shares,
        "debt share increased appropriately"
    );
}

rule HLP_integrityOfRepayShares(uint256 shares,address borrower) {
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // borrower is not one of the contracts in the scene
    nonSceneAddressRequirements(borrower);
    nonSceneAddressRequirements(e.msg.sender);
    synchronous_siloStorage_erc20cvl(e);
    totalSuppliesMoreThanBalances(borrower, silo0);
    
    mathint repayerBalanceBefore = balanceOfCVL(token0,e.msg.sender);
    mathint siloBalanceBefore  = balanceOfCVL(token0,silo0);
    mathint shareDebtTokenBefore = balanceOfCVL(shareDebtToken0,borrower);
    require shares <= shareDebtTokenBefore;
       
    mathint assets = repayShares(e, shares, borrower);

    mathint repayerBalanceAfter = balanceOfCVL(token0,e.msg.sender);
    mathint siloBalanceAfter  = balanceOfCVL(token0,silo0);
    mathint shareDebtTokenAfter = balanceOfCVL(shareDebtToken0,borrower);

    assert (
        repayerBalanceAfter == repayerBalanceBefore - assets,
        "token balance increased appropriately"
    );
    assert (
        siloBalanceAfter == siloBalanceBefore + assets,
        "silo balance of token decreased appropriately"
    );
    assert (
        shareDebtTokenAfter == shareDebtTokenBefore - shares,
        "debt share increased appropriately"
    );
}

// ---- Deposit/Mint -----------------------------------------------------------

/// @title Integrity of deposit
/// @status Done: https://vaas-stg.certora.com/output/39601/6a9f19160e884c9991fc0e9adb51afac?anonymousKey=bffdda9bd17af80e1aa274b70bafa2fe2acfc1a6
rule HLP_integrityOfDeposit(address receiver, uint256 assets) {
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    require e.msg.sender != silo0;

    totalSuppliesMoreThanBalances(receiver, silo0);
    synchronous_siloStorage_erc20cvl(e);

    mathint totalCollateralBefore = ghostTotalAssets[silo0][COLLATERAL_ASSET_TYPE()];
    mathint balanceCollateralBefore = balanceOfCVL(silo0,receiver);
    mathint balanceTokenBefore = balanceOfCVL(token0,e.msg.sender);
    mathint siloBalanceBefore  = balanceOfCVL(token0,silo0);
    
    mathint shares = deposit(e, assets, receiver);

    mathint totalCollateralAfter = ghostTotalAssets[silo0][COLLATERAL_ASSET_TYPE()];
    mathint balanceCollateralAfter = balanceOfCVL(silo0,receiver);
    mathint balanceTokenAfter = balanceOfCVL(token0,e.msg.sender);
    mathint siloBalanceAfter  = balanceOfCVL(token0,silo0);


    assert (shares > 0, "non-zero shares");
    assert (
        balanceCollateralAfter == balanceCollateralBefore + shares,
        "collateral shares increased by deposit"
    );
    assert (
        balanceTokenAfter == balanceTokenBefore - assets,
        "token balance decreased by deposit"
    );
    assert (
        siloBalanceAfter == siloBalanceBefore + assets,
        "silo balance of token increased appropriately"
    );
    assert (
        totalCollateralAfter == totalCollateralBefore + assets,""
    );
}


/// @title Integrity of mint
/// @status: Done https://vaas-stg.certora.com/output/39601/cfafce63b506448bb331bde0ce2d4638?anonymousKey=8982d16e1772dc713a388095c653324a1095f0e7
rule HLP_integrityOfMint(address receiver, uint256 shares) {
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    require e.msg.sender != silo0;
    
    totalSuppliesMoreThanBalances(receiver, silo0);
    synchronous_siloStorage_erc20cvl(e);
    
    mathint balanceCollateralBefore = balanceOfCVL(silo0,receiver);
    mathint balanceTokenBefore = balanceOfCVL(token0,e.msg.sender);
    mathint siloBalanceBefore  = balanceOfCVL(token0,silo0);
        
    mathint assets = mint(e, shares, receiver);

    mathint balanceCollateralAfter = balanceOfCVL(silo0,receiver);
    mathint balanceTokenAfter = balanceOfCVL(token0,e.msg.sender);
    mathint siloBalanceAfter  = balanceOfCVL(token0,silo0); 
   
    assert (
        balanceCollateralAfter == balanceCollateralBefore + shares,
        "collateral shares increased by mint"
    );
    assert (
        balanceTokenAfter == balanceTokenBefore - assets,
        "token balance decreased by mint"
    );
    assert (
        siloBalanceAfter == siloBalanceBefore + assets,
        "silo balance of token increased appropriately"
    );
}

// ---- Redeem/Withdraw --------------------------------------------------------

/// @title Integrity of redeem
/// @status: Done https://vaas-stg.certora.com/output/39601/d6ba40df683a417582b99a4a07996c80?anonymousKey=a34896d77cf347614a5969668dd17843bf53b089
rule HLP_integrityOfRedeem(address receiver, uint256 shares) {
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    totalSuppliesMoreThanBalances(receiver, silo0);
    synchronous_siloStorage_erc20cvl(e);
    
    mathint balanceCollateralBefore = balanceOfCVL(silo0,receiver);
    mathint balanceTokenBefore = balanceOfCVL(token0,receiver);
    mathint siloBalanceBefore  = balanceOfCVL(token0,silo0);
        
    mathint assets = redeem(e, shares, receiver, receiver);

    mathint balanceCollateralAfter = balanceOfCVL(silo0,receiver);
    mathint balanceTokenAfter = balanceOfCVL(token0,receiver);
    mathint siloBalanceAfter  = balanceOfCVL(token0,silo0);
   
    assert balanceCollateralAfter == balanceCollateralBefore - shares;
    assert balanceTokenAfter == balanceTokenBefore + assets;
    assert (
        siloBalanceAfter == siloBalanceBefore - assets,
        "silo balance of token decreased appropriately"
    );
}


/// @title Integrity of withdraw
/// @status Done: https://vaas-stg.certora.com/output/39601/fe9d02f2d8c641329304f04e7b32c155?anonymousKey=6684f7a4cb199e09e5a579aaa3870094b3767cda
rule HLP_integrityOfWithdraw(address receiver, uint256 assets) {
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    totalSuppliesMoreThanBalances(receiver, silo0);
    synchronous_siloStorage_erc20cvl(e);
    
    mathint totalCollateralBefore = ghostTotalAssets[silo0][COLLATERAL_ASSET_TYPE()];
    mathint balanceCollateralBefore = balanceOfCVL(silo0,receiver);
    mathint balanceTokenBefore = balanceOfCVL(token0,receiver);
    mathint siloBalanceBefore  = balanceOfCVL(token0,silo0);   

    mathint shares = withdraw(e, assets, receiver, receiver);

    mathint totalCollateralAfter = ghostTotalAssets[silo0][COLLATERAL_ASSET_TYPE()];
    mathint balanceCollateralAfter = balanceOfCVL(silo0,receiver);
    mathint balanceTokenAfter = balanceOfCVL(token0,receiver);
    mathint siloBalanceAfter  = balanceOfCVL(token0,silo0);

   
    assert balanceCollateralAfter == balanceCollateralBefore - shares;
    assert balanceTokenAfter == balanceTokenBefore + assets;
    assert (
        siloBalanceAfter == siloBalanceBefore - assets,
        "silo balance of token decreased appropriately"
    );
    assert totalCollateralAfter == totalCollateralBefore - assets;
}

rule HLP_integrityOfTransitionCollateral(uint256 shares,address owner){
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(owner);
    totalSuppliesMoreThanBalances(owner, silo0);
    synchronous_siloStorage_erc20cvl(e);


    mathint balanceTokenBefore = balanceOfCVL(token0,owner);
    mathint ownerBalanceCollateralBefore = balanceOfCVL(silo0,owner);
    mathint spenderBalanceCollateralBefore = balanceOfCVL(silo0,e.msg.sender);
    mathint balanceProtectedBefore = balanceOfCVL(shareProtectedCollateralToken0,owner);
    mathint siloBalanceBefore  = balanceOfCVL(token0,silo0);   

    transitionCollateral(e,shares,owner,ISilo.CollateralType.Collateral);

    mathint balanceTokenAfter = balanceOfCVL(token0,owner);
    mathint ownerBalanceCollateralAfter = balanceOfCVL(silo0,owner);
    mathint spenderBalanceCollateralAfter = balanceOfCVL(silo0,e.msg.sender);
    mathint balanceProtectedAfter = balanceOfCVL(shareProtectedCollateralToken0,owner);
    mathint siloBalanceAfter  = balanceOfCVL(token0,silo0);  

    assert balanceTokenAfter == balanceTokenBefore;
    assert ownerBalanceCollateralAfter == ownerBalanceCollateralBefore - shares;
    // assert balanceProtectedAfter == balanceProtectedBefore - shares;
    // assert spenderBalanceCollateralAfter == spenderBalanceCollateralBefore + shares; //not proved
}

rule HLP_integrityOfTransitionProtected(uint256 shares,address owner){
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(owner);
    totalSuppliesMoreThanBalances(owner, silo0);
    synchronous_siloStorage_erc20cvl(e);

    mathint balanceTokenBefore = balanceOfCVL(token0,owner);
    mathint balanceCollateralBefore = balanceOfCVL(silo0,owner);
    mathint balanceProtectedBefore = balanceOfCVL(shareProtectedCollateralToken0,owner);
    mathint siloBalanceBefore  = balanceOfCVL(token0,silo0);   

    transitionCollateral(e,shares,owner,ISilo.CollateralType.Protected);

    mathint balanceTokenAfter = balanceOfCVL(token0,owner);
    mathint balanceCollateralAfter = balanceOfCVL(silo0,owner);
    mathint balanceProtectedAfter = balanceOfCVL(shareProtectedCollateralToken0,owner);
    mathint siloBalanceAfter  = balanceOfCVL(token0,silo0);  

    assert balanceTokenAfter == balanceTokenBefore;
    // assert balanceCollateralAfter == balanceCollateralBefore + shares;
    assert balanceProtectedAfter == balanceProtectedBefore - shares;
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