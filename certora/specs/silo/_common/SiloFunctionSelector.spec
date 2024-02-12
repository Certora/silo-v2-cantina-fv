import "./SiloFunctionSig.spec";

function siloFnSelectorWithAssets(env e, method f, uint256 assetsOrShares) {
    address receiver;
    siloFnSelector(e, f, assetsOrShares, receiver);
}

function siloFnSelector(
    env e,
    method f,
    uint256 assetsOrShares,
    address receiver
) {
    require e.block.timestamp < max_uint64;
    require receiver != currentContract;

    if (f.selector == depositSig()) {
        deposit(e, assetsOrShares, receiver);
    } else if (f.selector == depositWithTypeSig()) {
        ISilo.AssetType anyType;
        deposit(e, assetsOrShares, receiver, anyType);
    } else if (f.selector == flashLoanSig()) {
        address token;
        bytes data;

        flashLoan(e, receiver, token, assetsOrShares, data);
    } else if (f.selector == mintSig()) {
        mint(e, assetsOrShares, receiver);
    } else if (f.selector == mintWithTypeSig()) {
        ISilo.AssetType anyType;
        mint(e, assetsOrShares, receiver, anyType);
    } else if (f.selector == borrowSig()) {
        address anyBorrower;
        borrow(e, assetsOrShares, receiver, anyBorrower);
    } else if (f.selector == borrowSharesSig()) {
        address anyBorrower;
        borrowShares(e, assetsOrShares, receiver, anyBorrower);
    } else if (f.selector == leverageSig()) {
        address anyBorrower;
        bytes data;
        require anyBorrower != currentContract;
        leverage(e, assetsOrShares, receiver, anyBorrower, data);
    } else if (f.selector == repaySig()) {
        address anyBorrower;
        require anyBorrower != currentContract;
        repay(e, assetsOrShares, anyBorrower);
    } else if (f.selector == repaySharesSig()) {
        address anyBorrower;
        require anyBorrower != currentContract;
        repayShares(e, assetsOrShares, anyBorrower);
    } else if (f.selector == transitionCollateralSig()) {
        ISilo.AssetType anyType;
        transitionCollateral(e, assetsOrShares, receiver, anyType);
    } else {
        calldataarg args;
        f(e, args);
    }
}