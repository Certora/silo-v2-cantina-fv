import "../mocks/General.spec";
import "../mocks/ActionsMock.spec";
import "../mocks/SiloMathLibMock.spec";
import "../mocks/SiloStdLibMock.spec";
import "../mocks/SiloERC4626LibMock.spec";
import "../mocks/SiloLendingLibMock.spec";

using SiloHarness as Harness;

methods {
    function getHooksAfter() external returns (uint24) envfree;
    function getHooksBefore() external returns (uint24) envfree;
    function getStoredTokenType() external returns (uint24) envfree;

    function _.balanceOf(address) external => DISPATCHER(true);
    function _.getConfig(address _silo) external => DISPATCHER(true);
}

ghost uint256 _assetsReturned;
ghost uint256 _sharesReturned;

// for events
persistent ghost bytes32 _eventSignature;
persistent ghost bytes32 _eventReceiver;
persistent ghost bytes32 _eventSender;
persistent ghost bytes32 _eventOwner;

hook LOG1(uint offset, uint length, bytes32 t1) {
    _eventSignature = t1;
}

hook LOG3(uint offset, uint length, bytes32 t1, bytes32 t2, bytes32 t3) {
    _eventSignature = t1;
    _eventSender = t2;
    _eventReceiver = t3;
}
hook LOG4(uint offset, uint length, bytes32 t1, bytes32 t2, bytes32 t3, bytes32 t4) {
    _eventSignature = t1;
    _eventSender = t2;
    _eventReceiver = t3;
    _eventOwner = t4;
}



/* ------------------------------------ Deposit ------------------------------------ */
/**
    This rule validates that the _deposit() function in Silo correctly passes on its parameters and
    that it correctly calls the appropriate event (deposit/depositProtected) and it does not
    modify shares/assets after execution.
**/
rule depositInternal(env e, uint256 _assets, uint256 _shares, address _receiver, ISilo.CollateralType _collateralType) {
    (_assetsReturned, _sharesReturned) = depositHarness(e, _assets, _shares, _receiver, _collateralType);
    verifyDepositParams(e, _assets, _shares, _receiver, _collateralType, true, true);
}
rule depositExternal1(env e, uint256 _assets, address _receiver) {
    _sharesReturned = deposit(e, _assets, _receiver);
    verifyDepositParams(e, _assets, 0, _receiver, ISilo.CollateralType.Collateral, false, true);
}
rule depositExternal2(env e, uint256 _assets, address _receiver, ISilo.CollateralType _collateralType) {
    _sharesReturned = deposit(e, _assets, _receiver, _collateralType);
    verifyDepositParams(e, _assets, 0, _receiver, _collateralType, false, true);
}
rule mintExternal2(env e, uint256 _shares, address _receiver, ISilo.CollateralType _collateralType) {
    _assetsReturned = mint(e, _shares, _receiver, _collateralType);
    verifyDepositParams(e, 0, _shares, _receiver, _collateralType, true, false);
}
rule mintExternal1(env e, uint256 _shares, address _receiver) {
    _assetsReturned = mint(e, _shares, _receiver);
    verifyDepositParams(e, 0, _shares, _receiver, ISilo.CollateralType.Collateral, true, false);
}
function verifyDepositParams(env e, uint256 _assets, uint256 _shares, address _receiver, ISilo.CollateralType _collateralType, bool checkReturnedAssets, bool checkReturnedShares) {
    // parameters passed to internal function unmodified
    assert _assets == _cachedAsset;
    assert _shares == _cachedShares;
    assert _receiver == _cachedReceiver;
    assert _collateralType == _cachedCollateralType;

    // verify returned values were not unmodified
    assert checkReturnedAssets => (_assets == _assetsReturned);
    assert checkReturnedShares => (_shares == _sharesReturned);

    // event checks
    assert hashAddress(e, _eventSender, e.msg.sender);
    assert hashAddress(e, _eventReceiver, _receiver);
    if (_collateralType == ISilo.CollateralType.Collateral) {
        assert _eventSignature == hashSignature(e, 0);
    } else {
        assert _eventSignature == hashSignature(e, 1);
    }
}

