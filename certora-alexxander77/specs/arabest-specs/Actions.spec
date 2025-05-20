import "../mocks/ShareTokenMock.spec";
import "../mocks/SiloLendingLibMock.spec";
import "../mocks/SiloERC4626LibMock.spec";
import "../mocks/General.spec";
import "../mocks/SiloConfig.spec";

using SiloHarness as Harness;

methods {
    function SiloStdLib.flashFee(
        address _config,
        address _token,
        uint256 _amount
    ) internal returns (uint256) => 1;

    function _.onFlashLoan( // IERC3156FlashBorrower, mocked in certora/mocks/EmptyFlashBorrower.sol
        address _initiator,
        address _token,
        uint256 _amount,
        uint256 _fee,
        bytes _data
    ) external => onFlashLoanMock() expect bytes32;

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

    function _.getConfigsForSolvency(address _borrower) external =>
        solvencyConfigsMock(_borrower) expect (ISiloConfig.ConfigData, ISiloConfig.ConfigData);

    function _.getConfigsForWithdraw(address _silo, address _depositOwner) external => CONSTANT;
    function _.getConfigsForBorrow(address _silo) external => CONSTANT;
    function _.getCollateralShareTokenAndAsset(address _silo, ISilo.CollateralType) external => CONSTANT;
    function _.getDebtShareTokenAndAsset(address _silo) external => CONSTANT;
    function CallBeforeQuoteLib.callSolvencyOracleBeforeQuote(ISiloConfig.ConfigData memory _config) internal => NONDET;
    function SiloStdLib.getFeesAndFeeReceiversWithAsset(address _silo) internal
        returns (address, address, uint256, uint256, address) => CONSTANT;
    function _.isSolvent(ISiloConfig.ConfigData memory _collateralConfig,
                       ISiloConfig.ConfigData memory _debtConfig,
                       address _borrower,
                       ISilo.AccrueInterestInMemory _accrueInMemory) internal => CONSTANT;
    function _.getConfig(address _silo) external => DISPATCHER(true);
    function _.balanceOf(address) external => DISPATCHER(true);
    function _.hookSetup() external => DISPATCHER(true);
    function _.safeTransfer(address token, address to, uint256 value) internal => safeTransferMock(token, to, value) expect (bool);

    function setHash0(bytes input) external envfree;
    function setHash1(bytes input) external envfree;
    function getHash0() external returns (bytes) envfree;
    function getHash1() external returns (bytes) envfree;
    function getAddressThis() external returns (address) envfree;
    function getCollateralConfig() external returns (ISiloConfig.ConfigData) envfree;
    function getDebtConfig() external returns (ISiloConfig.ConfigData) envfree;

    // switch collateral silo stuff
    function _.borrowerCollateralSilo(address _borrower) external =>
        mockBorrowerCollateralSilo(_borrower) expect (address);
    function _.setThisSiloAsCollateralSilo(address _borrower) external =>
        mockSetThisSiloAsCollateralSilo(_borrower) expect (bool);
    // update hooks things
    function _.hookReceiverConfig(address _silo) external => mockHookReceiverConfig(_silo) expect (uint24, uint24);
    function _.synchronizeHooks(uint24 _hooksBefore, uint24 _hooksAfter) external => DISPATCHER(true);
    function _.reentrancyGuardEntered() external => DISPATCHER(true);
}

function solvencyConfigsMock(address borrower) returns (ISiloConfig.ConfigData, ISiloConfig.ConfigData) {
    ISiloConfig.ConfigData collateralConfig = getCollateralConfig();
    ISiloConfig.ConfigData debtConfig = getDebtConfig();
    return (collateralConfig, debtConfig);
}
persistent ghost mathint safeTransferCalled;
persistent ghost mapping(mathint => address) _cacheListTokens;
persistent ghost mapping(mathint => address) _cacheListReceiver;
persistent ghost mapping(mathint => uint256) _cacheListValue;
function safeTransferMock(address token, address to, uint256 value) returns bool {
    _cacheListTokens[safeTransferCalled] = token;
    _cacheListReceiver[safeTransferCalled] = to;
    _cacheListValue[safeTransferCalled] = value;
    safeTransferCalled = safeTransferCalled + 1;
    return true;
}

function onFlashLoanMock() returns bytes32 {
    env e;
    return _FLASHLOAN_CALLBACK(e);
}

persistent ghost address _cachedAddress0;
persistent ghost uint256 _cachedAction0;
persistent ghost mathint _beforeActionCalled;

