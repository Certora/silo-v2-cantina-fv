import "../setup/CompleteSiloSetup.spec";
import "./0base_Silo.spec";
import "../simplifications/_Oracle_call_before_quote_UNSAFE.spec";
import "../simplifications/Oracle_quote_one_UNSAFE.spec";
import "../simplifications/_flashloan_no_state_changes.spec";

//------------------------------- RULES TEST START ----------------------------------
    // maxDeposit():using the results from maxDeposit() to call deposit() should be possible (satisfy not revert) //@audit-issue result is max_uint256 which reverts
    rule maxDepositWorksForDeposit(env e) {
        configForEightTokensSetupRequirements();
        address borrower;

        //call to max
        uint256 max = maxDeposit(e, borrower);

        //call to deposit
        deposit@withrevert(e, require_uint256(max-1), borrower);

        satisfy !lastReverted;
    }

    // maxMint():using the results from maxMint() to call mint() should be possible (satisfy not revert) //@audit-issue result is max_uint256 which reverts
    rule maxMintWorksForMint(env e) {
        configForEightTokensSetupRequirements();
        address borrower;

        //call to max
        uint256 max = maxMint(e, borrower);

        //call to mint
        mint@withrevert(e, require_uint256(max-1), borrower);

        satisfy !lastReverted;
    }

    // maxWithdraw():using the results from maxWithdraw() to call withdraw() should be possible (satisfy not revert)
    rule maxWithdrawWorksForWithdraw(env e) {
        configForEightTokensSetupRequirements();
        address borrower;

        // Block time-stamp >= interest rate time-stamp
        silosTimestampSetupRequirements(e);

        //call to max
        uint256 max = maxWithdraw(e, borrower);

        //call to withdraw
        withdraw@withrevert(e, max, borrower, borrower);

        satisfy !lastReverted;
    }

    // maxRedeem():using the results from maxRedeem() to call redeem() should be possible (satisfy not revert)
    rule maxRedeemWorksForRedeem(env e) {
        configForEightTokensSetupRequirements();
        address borrower;

        // Block time-stamp >= interest rate time-stamp
        silosTimestampSetupRequirements(e);

        //call to max
        uint256 max = maxRedeem(e, borrower);

        //call to redeem
        redeem@withrevert(e, max, borrower, borrower);

        satisfy !lastReverted;
    }

    // maxWithdraw(protected):using the results from maxWithdraw(protected) to call withdraw(protected) should be possible (satisfy not revert)
    rule maxWithdrawProtectedWorksForWithdrawProtected(env e) {
        configForEightTokensSetupRequirements();
        address borrower;

        // Block time-stamp >= interest rate time-stamp
        silosTimestampSetupRequirements(e);

        //call to max
        uint256 max = maxWithdraw(e, borrower, ISilo.CollateralType.Protected);

        //call to withdraw
        withdraw@withrevert(e, max, borrower, borrower, ISilo.CollateralType.Protected);

        satisfy !lastReverted;
    }

    // maxWithdraw(collateral):using the results from maxWithdraw(collateral) to call withdraw(collateral) should be possible (satisfy not revert)
    rule maxWithdrawCollateralWorksForWithdrawCollateral(env e) {
        configForEightTokensSetupRequirements();
        address borrower;

        // Block time-stamp >= interest rate time-stamp
        silosTimestampSetupRequirements(e);

        //call to max
        uint256 max = maxWithdraw(e, borrower, ISilo.CollateralType.Collateral);

        //call to withdraw
        withdraw@withrevert(e, max, borrower, borrower, ISilo.CollateralType.Collateral);

        satisfy !lastReverted;
    }

    // maxRedeem(protected):using the results from maxRedeem(protected) to call redeem(protected) should be possible (satisfy not revert)
    rule maxRedeemProtectedWorksForRedeemProtected(env e) {
        configForEightTokensSetupRequirements();
        address borrower;

        // Block time-stamp >= interest rate time-stamp
        silosTimestampSetupRequirements(e);

        //call to max
        uint256 max = maxRedeem(e, borrower, ISilo.CollateralType.Protected);

        //call to redeem
        redeem@withrevert(e, max, borrower, borrower, ISilo.CollateralType.Protected);

        satisfy !lastReverted;
    }
    
    // maxRedeem(collateral):using the results from maxRedeem(collateral) to call redeem(collateral) should be possible (satisfy not revert)
    rule maxRedeemCollateralWorksForRedeemCollateral(env e) {
        configForEightTokensSetupRequirements();
        address borrower;

        // Block time-stamp >= interest rate time-stamp
        silosTimestampSetupRequirements(e);

        //call to max
        uint256 max = maxRedeem(e, borrower, ISilo.CollateralType.Collateral);

        //call to redeem
        redeem@withrevert(e, max, borrower, borrower, ISilo.CollateralType.Collateral);

        satisfy !lastReverted;
    }

    // maxBorrow():using the results from maxBorrow() to call borrow() should be possible (satisfy not revert)
    rule maxBorrowWorksForBorrow(env e) {
        configForEightTokensSetupRequirements();
        address borrower;

        // Block time-stamp >= interest rate time-stamp
        silosTimestampSetupRequirements(e);

        //call to max
        uint256 max = maxBorrow(e, borrower);

        //call to borrow
        borrow@withrevert(e, max, borrower, borrower);

        satisfy !lastReverted;
    }
    
    // maxBorrowShares():using the results from maxBorrowShares() to call borrowShares() should be possible (satisfy not revert)
    rule maxBorrowSharesWorksForBorrowShares(env e) {
        configForEightTokensSetupRequirements();
        address borrower;

        //call to max
        uint256 max = maxBorrowShares(e, borrower);

        //call to borrow
        borrowShares@withrevert(e, max, borrower, borrower);

        satisfy !lastReverted;
    }
    
    // maxBorrowSameAsset():using the results from maxBorrowSameAsset() to call borrowSameAsset() should be possible (satisfy not revert)
    rule maxBorrowSameAssetWorksForBorrowSameAsset(env e) {
        configForEightTokensSetupRequirements();
        address borrower;

        //call to max
        uint256 max = maxBorrowSameAsset(e, borrower);

        //call to borrow
        borrowSameAsset@withrevert(e, max, borrower, borrower);

        satisfy !lastReverted;
    }
    
    // maxRepay():using the results from maxRepay() to call repay() should be possible (satisfy not revert)
    rule maxRepayWorksForRepay(env e) {
        configForEightTokensSetupRequirements();
        address borrower;

        //call to max
        uint256 max = maxRepay(e, borrower);

        //call to repay
        repay@withrevert(e, max, borrower);

        satisfy !lastReverted;
    }
    
    // maxRepayShares():using the results from maxRepayShares() to call repayShares() should be possible (satisfy not revert)
    rule maxRepaySharesWorksForRepayShares(env e) {
        configForEightTokensSetupRequirements();
        address borrower;

        //call to max
        uint256 max = maxRepayShares(e, borrower);

        //call to repay
        repayShares@withrevert(e, max, borrower);

        satisfy !lastReverted;
    }
    
    // maxFlashLoan():using the results from maxFlashLoan() to call flashLoan() should be possible (satisfy not revert)
    rule maxFlashLoanWorksForFlashLoan(env e) {
        configForEightTokensSetupRequirements();
        address receiver;
        address token = token0;
        uint256 amount;
        bytes data;

        //call to max
        uint256 max = maxFlashLoan(e, token);

        //call to flashLoan
        flashLoan@withrevert(e, receiver, token, amount, data);

        satisfy !lastReverted;
    }

    //maxFlashLoan(): for token != token0 the result is 0
    rule maxFlashLoanForTokenNotToken0(env e) {
        configForEightTokensSetupRequirements();
        address token;
        require(token != token0);

        //call to max
        uint256 max = maxFlashLoan(e, token);

        assert max == 0;
    }



//------------------------------- RULES TEST END ----------------------------------

//------------------------------- RULES PROBLEMS START ----------------------------------

//------------------------------- RULES PROBLEMS START ----------------------------------

//------------------------------- RULES OK START ------------------------------------

//------------------------------- RULES OK END ------------------------------------

//------------------------------- INVARIENTS OK START-------------------------------

//------------------------------- INVARIENTS OK END-------------------------------

//------------------------------- ISSUES OK START-------------------------------

//------------------------------- ISSUES OK END-------------------------------
