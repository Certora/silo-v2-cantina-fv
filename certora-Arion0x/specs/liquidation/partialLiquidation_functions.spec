// // @title Require that the second env has at least as much allowance and balance as first
function requireSecondEnvAtLeastAsFirst(env e1, env e2) {
    /// At least as much allowance as first `env`
    require (
        allowanceCVL(token0,e2.msg.sender,silo0) >= 
        allowanceCVL(token0,e1.msg.sender,silo0)
    );
    /// At least as much balance as first `env`
    require balanceOfCVL(token0,e2.msg.sender)>= balanceOfCVL(token0,e1.msg.sender);
}

function synchronous_siloStorage_erc20cvl(address silo){
    assert (silo == silo0 || silo == silo1);
    if (silo == silo0){
    mathint totalDebt;
    mathint totalCollateral;
    mathint totalProtected;
    totalProtected =  ghostTotalAssets[silo0][PROTECTED_ASSET_TYPE()];
    totalCollateral = ghostTotalAssets[silo0][COLLATERAL_ASSET_TYPE()];
    totalDebt = ghostTotalAssets[silo0][DEBT_ASSET_TYPE()]; 
    require totalProtected  == totalSupplyCVL(shareProtectedCollateralToken0);
    require totalCollateral == totalSupplyCVL(silo0);
    require totalDebt == totalSupplyCVL(shareDebtToken0);

    uint256 totalDebtStorage;
    uint256 totalCollateralStorage;
    uint256 totalProtectedStorage;
    totalDebtStorage = silo0.getTotalAssetsStorage(ISilo.AssetType.Debt);
    totalCollateralStorage = silo0.getTotalAssetsStorage(ISilo.AssetType.Collateral);
    totalProtectedStorage = silo0.getTotalAssetsStorage(ISilo.AssetType.Protected);
    require totalDebt == totalDebtStorage;
    require totalCollateral == totalCollateralStorage;
    require totalProtected == totalProtectedStorage;
    } else{
    mathint totalDebt;
    mathint totalCollateral;
    mathint totalProtected;
    totalProtected =  ghostTotalAssets[silo1][PROTECTED_ASSET_TYPE()];
    totalCollateral = ghostTotalAssets[silo1][COLLATERAL_ASSET_TYPE()];
    totalDebt = ghostTotalAssets[silo][DEBT_ASSET_TYPE()]; 
    require totalProtected  == totalSupplyCVL(shareProtectedCollateralToken1);
    require totalCollateral == totalSupplyCVL(silo1);
    require totalDebt == totalSupplyCVL(shareDebtToken1);

    uint256 totalDebtStorage;
    uint256 totalCollateralStorage;
    uint256 totalProtectedStorage;
    totalDebtStorage = silo1.getTotalAssetsStorage(ISilo.AssetType.Debt);
    totalCollateralStorage = silo1.getTotalAssetsStorage(ISilo.AssetType.Collateral);
    totalProtectedStorage = silo1.getTotalAssetsStorage(ISilo.AssetType.Protected);
    require totalDebt == totalDebtStorage;
    require totalCollateral == totalCollateralStorage;
    require totalProtected == totalProtectedStorage;
    }

}