persistent ghost address _cachedAddress1;
persistent ghost uint256 _cachedAction1;
persistent ghost mathint _afterActionCalled;
function beforeActionMock(address _silo, uint256 _action, bytes _input) returns bool {
    _cachedAddress0 = _silo;
    _cachedAction0 = _action;
    setHash0(_input);
    _beforeActionCalled = _beforeActionCalled + 1;
    return true;
}
function afterActionMock(address _silo, uint256 _action, bytes _input) returns bool {
    _cachedAddress1 = _silo;
    _cachedAction1 = _action;
    setHash1(_input);
    _afterActionCalled = _afterActionCalled + 1;
    return true;
}

rule depositIntegrity(env e, uint256 assetsIn, uint256 sharesIn, address receiver, ISilo.CollateralType collateralType) {
    initState(e);

    address shareToken;
    address asset;
    (shareToken, asset) = getCollateralShareToken(e, collateralType);

    uint assets;
    uint shares;
    (assets, shares) = depositActions(e, assetsIn, sharesIn, receiver, collateralType);


    assert e.msg.sender == _cachedDepositor;
    assert assets == _cachedAsset;
    assert assetsIn == _cachedAsset;
    assert shares == _cachedShares;
    assert sharesIn == _cachedShares;
    assert receiver == _cachedReceiver;
    assert shareToken == _cachedCollateralShareToken;
    assert asset == _cachedToken;
    assert collateralType == _cachedCollateralType;

    uint256 action = getDepositAction(e, collateralType);
    bytes dataBefore = encodeDepositDataBefore(e, assetsIn, sharesIn, receiver);
    bytes dataAfter = encodeDepositDataAfter(e, assetsIn, sharesIn, receiver, assets, shares);
    assert checkHooks(e, action, dataBefore, dataAfter);
    assert !reentrancyProtection;
    assert _cachedSiloAddr == Harness;
}

rule withdrawIntegrity(env e, ISilo.WithdrawArgs args) {
    initState(e);

    ISiloConfig.DepositConfig depositConfig;
    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;
    (depositConfig, collateralConfig, debtConfig) = getWithdrawConfigs(e, args.owner);

    address tokenToBeChecked = args.collateralType == ISilo.CollateralType.Collateral
                                       ? depositConfig.collateralShareToken
                                       : depositConfig.protectedShareToken;

    uint assets;
    uint shares;
    (assets, shares) = withdrawActions(e, args);

    assert depositConfig.token == _cachedToken;
    assert tokenToBeChecked == _cachedShareToken;
    assert assets == args.assets;
    assert shares == args.shares;
    assert args.assets == _cachedArgsAssets;
    assert args.shares == _cachedArgsShares;
    assert args.receiver == _cachedArgsReceiver;
    assert args.owner == _cachedArgsOwner;
    assert args.spender == _cachedArgsSpender;
    assert args.collateralType == _cachedArgsCollateralType;

    uint256 action = getWithdrawAction(e, args.collateralType);
    bytes dataBefore = encodeWithdrawDataBefore(e, args.assets, args.shares, args.receiver, args.owner, args.spender);
    bytes dataAfter = encodeWithdrawDataAfter(e, args.assets, args.shares, args.receiver, args.owner, args.spender, assets, shares);
    assert checkHooks(e, action, dataBefore, dataAfter);
    assert !reentrancyProtection;
    assert _cachedSiloAddr == Harness;
}

rule borrowIntegrity(env e, ISilo.BorrowArgs args) {
    initState(e);

    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;

    (collateralConfig, debtConfig) = getBorrowConfigs(e);

    uint assets;
    uint shares;
    (assets, shares) = borrowActions(e, args);

    assert debtConfig.debtShareToken == _cachedToken;
    assert debtConfig.token == _cachedDebtAsset;
    assert assets == args.assets;
    assert shares == args.shares;
    assert args.assets == _cachedArgsAssets;
    assert args.shares == _cachedArgsShares;
    assert args.receiver == _cachedArgsReceiver;
    assert args.borrower == _cachedArgsBorrower;

    uint256 action = 4; // borrow action 2**2
    bytes dataBefore = encodeBorrowDataBefore(e, args, e.msg.sender);
    bytes dataAfter = encodeBorrowDataAfter(e, args, e.msg.sender, assets, shares);
    assert checkHooks(e, action, dataBefore, dataAfter);
    assert !reentrancyProtection;
    assert _cachedSiloAddr == Harness;
}

