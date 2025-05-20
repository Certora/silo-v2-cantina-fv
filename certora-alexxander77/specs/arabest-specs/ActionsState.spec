using SiloHarness as Harness;

rule noStateChanges(method f, env e, calldataarg args) filtered { f -> (f.contract == Harness) && !stateModCalls(f) && !harnessCalls(f) } {
    storage beforeState = lastStorage;
    f(e, args);
    assert beforeState[Harness] == lastStorage[Harness];
}
rule yesStateChanges(method f, env e, calldataarg args) filtered { f -> (f.contract == Harness) && stateModCalls(f) && !harnessCalls(f) } {
    storage beforeState = lastStorage;
    f(e, args);
    assert beforeState[Harness] != lastStorage[Harness];
}

definition sig00(method f) returns bool = f.selector == sig:SiloHarness.redeem(uint256,address,address).selector;
definition sig01(method f) returns bool = f.selector == sig:SiloHarness.permit(address,address,uint256,uint256,uint8,bytes32,bytes32).selector;
definition sig02(method f) returns bool = f.selector == sig:SiloHarness.withdrawFees().selector;
definition sig03(method f) returns bool = f.selector == sig:SiloHarness.burn(address,address,uint256).selector;
definition sig04(method f) returns bool = f.selector == sig:SiloHarness.mint(address,address,uint256).selector;
definition sig05(method f) returns bool = f.selector == sig:SiloHarness.withdrawFee(address).selector;
definition sig06(method f) returns bool = f.selector == sig:SiloHarness.withdrawActions(ISilo.WithdrawArgs).selector;
definition sig07(method f) returns bool = f.selector == sig:SiloHarness.withdraw(uint256,address,address,ISilo.CollateralType).selector;
definition sig08(method f) returns bool = f.selector == sig:SiloHarness.redeem(uint256,address,address,ISilo.CollateralType).selector;
definition sig09(method f) returns bool = f.selector == sig:SiloHarness.borrowSameAsset(uint256,address,address).selector;
definition sig10(method f) returns bool = f.selector == sig:SiloHarness.borrow(uint256,address,address).selector;
definition sig11(method f) returns bool = f.selector == sig:SiloHarness.withdraw(uint256,address,address).selector;
definition sig12(method f) returns bool = f.selector == sig:SiloHarness.borrowShares(uint256,address,address).selector;
definition sig13(method f) returns bool = f.selector == sig:SiloHarness.repayActions(uint256,uint256,address,address).selector;
definition sig14(method f) returns bool = f.selector == sig:SiloHarness.borrowSameAssetActions(ISilo.BorrowArgs).selector;
definition sig15(method f) returns bool = f.selector == sig:SiloHarness.borrowActions(ISilo.BorrowArgs).selector;
definition sig16(method f) returns bool = f.selector == sig:SiloHarness.deposit(uint256,address).selector;
definition sig17(method f) returns bool = f.selector == sig:SiloHarness.repayShares(uint256,address).selector;
definition sig18(method f) returns bool = f.selector == sig:SiloHarness.repay(uint256,address).selector;
definition sig19(method f) returns bool = f.selector == sig:SiloHarness.mint(uint256,address).selector;
definition sig20(method f) returns bool = f.selector == sig:SiloHarness.transitionCollateralActions(ISilo.TransitionCollateralArgs).selector;
definition sig21(method f) returns bool = f.selector == sig:SiloHarness.deposit(uint256,address,ISilo.CollateralType).selector;
definition sig22(method f) returns bool = f.selector == sig:SiloHarness.transitionCollateral(uint256,address,ISilo.CollateralType).selector;
definition sig23(method f) returns bool = f.selector == sig:SiloHarness.mint(uint256,address,ISilo.CollateralType).selector;
definition sig24(method f) returns bool = f.selector == sig:SiloHarness.depositActions(uint256,uint256,address,ISilo.CollateralType).selector;
definition sig25(method f) returns bool = f.selector == sig:SiloHarness.depositHarness(uint256,uint256,address,ISilo.CollateralType).selector;
definition sig26(method f) returns bool = f.selector == sig:SiloHarness.withdrawHarness(uint256,uint256,address,address,address,ISilo.CollateralType).selector;

definition stateModCalls(method f) returns bool = sig00(f) || sig01(f) || sig02(f) || sig03(f) || sig04(f) || sig05(f) || sig06(f) || sig07(f) || sig08(f) || sig09(f) || sig10(f) || sig11(f) || sig12(f) || sig13(f) || sig14(f) || sig15(f) || sig16(f) || sig17(f) || sig18(f) || sig19(f) || sig20(f) || sig21(f) || sig22(f) || sig23(f) || sig24(f) || sig25(f) || sig26(f);



definition excl00(method f) returns bool = f.selector == sig:SiloHarness.setDebtConfig(ISiloConfig.ConfigData).selector;
definition excl01(method f) returns bool = f.selector == sig:SiloHarness.setCollateralConfig(ISiloConfig.ConfigData).selector;
definition excl02(method f) returns bool = f.selector == sig:SiloHarness.setHash0(bytes).selector;
definition excl03(method f) returns bool = f.selector == sig:SiloHarness.setHash1(bytes).selector;
definition excl04(method f) returns bool = f.selector == sig:SiloHarness.accrueInterestForConfig(address,uint256,uint256).selector;
definition excl05(method f) returns bool = f.selector == sig:SiloHarness.getAccrueInterestForAssetHarness(address,uint256,uint256).selector;
definition excl06(method f) returns bool = f.selector == sig:SiloHarness.initialize(address).selector;
definition excl07(method f) returns bool = f.selector == sig:SiloHarness.approve(address,uint256).selector;
definition excl08(method f) returns bool = f.selector == sig:SiloHarness.transfer(address,uint256).selector;
definition excl09(method f) returns bool = f.selector == sig:SiloHarness.accrueInterest().selector;
definition excl10(method f) returns bool = f.selector == sig:SiloHarness.getAccrueInterestHarness().selector;
definition excl11(method f) returns bool = f.selector == sig:SiloHarness.synchronizeHooks(uint24,uint24).selector;
definition excl12(method f) returns bool = f.selector == sig:SiloHarness.flashLoan(address,address,uint256,bytes).selector;
definition excl13(method f) returns bool = f.selector == sig:SiloHarness.callOnBehalfOfSilo(address, uint256, ISilo.CallType, bytes).selector;
definition excl14(method f) returns bool = f.selector == sig:SiloHarness.transferFrom(address,address,uint256).selector;
definition excl15(method f) returns bool = f.selector == sig:SiloHarness.forwardTransferFromNoChecks(address,address,uint256).selector;

// these are harness functions that don't need to be checked
definition harnessCalls(method f) returns bool = excl00(f) || excl01(f) || excl02(f) || excl03(f) || excl04(f) || excl05(f) || excl06(f) || excl07(f) || excl08(f) || excl09(f) || excl10(f) || excl11(f) || excl12(f) || excl13(f) || excl14(f) || excl15(f);