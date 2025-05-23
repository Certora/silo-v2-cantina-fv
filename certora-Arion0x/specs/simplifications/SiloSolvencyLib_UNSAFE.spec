

import "../setup/two_silos_methods.spec";
// import "../setup/single_silo_methods.spec";


methods {
    // Summarizations:
    function SiloSolvencyLib.calculateLtv(
        SiloSolvencyLib.LtvData memory _ltvData, 
        address _collateralToken, 
        address _debtToken
    ) internal returns (uint256,uint256,uint256) =>
    calculateLtvCVL(_ltvData, _collateralToken, _debtToken);
    
    
    function SiloSolvencyLib.getAssetsDataForLtvCalculations(
        ISiloConfig.ConfigData memory _collateralConfig,
        ISiloConfig.ConfigData memory _debtConfig,
        address _borrower,
        ISilo.OracleType _oracleType,
        ISilo.AccrueInterestInMemory _accrueInMemory,
        uint256 _debtShareBalanceCached
    ) internal returns (SiloSolvencyLib.LtvData memory)  =>
    calculateAssetsDataCVL(_collateralConfig.silo, _debtConfig.silo, _borrower, _debtShareBalanceCached);
}

/*
abstractLTV value (
    address collateralToken
    address debtToken
    uint256 borrowerProtectedAssets
    uint256 borrowerCollateralAssets
    uint256 borrowerDebtAssets
)
*/
ghost abstractLTV_collateralValue(address,address,uint256,uint256,uint256) returns uint256;
ghost abstractLTV_debtValue(address,address,uint256,uint256,uint256) returns uint256;
ghost abstractLTV_ltvBefore(address,address,uint256,uint256,uint256) returns uint256;

function calculateLtvCVL(SiloSolvencyLib.LtvData ltvData, address collateralToken, address debtToken) returns (uint256,uint256,uint256) {
    uint256 P = ltvData.borrowerProtectedAssets;
    uint256 C = ltvData.borrowerCollateralAssets;
    uint256 D = ltvData.borrowerDebtAssets;
    return (
        abstractLTV_collateralValue(collateralToken, debtToken, P, C, D),
        abstractLTV_debtValue(collateralToken, debtToken, P, C, D),
        abstractLTV_ltvBefore(collateralToken, debtToken, P, C, D)
    );
}

/*
/// Shares to assets abstract conversion : f(shares balance, total assets) -> assets 
*/
ghost assetsData_collateral(uint256,uint256) returns uint256 {
    axiom forall uint256 balance1. forall uint256 balance2. forall uint256 assets.
        balance1 <= balance2 => assetsData_collateral(balance1, assets) <= assetsData_collateral(balance2, assets);
    axiom forall uint256 assets1. forall uint256 assets2. forall uint256 balance.
        assets1 <= assets2 => assetsData_collateral(balance, assets1) <= assetsData_collateral(balance, assets2);
    axiom forall uint256 assets. assetsData_collateral(0, assets) == 0;
    axiom forall uint256 balance. assetsData_collateral(balance, 0) == 0;
    axiom forall uint256 assets. forall uint256 balance. assetsData_collateral(balance, assets) <= assets;
}

ghost assetsData_protected(uint256,uint256) returns uint256 {
    axiom forall uint256 balance1. forall uint256 balance2. forall uint256 assets.
        balance1 <= balance2 => assetsData_protected(balance1, assets) <= assetsData_protected(balance2, assets);
    axiom forall uint256 assets1. forall uint256 assets2. forall uint256 balance.
        assets1 <= assets2 => assetsData_protected(balance, assets1) <= assetsData_protected(balance, assets2);
    axiom forall uint256 assets. assetsData_protected(0, assets) == 0;
    axiom forall uint256 balance. assetsData_protected(balance, 0) == 0;
    axiom forall uint256 assets. forall uint256 balance. assetsData_collateral(balance, assets) <= assets;
}

ghost assetsData_debt(uint256,uint256) returns uint256 {
    axiom forall uint256 balance1. forall uint256 balance2. forall uint256 assets.
        balance1 <= balance2 => assetsData_debt(balance1, assets) <= assetsData_debt(balance2, assets);
    axiom forall uint256 assets1. forall uint256 assets2. forall uint256 balance.
        assets1 <= assets2 => assetsData_debt(balance, assets1) <= assetsData_debt(balance, assets2);
    axiom forall uint256 assets. assetsData_debt(0, assets) == 0;
    axiom forall uint256 balance. assetsData_debt(balance, 0) == 0;
    axiom forall uint256 assets. forall uint256 balance. assetsData_collateral(balance, assets) <= assets;
}

/*
Summary for getAssetsDataForLtvCalculations()
Doesn't include timestamp dependence - assumes last timestamp is the current timestamp, so
that the total assets values already include the interest.
*/
function calculateAssetsDataCVL(address silo_collateral, address silo_debt, address borrower, uint256 debtShareBalanceCached) returns SiloSolvencyLib.LtvData {
    uint256 balanceCollateral;
    uint256 balanceProtected;
    uint256 balanceDebt;

    uint256 totalCollateral;
    uint256 totalProtected;
    uint256 totalDebt;
    env e;
    require ((silo_collateral == silo0 && silo_debt == silo1) || (silo_collateral == silo1 && silo_debt == silo0));
    /// Fetch shares balances and total assets for each token:
    if(silo_collateral == silo0 && silo_debt == silo1) {
        require balanceProtected == balanceOfCVL(shareProtectedCollateralToken0,borrower);
        require balanceCollateral == balanceOfCVL(silo0,borrower);
        require balanceDebt == (debtShareBalanceCached == 0 ?   balanceOfCVL(shareDebtToken1,borrower) : debtShareBalanceCached);

        mathint totalCollateralAssets; mathint totalProtectedAssets;
        totalCollateralAssets, totalProtectedAssets = silo0.getCollateralAndProtectedTotalsStorage(e);  

        require totalProtected == totalProtectedAssets;
        require totalDebt == silo1.getTotalAssetsStorage(ISilo.AssetType.Debt);
        require totalCollateral == totalCollateralAssets;
    }
    else if(silo_collateral == silo1 && silo_debt == silo0) {
        require balanceProtected  == balanceOfCVL(shareProtectedCollateralToken1,borrower);
        require balanceCollateral == balanceOfCVL(silo1,borrower);
        require balanceDebt == (debtShareBalanceCached == 0 ? balanceOfCVL(shareDebtToken0,borrower) : debtShareBalanceCached);

        mathint totalCollateralAssets; mathint totalProtectedAssets;
        totalCollateralAssets, totalProtectedAssets = silo1.getCollateralAndProtectedTotalsStorage(e); 

        require totalProtected == totalProtectedAssets;
        require totalDebt == silo0.getTotalAssetsStorage(ISilo.AssetType.Debt);
        require totalCollateral == totalCollateralAssets;
    }
    else {
        assert false, "Only (silo0,silo1) or (silo1,silo0) are expected.";
    }

    SiloSolvencyLib.LtvData ltvData; 

    require ltvData.borrowerCollateralAssets == assetsData_collateral(balanceCollateral, totalCollateral);
    require ltvData.borrowerProtectedAssets == assetsData_protected(balanceProtected, totalProtected);
    require ltvData.borrowerDebtAssets == assetsData_debt(balanceDebt, totalDebt);

    return ltvData;
}
