import "../mocks/PartialLiquidationMethodsReentrancy.spec";

rule reentrancyOnOff(env e) {
    onReentrancy = false;
    onReentrancyCount = 0;
    offReentrancyCount = 0;
    address _collateralAsset; address _debtAsset; address _borrower; uint256 _maxDebtToCover; bool _receiveSToken; // calldataarg
    liquidationCall(e, _collateralAsset, _debtAsset, _borrower, _maxDebtToCover, _receiveSToken);
    assert (onReentrancyCount == 1 && offReentrancyCount == 1 && !onReentrancy);
}