rule borrowSameAssetIntegrity(env e, ISilo.BorrowArgs args) {
    initState(e);

    ISiloConfig.ConfigData collateralConfig = getBaseConfig(e);
    ISiloConfig.ConfigData debtConfig = collateralConfig;

    uint assets;
    uint shares;
    (assets, shares) = borrowSameAssetActions(e, args);

    assert debtConfig.debtShareToken == _cachedToken;
    assert debtConfig.token == _cachedDebtAsset;
    assert assets == args.assets;
    assert shares == args.shares;
    assert args.assets == _cachedArgsAssets;
    assert args.shares == _cachedArgsShares;
    assert args.receiver == _cachedArgsReceiver;
    assert args.borrower == _cachedArgsBorrower;

    uint256 action = 8; // borrow same asset action 2**3
    bytes dataBefore = encodeBorrowDataBefore(e, args, e.msg.sender);
    bytes dataAfter = encodeBorrowDataAfter(e, args, e.msg.sender, assets, shares);
    assert checkHooks(e, action, dataBefore, dataAfter);
    assert !reentrancyProtection;
    assert _cachedSiloAddr == Harness;
}

rule repayIntegrity(env e, uint256 assetsIn, uint256 sharesIn, address borrower, address repayer) {
    initState(e);

    address _token;
    address _debtAsset;
    (_token, _debtAsset) = getDebtShareToken(e);

    uint _assets;
    uint _shares;
    (_assets, _shares) = repayActions(e, assetsIn, sharesIn, borrower, repayer);

    assert _assets == _cachedAsset;
    assert assetsIn == _cachedAsset;
    assert _shares == _cachedShares;
    assert sharesIn == _cachedShares;
    assert borrower == _cachedBorrower;
    assert repayer == _cachedRepayer;
    assert _token == _cachedToken;
    assert _debtAsset == _cachedDebtAsset;
//    assert checkHooks(e, 16); // repay action 2**4

    uint256 action = 16; // repay action 2**4
    bytes dataBefore = encodeRepayDataBefore(e, assetsIn, sharesIn, borrower, repayer);
    bytes dataAfter = encodeRepayDataAfter(e, assetsIn, sharesIn, borrower, repayer, _assets, _shares);
    assert checkHooks(e, action, dataBefore, dataAfter);
    assert !reentrancyProtection;
    assert _cachedSiloAddr == Harness;
}

rule transitionCollateralIntegrity(env e, ISilo.TransitionCollateralArgs args) {
    initState(e);

    ISiloConfig.DepositConfig depositConfig;
    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;
    (depositConfig, collateralConfig, debtConfig) = getWithdrawConfigs(e, args.owner);

    address shareTokenFrom = args.transitionFrom == ISilo.CollateralType.Collateral
                                       ? depositConfig.collateralShareToken
                                       : depositConfig.protectedShareToken;


    ISilo.CollateralType depositType; address shareTokenTo;
    if (args.transitionFrom == ISilo.CollateralType.Collateral) {
        depositType = ISilo.CollateralType.Protected;
        shareTokenTo = depositConfig.protectedShareToken;
    } else {
        depositType = ISilo.CollateralType.Collateral;
        shareTokenTo = depositConfig.collateralShareToken;
    }

    uint assets;
    uint shares;
    (assets, shares) = transitionCollateralActions(e, args);

    // from withdraw
    assert 0 == _cachedToken;
    assert shareTokenFrom == _cachedShareToken;
    assert 0 == _cachedArgsAssets;
    assert args.shares == _cachedArgsShares;
    assert args.owner == _cachedArgsReceiver;
    assert args.owner == _cachedArgsOwner;
    assert e.msg.sender == _cachedArgsSpender;
    assert args.transitionFrom == _cachedArgsCollateralType;

    // from deposit
    assert 0 == _cachedToken;
    assert e.msg.sender == _cachedDepositor;
    assert 0 == _cachedAsset;
    assert 0 == _cachedShares;
    assert args.owner == _cachedReceiver;
    assert shareTokenTo == _cachedCollateralShareToken;
    assert depositType == _cachedCollateralType;

    uint256 action = getTransitionCollateralActionAction(e, args.transitionFrom);
    bytes dataBefore = encodeTransitionCollateralBefore(e, args.shares, args.owner);
    bytes dataAfter = encodeTransitionCollateralAfter(e, assets, args.owner, shares);
    assert checkHooks(e, action, dataBefore, dataAfter);
    assert !reentrancyProtection;
    assert _cachedSiloAddr == Harness;
}

