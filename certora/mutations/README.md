
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
Mutation: Incorrect share transfer logic
Vulnerability: Shares can be transferred to unauthorized addresses
Formal Property: A property ensuring share transfers maintain system invariants
