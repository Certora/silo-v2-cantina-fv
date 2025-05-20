import "../mocks/PartialLiquidationMethods1.spec";


rule liquidatorOrPLReceivedCorrectShares(env e) {
    sharesCollateralCached = 0;
    sharesProtectedCached = 0;

    onReentrancy = false;
    nonSceneAddressRequirements(e.msg.sender);
    siloRequirements(e);
    address _collateralAsset; address _debtAsset; address _borrower; uint256 _maxDebtToCover; bool _receiveSToken; // calldataarg

    totalSuppliesMoreThanThreeBalances(e.msg.sender, Harness, _borrower);

    uint256 balanceLiquidatorBeforeSharesC;
    uint256 balanceLiquidatorBeforeSharesP;

    address collateralShareToken;
    address shareProtectedCollateralToken;

    if(_collateralAsset == Token0) {
        collateralShareToken = Silo0;
        shareProtectedCollateralToken = ShareProtectedCollateralToken0;
    }
    else {
        collateralShareToken = Silo1;
        shareProtectedCollateralToken = ShareProtectedCollateralToken1;
    }

    balanceLiquidatorBeforeSharesC = getERCBalance(collateralShareToken, e.msg.sender);
    balanceLiquidatorBeforeSharesP = getERCBalance(shareProtectedCollateralToken, e.msg.sender);

    liquidationCall(e, _collateralAsset, _debtAsset, _borrower, _maxDebtToCover, _receiveSToken);

    uint256 balanceLiquidatorAfterSharesC;
    uint256 balanceLiquidatorAfterSharesP;

    balanceLiquidatorAfterSharesC = getERCBalance(collateralShareToken, e.msg.sender);
    balanceLiquidatorAfterSharesP = getERCBalance(shareProtectedCollateralToken, e.msg.sender);

    if(_receiveSToken) {
        if(_borrower != e.msg.sender) {
            assert (balanceLiquidatorAfterSharesC == balanceLiquidatorBeforeSharesC + sharesCollateralCached);
            assert (balanceLiquidatorAfterSharesP == balanceLiquidatorBeforeSharesP + sharesProtectedCached);
        }
        else {
            assert (balanceLiquidatorAfterSharesC == balanceLiquidatorBeforeSharesC);
            assert (balanceLiquidatorAfterSharesP == balanceLiquidatorBeforeSharesP);
        }
    }
    else {
        if(_borrower != e.msg.sender) {
            assert (balanceLiquidatorAfterSharesC == balanceLiquidatorBeforeSharesC);
            assert (balanceLiquidatorAfterSharesP == balanceLiquidatorBeforeSharesP);
        }
        else {
            assert (balanceLiquidatorAfterSharesC == balanceLiquidatorBeforeSharesC - sharesCollateralCached);
            assert (balanceLiquidatorAfterSharesP == balanceLiquidatorBeforeSharesP - sharesProtectedCached);
        }
    }
}