persistent ghost mapping(address => address) borrowerSilos;
persistent ghost mathint _set;
function mockBorrowerCollateralSilo(address borrower) returns address {
    if (_set == 0) {
        return getAddressThis();
    } else if (_set == 1) {
        require borrowerSilos[borrower] != getAddressThis();
        return borrowerSilos[borrower];
    } else {
        return getAddressThis();
    }
}
function mockSetThisSiloAsCollateralSilo(address borrower) returns bool {
    _set = 2;
    return true;
}
rule switchCollateralIntegrity(env e) {
    initState(e);
    _set = 1;
    switchCollateral(e);

    uint256 action = 256; // switch collateral action 2**8
    bytes dataBefore = encodeSwitchCollateralDataBefore(e, e.msg.sender);
    bytes dataAfter = encodeSwitchCollateralDataAfter(e, e.msg.sender);
    assert checkHooks(e, action, dataBefore, dataAfter);
    assert !reentrancyProtection;

    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;
    (collateralConfig, debtConfig) = getSolvencyConfigs(e);
    assert (debtConfig.silo != 0) => (_cachedSiloAddr == Harness);
}
rule switchCollateralRevertConditions(env e) {
    initState(e);
    havoc _set assuming _set@new == 0 || _set@new == 1;

    bool siloSetBefore = _set == 0;

    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;
    setCollateralConfig(e, collateralConfig);
    setDebtConfig(e, debtConfig);
    bool solventUser = solvencyCheck(e, collateralConfig, debtConfig, e.msg.sender, ISilo.AccrueInterestInMemory.No);
    bool solvency = debtConfig.silo != 0;

    switchCollateral@withrevert(e);

    assert ((solvency && !solventUser) || siloSetBefore) == lastReverted;
    assert !lastReverted => _set == 2;
}

function initState(env e) {
    _beforeActionCalled = 0;
    _afterActionCalled = 0;
    reentrancyProtection = false;
    initialize(e, siloConfigHelper(e));
}
function checkHooks(env e, uint256 action, bytes dataBefore, bytes dataAfter) returns bool {
    // if action matches the bitmask, then before/after action should have been called exactly once.
    // otherwise, actions would be called 0 times.
    bool c1 = matchAction(e, getHooksBefore(e), action) == (_beforeActionCalled == 1);
    bool c2 = matchAction(e, getHooksAfter(e), action) == (_afterActionCalled == 1);
    // if before/after action was called, then _cachedActions should contain the action value
    bool c3 = matchAction(e, getHooksBefore(e), action) && (_beforeActionCalled == 1)
        => action == _cachedAction0
        && dataBefore == getHash0()
        && getAddressThis() == _cachedAddress0;
    bool c4 = matchAction(e, getHooksAfter(e), action) && (_afterActionCalled == 1)
        => action == _cachedAction1
        && dataAfter == getHash1()
        && getAddressThis() == _cachedAddress1;
    return c1 && c2 && c3 && c4;
}

persistent ghost uint24 _cacheHookBefore;
persistent ghost uint24 _cacheHookAfter;

persistent ghost mapping(address => uint24) hooksForAddressBefore;
persistent ghost mapping(address => uint24) hooksForAddressAfter;

function mockHookReceiverConfig(address silo) returns (uint24, uint24) {
    uint24 hook1;
    uint24 hook2;
    hook1 = hooksForAddressBefore[silo];
    hook2 = hooksForAddressAfter[silo];
    return (hook1, hook2);
}

rule updateHooksReverts(env e) {
    initialize(e, siloConfigHelper(e));
    ISiloConfig.ConfigData cfg = getBaseConfig(e);
    bool reentrantOn = siloConfigHelper(e).reentrancyGuardEntered(e);


    updateHooksAction@withrevert(e);
    bool _cacheReverted = lastReverted;

    bool c1 = getAddressThis() != cfg.collateralShareToken.silo(e);
    bool c2 = getAddressThis() != cfg.protectedShareToken.silo(e);
    bool c3 = getAddressThis() != cfg.debtShareToken.silo(e);

    assert _cacheReverted == (reentrantOn || c1 || c2 || c3);
}

