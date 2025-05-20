/* Rules concerning repay and repayShares  */

import "../setup/CompleteSiloSetup.spec";
import "./0base_Silo.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";
import "../simplifications/_Oracle_call_before_quote_UNSAFE.spec";
import "../simplifications/Oracle_quote_one_UNSAFE.spec";
// import "../simplifications/_flashloan_no_state_changes.spec";

using EmptyFlashloanReceiver as flashLoanReceiver;

methods{
    function _.onFlashLoan(address, address, uint256, uint256, bytes) external => DISPATCHER(true);
}

//------------------------------- RULES  ----------------------------------


    // flashLoan() should reduce allowance of silo for receiver by repayment amount
    rule flashLoanIncreasesBalanceOfSilo(env e) { //@audit-issue run this to see if it passes
        configForEightTokensSetupRequirements();
        uint256 amount;
        address receiver = flashLoanReceiver;
        require receiver != silo0;
        address token = token0;
        bytes data;


        //setup
        uint256 flashloanFee;
        (_, _, flashloanFee, _) = siloConfig.getFeesWithAsset(e, silo0);
        uint256 feeToPay = require_uint256(amount * flashloanFee / 10^18); 
        uint256 finalFee = flashloanFee != 0 && feeToPay == 0 ? 1 : feeToPay;

        //values before
        uint256 allowanceBefore = token0.allowance(flashLoanReceiver, silo0);
        uint256 balanceReceiverBefore = token0.balanceOf(receiver);

        //flashLoan()
        flashLoan(e, receiver, token, amount, data);

        //values after
        uint256 allowanceAfter = token0.allowance(flashLoanReceiver, silo0);
        uint256 balanceReceiverAfter = token0.balanceOf(receiver);

        //allowance reduced by amount
        assert balanceReceiverAfter == balanceReceiverBefore - finalFee;
    }


    // * `flashLoan()` should never change any storage if flashloanFee is zero 
    rule flashLoanNoChangeIfFeeZero(env e) {
        configForEightTokensSetupRequirements();
        uint256 amount;
        address receiver = flashLoanReceiver;
        address token = token0;
        bytes data;

        uint256 flashloanFee;
        (_, _, flashloanFee, _) = siloConfig.getFeesWithAsset(e, silo0);
        require flashloanFee == 0;

        //vales before
        uint256 allowanceBefore = token0.allowance(flashLoanReceiver, silo0);
        uint256 siloBalanceToken0Before = token0.balanceOf(silo0);
        uint256 daoAndDeployerRevenueBefore;
        (daoAndDeployerRevenueBefore, _, _, _, _) = getSiloStorage();

        //flashLoan()
        flashLoan(e, receiver, token, amount, data);

        //values after
        uint256 allowanceAfter = token0.allowance(flashLoanReceiver, silo0);
        uint256 siloBalanceToken0After = token0.balanceOf(silo0);
        uint256 daoAndDeployerRevenueAfter;
        (daoAndDeployerRevenueAfter, _, _, _, _) = getSiloStorage();

        //storage unchanged
        assert allowanceBefore != max_uint256 => allowanceAfter == allowanceBefore - amount;
        assert siloBalanceToken0After == siloBalanceToken0Before;
        assert daoAndDeployerRevenueAfter == daoAndDeployerRevenueBefore;
    }

    // * `flashLoan()` daoAndDeployerRevenue and Silo asset balance should increase by flashFee()
    rule flashLoanDaoAndDeployerRevenueAndSiloBalanceIncreaseByFlashFee(env e) {
        configForEightTokensSetupRequirements();
        uint256 amount;
        address receiver = flashLoanReceiver;
        require receiver != silo0;
        address token = token0;
        bytes data;

        //setup
        totalSuppliesMoreThanBalances(receiver, silo0);

        //balances before
        uint256 daoAndDeployerRevenueBefore = getSiloDataDaoAndDeployerRevenue();
        uint256 siloBalanceBefore = token0.balanceOf(silo0);

        //falshFee
        uint256 flashFee = flashFeeHarness(token, amount);

        //call flashLoan()
        flashLoan(e, receiver, token, amount, data);

        //balances after
        uint256 daoAndDeployerRevenueAfter = getSiloDataDaoAndDeployerRevenue();
        uint256 siloBalanceAfter = token0.balanceOf(silo0);

        //balances increased by flashFee
        assert daoAndDeployerRevenueAfter == daoAndDeployerRevenueBefore + flashFee;
        assert siloBalanceAfter == siloBalanceBefore + flashFee;
    }

    // flashLoan() does not change assets or shareBalances
    rule flashLoanDoesNotChangeAssetsOrShareBalances(env e) {
        configForEightTokensSetupRequirements();
        uint256 amount;
        address receiver = flashLoanReceiver;
        address token = token0;
        bytes data;
        address user;

        //assets before
        uint256 protectedAssetsBefore;
        uint256 collateralAssetsBefore;
        uint256 debtAssetsBefore;
        (protectedAssetsBefore, collateralAssetsBefore, debtAssetsBefore) = totalAssetsHarness(e);
        uint256 userProtecteSharesBefore = shareProtectedCollateralToken0.balanceOf(user);
        uint256 userCollateralSharesBefore = silo0.balanceOf(user);
        uint256 userDebtSharesBefore = shareDebtToken0.balanceOf(user);

        //flashLoan()
        flashLoan(e, receiver, token, amount, data);

        //assets after
        uint256 protectedAssetsAfter;
        uint256 collateralAssetsAfter;
        uint256 debtAssetsAfter;
        (protectedAssetsAfter, collateralAssetsAfter, debtAssetsAfter) = totalAssetsHarness(e);
        uint256 userProtecteSharesAfter = shareProtectedCollateralToken0.balanceOf(user);
        uint256 userCollateralSharesAfter = silo0.balanceOf(user);
        uint256 userDebtSharesAfter = shareDebtToken0.balanceOf(user);

        //assets unchanged
        assert protectedAssetsBefore == protectedAssetsAfter;
        assert collateralAssetsBefore == collateralAssetsAfter;
        assert debtAssetsBefore == debtAssetsAfter;
        assert userProtecteSharesBefore == userProtecteSharesAfter;
        assert userCollateralSharesBefore == userCollateralSharesAfter;
        assert userDebtSharesBefore == userDebtSharesAfter;
    }

    // maxFlashLoan() returns siloBalance - protected Assets
    rule maxFlashLoanReturnsSiloBalanceMinusProtectedAssets(env e) {
        configForEightTokensSetupRequirements();
        uint256 siloBalance = token0.balanceOf(silo0);
        uint256 protectedAssets = totalProtectedAssetsHarness();
        require siloBalance >= protectedAssets;
        uint256 maxFlashLoanValue = maxFlashLoan(token0);
        assert maxFlashLoanValue == siloBalance - protectedAssets;
    }

    // * `maxFlashLoan()` should return the same value before and after deposit/withdraw of protected assets and `withdrawFees()`
    rule maxFlashLoanUnchangedAfterDepositWithdrawProtected(env e) {
        configForEightTokensSetupRequirements();
        uint256 assets1;
        uint256 assets2;
        uint256 shares;
        address receiver = flashLoanReceiver;
        address owner;
        nonSceneAddressRequirements(e.msg.sender);
        nonSceneAddressRequirements(receiver);
        totalSuppliesMoreThanThreeBalances(e.msg.sender, owner, silo0);

        //value before
        uint256 maxFlashLoanBefore = maxFlashLoan(token0);

        //deposit
        deposit(e, assets1, receiver, ISilo.CollateralType.Protected);

        //value after deposit
        uint256 maxFlashLoanAfterDeposit = maxFlashLoan(token0);

        //withdraw
        withdraw(e, assets2, receiver, owner, ISilo.CollateralType.Protected);

        //value after withdraw
        uint256 maxFlashLoanAfterWithdraw = maxFlashLoan(token0);

        //maxFlashloan the same
        assert maxFlashLoanBefore == maxFlashLoanAfterDeposit;
        assert maxFlashLoanBefore == maxFlashLoanAfterWithdraw;
    }

    // flashLoan() reverts for token which are not token0
    rule flashLoanRevertsForNonToken0(env e) {
        configForEightTokensSetupRequirements();
        uint256 amount;
        address receiver = flashLoanReceiver;
        address token = token1;
        bytes data;

        flashLoan@withrevert(e, receiver, token, amount, data);

        assert lastReverted;
    }

    // flashLoan() reverts for fees > max_uint192
    rule flashLoanRevertsForFeesGreaterThanMaxUint192(env e) {
        configForEightTokensSetupRequirements();
        uint256 amount;
        address receiver = flashLoanReceiver;
        address token = token0;
        bytes data;

        uint256 flashLoanFee = flashFeeHarness(token, amount);
        require(flashLoanFee > max_uint192);

        flashLoan@withrevert(e, receiver, token, amount, data);

        assert lastReverted;
    }

    // flashLoan() reverts for amount > maxFlashLoan
    rule flashLoanRevertsForAmountGreaterThanMaxFlashLoan(env e) {
        configForEightTokensSetupRequirements();
        uint256 amount;
        address receiver = flashLoanReceiver;
        address token = token0;
        bytes data;
        uint256 maxFlashloan = maxFlashLoan(token0);
        require amount > maxFlashloan; 

        flashLoan@withrevert(e, receiver, token, amount, data);

        assert lastReverted;
    }

    // maxFlashLoan() returns 0 for token which are not token0
    rule maxFlashLoanReturnsZeroForNonToken0(env e) {
        configForEightTokensSetupRequirements();
        uint256 maxFlashLoanValue = maxFlashLoan(token1);
        assert maxFlashLoanValue == 0;
    }

    // * `flashFee()` returns non-zero value if fee is set to non-zero value
    rule flashFeeNonZero(env e) {
        configForEightTokensSetupRequirements();
        uint256 amount;
        require amount > 0;

        uint256 flashLoanFee;
        (_, _, flashLoanFee, _) = siloConfig.getFeesWithAsset(e, silo0);
        require flashLoanFee > 0;

        //flashFee()
        uint256 flashFee = flashFeeHarness(token0, amount);

        //flashFee() non-zero
        assert flashFee > 0;
    }

    // flashLoan() reverts for amount 0
    rule flashLoanRevertsForAmountZero(env e) {
        configForEightTokensSetupRequirements();
        uint256 amount = 0;
        address receiver = flashLoanReceiver;
        address token = token0;
        bytes data;

        flashLoan@withrevert(e, receiver, token, amount, data);

        assert lastReverted;
    }

