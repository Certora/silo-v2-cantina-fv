import "General.spec";

methods {
    function SiloLendingLib.repay(
         address _debtShareToken,
         address _debtAsset,
         uint256 _assets,
         uint256 _shares,
         address _borrower,
         address _repayer
     ) internal returns (uint256, uint256) =>
        repayMock(_debtShareToken, _debtAsset, _assets, _shares, _borrower, _repayer);

    function SiloLendingLib.borrow(
        address _debtShareToken,
        address _token,
        address _spender,
        ISilo.BorrowArgs memory _args
    ) internal returns (uint256, uint256) =>
        borrowMock(_debtShareToken, _token, _spender, _args);

    function SiloLendingLib.maxBorrow(address _borrower, bool _sameAsset)
            internal returns (uint256, uint256) =>
            maxBorrowMock(_borrower, _sameAsset);
}

function repayMock(
     address _debtShareToken,
     address _debtAsset,
     uint256 _assets,
     uint256 _shares,
     address _borrower,
     address _repayer
) returns (uint256, uint256) {
    _cachedToken = _debtShareToken;
    _cachedDebtAsset = _debtAsset;
    _cachedAsset = _assets;
    _cachedShares = _shares;
    _cachedBorrower = _borrower;
    _cachedRepayer = _repayer;

    return (_assets, _shares);
}
function borrowMock(
    address _debtShareToken,
    address _token,
    address _spender,
    ISilo.BorrowArgs _args
) returns (uint256, uint256) {
    _cachedToken = _debtShareToken;
    _cachedDebtAsset = _token;
    _cachedSpender = _spender;

    _cachedArgsAssets = _args.assets;
    _cachedArgsShares = _args.shares;
    _cachedArgsReceiver = _args.receiver;
    _cachedArgsBorrower = _args.borrower;

    return (_args.assets, _args.shares);
}

function maxBorrowMock(address _borrower, bool _sameAsset) returns (uint256, uint256) {
    _cachedOwner = _borrower;
    _cachedSameAsset = _sameAsset;
    return (_passedAssets, _passedShares);
}