/**
    This function validates whether the _previewMint() function in Silo correctly
    passes its parameters to the internal functions it uses & if the returned value
    is the expected one.
**/
rule mintPreviewInternal(env e, uint256 _shares, ISilo.CollateralType _collateralType) {
    _passedShares = _shares;
    _previewType = 0;
    _sharesReturned = previewMintHarness(e, _shares, _collateralType);

    assert verifyPreviewParams(e, ROUNDING_mint(e), _shares, _collateralType);
}
rule mintPreviewExternal1(env e, uint256 _shares) {
    _passedShares = _shares;
    _previewType = 0;
    _sharesReturned = previewMint(e, _shares, ISilo.CollateralType.Collateral);

    assert verifyPreviewParams(e, ROUNDING_mint(e), _shares, ISilo.CollateralType.Collateral);
}
rule mintPreviewExternal2(env e, uint256 _shares, ISilo.CollateralType _collateralType) {
    _passedShares = _shares;
    _previewType = 0;
    _sharesReturned = previewMint(e, _shares, _collateralType);

    assert verifyPreviewParams(e, ROUNDING_mint(e), _shares, _collateralType);
}

rule maxDepositIntegrity(env e, address _owner) {
    uint256 expectedMaxDeposit = maxDeposit(e, _owner);
    assert expectedMaxDeposit == MAX_UINT256(e);
}
rule maxMintIntegrity(env e, address _owner) {
    uint256 expectedMaxMint = maxMint(e, _owner);
    assert expectedMaxMint == MAX_UINT256(e);
}
rule maxWithdrawIntegrity(env e, address _owner) {
    uint256 expectedMaxWithdraw = maxWithdraw(e, _owner);
    assert _owner == _cachedOwner;
    assert expectedMaxWithdraw == _passedAssets;
    assert _cachedCollateralType == ISilo.CollateralType.Collateral;
}
rule maxRedeemIntegrity(env e, address _owner) {
    uint256 expectedMaxRedeem = maxRedeem(e, _owner);
    assert _owner == _cachedOwner;
    assert expectedMaxRedeem == _passedShares;
    assert _cachedCollateralType == ISilo.CollateralType.Collateral;
}
rule maxWithdrawIntegrityWithType(env e, address _owner, ISilo.CollateralType _collateralType) {
    uint256 expectedMaxWithdrawWithType = maxWithdraw(e, _owner, _collateralType);
    assert _owner == _cachedOwner;
    assert expectedMaxWithdrawWithType == _passedAssets;
    assert _cachedCollateralType == _collateralType;
}
rule maxRedeemIntegrityWithType(env e, address _owner, ISilo.CollateralType _collateralType) {
    uint256 expectedMaxRedeemWithType = maxRedeem(e, _owner, _collateralType);
    assert _owner == _cachedOwner;
    assert expectedMaxRedeemWithType == _passedShares;
    assert _cachedCollateralType == _collateralType;
}
rule maxBorrowSharesIntegrity(env e, address _owner) {
    uint256 expectedMaxBorrowShares = maxBorrowShares(e, _owner);
    assert _owner == _cachedOwner;
    assert expectedMaxBorrowShares == _passedShares;
    assert _cachedSameAsset == false;
}
rule maxBorrowSameAssetIntegrity(env e, address _owner) {
    uint256 expectedMaxBorrowSameAssetsShares = maxBorrowSameAsset(e, _owner);
    assert _owner == _cachedOwner;
    assert expectedMaxBorrowSameAssetsShares == _passedAssets;
    assert _cachedSameAsset == true;
}
rule maxRepayIntegrity(env e, address _owner) {
    uint256 expectedMaxRepay = maxRepay(e, _owner);
    assert _owner == _cachedOwner;
    assert expectedMaxRepay == _passedAssets;
}
rule maxFlashLoanIntegrity(env e, address _owner) {
    uint256 expectedMaxFlashLoan = maxFlashLoan(e, _owner);
    assert _owner == _cachedOwner;
    assert expectedMaxFlashLoan == _passedAssets;
}

