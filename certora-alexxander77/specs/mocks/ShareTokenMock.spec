

methods {
    function ShareToken._afterTokenTransfer(
        address _sender,
        address _recipient,
        uint256 _amount
    ) internal =>
    afterTokenTransferMock(_sender, _recipient, _amount);

    function ShareToken._crossNonReentrantBefore()
        internal returns (address) => NONDET;

    function _.turnOffReentrancyProtection() external => turnOffReentrancyMock() expect void;
    function _.turnOnReentrancyProtection() external => turnOnReentrancyMock() expect void;

    function ShareCollateralTokenLib.isSolventAfterCollateralTransfer(
        address _sender
    ) external returns (bool) => isSolventAfterCollateralTransferMock(_sender);
}

ghost address _cachedSender;
ghost address _cachedRecipient;
ghost uint256 _cachedAmount;

function afterTokenTransferMock(address _sender, address _recipient, uint256 _amount) {
    _cachedSender = _sender;
    _cachedRecipient = _recipient;
    _cachedAmount = _amount;
}

persistent ghost bool userSolvency;
function isSolventAfterCollateralTransferMock(address _sender) returns bool {
    return userSolvency;
}

persistent ghost bool reentrancyProtection;
function turnOffReentrancyMock() {
    assert reentrancyProtection;
    reentrancyProtection = false;
}
function turnOnReentrancyMock() {
    assert !reentrancyProtection;
    reentrancyProtection = true;
}