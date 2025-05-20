using Silo0 as Silo0;
using Silo1 as Silo1;
using ShareCollateralToken0 as ShareCollateralToken0;
using ShareCollateralToken1 as ShareCollateralToken1;
using ShareProtectedCollateralToken0 as ShareProtectedCollateralToken0;
using ShareProtectedCollateralToken1 as ShareProtectedCollateralToken1;
using Token0 as Token0;
using Token1 as Token1;

using ShareDebtToken0 as ShareDebtToken0;
using ShareDebtToken1 as ShareDebtToken1;

using SiloConfig as SiloConfig;

using PartialLiquidationHarness as Harness;

methods {

    // ENVFREE
    function Harness.getERCBalance(address token, address addr) external returns (uint256) envfree;
    function Harness.emptyConfigDatas() external returns (ISiloConfig.ConfigData, ISiloConfig.ConfigData) envfree;
    function SiloConfig.getConfig(address _silo) external returns (ISiloConfig.ConfigData) envfree;

    // ERC20 summaries
    function _.name() external => PER_CALLEE_CONSTANT DELETE;
    function _.symbol() external => PER_CALLEE_CONSTANT DELETE;
    function _.decimals() external => PER_CALLEE_CONSTANT;
    function _.totalSupply() external => DISPATCHER(true);
    function _.balanceOf(address) external => DISPATCHER(true);
    function _.allowance(address,address) external => DISPATCHER(true);
    function _.approve(address,uint256) external => DISPATCHER(true);
    function _.transfer(address,uint256) external => DISPATCHER(true);
    function _.transferFrom(address,address,uint256) external => DISPATCHER(true);

    function _._afterTokenTransfer(address _sender, address _recipient, uint256 _amount) internal => NONDET;
    function _._beforeTokenTransfer(address _sender, address _recipient, uint256 _amount) internal => NONDET;


    function Token0.totalSupply() external returns(uint256) envfree;
    function Silo0.totalSupply() external returns(uint256) envfree;
    function ShareDebtToken0.totalSupply() external returns(uint256) envfree;
    function ShareProtectedCollateralToken0.totalSupply() external returns(uint256) envfree;
    function ShareCollateralToken0.totalSupply() external returns(uint256) envfree;

    function Token1.totalSupply() external returns(uint256) envfree;
    function Silo1.totalSupply() external returns(uint256) envfree;
    function ShareDebtToken1.totalSupply() external returns(uint256) envfree;
    function ShareProtectedCollateralToken1.totalSupply() external returns(uint256) envfree;
    function ShareCollateralToken1.totalSupply() external returns(uint256) envfree;

    function Token0.balanceOf(address) external returns(uint256) envfree;
    function Silo0.balanceOf(address) external returns(uint256) envfree;
    function ShareDebtToken0.balanceOf(address) external returns(uint256) envfree;
    function ShareProtectedCollateralToken0.balanceOf(
        address
    ) external returns(uint256) envfree;
    function ShareCollateralToken0.balanceOf(
        address
    ) external returns(uint256) envfree;

    function Token1.balanceOf(address) external returns(uint256) envfree;
    function Silo1.balanceOf(address) external returns(uint256) envfree;
    function ShareDebtToken1.balanceOf(address) external returns(uint256) envfree;
    function ShareProtectedCollateralToken1.balanceOf(
        address
    ) external returns(uint256) envfree;
    function ShareCollateralToken1.balanceOf(
        address
    ) external returns(uint256) envfree;


    // NONDET summaries
    function _.accrueInterest() external => NONDET;
    function _.callSolvencyOracleBeforeQuote() external => NONDET;
    function _.beforeQuote(address) external => NONDET;
    function _.reentrancyGuardEntered() external => NONDET;
    function _.getTotalAssetsStorage(ISilo.AssetType _assetType) external => NONDET;

    function ShareCollateralTokenLib.isSolventAfterCollateralTransfer(
        address _sender
    ) external returns (bool) => NONDET;

    // DISPATCHED summaries
    function _.forwardTransferFromNoChecks(address, address, uint256) external => NONDET;
//    function _.repay(uint256 _assets, address _borrower) external => DISPATCHER(true);
    function _.burn(address, address, uint256) external => NONDET;
//    function _.redeem(uint256, address, address, ISilo.CollateralType) external => DISPATCHER(true);

    // MOCKED summaries
    function _.turnOnReentrancyProtection() external => turnOnReentrancyProtectionMock() expect void;
    function _.turnOffReentrancyProtection() external => turnOffReentrancyProtectionMock() expect void;

    function SiloConfig.getConfigsForSolvency(address _borrower) external returns (ISiloConfig.ConfigData memory, ISiloConfig.ConfigData memory) =>
    solvencyConfigsMock(_borrower);

    function _.getConfigsForSolvency(address _borrower) external =>
        solvencyConfigsMock(_borrower) expect (ISiloConfig.ConfigData memory, ISiloConfig.ConfigData memory);

//    function SiloConfig.getConfigsForSolvency(address _borrower) external returns (ISiloConfig.ConfigData memory, ISiloConfig.ConfigData memory)
//        => CONSTANT;
//
//    function _.getConfigsForSolvency(address _borrower) external
//        => CONSTANT;


    function PartialLiquidationExecLib.getExactLiquidationAmounts(ISiloConfig.ConfigData _collateralConfig,
                                                  ISiloConfig.ConfigData _debtConfig,
                                                  address _user,
                                                  uint256 _maxDebtToCover,
                                                  uint256 _liquidationFee) external returns(uint256, uint256, uint256, bytes4)
                                                                         => getExactLiqMock();

    function SiloMathLib.convertToShares(uint256 _assets,
        uint256 _totalAssets,
        uint256 _totalShares,
        Math.Rounding _rounding,
        ISilo.AssetType _assetType) internal returns(uint256)=> convertToSharesMock(_assetType);

    function _.previewRedeem(uint256, ISilo.CollateralType) external => previewRedeemMock() expect (uint256);

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

}
persistent ghost bool balanceUpdateFlag;
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
persistent ghost bool onReentrancy;
persistent ghost mathint onReentrancyCount;
persistent ghost mathint offReentrancyCount;