// Same as above for _previewDeposit();
rule depositPreviewInternal(env e, uint256 _assets, ISilo.CollateralType _collateralType) {
    _passedAssets = _assets;
    _previewType = 1;
    _sharesReturned = previewDepositHarness(e, _assets, _collateralType);

    assert verifyPreviewParams(e, ROUNDING_deposit(e), _assets, _collateralType);
}
rule depositPreviewExternal1(env e, uint256 _assets, ISilo.CollateralType _collateralType) {
    _passedAssets = _assets;
    _previewType = 1;
    _sharesReturned = previewDeposit(e, _assets, _collateralType);

    assert verifyPreviewParams(e, ROUNDING_deposit(e), _assets, _collateralType);
}
rule depositPreviewExternal2(env e, uint256 _assets) {
    _passedAssets = _assets;
    _previewType = 1;
    _sharesReturned = previewDeposit(e, _assets);

    assert verifyPreviewParams(e, ROUNDING_deposit(e), _assets, ISilo.CollateralType.Collateral);
}

/* ------------------------------------ Withdraw ------------------------------------ */
/**
    This rule validates that the _withdraw() function in Silo correctly passes on its parameters and
    that it correctly calls the appropriate event (withdraw/withdrawProtected) and it does not
    modify shares/assets after execution.
**/
rule withdrawInternal(env e, ISilo.WithdrawArgs withdrawArgs) {
    (_assetsReturned, _sharesReturned) = withdrawHarness(e,
        withdrawArgs.assets,
        withdrawArgs.shares,
        withdrawArgs.receiver,
        withdrawArgs.owner,
        withdrawArgs.spender,
        withdrawArgs.collateralType
    );
    verifyWithdrawParams(e, withdrawArgs, true, true);
}
rule withdrawExternal1(env e, ISilo.WithdrawArgs withdrawArgs) {
    _sharesReturned = withdraw(e,
             withdrawArgs.assets,
             withdrawArgs.receiver,
             withdrawArgs.owner,
             withdrawArgs.collateralType
    );
    require withdrawArgs.shares == 0;
    require withdrawArgs.spender == e.msg.sender;
    verifyWithdrawParams(e, withdrawArgs, false, true);
}
rule withdrawExternal2(env e, ISilo.WithdrawArgs withdrawArgs) {
    _sharesReturned = withdraw(e,
        withdrawArgs.assets,
        withdrawArgs.receiver,
        withdrawArgs.owner
    );
    require withdrawArgs.shares == 0;
    require withdrawArgs.spender == e.msg.sender;
    require withdrawArgs.collateralType == ISilo.CollateralType.Collateral;
    verifyWithdrawParams(e, withdrawArgs, false, true);
}
rule redeemExternal1(env e, ISilo.WithdrawArgs withdrawArgs) {
    _assetsReturned = redeem(e,
             withdrawArgs.shares,
             withdrawArgs.receiver,
             withdrawArgs.owner,
             withdrawArgs.collateralType
    );
    require withdrawArgs.assets == 0;
    require withdrawArgs.spender == e.msg.sender;
    verifyWithdrawParams(e, withdrawArgs, true, false);
}
rule redeemExternal2(env e, ISilo.WithdrawArgs withdrawArgs) {
    _assetsReturned = redeem(e,
        withdrawArgs.shares,
        withdrawArgs.receiver,
        withdrawArgs.owner
    );
    require withdrawArgs.assets == 0;
    require withdrawArgs.spender == e.msg.sender;
    require withdrawArgs.collateralType == ISilo.CollateralType.Collateral;
    verifyWithdrawParams(e, withdrawArgs, true, false);
}
function verifyWithdrawParams(env e, ISilo.WithdrawArgs withdrawArgs, bool checkReturnedAssets, bool checkReturnedShares) {
    // parameters passed to internal function unmodified
    assert withdrawArgs.assets == _cachedAsset;
    assert withdrawArgs.shares == _cachedShares;
    assert withdrawArgs.receiver == _cachedReceiver;
    assert withdrawArgs.collateralType == _cachedCollateralType;

    // verify returned values were not unmodified
    assert checkReturnedAssets => (withdrawArgs.assets == _assetsReturned);
    assert checkReturnedShares => (withdrawArgs.shares == _sharesReturned);

    // event checks
    assert hashAddress(e, _eventSender, e.msg.sender);
    assert hashAddress(e, _eventReceiver, withdrawArgs.receiver);
    assert hashAddress(e, _eventOwner, withdrawArgs.owner);
    if (withdrawArgs.collateralType == ISilo.CollateralType.Collateral) {
        assert _eventSignature == hashSignature(e, 2);
    } else {
        assert _eventSignature == hashSignature(e, 3);
    }
}

