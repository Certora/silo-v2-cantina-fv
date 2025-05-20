import "General.spec";

methods {
    function Actions.deposit(
        uint256 _assets, uint256 _shares, address _receiver, ISilo.CollateralType _collateralType
    ) external returns (uint256, uint256) =>
        depositMock(_assets, _shares, _receiver, _collateralType);

    function Actions.withdraw(
        ISilo.WithdrawArgs _args
    ) external returns (uint256, uint256) =>
        withdrawMock(_args);

    function Actions.callOnBehalfOfSilo(
        address _target, uint256 _value, ISilo.CallType _callType, bytes calldata _input
    ) internal returns (bool, bytes memory) =>
        callOnBehalfOfSiloMock(_target, _value, _callType, _input);

    function Actions.updateHooks() external returns (uint24, uint24) =>
        updateHooksMock();

    function setHash0(bytes input) external envfree;
    function setHash1(bytes input) external envfree;
    function getHash0() external returns (bytes) envfree;
    function getHash1() external returns (bytes) envfree;

    function Views.maxRepay(address _borrower) external returns (uint256) =>
        maxMock(_borrower);
    function Views.maxFlashLoan(address _token) internal returns (uint256) =>
        maxMock(_token);
}

function depositMock(
    uint256 _assets,
    uint256 _shares,
    address _receiver,
    ISilo.CollateralType _collateralType
) returns (uint256, uint256) {
    _cachedAsset = _assets;
    _cachedShares = _shares;
    _cachedReceiver = _receiver;
    _cachedCollateralType = _collateralType;

    return (_assets, _shares);
}

function withdrawMock(
    ISilo.WithdrawArgs args
) returns (uint256, uint256) {
    _cachedAsset = args.assets;
    _cachedShares = args.shares;
    _cachedReceiver = args.receiver;
    _cachedOwner = args.owner;
    _cachedSpender = args.spender;
    _cachedCollateralType = args.collateralType;

    return (args.assets, args.shares);
}

function callOnBehalfOfSiloMock(address _target, uint256 _value, ISilo.CallType _callType, bytes _input) returns (bool, bytes) {
    _cachedTarget = _target;
    _cachedValue = _value;
    _cachedCallType = _callType;
    setHash0(_input);
    bytes _returnedData;
    setHash1(_returnedData);
    return (_returnedSuccess, _returnedData);
}

function updateHooksMock() returns (uint24, uint24) {
    _actionCalled = true;
    return (0,0);
}
function maxMock(address _owner) returns uint256 {
    _cachedOwner = _owner;
    return _passedAssets;
}