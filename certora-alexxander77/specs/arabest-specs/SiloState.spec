import "../mocks/General.spec";
import "../mocks/ActionsMock.spec";
import "../mocks/SiloMathLibMock.spec";
import "../mocks/SiloStdLibMock.spec";

using SiloHarness as Harness;

methods {
    function getHooksAfter() external returns (uint24) envfree;
    function getHooksBefore() external returns (uint24) envfree;
    function getStoredTokenType() external returns (uint24) envfree;

    function _.balanceOf(address) external => DISPATCHER(true);
    function _.getConfig(address _silo) external => DISPATCHER(true);
}

/* ------------------------------------ general transactions ------------------------------------ */
rule noBalanceModificationAllowed(env e, method f, calldataarg args) filtered { f -> !excluded(f) && !excluded2(f) && !canDecreaseBalance(f) && !canIncreaseBalance(f) } {
    address tokenOwner;
    uint256 balanceBefore = getBalanceOf(e, tokenOwner);
    Harness.f(e, args);
    uint256 balanceAfter = getBalanceOf(e, tokenOwner);
    assert balanceAfter == balanceBefore;
}
rule onlyAllowedBalanceModification(env e, method f, calldataarg args) filtered { f -> !excluded(f) && !excluded2(f) } {
    address tokenOwner;
    uint256 balanceBefore = getBalanceOf(e, tokenOwner);
    Harness.f(e, args);
    uint256 balanceAfter = getBalanceOf(e, tokenOwner);
    assert balanceAfter < balanceBefore => canDecreaseBalance(f);
    assert balanceAfter > balanceBefore => canIncreaseBalance(f);
}


definition canDecreaseBalance(method f) returns bool =
    f.selector == sig:SiloHarness.callOnBehalfOfSilo(address,uint256,ISilo.CallType,bytes).selector ||
    f.selector == sig:SiloHarness.forwardTransferFromNoChecks(address,address,uint256).selector ||
    f.selector == sig:SiloHarness.mint(address,address,uint256).selector ||
    f.selector == sig:SiloHarness.burn(address,address,uint256).selector ||
    f.selector == sig:SiloHarness.redeem(uint256,address,address).selector ||
    f.selector == sig:SiloHarness.redeem(uint256,address,address,ISilo.CollateralType).selector ||
    f.selector == sig:SiloHarness.transitionCollateral(uint256,address,ISilo.CollateralType).selector ||
    f.selector == sig:SiloHarness.transfer(address,uint256).selector ||
    f.selector == sig:SiloHarness.transferFrom(address,address,uint256).selector ||
    f.selector == sig:SiloHarness.withdraw(uint256,address,address).selector ||
    f.selector == sig:SiloHarness.withdraw(uint256,address,address,ISilo.CollateralType).selector;

definition canIncreaseBalance(method f) returns bool =
    f.selector == sig:SiloHarness.callOnBehalfOfSilo(address,uint256,ISilo.CallType,bytes).selector ||
    f.selector == sig:SiloHarness.transfer(address,uint256).selector ||
    f.selector == sig:SiloHarness.transferFrom(address,address,uint256).selector ||
    f.selector == sig:SiloHarness.forwardTransferFromNoChecks(address,address,uint256).selector ||
    f.selector == sig:SiloHarness.deposit(uint256,address).selector ||
    f.selector == sig:SiloHarness.deposit(uint256,address,ISilo.CollateralType).selector ||
    f.selector == sig:SiloHarness.mint(uint256,address).selector ||
    f.selector == sig:SiloHarness.mint(address,address,uint256).selector ||
    f.selector == sig:SiloHarness.mint(uint256,address,ISilo.CollateralType).selector;

definition burnSig(method f) returns bool = f.selector == sig:SiloHarness.burn(address,address,uint256).selector;
definition mintSig(method f) returns bool = f.selector == sig:SiloHarness.mint(address,address,uint256).selector;
definition transferFromSig(method f) returns bool = f.selector == sig:SiloHarness.transferFrom(address, address, uint256).selector;
definition transferSig(method f) returns bool = f.selector == sig:SiloHarness.transfer(address, uint256).selector;
definition transferNoChecksSig(method f) returns bool = f.selector == sig:SiloHarness.forwardTransferFromNoChecks(address, address, uint256).selector;

definition ERC20Transfers(method f) returns bool = burnSig(f) || mintSig(f) || transferSig(f) || transferFromSig(f) || transferNoChecksSig(f);

// harness functions that don't need checking
definition sig1(method f) returns bool = f.selector == sig:SiloHarness.repayShares(uint256,address).selector;
definition sig2(method f) returns bool = f.selector == sig:SiloHarness.transitionCollateralActions(ISilo.TransitionCollateralArgs).selector;
definition sig3(method f) returns bool = f.selector == sig:SiloHarness.transitionCollateral(uint256,address,ISilo.CollateralType).selector;
definition excluded(method f) returns bool = sig1(f) || sig2(f) || sig3(f);

definition sig01(method f) returns bool = f.selector == sig:SiloHarness.burn(address,address,uint256).selector;
definition sig02(method f) returns bool = f.selector == sig:SiloHarness.forwardTransferFromNoChecks(address,address,uint256).selector;
definition sig03(method f) returns bool = f.selector == sig:SiloHarness.mint(address,address,uint256).selector;
definition sig04(method f) returns bool = f.selector == sig:SiloHarness.callOnBehalfOfSilo(address,uint256,ISilo.CallType,bytes).selector;
definition sig05(method f) returns bool = f.selector == sig:SiloHarness.transfer(address,uint256).selector;
definition excluded2(method f) returns bool = sig01(f) || sig02(f) || sig03(f) || sig04(f) || sig05(f);