rule withdrawFeesIntegrity(env e, address _silo) {
    safeTransferCalled = 0;
    initState(e);
    address daoFeeReceiver; address deployerFeeReceiver; uint256 daoFee; uint256 deployerFee; address asset;
    (daoFeeReceiver,deployerFeeReceiver,daoFee,deployerFee,asset) = getFeesAndFeeReceivers(e, _silo);

    // calculations for return params in else block
    require (daoFee + deployerFee) != 0;
    uint256 siloBalance = getBalanceOfToken(e, asset, getAddressThis());
    uint256 protectedAssets = getProtectedAssets(e);
    require protectedAssets <= siloBalance;
    uint256 availableLiquidity = require_uint256(siloBalance - protectedAssets);
    uint256 earnedFees;
    if (getDaoAndDeployerRevenue(e) > availableLiquidity) {
        earnedFees = availableLiquidity;
    } else {
        earnedFees = getDaoAndDeployerRevenue(e);
    }
    require earnedFees * daoFee < MAX_UINT256(e);
    require daoFee + deployerFee < MAX_UINT256(e);
    uint256 expectedDaoRevenue1 = require_uint256(earnedFees * daoFee);
    uint256 expectedDaoRevenue2 = require_uint256(expectedDaoRevenue1 / (daoFee + deployerFee));
    uint256 expectedDeployerRevenue = require_uint256(earnedFees - expectedDaoRevenue2);

    uint256 daoRevenue; uint256 deployerRevenue;
    (daoRevenue, deployerRevenue) = withdrawFee(e, _silo);

    // return values never touched in if
    assert (deployerFeeReceiver == 0) => (
        // return params
        (safeTransferCalled == 1) &&
        (daoRevenue == 0) &&
        (deployerRevenue == 0) &&
        // transfer params
        (_cacheListTokens[0]) == asset &&
        (_cacheListReceiver[0]) == daoFeeReceiver &&
        (_cacheListValue[0]) == earnedFees
    );
    // else values
    assert (deployerFeeReceiver != 0) => (
        // return params
        (safeTransferCalled == 2) &&
        (daoRevenue == expectedDaoRevenue2) &&
        (deployerRevenue == expectedDeployerRevenue) &&
        // transfer 1 params
        (_cacheListTokens[0]) == asset &&
        (_cacheListReceiver[0]) == daoFeeReceiver &&
        (_cacheListValue[0]) == daoRevenue &&
        // transfer 2 params
        (_cacheListTokens[1]) == asset &&
        (_cacheListReceiver[1]) == deployerFeeReceiver &&
        (_cacheListValue[1]) == deployerRevenue
    );
    assert !reentrancyProtection;
}

rule callOnBehalfOfSiloRevertCondition(env e) {
    require e.msg.value == 0;
    bool isInit = getStorage(e).siloConfig != 0;
    initialize(e, siloConfigHelper(e));

    address hookReceiver = getStoredHookReceiver(e);

    assert
       (getStorage(e).silo == silo(e)
       && getStorage(e).siloConfig == siloConfigHelper(e)

       && hookReceiver == hookReceiverHelper(e)
       && getStoredTokenType(e) == 2048 // collateral token 2**11
       && getStorage(e).transferWithChecks
       );

    address _target; uint256 _value; ISilo.CallType _callType; bytes _input;

    _called = false;
    _delegatecalled = false;

    callOnBehalfOfSilo@withrevert(e, _target, _value, _callType, _input);
    bool _cacheRevert = lastReverted;
    assert (e.msg.sender == hookReceiver) == !_cacheRevert;

}

rule callOnBehalfOfSiloCorrectCall(env e) {
    address _target; uint256 _value; ISilo.CallType _callType; bytes _input;

    _cacheTarget = _target;
    _called = false;
    _delegatecalled = false;

    bool success; bytes result;
    (success, result) = callOnBehalfOfSilo(e, _target, _value, _callType, _input);

    assert (_callType == ISilo.CallType.Delegatecall) == (_delegatecalled && !_called);
    assert (_callType != ISilo.CallType.Delegatecall) == (_called && !_delegatecalled && (_value == _cacheValue)) ;
    assert _input.length == _cacheLen;
}

persistent ghost address _cacheTarget;
persistent ghost uint _cacheValue;
persistent ghost uint _cacheLen;
persistent ghost bool _called;
persistent ghost bool _delegatecalled;

hook CALL(uint g, address addr, uint value, uint argsOffset, uint argsLength, uint retOffset, uint retLength) uint rc {
    if (addr == _cacheTarget) {
        _cacheValue = value;
        _called = true;
        _cacheLen = argsLength;
    }
}

hook DELEGATECALL(uint g, address addr, uint argsOffset, uint argsLength, uint retOffset, uint retLength) uint rc {
    if (addr == _cacheTarget) {
        _delegatecalled = true;
        _cacheLen = argsLength;
    }
}