import "../mocks/General.spec";

using FlashLoanHarness as Harness;
using Token0 as Token0;

methods {
    function _.beforeAction(
        address _silo,
        uint256 _action,
        bytes _input
    ) external => beforeActionMock(_silo, _action, _input) expect (bool);

    function _.afterAction(
        address _silo,
        uint256 _action,
        bytes _inputAndOutput
    ) external => afterActionMock(_silo, _action, _inputAndOutput) expect (bool);

    function getFlashFeeOpt(address, uint256) external returns(uint256, address, uint256) envfree;
    function getHooksAfter() external returns (uint24) envfree;
    function getHooksBefore() external returns (uint24) envfree;

    function _.getConfig(address _silo) external => DISPATCHER(true);
    function _.getAssetForSilo(address _silo) external => DISPATCHER(true);
    function _.balanceOf(address) external => DISPATCHER(true);
    function _.transfer(address,uint256)             external => DISPATCHER(true);
    function _.transferFrom(address,address,uint256) external => DISPATCHER(true);
    function _.onFlashLoan(address,address,uint256,uint256,bytes) external => DISPATCHER(true);

    function FlashLoanHarness.transfer(address, uint256) external returns(bool) => NONDET;
    function FlashLoanHarness.transferFrom(address,address, uint256) external returns(bool) => NONDET;

    function ShareCollateralTokenLib.isSolventAfterCollateralTransfer(
        address _sender
    ) external returns (bool) => NONDET;

    function _.getFeesWithAsset(address _silo) external => DISPATCHER(true);


}

// for events
persistent ghost bytes32 _eventSignature;

hook LOG1(uint offset, uint length, bytes32 t1) {
    _eventSignature = t1;
}

persistent ghost mathint _beforeActionCalled;
persistent ghost mathint _afterActionCalled;

function beforeActionMock(address _silo, uint256 _action, bytes _input) returns bool {

    _beforeActionCalled = _beforeActionCalled + 1;
    return true;
}
function afterActionMock(address _silo, uint256 _action, bytes _input) returns bool {

    _afterActionCalled = _afterActionCalled + 1;
    return true;
}

function minimalInitHookState() {
    _beforeActionCalled = 0;
    _afterActionCalled = 0;
}

/* ------------------------------------ Flash Loans --------------------------------------------- */
rule maxFlashLoanCorrect(env e, address token) {

    initialize(e, siloConfigHelper(e));

    address targetAsset = getAssetForSilo(e);
    uint256 protectedAssets = getProtectedAssets(e);
    uint256 contractAssetBalance = getBalanceOfToken(e, targetAsset, currentContract);

    uint256 maxFlashLoan = maxFlashLoan(e, token);

    if(targetAsset == token) {
        assert (contractAssetBalance > protectedAssets) => (maxFlashLoan == (contractAssetBalance - protectedAssets));
        assert (contractAssetBalance <= protectedAssets => (maxFlashLoan == 0));
    }
    else {
        assert maxFlashLoan == 0;
    }
}

rule flashLoanHooks(env e, calldataarg args, address token, address receiver, uint256 amount, bytes data) {
    minimalInitHookState();
    initialize(e, siloConfigHelper(e));
    require(receiver == flashLoanReceiverHelper(e));

    address asset = getAssetForSilo(e);
    // 2**6 is flash loan hook
    bool hookBeforeEnabled = matchAction(e, getHooksBefore(), 64);
    bool hookAfterEnabled = matchAction(e, getHooksAfter(), 64);

    uint256 balanceFlashReceiverBefore = getBalanceOfToken(e, asset, flashLoanReceiverHelper(e));

    bool success = flashLoan(e, receiver, token, amount, data);

    uint256 checkpointBalanceFlashReceiver = getRecordedBalanceFlashReceiver(e);
    assert (hookBeforeEnabled == (_beforeActionCalled == 1));
    assert (hookAfterEnabled == (_afterActionCalled == 1));
    assert checkpointBalanceFlashReceiver == balanceFlashReceiverBefore + amount;
}

rule flashLoanHooksParams(env e, calldataarg args, address token, address receiver, uint256 amount, bytes data) {
    address siloConfigHelper = siloConfigHelper(e);
    minimalInitHookState();
    initialize(e, siloConfigHelper);
    require(receiver == flashLoanReceiverHelper(e));
    address asset;
    uint256 fee;
    uint256 calculatedFee;

    (fee, asset, calculatedFee) = getFlashFeeOpt(siloConfigHelper, amount);

    bool success = flashLoan(e, receiver, token, amount, data);

    uint256 checkpointBalanceFlashReceiver;
    address cachedInitiator;
    address cachedToken;
    uint256 cachedAmount;
    uint256 cachedFee;

    (checkpointBalanceFlashReceiver,cachedInitiator,cachedToken,cachedAmount,cachedFee) = getRecordedParamsOnFlashLoan(e);

    assert cachedInitiator == e.msg.sender;
    assert cachedToken == token;
    assert cachedAmount == amount;
    assert cachedFee == calculatedFee;
}

rule flashLoanFeeAndBalances(env e, calldataarg args, address token, address receiver, uint256 amount, bytes data) {
    address siloConfigHelper = siloConfigHelper(e);
    minimalInitHookState();
    initialize(e, siloConfigHelper);
    require(data.length == 0);
    uint256 fee;
    uint256 calculatedFee;
    address asset;
    uint192 daoRevenueCached = getDaoAndDeployerRevenue(e);
    (fee, asset, calculatedFee) = getFlashFeeOpt(siloConfigHelper, amount);
    uint256 assetBalanceContractBefore = getBalanceOfToken(e, asset, currentContract);
    uint256 assetBalanceReceiverBefore = getBalanceOfToken(e, asset, receiver);
    require(fee < 500000000000000000);
    bool success = flashLoan(e, receiver, token, amount, data);
    uint256 assetBalanceContractAfter = getBalanceOfToken(e, asset, currentContract);
    uint256 assetBalanceReceiverAfter = getBalanceOfToken(e, asset, receiver);

    assert getDaoAndDeployerRevenue(e) == daoRevenueCached + calculatedFee;
    assert assetBalanceContractAfter == assetBalanceContractBefore + calculatedFee;
    assert assetBalanceReceiverAfter == assetBalanceReceiverBefore - calculatedFee;
}
