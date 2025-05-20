/* Rules concerning borrow shares  */

import "../setup/CompleteSiloSetup.spec";
import "./0base_Silo.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";
import "../simplifications/_Oracle_call_before_quote_UNSAFE.spec";
import "../simplifications/_hooks_no_state_change.spec";
import "../simplifications/Oracle_quote_one_UNSAFE.spec";

//------------------------------- RULES TEST START ----------------------------------

    // borrowShares decreases balanceToken0 of silo0 by _assets
    rule borrowSharesDecreasesBalanceOfToken0ByAssets(env e) {
        configForEightTokensSetupRequirements();
        address receiver;
        address borrower;
        uint256 shares;
        SafeAssumptions_withInvariants(e, receiver);
        SafeAssumptions_withInvariants(e, borrower);
        require(receiver != silo0);
        
        //values before
        uint256 balanceToken0Before = token0.balanceOf(silo0);

        //function call
        uint256 assets = borrowShares(e, shares, receiver, borrower);

        //values after
        uint256 balanceToken0After = token0.balanceOf(silo0);

        //asserts
        assert balanceToken0After == balanceToken0Before - assets;
    }

    // borrowShares increses balanceToken0 of receiver by _assets 
    rule borrowSharesIncreasesBalanceOfToken0OfReceiverByAssets(env e) {
        configForEightTokensSetupRequirements();
        address receiver;
        address borrower;
        uint256 shares;
        totalSuppliesMoreThanBalances(receiver, silo0);
        require(receiver != silo0);

        
        //values before
        uint256 balanceToken0Before = token0.balanceOf(receiver);

        //function call
        uint256 assets = borrowShares(e, shares, receiver, borrower);

        //values after
        uint256 balanceToken0After = token0.balanceOf(receiver);

        //asserts
        assert balanceToken0After == balanceToken0Before + assets;
    }

    // borrowShares increses total supply of debtShare by increase of debt shares of borrowShares
    rule borrowSharesIncreasesTotalSupplyOfDebtShareByShares(env e) {
        configForEightTokensSetupRequirements();
        address receiver;
        address borrower;
        uint256 shares;
        totalSuppliesMoreThanBalances(receiver, silo0);
        
        //values before
        uint256 totalSupplyDebtShareBefore = shareDebtToken0.totalSupply();
        require(totalSupplyDebtShareBefore + shares < max_uint256);
        uint256 balanceDebtShareBefore = shareDebtToken0.balanceOf(borrower);

        //function call
        borrowShares(e, shares, receiver, borrower);

        //values after
        uint256 totalSupplyDebtShareAfter = shareDebtToken0.totalSupply();
        uint256 balanceDebtShareAfter = shareDebtToken0.balanceOf(borrower);

        //asserts
        assert totalSupplyDebtShareAfter == totalSupplyDebtShareBefore + shares;
        assert balanceDebtShareAfter == balanceDebtShareBefore + shares;
    }

    // borrowShares results in > 0 debtShare for the borrower
    rule borrowSharesResultsInPositiveDebtShareForBorrower(env e) {
        configForEightTokensSetupRequirements();
        address receiver;
        address borrower;
        uint256 shares;
        totalSuppliesMoreThanBalances(receiver, silo0);
        
        //values before
        uint256 balanceDebtShareBefore = shareDebtToken0.balanceOf(borrower);
        require(balanceDebtShareBefore + shares < max_uint256);

        //function call
        borrowShares(e, shares, receiver, borrower);

        //values after
        uint256 balanceDebtShareAfter = shareDebtToken0.balanceOf(borrower);

        //asserts
        assert balanceDebtShareAfter > balanceDebtShareBefore;
    }

    // borrowShares increases debtAssets by _assets if no interest is accrued
    rule borrowSharesIncreasesDebtAssetsByAssetsIfNoInterestIsAccrued(env e) {
        configForEightTokensSetupRequirements();
        address receiver;
        address borrower;
        uint256 shares;
        totalSuppliesMoreThanBalances(receiver, silo0);
        
        //values before
        uint256 debtAssetsBefore;
        (_, _, _, _, debtAssetsBefore) = getSiloStorage();
        
        //function call
        uint256 assets = borrowShares(e, shares, receiver, borrower);

        //values after
        uint256 debtAssetsAfter;
        (_, _, _, _, debtAssetsAfter) = getSiloStorage();

        //asserts
        assert debtAssetsAfter == debtAssetsBefore + assets;
    }

    // borrowShares reverts if borrower has debtShares in silo1
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

    // borrowShares sets silo1 as borrowShareserCollateralSilo
    rule borrowSharesSetsBorrowerCollateralSilo(env e) {
        configForEightTokensSetupRequirements();
        address receiver;
        address borrower;
        uint256 shares;

        totalSuppliesMoreThanBalances(receiver, silo0);        
        //function call
        borrowShares(e, shares, receiver, borrower);

        //asserts
        assert siloConfig.borrowerCollateralSilo(borrower) == silo1;
    }

    // borrowShares is solvent after borrowShares (isBelowMaxLtv)
    rule borrowSharesIsSolventAfterBorrowShares(env e) {
        configForEightTokensSetupRequirements();
        address receiver;
        address borrower;
        uint256 shares;
        totalSuppliesMoreThanBalances(receiver, silo0);
        uint256 maxLtv = siloConfig.getConfig(e, silo0).maxLtv;

        //values before
        uint256 ltvBorrowerBefore = getLTV(e, borrower);
        
        //function call
        borrowShares(e, shares, receiver, borrower);

        //values after
        uint256 ltvBorrowerAfter = getLTV(e, borrower);

        //asserts
        assert ltvBorrowerAfter <= maxLtv;
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