/**
    This function validates whether the _previewRedeem() function in Silo correctly
    passes its parameters to the internal functions it uses & if the returned value
    is the expected one.
**/
rule redeemPreviewInternal(env e, uint256 _shares, ISilo.CollateralType _collateralType) {
    _passedShares = _shares;
    _previewType = 2;
    _sharesReturned = previewRedeemHarness(e, _shares, _collateralType);

    assert verifyPreviewParams(e, ROUNDING_redeem(e), _shares, _collateralType);
}
rule redeemPreviewExternal1(env e, uint256 _shares) {
    _passedShares = _shares;
    _previewType = 2;
    _sharesReturned = previewRedeem(e, _shares, ISilo.CollateralType.Collateral);

    assert verifyPreviewParams(e, ROUNDING_redeem(e), _shares, ISilo.CollateralType.Collateral);
}
rule redeemPreviewExternal2(env e, uint256 _shares, ISilo.CollateralType _collateralType) {
    _passedShares = _shares;
    _previewType = 2;
    _sharesReturned = previewRedeem(e, _shares, _collateralType);

    assert verifyPreviewParams(e, ROUNDING_redeem(e), _shares, _collateralType);
}

// Same as above for _previewWithdraw();
rule withdrawPreviewInternal(env e, uint256 _assets, ISilo.CollateralType _collateralType) {
    _passedAssets = _assets;
    _previewType = 3;
    _sharesReturned = previewWithdrawHarness(e, _assets, _collateralType);

    assert verifyPreviewParams(e, ROUNDING_withdraw(e), _assets, _collateralType);
}
rule withdrawPreviewExternal1(env e, uint256 _assets) {
    _passedAssets = _assets;
    _previewType = 3;
    _sharesReturned = previewWithdraw(e, _assets, ISilo.CollateralType.Collateral);

    assert verifyPreviewParams(e, ROUNDING_withdraw(e), _assets, ISilo.CollateralType.Collateral);
}
rule withdrawPreviewExternal2(env e, uint256 _assets, ISilo.CollateralType _collateralType) {
    _passedAssets = _assets;
    _previewType = 3;
    _sharesReturned = previewWithdraw(e, _assets, _collateralType);

    assert verifyPreviewParams(e, ROUNDING_withdraw(e), _assets, _collateralType);
}

function verifyPreviewParams(env e, Math.Rounding rounding, uint256 _assets, ISilo.CollateralType _collateralType) returns bool {
    return _cachedRoundingType == rounding
    && _cachedAssetType == expectedAssetType(e, _collateralType)
    && _expectedReturn == _sharesReturned;
}

