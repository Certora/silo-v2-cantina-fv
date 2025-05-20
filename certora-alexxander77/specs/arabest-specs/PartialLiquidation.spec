import "../mocks/PartialLiquidationMethods.spec";

rule correctBalancesAltered(env e) {
    sharesCollateralCached = 0;
    sharesProtectedCached = 0;

    initBalanceFlags();

    onReentrancy = false;
    nonSceneAddressRequirements(e.msg.sender);
    siloRequirements(e);
    address _collateralAsset; address _debtAsset; address _borrower; uint256 _maxDebtToCover; bool _receiveSToken; // calldataarg

    liquidationCall(e, _collateralAsset, _debtAsset, _borrower, _maxDebtToCover, _receiveSToken);
    if(_collateralAsset == Token0) {
        assert balanceUpdateFlag1 && balanceUpdateFlagD1;

        assert (sharesCollateralCached != 0) == balanceUpdateFlagS0;
        assert (sharesProtectedCached != 0) == balanceUpdateFlagP0;

        assert balanceUpdateFlag0 == (!_receiveSToken && (sharesCollateralCached != 0 || sharesProtectedCached != 0));
        assert !balanceUpdateFlagS1 && !balanceUpdateFlagP1 && !balanceUpdateFlagD0;
    }
    else {
        assert balanceUpdateFlag0 && balanceUpdateFlagD0;

        assert (sharesCollateralCached != 0) == balanceUpdateFlagS1;
        assert (sharesProtectedCached != 0) == balanceUpdateFlagP1;

        assert balanceUpdateFlag1 == (!_receiveSToken && (sharesCollateralCached != 0 || sharesProtectedCached != 0));
        assert !balanceUpdateFlagS0 && !balanceUpdateFlagP0 && !balanceUpdateFlagD1;
    }

}

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
rule correctInitialize(env e) {
    address siloConfig;
    bytes data;

    address siloConfigStored = siloConfig(e);
    initialize@withrevert(e, siloConfig, data);

    bool lastRevertedCached = lastReverted;

    if(!lastRevertedCached) {
        assert siloConfig == siloConfig(e);
    }
    assert lastRevertedCached == (siloConfig == 0 || siloConfigStored != 0);

}
rule correctTokensReceived(env e) {
    sharesCollateralCached = 0;
    sharesProtectedCached = 0;
    balanceUpdateFlag0 = false;
    balanceUpdateFlag1 = false;

    onReentrancy = false;
    nonSceneAddressRequirements(e.msg.sender);
    siloRequirements(e);

    address _collateralAsset; address _debtAsset; address _borrower; uint256 _maxDebtToCover; bool _receiveSToken; // calldataarg

    liquidationCall(e, _collateralAsset, _debtAsset, _borrower, _maxDebtToCover, _receiveSToken);

    if (_receiveSToken) {
        if (_collateralAsset == Token0) {
            assert !balanceUpdateFlag0;
        }
        else {
            assert !balanceUpdateFlag1;
        }
    }
    else {
        if(sharesCollateralCached != 0 || sharesProtectedCached != 0) {
            assert balanceUpdateFlag0 && balanceUpdateFlag1;
        }
        else {
            if (_collateralAsset == Token0) {
                assert !balanceUpdateFlag0 && balanceUpdateFlag1;
            }
            else {
                assert !balanceUpdateFlag1 && balanceUpdateFlag0;
            }
        }
    }
}

// The Token0 or Token1 balance of the liquidator must have decreased
rule liquidatorDecreasedAssets(env e, calldataarg args) {

    onReentrancy = false;
    nonSceneAddressRequirements(e.msg.sender);
    siloRequirements(e);

    uint256 balanceLiquidatorBefore0 = getERCBalance(Token0, e.msg.sender);
    uint256 balanceLiquidatorBefore1 = getERCBalance(Token1, e.msg.sender);

    address _collateralAsset; address _debtAsset; address _borrower; uint256 _maxDebtToCover; bool _receiveSToken; // calldataarg
    liquidationCall(e, _collateralAsset, _debtAsset, _borrower, _maxDebtToCover, _receiveSToken);
    uint256 balanceLiquidatorAfter0 = getERCBalance(Token0, e.msg.sender);
    uint256 balanceLiquidatorAfter1 = getERCBalance(Token1, e.msg.sender);
    assert (balanceLiquidatorAfter0 < balanceLiquidatorBefore0 || balanceLiquidatorAfter1 < balanceLiquidatorBefore1);
}

// One of the Silos must have its balance increased by the repaid debt
rule siloAssetBalanceIncreased(env e, calldataarg args) {

    onReentrancy = false;
    nonSceneAddressRequirements(e.msg.sender);
    siloRequirements(e);

//    totalSuppliesMoreThanThreeBalances(e.msg.sender, Harness, Silo0);
//    totalSuppliesMoreThanThreeBalances(e.msg.sender, Harness, Silo1);

    uint256 balanceSilo0Before = getERCBalance(Token0, Silo0);
    uint256 balanceSilo1Before = getERCBalance(Token1, Silo1);

    address _collateralAsset; address _debtAsset; address _borrower; uint256 _maxDebtToCover; bool _receiveSToken; // calldataarg
    liquidationCall(e, _collateralAsset, _debtAsset, _borrower, _maxDebtToCover, _receiveSToken);
    uint256 balanceSilo0After = getERCBalance(Token0, Silo0);
    uint256 balanceSilo1After = getERCBalance(Token1, Silo1);

    require balanceSilo0Before + repayDebtAssetsCached < max_uint;
    require balanceSilo1Before + repayDebtAssetsCached < max_uint;

    assert (balanceSilo0After == balanceSilo0Before + repayDebtAssetsCached)
            || (balanceSilo1After == balanceSilo1Before + repayDebtAssetsCached), "The debt asset silo balance should increase by exactly repayDebtAssetsCached";
}

rule reentrancyOnOff(env e) {
    onReentrancy = false;
    onReentrancyCount = 0;
    offReentrancyCount = 0;
    address _collateralAsset; address _debtAsset; address _borrower; uint256 _maxDebtToCover; bool _receiveSToken; // calldataarg
    liquidationCall(e, _collateralAsset, _debtAsset, _borrower, _maxDebtToCover, _receiveSToken);
    assert (onReentrancyCount == 1 && offReentrancyCount == 1 && !onReentrancy);
}


rule balanceNoChange(address token, env e) {
    requireTokenInScene(token);
    nonSceneAddressRequirements(e.msg.sender);
    siloRequirements(e);
    uint256 liquidatorBalanceBefore = getERCBalance(token, Harness);
    address _collateralAsset; address _debtAsset; address _borrower; uint256 _maxDebtToCover; bool _receiveSToken; // calldataarg

    require Harness != _borrower;
    liquidationCall(e, _collateralAsset, _debtAsset, _borrower, _maxDebtToCover, _receiveSToken);
    assert liquidatorBalanceBefore == getERCBalance(token, Harness);
}










