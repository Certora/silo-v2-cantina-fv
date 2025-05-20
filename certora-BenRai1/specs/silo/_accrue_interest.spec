import "../setup/CompleteSiloSetup.spec";

// methods{
    
// }


//------------------------------- RULES TEST START ----------------------------------

    // * `deposit()`/`mint()`/`repay()`/`repayShares()`/`borrowSameAsset()` should always call `accrueInterest()` on one (called) Silo

    // * `accrueInterest()` should never revert
    rule accrueInterestNeverRevert(env e) {
        configForEightTokensSetupRequirements();

        uint256 daoFee;
        uint256 deployerFee;
        (daoFee, deployerFee, _, _) = siloConfig.getFeesWithAsset(e, silo0);

        require(e.msg.value == 0);
        require(daoFee + deployerFee < 10^18); //less than 100%
        //function call
        accrueInterest@withrevert(e);

        assert !lastReverted;
    }

    // * `accrueInterest()` should be invisible for any other function including other silo and share tokens //@audit HÄ?

    // * `accrueInterest()` calling twice is the same as calling once (in a single block) //@audit-issue check for default havoc
    rule accrueInterestTwiceIsSameAsOnce(env e) {
        configForEightTokensSetupRequirements();

        require(e.msg.value == 0);

        //inital state
        storage init = lastStorage;

        //one call
        accrueInterest(e);
        storage oneCall = lastStorage;

        //two calls
        accrueInterest(e);
        accrueInterest(e);

        storage twoCalls = lastStorage;
        assert oneCall == twoCalls;
    }

    // * `accrueInterest()` should never decrease total collateral and total debt
    rule accrueInterestNeverDecreaseTotalCollateralAndTotalDebt(env e) {
        configForEightTokensSetupRequirements();

        //values before
        uint256 totalProtectedAssetsBefore = getTotalAssetsStorage(ISilo.AssetType.Protected);
        uint256 totalCollateralAssetsBefore = getTotalAssetsStorage(ISilo.AssetType.Collateral);
        uint256 totalDebtAssetsBefore = getTotalAssetsStorage(ISilo.AssetType.Debt);

        //function call
        accrueInterest(e);

        //values after
        uint256 totalProtectedAssetsAfter = getTotalAssetsStorage(ISilo.AssetType.Protected);
        uint256 totalCollateralAssetsAfter = getTotalAssetsStorage(ISilo.AssetType.Collateral);
        uint256 totalDebtAssetsAfter = getTotalAssetsStorage(ISilo.AssetType.Debt);

        assert totalProtectedAssetsAfter >= totalProtectedAssetsBefore;
        assert totalCollateralAssetsAfter >= totalCollateralAssetsBefore;
        assert totalDebtAssetsAfter >= totalDebtAssetsBefore;
    }

    // * `withdraw()`/`redeem()`/`borrow()`/`borrowShares()` should always call `accrueInterest()` on both Silos

    // * `accrueInterestForSilo()` is equal to `accrueInterest()`. All storage should be equally updated.
    rule accrueInterestForConfigIsEqual(env e) {
        configForEightTokensSetupRequirements();


        //inital state
        storage init = lastStorage;

        //function call
        siloConfig.accrueInterestForSilo(e, silo0);
        storage configCall = lastStorage;

        //function call
        accrueInterest(e);
        storage directCall = lastStorage;

        assert configCall == directCall;
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