function turnOnReentrancyProtectionMock() {
    onReentrancy = true;
    onReentrancyCount = onReentrancyCount + 1;
}

function turnOffReentrancyProtectionMock() {
    onReentrancy = false;
    offReentrancyCount = offReentrancyCount + 1;
}

function previewRedeemMock() returns uint256 {
    uint256 x;
    return x;
}

persistent ghost uint256 repayDebtAssetsCached;
persistent ghost bytes4 errorCodeCached;

persistent ghost bool maxDebtFlag {
    init_state axiom maxDebtFlag == false;
}
function getExactLiqMock() returns (uint256, uint256, uint256, bytes4) {
    uint256 x;
    uint256 y;
    uint256 z;
    bytes4 a;
    repayDebtAssetsCached=z;
    errorCodeCached = a;
    require !maxDebtFlag => (z != 0); // repayDebtAsset should not be zero
    return (x, y, z, a);
}
persistent ghost uint256 sharesCollateralCached;
persistent ghost uint256 sharesProtectedCached;

function convertToSharesMock(ISilo.AssetType _assetType) returns uint256 {

    uint256 x;
    if(_assetType == ISilo.AssetType.Collateral) {
        sharesCollateralCached = x;
    }
    else {
        sharesProtectedCached = x;
    }
    return x;
}

// @todo this restricts revert condition space
persistent ghost bool debtSiloFlag {
    init_state axiom debtSiloFlag == false;
}
function solvencyConfigsMock(address borrower) returns(ISiloConfig.ConfigData, ISiloConfig.ConfigData) {
    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;

    uint256 bal0 = getERCBalance(ShareDebtToken0, borrower);
    uint256 bal1 = getERCBalance(ShareDebtToken1, borrower);

    require(bal0 == 0 || bal1 == 0);

    if (bal0 == 0 && bal1 == 0) {
        (collateralConfig, debtConfig) = emptyConfigDatas();
    }
    else if (bal0 != 0) {
        debtConfig = SiloConfig.getConfig(Silo0);
        collateralConfig = SiloConfig.getConfig(Silo1);
    }
    else {
        debtConfig = SiloConfig.getConfig(Silo1);
        collateralConfig = SiloConfig.getConfig(Silo0);
    }

    if (debtSiloFlag) {
        require debtConfig.silo == 0;
    }

    return (collateralConfig, debtConfig);
}