/* ------------------------------------ Initialize --------------------------------------------- */
rule correctInitialize(env e) {
    initialize(e, siloConfigHelper(e));

    address silo; address siloConfig; address hookReceiver; uint24 tokenType; bool transferWithChecks;
    (silo, siloConfig, hookReceiver, tokenType, transferWithChecks) = getInitializeStateResult(e);

    assert silo == silo(e);
    assert siloConfig == siloConfigHelper(e);

    assert hookReceiver == hookReceiverHelper(e);
    assert tokenType == 2048; // collateral token 2**11
    assert transferWithChecks;
}
rule initializeRevertConditions(env e) {
    bool isInitialized = getStorage(e).siloConfig != 0;
    initialize@withrevert(e, siloConfigHelper(e));
    assert lastReverted == isInitialized;
}

rule flashLoanCorrectRevertCond(env e, calldataarg args, address token, address receiver, uint256 amount, bytes data) {
    _eventSignature = keccak256("ujik");
    initialize(e, siloConfigHelper(e));
    uint256 fee;
    uint256 calculatedFee;
    address asset;
    uint192 daoRevenueCached = getDaoAndDeployerRevenue(e);
    (fee, asset, calculatedFee) = getFlashFeeHelper(e, amount);

    // this fee is straight from the config (include the precision)
    require(fee < 500000000000000000);

    flashLoan@withrevert(e, receiver, token, amount, data);

    assert (amount == 0) => lastReverted;
}

/* -------------------------------- external getters --------------------------------  */

definition getLiquiditySig(method f) returns bool = f.selector == sig:Harness.getLiquidity().selector;
definition getTotalAssetsStorageSig(method f) returns bool = f.selector == sig:Harness.getTotalAssetsStorage(ISilo.AssetType).selector;
definition getSiloStorageSig(method f) returns bool = f.selector == sig:Harness.getSiloStorage().selector;
definition getCollateralAssetsSig(method f) returns bool = f.selector == sig:Harness.getCollateralAssets().selector;
definition getDebtAssetsSig(method f) returns bool = f.selector == sig:Harness.getDebtAssets().selector;
definition getCollateralAndProtectedTotalsStorageSig(method f) returns bool = f.selector == sig:Harness.getCollateralAndProtectedTotalsStorage().selector;
definition getCollateralAndDebtTotalsStorageSig(method f) returns bool = f.selector == sig:Harness.getCollateralAndDebtTotalsStorage().selector;
definition getAssetSig(method f) returns bool = f.selector == sig:Harness.asset().selector;
definition getters(method f) returns bool = getLiquiditySig(f) || getTotalAssetsStorageSig(f) || getSiloStorageSig(f) || getCollateralAssetsSig(f) || getDebtAssetsSig(f) || getCollateralAndProtectedTotalsStorageSig(f) || getCollateralAndDebtTotalsStorageSig(f) || getAssetSig(f);

rule gettersAreView(method f) filtered { f -> getters(f) } {
    assert f.isView;
}

rule get_totalAssetsStorage(env e, ISilo.AssetType assetType) {
    uint256 actualAssets = getTypeAssets(e, assetType);
    uint256 expectedAssets = getTotalAssetsStorage(e, assetType);
    assert actualAssets == expectedAssets;
}
rule get_siloStorage(env e) {
    uint192 actualDaoAndDeployerRevenue = getDaoAndDeployerRevenue(e);
    uint64 actualInterestRateTimestamp = getInterestRateTimestamp(e);
    uint256 actualProtectedAssets = getTypeAssets(e, ISilo.AssetType.Protected);
    uint256 actualCollateralAssets = getTypeAssets(e, ISilo.AssetType.Collateral);
    uint256 actualDebtAssets = getTypeAssets(e, ISilo.AssetType.Debt);

    uint192 expectedDaoAndDeployerRevenue; uint64 expectedInterestRateTimestamp; uint256 expectedProtectedAssets; uint256 expectedCollateralAssets; uint256 expectedDebtAssets;
    (expectedDaoAndDeployerRevenue, expectedInterestRateTimestamp, expectedProtectedAssets, expectedCollateralAssets, expectedDebtAssets
    ) = getSiloStorage(e);

    assert actualDaoAndDeployerRevenue == expectedDaoAndDeployerRevenue;
    assert actualInterestRateTimestamp == expectedInterestRateTimestamp;
    assert actualProtectedAssets == expectedProtectedAssets;
    assert actualCollateralAssets == expectedCollateralAssets;
    assert actualDebtAssets == expectedDebtAssets;
}
rule get_collateralAssets(env e) {
    uint256 actualColAssets = totalAssetsHarness(e);
    uint256 expectedColAssets = getCollateralAssets(e);
    assert actualColAssets == expectedColAssets;
}


