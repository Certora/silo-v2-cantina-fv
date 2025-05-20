import "../mocks/PartialLiquidationRevertMethods.spec";

methods {
    // NONDET summaries
    function _.safeTransferFrom(address, address, uint) external => NONDET;
    function _.safeIncreaseAllowance(address, uint) external => NONDET;
    function _.redeem(uint256, address, address, ISilo.CollateralType) external => NONDET;
    function _.repay(uint256 _assets, address _borrower) external => NONDET;
}

// Revert conditions for liquidationCall()
rule liqCallRevertWhen0MaxDebt(env e, address _collateralAsset, address _debtAsset, address _borrower, uint256 _maxDebtToCover, bool _receiveSToken) {
    address debtSilo; address debtAsset; address collateralSilo; address collateralAsset;
    (debtSilo, debtAsset, collateralSilo, collateralAsset) = liqCallRevertSetup(e, _borrower, _maxDebtToCover);

    require _maxDebtToCover == 0;
    maxDebtFlag = true;
    liquidationCall@withrevert(e, _collateralAsset, _debtAsset, _borrower, _maxDebtToCover, _receiveSToken);

    assert lastReverted, "Call should have reverted, max debt is 0";
}

rule liqCallRevertWhen0DebtAsset(env e, address _collateralAsset, address _debtAsset, address _borrower, uint256 _maxDebtToCover, bool _receiveSToken) {
    nonSceneAddressRequirements(e.msg.sender);
    siloRequirements(e);

    // require _debtAsset == 0 // just calling the function with 0 for simplicity
    liquidationCall@withrevert(e, _collateralAsset, 0, _borrower, _maxDebtToCover, _receiveSToken);

    assert lastReverted, "Call should have reverted, debtAsset is 0";
}

rule liqCallRevertWhenDebtSiloIsAddressZero(env e, address _collateralAsset, address _debtAsset, address _borrower, uint256 _maxDebtToCover, bool _receiveSToken) {
    address debtSilo; address debtAsset; address collateralSilo; address collateralAsset;
    (debtSilo, debtAsset, collateralSilo, collateralAsset) = liqCallRevertSetup(e, _borrower, _maxDebtToCover);

    debtSiloFlag = true;
    liquidationCall@withrevert(e, _collateralAsset, _debtAsset, _borrower, _maxDebtToCover, _receiveSToken);
    require !lastHasThrown;
    assert lastReverted, "Call should have reverted, debtSilo is uninitialized";
}

rule liqCallRevertWhenUnexpectedCollateralToken(env e, address _collateralAsset, address _debtAsset, address _borrower, uint256 _maxDebtToCover, bool _receiveSToken) {
    address debtSilo; address debtAsset; address collateralSilo; address collateralAsset;
    (debtSilo, debtAsset, collateralSilo, collateralAsset) = liqCallRevertSetup(e, _borrower, _maxDebtToCover);

    require _collateralAsset != collateralAsset;
    liquidationCall@withrevert(e, _collateralAsset, _debtAsset, _borrower, _maxDebtToCover, _receiveSToken);

    assert lastReverted, "Call should have reverted, collateral token is unexpected";
}

rule liqCallRevertWhenUnexpectedDebtToken(env e, address _collateralAsset, address _debtAsset, address _borrower, uint256 _maxDebtToCover, bool _receiveSToken) {
    address debtSilo; address debtAsset; address collateralSilo; address collateralAsset;
    (debtSilo, debtAsset, collateralSilo, collateralAsset) = liqCallRevertSetup(e, _borrower, _maxDebtToCover);

    require _debtAsset != debtAsset;
    liquidationCall@withrevert(e, _collateralAsset, _debtAsset, _borrower, _maxDebtToCover, _receiveSToken);

    assert lastReverted, "Call should have reverted, debt token is unexpected";
}


rule liqCallRevertWhenExactAmountErrorNotNull(env e, address _collateralAsset, address _debtAsset, address _borrower, uint256 _maxDebtToCover, bool _receiveSToken) {
    address debtSilo; address debtAsset; address collateralSilo; address collateralAsset;
    (debtSilo, debtAsset, collateralSilo, collateralAsset) = liqCallRevertSetup(e, _borrower, _maxDebtToCover);

    liquidationCall@withrevert(e, _collateralAsset, _debtAsset, _borrower, _maxDebtToCover, _receiveSToken);
    require errorCodeCached != to_bytes4(0);

    assert lastReverted, "Call should have reverted when params.customError not empty";
}

rule liqCallRevertWhenDebtAssetExceedMaxCover(env e, address _collateralAsset, address _debtAsset, address _borrower, uint256 _maxDebtToCover, bool _receiveSToken) {
    address debtSilo; address debtAsset; address collateralSilo; address collateralAsset;
    (debtSilo, debtAsset, collateralSilo, collateralAsset) = liqCallRevertSetup(e, _borrower, _maxDebtToCover);

    liquidationCall@withrevert(e, _collateralAsset, _debtAsset, _borrower, _maxDebtToCover, _receiveSToken);
    require repayDebtAssetsCached > _maxDebtToCover;

    assert lastReverted, "Call should have reverted when repayDebtAsset exceeds maxDeDebtToCover";
}