function nonSceneAddressRequirements(address sender) {
    require sender != Silo0;
    require sender != Silo1;
    require sender != SiloConfig;

    require sender != ShareDebtToken0;
    require sender != ShareProtectedCollateralToken0;
    require sender != ShareDebtToken1;
    require sender != ShareProtectedCollateralToken1;

    require sender != Token0;
    require sender != Token1;
}

function siloRequirements(env e) {
    uint x;
    uint256 y;
    require(ShareDebtToken0.silo(e) == Silo0);
    require(ShareDebtToken1.silo(e) == Silo1);

    require(Silo0.assetToken == Token0);
    require(Silo0.debtShareToken == ShareDebtToken0);
    require(Silo0.shareCollateralToken == Silo0);
    require(Silo0.shareProtectedToken == ShareProtectedCollateralToken0);
    require(Silo0.sharesToReturn == x);

    require(Silo1.assetToken == Token1);
    require(Silo1.debtShareToken == ShareDebtToken1);
    require(Silo1.shareCollateralToken == Silo1);
    require(Silo1.shareProtectedToken == ShareProtectedCollateralToken1);
    require(Silo1.sharesToReturn == y);
}

persistent ghost bool balanceUpdateFlag0;
persistent ghost bool balanceUpdateFlag1;

hook Sstore Token0._balances[KEY address account] uint256 newBalance (uint256 previousBalance) {
    balanceUpdateFlag0 = true;
}
hook Sstore Token1._balances[KEY address account] uint256 newBalance (uint256 previousBalance) {
    balanceUpdateFlag1 = true;
}

function totalSupplyMoreThanBalance(address user1) {
    require (
        to_mathint(Silo0.totalSupply()) >=
        Silo0.balanceOf(user1)
    );
    require (
        to_mathint(ShareDebtToken0.totalSupply()) >=
        ShareDebtToken0.balanceOf(user1)
    );
    require (
        to_mathint(ShareProtectedCollateralToken0.totalSupply()) >=
        ShareProtectedCollateralToken0.balanceOf(user1)
    );
    require (
        to_mathint(Token0.totalSupply()) >=
        Token0.balanceOf(user1)
    );

    require (
        to_mathint(Silo1.totalSupply()) >=
        Silo1.balanceOf(user1)
    );
    require (
        to_mathint(ShareDebtToken1.totalSupply()) >=
        ShareDebtToken1.balanceOf(user1)
    );
    require (
        to_mathint(ShareProtectedCollateralToken1.totalSupply()) >=
        ShareProtectedCollateralToken1.balanceOf(user1)
    );
    require (
        to_mathint(Token1.totalSupply()) >=
        Token1.balanceOf(user1)
    );
}

function totalSuppliesMoreThanBalances(address user1, address user2) {
    if (user1 == user2)
    {
        totalSupplyMoreThanBalance(user1);
        return;
    }
    // require user1 != user2;
    require (
        to_mathint(Silo0.totalSupply()) >=
        Silo0.balanceOf(user1) + Silo0.balanceOf(user2)
    );
    require (
        to_mathint(ShareDebtToken0.totalSupply()) >=
        ShareDebtToken0.balanceOf(user1) + ShareDebtToken0.balanceOf(user2)
    );
    require (
        to_mathint(ShareProtectedCollateralToken0.totalSupply()) >=
        ShareProtectedCollateralToken0.balanceOf(user1) +
        ShareProtectedCollateralToken0.balanceOf(user2)
    );
    require (
        to_mathint(Token0.totalSupply()) >=
        Token0.balanceOf(user1) + Token0.balanceOf(user2)
    );

    require (
        to_mathint(Silo1.totalSupply()) >=
        Silo1.balanceOf(user1) + Silo1.balanceOf(user2)
    );
    require (
        to_mathint(ShareDebtToken1.totalSupply()) >=
        ShareDebtToken1.balanceOf(user1) + ShareDebtToken1.balanceOf(user2)
    );
    require (
        to_mathint(ShareProtectedCollateralToken1.totalSupply()) >=
        ShareProtectedCollateralToken1.balanceOf(user1) +
        ShareProtectedCollateralToken1.balanceOf(user2)
    );
    require (
        to_mathint(Token1.totalSupply()) >=
        Token1.balanceOf(user1) + Token1.balanceOf(user2)
    );
}

