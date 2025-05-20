import "General.spec";

methods {
    function SiloERC4626Lib.deposit(
        address _token,
        address _depositor,
        uint256 _assets,
        uint256 _shares,
        address _receiver,
        address _collateralShareToken,
        ISilo.CollateralType _collateralType
    ) internal returns (uint256, uint256) =>
        depositMock4626(_token, _depositor, _assets, _shares, _receiver, _collateralShareToken, _collateralType);

    function SiloERC4626Lib.withdraw(
        address _asset,
        address _shareToken,
        ISilo.WithdrawArgs memory _args
    ) internal returns (uint256, uint256) =>
        withdrawMock4626(_asset, _shareToken, _args);

    function SiloERC4626Lib.maxWithdraw(
            address _owner,
            ISilo.CollateralType _collateralType,
            uint256 _totalAssets
        ) internal returns (uint256, uint256) =>
            maxWithdrawMock(_owner, _collateralType, _totalAssets);
}

function depositMock4626(
    address _token,
    address _depositor,
    uint256 _assets,
    uint256 _shares,
    address _receiver,
    address _collateralShareToken,
    ISilo.CollateralType _collateralType
) returns (uint256, uint256) {
    _cachedToken = _token;
    _cachedDepositor = _depositor;
    _cachedAsset = _assets;
    _cachedShares = _shares;
    _cachedReceiver = _receiver;
    _cachedCollateralShareToken = _collateralShareToken;
    _cachedCollateralType = _collateralType;

    return (_assets, _shares);
}

function withdrawMock4626(
    address _asset,
    address _shareToken,
    ISilo.WithdrawArgs _args
) returns (uint256, uint256) {
    _cachedToken = _asset;
    _cachedShareToken = _shareToken;

    _cachedArgsAssets = _args.assets;
    _cachedArgsShares = _args.shares;
    _cachedArgsReceiver = _args.receiver;
    _cachedArgsOwner = _args.owner;
    _cachedArgsSpender = _args.spender;
    _cachedArgsCollateralType = _args.collateralType;

    return (_args.assets, _args.shares);
}

function maxWithdrawMock(address _owner, ISilo.CollateralType _collateralType, uint256 _totalAssets) returns (uint256, uint256) {
    _cachedOwner = _owner;
    _cachedCollateralType = _collateralType;
    return (_passedAssets, _passedShares);
}