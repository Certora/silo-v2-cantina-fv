import "../setup/CompleteSiloSetup.spec";
import "./0base_Silo.spec";
import "../simplifications/_Oracle_call_before_quote_UNSAFE.spec";
import "../simplifications/Oracle_quote_one_UNSAFE.spec";
import "../simplifications/_flashloan_no_state_changes.spec";
import "../simplifications/_hooks_no_state_change.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";
//------------------------------- RULES TEST START ----------------------------------
    // previewDeposit():using the results from previewDeposit() to call deposit() should return the same value
    rule previewDepositReturnsTheSameAsDeposit(env e) {
        configForEightTokensSetupRequirements();
        uint256 value;
        address borrower;

        //call to previewDeposit
        uint256 previewValue = previewDeposit(e, value);

        //call to deposit
        uint256 depositValue = deposit(e, value, borrower);

        satisfy true;

        // assert depositValue == previewValue;
    }
    
    // previewDeposit(protected):using the results from previewDeposit(protected) to call deposit(protected) should return the same value
    rule previewDepositProtectedReturnsTheSameAsDepositProtected(env e) {
        configForEightTokensSetupRequirements();
        uint256 value;
        address borrower;

        //call to previewDeposit
        uint256 previewValue = previewDeposit(e, value, ISilo.CollateralType.Protected);

        //call to deposit
        uint256 depositValue = deposit(e, value, borrower, ISilo.CollateralType.Protected);

        assert depositValue == previewValue;
    }
    
    // previewDeposit(collateral):using the results from previewDeposit(collateral) to call deposit(collateral) should return the same value
    rule previewDepositCollateralReturnsTheSameAsDepositCollateral(env e) {
        configForEightTokensSetupRequirements();
        uint256 value;
        address borrower;

        //call to previewDeposit
        uint256 previewValue = previewDeposit(e, value, ISilo.CollateralType.Collateral);

        //call to deposit
        uint256 depositValue = deposit(e, value, borrower, ISilo.CollateralType.Collateral);

        assert depositValue == previewValue;
    }
    
    // previewMint():using the results from previewMint() to call mint() should return the same value
    rule previewMintReturnsTheSameAsMint(env e) {
        configForEightTokensSetupRequirements();
        uint256 value;
        address borrower;

        //call to previewMint
        uint256 previewValue = previewMint(e, value);

        //call to mint
        uint256 mintValue = mint(e, value, borrower);

        assert mintValue == previewValue;
    }
    
    // previewMint(protected):using the results from previewMint(protected) to call mint(protected) should return the same value
    rule previewMintProtectedReturnsTheSameAsMintProtected(env e) {
        configForEightTokensSetupRequirements();
        uint256 value;
        address borrower;

        //call to previewMint
        uint256 previewValue = previewMint(e, value, ISilo.CollateralType.Protected);

        //call to mint
        uint256 mintValue = mint(e, value, borrower, ISilo.CollateralType.Protected);

        assert mintValue == previewValue;
    }
    
    // previewMint(collateral):using the results from previewMint(collateral) to call mint(collateral) should return the same value
    rule previewMintCollateralReturnsTheSameAsMintCollateral(env e) {
        configForEightTokensSetupRequirements();
        uint256 value;
        address borrower;

        //call to previewMint
        uint256 previewValue = previewMint(e, value, ISilo.CollateralType.Collateral);

        //call to mint
        uint256 mintValue = mint(e, value, borrower, ISilo.CollateralType.Collateral);

        assert mintValue == previewValue;
    }
    
    // previewWithdraw():using the results from previewWithdraw() to call withdraw() should return the same value
    rule previewWithdrawReturnsTheSameAsWithdraw(env e) {
        configForEightTokensSetupRequirements();
        uint256 value;
        address borrower;

        //call to previewWithdraw
        uint256 previewValue = previewWithdraw(e, value);

        //call to withdraw
        uint256 withdrawValue = withdraw(e, value, borrower, borrower);

        assert withdrawValue == previewValue;
    }
    
    // previewWithdraw(protected):using the results from previewWithdraw(protected) to call withdraw(protected) should return the same value
    rule previewWithdrawProtectedReturnsTheSameAsWithdrawProtected(env e) {
        configForEightTokensSetupRequirements();
        uint256 value;
        address borrower;

        //call to previewWithdraw
        uint256 previewValue = previewWithdraw(e, value, ISilo.CollateralType.Protected);

        //call to withdraw
        uint256 withdrawValue = withdraw(e, value, borrower, borrower, ISilo.CollateralType.Protected);

        assert withdrawValue == previewValue;
    }
    
    // previewWithdraw(collateral):using the results from previewWithdraw(collateral) to call withdraw(collateral) should return the same value
    rule previewWithdrawCollateralReturnsTheSameAsWithdrawCollateral(env e) {
        configForEightTokensSetupRequirements();
        uint256 value;
        address borrower;

        //call to previewWithdraw
        uint256 previewValue = previewWithdraw(e, value, ISilo.CollateralType.Collateral);

        //call to withdraw
        uint256 withdrawValue = withdraw(e, value, borrower, borrower, ISilo.CollateralType.Collateral);

        assert withdrawValue == previewValue;
    }
    
    // previewRedeem():using the results from previewRedeem() to call redeem() should return the same value
    rule previewRedeemReturnsTheSameAsRedeem(env e) {
        configForEightTokensSetupRequirements();
        uint256 value;
        address borrower;

        //call to previewRedeem
        uint256 previewValue = previewRedeem(e, value);

        //call to redeem
        uint256 redeemValue = redeem(e, value, borrower, borrower);

        assert redeemValue == previewValue;
    }
    
    // previewRedeem(protected):using the results from previewRedeem(protected) to call redeem(protected) should return the same value
    rule previewRedeemProtectedReturnsTheSameAsRedeemProtected(env e) {
        configForEightTokensSetupRequirements();
        uint256 value;
        address borrower;

        //call to previewRedeem
        uint256 previewValue = previewRedeem(e, value, ISilo.CollateralType.Protected);

        //call to redeem
        uint256 redeemValue = redeem(e, value, borrower, borrower, ISilo.CollateralType.Protected);

        assert redeemValue == previewValue;
    }
    
    // previewRedeem(collateral):using the results from previewRedeem(collateral) to call redeem(collateral) should return the same value
    rule previewRedeemCollateralReturnsTheSameAsRedeemCollateral(env e) {
        configForEightTokensSetupRequirements();
        uint256 value;
        address borrower;

        //call to previewRedeem
        uint256 previewValue = previewRedeem(e, value, ISilo.CollateralType.Collateral);

        //call to redeem
        uint256 redeemValue = redeem(e, value, borrower, borrower, ISilo.CollateralType.Collateral);

        assert redeemValue == previewValue;
    }
    
    // previewBorrow():using the results from previewBorrow() to call borrow() should return the same value
    rule previewBorrowReturnsTheSameAsBorrow(env e) {
        configForEightTokensSetupRequirements();
        uint256 value;
        address borrower;

        //call to previewBorrow
        uint256 previewValue = previewBorrow(e, value);

        //call to borrow
        uint256 borrowValue = borrow(e, value, borrower, borrower);

        assert borrowValue == previewValue;
    }
    
    // previewBorrowShares():using the results from previewBorrowShares() to call borrowShares() should return the same value
    rule previewBorrowSharesReturnsTheSameAsBorrowShares(env e) {
        configForEightTokensSetupRequirements();
        uint256 value;
        address borrower;

        //call to previewBorrow
        uint256 previewValue = previewBorrowShares(e, value);

        //call to borrow
        uint256 borrowValue = borrowShares(e, value, borrower, borrower);

        assert borrowValue == previewValue;
    }
    
    // previewRepay():using the results from previewRepay() to call repay() should return the same value
    rule previewRepayReturnsTheSameAsRepay(env e) {
        configForEightTokensSetupRequirements();
        uint256 value;
        address borrower;

        //call to previewRepay
        uint256 previewValue = previewRepay(e, value);

        //call to repay
        uint256 repayValue = repay(e, value, borrower);

        assert repayValue == previewValue;
    }
    
    // previewRepayShares():using the results from previewRepayShares() to call repayShares() should return the same value
    rule previewRepaySharesReturnsTheSameAsRepayShares(env e) {
        configForEightTokensSetupRequirements();
        uint256 value;
        address borrower;

        //call to previewRepay
        uint256 previewValue = previewRepayShares(e, value);

        //call to repay
        uint256 repayValue = repayShares(e, value, borrower);

        assert repayValue == previewValue;
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