function totalSuppliesMoreThanThreeBalances(address user1, address user2, address user3) {
    if (user1 == user2 || user2 == user3) {
        totalSuppliesMoreThanBalances(user1, user3); return;
    }
    if (user1 == user3) {
        totalSuppliesMoreThanBalances(user1, user2); return;
    }
    //require user1 != user2 && user1 != user3 && user2 != user3;
    require (
        to_mathint(Silo0.totalSupply()) >=
        Silo0.balanceOf(user1) + Silo0.balanceOf(user2) + Silo0.balanceOf(user3)
    );
    require (
        to_mathint(ShareDebtToken0.totalSupply()) >=
        ShareDebtToken0.balanceOf(user1) +
        ShareDebtToken0.balanceOf(user2) +
        ShareDebtToken0.balanceOf(user3)
    );
    require (
        to_mathint(ShareProtectedCollateralToken0.totalSupply()) >=
        ShareProtectedCollateralToken0.balanceOf(user1) +
        ShareProtectedCollateralToken0.balanceOf(user2) +
        ShareProtectedCollateralToken0.balanceOf(user3)
    );
    require (
        to_mathint(Token0.totalSupply()) >=
        Token0.balanceOf(user1) + Token0.balanceOf(user2) + Token0.balanceOf(user3)
    );

    require (
        to_mathint(Silo1.totalSupply()) >=
        Silo1.balanceOf(user1) + Silo1.balanceOf(user2) + Silo1.balanceOf(user3)
    );
    require (
        to_mathint(ShareDebtToken1.totalSupply()) >=
        ShareDebtToken1.balanceOf(user1) +
        ShareDebtToken1.balanceOf(user2) +
        ShareDebtToken1.balanceOf(user3)
    );
    require (
        to_mathint(ShareProtectedCollateralToken1.totalSupply()) >=
        ShareProtectedCollateralToken1.balanceOf(user1) +
        ShareProtectedCollateralToken1.balanceOf(user2) +
        ShareProtectedCollateralToken1.balanceOf(user3)
    );
    require (
        to_mathint(Token1.totalSupply()) >=
        Token1.balanceOf(user1) + Token1.balanceOf(user2) + Token1.balanceOf(user3)
    );
}

function liqCallRevertSetup(env e, address _borrower, uint256 _maxDebtToCover) returns (address, address, address, address) {
    require(e.msg.sender != 0);
    onReentrancy = false;
    address debtSilo; address debtAsset; address collateralSilo; address collateralAsset;

    address siloConfig = siloConfig(e);

    (debtSilo, debtAsset, collateralSilo, collateralAsset) = getConfigsForSolvencyHarness(e, siloConfig, _borrower);

    uint256 balanceSenderCached = getERCBalance(debtAsset, e.msg.sender);
    uint256 balanceHarnessCached = getERCBalance(debtAsset, currentContract);

    uint256 allowanceSenderCached = getERCAllowance(e, debtAsset, e.msg.sender, currentContract);
    uint256 allowanceHarnessToSilo = getERCAllowance(e, debtAsset, currentContract, debtSilo);

    require(allowanceHarnessToSilo + _maxDebtToCover <= MAX_UINT256(e));
    require(balanceSenderCached >= _maxDebtToCover);
    // maybe make these conditions ?
    require(allowanceSenderCached >= _maxDebtToCover);
    require(balanceSenderCached + balanceHarnessCached <= MAX_UINT256(e));

    if(collateralSilo == Silo0) {
        require(getERCBalance(ShareCollateralToken0, _borrower) >= sharesCollateralCached);
        require(getERCBalance(ShareProtectedCollateralToken0, _borrower) >= sharesProtectedCached);
    }
    if(collateralSilo == Silo1) {
        require(getERCBalance(ShareCollateralToken1, _borrower) >= sharesCollateralCached);
        require(getERCBalance(ShareProtectedCollateralToken1, _borrower) >= sharesProtectedCached);
    }
    return (debtSilo, debtAsset, collateralSilo, collateralAsset);
}