/* -------------------------------- parameter checks --------------------------------  */

rule callOnBehalfOfSiloIntegrity(env e, address _target, uint256 _value, ISilo.CallType _callType, bytes _input) {
    bool success; bytes result;
    (success, result) = callOnBehalfOfSilo(e, _target, _value, _callType, _input);

    assert success == _returnedSuccess;
    assert _target == _cachedTarget;
    assert _value == _cachedValue;
    assert _callType == _cachedCallType;
}

rule updateHooksIntegrity(env e) {
    updateHooks(e);
    assert _actionCalled;
    assert _eventSignature == hashSignature(e, 5);
}

/* conversions */
rule conversionCrossIntegrity(env e, uint256 _assets, uint256 _shares, ISilo.AssetType _assetType) {
    uint256 sharesNoType = convertToShares(e, _assets);
    uint256 sharesWithType = convertToShares(e, _assets, _assetType);
    assert (_assetType == ISilo.AssetType.Collateral) => (sharesNoType == sharesWithType);

    uint256 assetsNoType = convertToAssets(e, _shares);
    uint256 assetsWithType = convertToAssets(e, _shares, _assetType);
    assert (_assetType == ISilo.AssetType.Collateral) => (assetsNoType == assetsWithType);
}
rule toAssetsIntegrity(env e, uint256 _shares, ISilo.AssetType _assetType) {
    uint256 sharesNoType = convertToAssets(e, _shares);
    assert _shares == _cachedShares;
    assert _cachedAssetType == ISilo.AssetType.Collateral;
    assert _cachedRoundingType == ROUNDING_DEPOSIT_TO_ASSETS(e);
    assert sharesNoType == require_uint256(_cachedShares + _cachedTotalAssets + _cachedTotalShares);

    uint256 sharesWithType = convertToAssets(e, _shares, _assetType);
    assert _shares == _cachedShares;
    assert _cachedAssetType == _assetType;
    assert (_assetType == ISilo.AssetType.Debt) => (_cachedRoundingType == ROUNDING_BORROW_TO_ASSETS(e));
    assert (_assetType != ISilo.AssetType.Debt) => (_cachedRoundingType == ROUNDING_DEPOSIT_TO_ASSETS(e));
    assert sharesNoType == require_uint256(_cachedShares + _cachedTotalAssets + _cachedTotalShares);
}
rule toSharesIntegrity(env e, uint256 _assets, ISilo.AssetType _assetType) {
    uint256 sharesNoType = convertToShares(e, _assets);
    assert _assets == _cachedAssets;
    assert _cachedAssetType == ISilo.AssetType.Collateral;
    assert _cachedRoundingType == ROUNDING_DEPOSIT_TO_SHARES(e);
    assert sharesNoType == require_uint256(_cachedAssets + _cachedTotalAssets + _cachedTotalShares);

    uint256 sharesWithType = convertToShares(e, _assets, _assetType);
    assert _assets == _cachedAssets;
    assert _cachedAssetType == _assetType;
    assert (_assetType == ISilo.AssetType.Debt) => (_cachedRoundingType == ROUNDING_BORROW_TO_SHARES(e));
    assert (_assetType != ISilo.AssetType.Debt) => (_cachedRoundingType == ROUNDING_DEPOSIT_TO_SHARES(e));
    assert sharesNoType == require_uint256(_cachedAssets + _cachedTotalAssets + _cachedTotalShares);
}