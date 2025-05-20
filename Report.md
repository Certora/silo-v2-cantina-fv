# Certora Contest Report: Silo V2

## Table of contents

- [**Overview**](#overview)
    - [**About Certora**](#about-certora)
    - [**Summary**](#summary)
- [**Mutations**](#mutations)
- [**Notable Properties**](#notable-properties)
    - [**Caught Real Bugs**](#caught-real-bugs)
    - [**Caught Mutations in Contract: Silo**](#caught-mutations-in-contract-silo)
    - [**Caught Mutations in Contract: Actions**](#caught-mutations-in-contract-actions)
    - [**Caught Mutations in Contract: PartialLiquidation**](#caught-mutations-in-contract-partial-liquidation)
- [**Disclaimer**](#disclaimer)

# Overview

## About Certora

Certora is a Web3 security company that provides industry-leading formal verification tools and smart contract audits. Certora’s flagship security product, Certora Prover, is a unique SaaS product which locates hard-to-find bugs in smart contracts or mathematically proves their absence.

A formal verification contest is a competition where members of the community mathematically validate the accuracy of smart contracts, in return for a reward offered by the sponsor based on the participants' findings and property coverage.

In the formal verification contest detailed here, contenders formally verified Silo V2 smart contracts. This formal verification contest was held from January 13, 2025 until February 10, 2025 as part of the [audit hosted by Cantina](https://cantina.xyz/competitions/18f1e37b-9ac2-4ba9-b32e-50344500c1a7).

## Summary 

Code "mutations" were introduced to evaluate the quality of the specifications written by the contest participants. The mutations are described below and were made available at the end of the contest in the [updated mutations directory in the contest repository here](https://github.com/Certora/silo-v2-cantina-fv/tree/main/certora/mutations). 

There were 229 properties submitted by 36 participants that successfully caught mutations. Some of those properties are included below in this report as examples of high-quality properties. Additionally, the top specifications have been added to the [contest repo](https://github.com/Certora/silo-v2-cantina-fv). You can find the final results for the competition [here](https://docs.google.com/spreadsheets/d/1libTv86GVO0MKF9gl-4PRoVXPtp_6xEmss0HT0ZNIdo/edit?pli=1&gid=1970712821#gid=1970712821)

# Mutations


## Actions Mutations
**Actions_0:** 
Mutation: During switchCollateralToThisSilo(), skip reset of reentrancy protection if user has no debt.
Vulnerability: May prevent normally allowed reentrancy by hook receiver's afterAction() function.
Formal Property:  Reentrancy protection is disabled after actions.

**Actions_1:** 
Mutation: Skip check in borrow() for existing debt in the other silo
Vulnerability: Allows a user to borrow from both silos, violating Silo design principle.
Formal Property: A user never has debt in both silos.

**Actions_2:** 
Mutation: Skip LTV check in borrowSameAsset function.
Vulnerability: Allows users to borrow more than their collateral allows, leading to undercollateralized positions.
Formal Property: A property verifying that a user's debt-to-collateral ratio always remains below the maximum allowed LTV.

**Actions_4:**
Mutation: Change repay function to not properly update the debt shares.
Vulnerability: Allows repaying less than the required amount while clearing the full debt.
Formal Property: A property verifying that debt accounting is always accurate after repayments.

**Actions_5:** 
Mutation: Bypass solvency check in withdraw function.
Vulnerability: Allows users to withdraw collateral even if it makes their position undercollateralized.
Formal Property: A property ensuring positions remain solvent after any withdrawal.

**Actions_6:** 
Mutation: Incorrect fee calculation in withdrawFees.
Vulnerability: Could allow extracting more fees than earned.
Formal Property: A property verifying that fees withdrawn never exceed fees accrued.

**Actions_7:** 
Mutation: Bypass permission check in callOnBehalfOfSilo.
Vulnerability: Allows unauthorized calls using the Silo's authority.
Formal Property: A property ensuring only authorized addresses can perform privileged operations.

**Actions_8:** 
Mutation: Allow double initialization.
Vulnerability: Enables overwriting critical configuration parameters.
Formal Property: A property verifying initialization can only happen once.

**Actions_9:** 
Mutation: Integer overflow in deposit calculation.
Vulnerability: Could lead to incorrect share allocation for large deposits.
Formal Property: A property ensuring mathematical operations don't overflow.

## PartialLiquidation Mutations
**PartialLiquidation_0:** 
Mutation: Skip interest accrual on collateral in other silo prior to liquidation.
Vulnerability: Allows liquidating a position that is healthy.
Formal Property: All interest is accrued for a position before liquidation.

**PartialLiquidation_1:** 
Mutation: Improper reentrancy protection during liquidation.
Vulnerability: Denial of service, liquidation fails due to improper state.
Formal Property: Liquidation can succeed.

**PartialLiquidation_2:** 
Mutation: Incorrect liquidation threshold calculation.
Vulnerability: Allows liquidating healthy positions.
Formal Property: A property verifying only undercollateralized positions can be liquidated.

**PartialLiquidation_3:**
Mutation: Missing access control in liquidation execution.
Vulnerability: Allows unauthorized entities to perform liquidations.
Formal Property: A property ensuring only authorized liquidators can perform liquidations.

**PartialLiquidation_4:** 
Mutation: Skip repayment validation check in liquidation.
Vulnerability: Allows performing liquidations without actually repaying debt.
Formal Property: A property ensuring debt is properly repaid during liquidation.

**PartialLiquidation_5:** 
Mutation: Incorrect asset transfer amount during liquidation.
Vulnerability: Liquidator can receive more collateral than entitled to.
Formal Property: A property verifying correct collateral-to-debt exchange rates during liquidation.

**PartialLiquidation_6:** 
Mutation: Missing final solvency check after liquidation.
Vulnerability: Liquidation might leave the position still underwater.
Formal Property: A property ensuring positions are solvent after liquidation.

**PartialLiquidation_7:** 
Mutation: Improper initialization allowing overwriting config.
Vulnerability: Can reset crucial liquidation parameters.
Formal Property: A property verifying configuration cannot be changed after initialization.

**PartialLiquidation_8:** 
Mutation: Remove slippage protection during liquidation.
Vulnerability: Enables price manipulation during liquidations.
Formal Property: A property ensuring minimum received collateral during liquidation.

**PartialLiquidation_9:** 
Mutation: Improper calculation of liquidation incentive.
Vulnerability: Liquidators receive insufficient incentive to perform liquidations.
Formal Property: A property verifying liquidation incentives are correctly calculated.

## Silo Mutations
**Silo_0:** 
Mutation: Add unauthorized arbitrary transfer function.
Vulnerability: Allows transfer of any silo funds to any receiver.
Formal Property: Collateral cannot be transferred while in use.

**Silo_1:** 
Mutation: Allow withdrawing the same collateral twice.
Vulnerability: Enables double-spending of collateral.
Formal Property: A property ensuring collateral accounting is consistent.

**Silo_2:** 
Mutation: Skip permission check in privileged function.
Vulnerability: Allows unauthorized address to perform privileged operations.
Formal Property: A property verifying only authorized users can call certain functions.

**Silo_3:** 
Mutation: Incorrect asset-to-share conversion calculation.
Vulnerability: Users receive incorrect shares for assets deposited.
Formal Property: A property ensuring consistent conversion between assets and shares.

**Silo_4:** 
Mutation: Remove maximum borrowing limit check.
Vulnerability: Allows borrowing unlimited amounts even with little collateral.
Formal Property: A property verifying users cannot borrow more than allowed by their collateral.

**Silo_5:** 
Mutation: Skip interest accrual in critical function.
Vulnerability: Interest not properly accumulated before state-changing operations.
Formal Property: A property ensuring interest is always accrued before state changes.

**Silo_6:** 
Mutation: Incorrect state update after deposit.
Vulnerability: Deposit not properly recorded in the system.
Formal Property: A property verifying state consistency after deposits.

**Silo_7:** 
Mutation: Remove flashloan fee calculation.
Vulnerability: Flashloans can be used without paying fees.
Formal Property: A property ensuring fees are always charged for flashloans.

**Silo_8:** 
Mutation: Skip validation in asset conversion functions.
Vulnerability: Converting between assets and shares gives incorrect results.
Formal Property: A property verifying mathematical consistency in asset/share conversions.

**Silo_9:** 
Mutation: Incorrect share transfer logic.
Vulnerability: Shares can be transferred to unauthorized addresses.
Formal Property: A property ensuring share transfers maintain system invariants.

# Notable Properties

## Caught Real Bugs

### Liquidation Should Not Allow Reentrancy

*Author:* Vulsight

**Real bug caught by this property:** The partial liquidation process disables reentrancy protection prematurely - right before calling repay(). Because the repay flow invokes hooks (e.g., beforeAction/afterAction), attackers can re‑enter mid‑liquidation to do repeated / full liquidation when only a partial liquidation is warranted. The rule below detects this flaw by detecting scenarios where a liquidation can reenter via a state-changing function (other than the expected repay()).

```
rule HLP_liquidationMechanismShouldNotAllowReentrancy(address borrower) {
    env e;
    silosTimestampSetupRequirements(e);  
    nonSceneAddressRequirements(borrower);
    totalSuppliesMoreThanBalances(borrower,silo0);

    uint256 amount;
    mathint siloId= siloConfig.SILO_ID(e);

    crossReentrantChangeCount=0;
    hookCall=0;
    liquidationCall(e,token0,token1,borrower,amount,true);
    
    // We should not enter more than twice during liquidationCall.
    assert(crossReentrantChangeCount <= 2);
}
```

## Caught Mutations in Contract: Silo

### Consistency of Preview, Deposit, and ConvertToShares

*Author:* Arion0x

Mutation(s) caught: Silo_3, Silo_6, Silo_8

```
rule HLP_Preview_Deposit_ConvertToShares(address receiver)
{
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    totalSuppliesMoreThanBalances(receiver, silo0);

    requireInvariant assetsZeroInterestRateTimestampZero(e) ;
    
    uint256 assets;
    uint256 sharesReported = previewDeposit(e, assets);
    uint256 sharesReceived = deposit(e, assets, receiver);
    uint256 sharesCalculated = convertToShares(e,assets);

    assert ((sharesReported == sharesReceived) &&
     (sharesReported == sharesCalculated) && (sharesReceived == sharesCalculated));
}
```

### Balance Change Only By Expected Functions

*Author:* alexxander77

Mutation(s) caught: Silo_7, Silo_P

```
rule onlyAllowedBalanceModification(env e, method f, calldataarg args) filtered { f -> !excluded(f) && !excluded2(f) } {
    address tokenOwner;
    uint256 balanceBefore = getBalanceOf(e, tokenOwner);
    Harness.f(e, args);
    uint256 balanceAfter = getBalanceOf(e, tokenOwner);
    assert balanceAfter < balanceBefore => canDecreaseBalance(f);
    assert balanceAfter > balanceBefore => canIncreaseBalance(f);
}
```

### Consistency of Preview, Mint, and ConvertToAssets

*Author:* Arion0x

Mutation(s) caught: Silo_6, Silo_8

```
rule HLP_Preview_Mint_ConvertToAssets(address receiver)
{
    env e;

    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // receiver is not one of the contracts in the scene
    nonSceneAddressRequirements(receiver);
    totalSuppliesMoreThanBalances(receiver, silo0);
    
    requireInvariant assetsZeroInterestRateTimestampZero(e) ;

    uint256 shares;
    uint256 assetsReported = previewMint(e, shares);
    uint256 assetsPaid = mint(e, shares, receiver);
    uint256 assetsCalculated = convertToAssets(e,shares);


    assert assetsReported == assetsPaid &&
           assetsReported == assetsCalculated &&
           assetsPaid     == assetsCalculated;
}
```

### Cannot Borrow from Both Silos

*Author:* BenRai1

Mutation(s) caught: Actions_1, Silo_5

```
rule borrowSharesRevertsIfBorrowerHasDebtSharesInSilo1(env e) {
    configForEightTokensSetupRequirements();
    address receiver;
    address borrower;
    uint256 shares;
    uint256 debtSharesInSilo1 = shareDebtToken1.balanceOf(borrower);
    require(debtSharesInSilo1 > 0);
    
    //function call
    borrowShares@withrevert(e, shares, receiver, borrower);

    assert lastReverted;
}
```


## Caught Mutations in Contract: Actions

### State Changes When Expected

*Author:* alexxander77

Mutation(s) caught: Actions_5, Silo_1, Silo_5

```
rule yesStateChanges(method f, env e, calldataarg args) filtered { f -> (f.contract == Harness) && stateModCalls(f) && !harnessCalls(f) } {
    storage beforeState = lastStorage;
    f(e, args);
    assert beforeState[Harness] != lastStorage[Harness];
}
```

### Borrower Cannot Be Immediately Insolvent

*Author:* Arion0x

Mutation(s) caught: ***Actions_2 - Solo catch!***

```
rule borrowSameRespectLTV(env e,uint256 assets, address _receiver, address _borrower){
    // Block time-stamp >= interest rate time-stamp
    silosTimestampSetupRequirements(e);
    // e.msg.sender is not one of the contracts in the scene
    nonSceneAddressRequirements(e.msg.sender);
    synchronous_siloStorage_erc20cvl(e);
    require e.msg.sender !=0;

    ISiloConfig.ConfigData collateralConfig;

    collateralConfig = CVLGetConfig(currentContract);

    mathint maxLTVCounterPre_collateral = maxLtvOracleGhost[collateralConfig.silo];

    borrowSameAsset(e,assets,_receiver,_borrower);

    assert isBelowMaxLTVHarness(e,collateralConfig,collateralConfig,_borrower,ISilo.AccrueInterestInMemory.No);
    //borrow same shouldnt trigger oracles because collateralSilo == debtSilo
    assert maxLtvOracleGhost[collateralConfig.silo] == maxLTVCounterPre_collateral;
}
```

### Functions Restricted to HookReceivers

*Author:* BenRai1

Mutation(s) caught: Actions_3, Actions_7

```
rule onlyHookReceiverCanCallSpecificFunctions(env e, method f, calldataarg args) filtered { f->
    f.selector == sig:Silo0.callOnBehalfOfSilo(address,uint256,ISilo.CallType,bytes).selector ||
    f.selector == sig:shareDebtToken0.callOnBehalfOfShareToken(address,uint256,ISilo.CallType,bytes).selector ||
    f.selector == sig:Silo0.forwardTransferFromNoChecks(address,address,uint256).selector
}{
    configForEightTokensSetupRequirements();
    address sender = e.msg.sender;
    address hookreceiverSilo = hookReceiver(e);
    address hookreceiverShareDebtToken = shareDebtToken0.hookReceiver(e);
    address hookreceiverShareProtectedCollateralToken = shareProtectedCollateralToken0.hookReceiver(e);
    require(sender != hookreceiverSilo && sender != hookreceiverShareDebtToken && sender != hookreceiverShareProtectedCollateralToken);

    f@withrevert(e, args);

    assert lastReverted;
}
```

## Caught Mutations in Contract: PartialLiquidation 

### Interest Accrued Before Liquidation

*Author:* LSHFGJ

Mutation(s) caught: ***PartialLiquidation_0 - Solo catch!***

```
rule interestAccrued(env e, calldataarg args) {
    silosTimestampSetupRequirements(e);
    address collateralConfigAsset;
    address debtConfigAsset;
    address collateralConfigSilo;
    address debtConfigSilo;
    collateralConfigAsset, debtConfigAsset, collateralConfigSilo, debtConfigSilo = fetchConfigs(e, args);
    assert collateralConfigSilo.getSiloDataInterestRateTimestamp(e) == e.block.timestamp;
    assert debtConfigSilo.getSiloDataInterestRateTimestamp(e) == e.block.timestamp;
}
```

### Liquidator Repays Without Overpaying

*Author:* burhankhaja

Mutation(s) caught: PartialLiquidation_4, PartialLiquidation_8

```
rule AssetsUptoMaxCoverageAreTakenFromLiquidator {
    env e;
    address _collateralAsset;
    address _debtAsset;
    address _borrower;
    uint256 _maxDebtToCover;
    bool _receiveSToken;

    require _receiveSToken; 

    mathint LiquidatorAssetBalanceBefore = assetTokenBalances[e.msg.sender];


    //Liquidation call
    liquidationCall( e, 
        _collateralAsset,
        _debtAsset,
        _borrower,
        _maxDebtToCover,
        _receiveSToken
    ); 

    mathint LiquidatorAssetBalanceAfter = assetTokenBalances[e.msg.sender];


    assert LiquidatorAssetBalanceAfter < LiquidatorAssetBalanceBefore && LiquidatorAssetBalanceAfter >= LiquidatorAssetBalanceBefore - _maxDebtToCover, "assets tokens must be taken from liquidator but not more than his expected max coverage limit";
}
```

# Disclaimer

The Certora Prover takes a contract and a specification as input and formally proves that the contract satisfies the specification in all scenarios. Notably, the guarantees of the Certora Prover are scoped to the provided specification and the Certora Prover does not check any cases not covered by the specification. 

Certora does not provide a warranty of any kind, explicit or implied. The contents of this report should not be construed as a complete guarantee that the contract is secure in all dimensions. In no event shall Certora or any of its employees or community participants be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the results reported here. All smart contract software should be used at the sole risk and responsibility of users.