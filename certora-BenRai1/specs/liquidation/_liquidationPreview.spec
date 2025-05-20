//------------------------- Defintions --------------------------
definition _BAD_DEBT() returns uint256 = 10^18;


//------------------------------- RULES TEST START ----------------------------------

    // // liquidationPreview() ltvAfter never higher than ltvBefore
    // rule ltvAfterNeverHigherThanBefore(env e) {
    //     uint256 ltvBefore;
    //     uint256 sumOfCollateralAssets;
    //     uint256 sumOfCollateralValue;
    //     uint256 borrowerDebtAssets;
    //     uint256 borrowerDebtValue;
    //     PartialLiquidationLib.LiquidationPreviewParams _params;
    //     require (sumOfCollateralAssets > 0 <=> sumOfCollateralValue > 0);
    //     require (borrowerDebtAssets > 0 <=> borrowerDebtValue > 0);

    //     uint256 actuallLtv = calculateLtvAfterHarness(e, sumOfCollateralValue, borrowerDebtValue, 0,0);

    //     require ltvBefore == actuallLtv;

    //     uint256 collateralToLiquidate; 
    //     uint256 debtToRepay;
    //     uint256 ltvAfter;

    //     //function call 
    //     (collateralToLiquidate, debtToRepay, ltvAfter) = liquidationPreviewHarness(e, ltvBefore, sumOfCollateralAssets, sumOfCollateralValue, borrowerDebtAssets, borrowerDebtValue, _params);

    //     //check
    //     assert ltvAfter <= ltvBefore;
        
    // }

    
    // // liquidationPreview() debtToRapay != 0 => collateralToLiquidate is debtToRepay + Fees
    // rule debtToRepayNotZeroCollateralToLiquidateDebtToRepayFees(env e) {
    //     uint256 ltvBefore;
    //     uint256 sumOfCollateralAssets;
    //     uint256 sumOfCollateralValue;
    //     uint256 borrowerDebtAssets;
    //     uint256 borrowerDebtValue;
    //     PartialLiquidationLib.LiquidationPreviewParams params;
    //     require(sumOfCollateralValue > 0 <=> sumOfCollateralAssets > 0);
    //     require(borrowerDebtValue > 0 <=> borrowerDebtAssets > 0);

    //     uint256 collateralToLiquidate; 
    //     uint256 debtToRepay;
    //     uint256 ltvAfter;

    //     //function call 
    //     (collateralToLiquidate, debtToRepay, ltvAfter) = liquidationPreviewHarness(e, ltvBefore, sumOfCollateralAssets, sumOfCollateralValue, borrowerDebtAssets, borrowerDebtValue, params);
    //     require(debtToRepay != 0);

    //     uint256 assetsAndFees = calculateCollateralToLiquidateHarness(e, debtToRepay, sumOfCollateralValue, params.liquidationFee);

    //     //check
    //         assert collateralToLiquidate == assetsAndFees;
    // }

   

//------------------------------- RULES TEST END ----------------------------------

//------------------------------- RULES PROBLEMS START ----------------------------------

//------------------------------- RULES PROBLEMS START ----------------------------------

//------------------------------- RULES OK START ------------------------------------

     // liquidationPreview() ltvAfter equals the result from borrwer values before and return values
    rule ltvAfterEqualsBorrowerValuesBeforeAndReturnValues(env e) {
        uint256 ltvBefore;
        uint256 sumOfCollateralAssets;
        uint256 sumOfCollateralValue;
        uint256 borrowerDebtAssets;
        uint256 borrowerDebtValue;
        PartialLiquidationLib.LiquidationPreviewParams _params;
        //exchangeRate = 1
        require(sumOfCollateralValue == sumOfCollateralAssets);
        require(borrowerDebtValue == borrowerDebtAssets);

        uint256 collateralToLiquidate; 
        uint256 debtToRepay;
        uint256 ltvAfter;

        //function call 
        (collateralToLiquidate, debtToRepay, ltvAfter) = liquidationPreviewHarness(e, ltvBefore, sumOfCollateralAssets, sumOfCollateralValue, borrowerDebtAssets, borrowerDebtValue, _params);

        uint256 targetLtvAfter = collateralToLiquidate == sumOfCollateralValue ?  0 : calculateLtvAfterHarness(e, sumOfCollateralValue, borrowerDebtValue, collateralToLiquidate, debtToRepay); 

        //check
        assert ltvAfter == targetLtvAfter;
    }

    // liquidationPreview() collateralToLiquidate never bigger than sumOfCollateralAssets
    rule collateralToLiquidateNeverBiggerThanSumOfCollateralAssets(env e) {
        uint256 ltvBefore;
        uint256 sumOfCollateralAssets;
        uint256 sumOfCollateralValue;
        uint256 borrowerDebtAssets;
        uint256 borrowerDebtValue;
        PartialLiquidationLib.LiquidationPreviewParams _params;

        uint256 collateralToLiquidate; 
        uint256 debtToRepay;
        uint256 ltvAfter;

        //function call 
        (collateralToLiquidate, debtToRepay, ltvAfter) = liquidationPreviewHarness(e, ltvBefore, sumOfCollateralAssets, sumOfCollateralValue, borrowerDebtAssets, borrowerDebtValue, _params);

        //check
        assert collateralToLiquidate <= sumOfCollateralAssets;
        
    }
  
    // liquidationPreview() if BAD_DEBT, debt to rapay is the smaller of _params.maxDebtToCover and _borrowerDebtAssets
    rule ifBadDebtDebtToRepaySmallerOf(env e) {
        uint256 ltvBefore;
        uint256 sumOfCollateralAssets;
        uint256 sumOfCollateralValue;
        uint256 borrowerDebtAssets;
        uint256 borrowerDebtValue;
        PartialLiquidationLib.LiquidationPreviewParams _params;
        require(ltvBefore >= _BAD_DEBT());

        uint256 collateralToLiquidate; 
        uint256 debtToRepay;
        uint256 ltvAfter;

        //function call 
        (collateralToLiquidate, debtToRepay, ltvAfter) = liquidationPreviewHarness(e, ltvBefore, sumOfCollateralAssets, sumOfCollateralValue, borrowerDebtAssets, borrowerDebtValue, _params);

        uint256 targetDebtToRepay = _params.maxDebtToCover < borrowerDebtAssets ? _params.maxDebtToCover : borrowerDebtAssets;

        //check
            assert debtToRepay == targetDebtToRepay;
    }
    
    // liquidationPreview() debtToRepay never bigger than borrowerDebtAssets
    rule debtToRepayNeverBiggerThanBorrowerDebtAssets(env e) {
        uint256 ltvBefore;
        uint256 sumOfCollateralAssets;
        uint256 sumOfCollateralValue;
        uint256 borrowerDebtAssets;
        uint256 borrowerDebtValue;
        PartialLiquidationLib.LiquidationPreviewParams _params;

        uint256 collateralToLiquidate; 
        uint256 debtToRepay;
        uint256 ltvAfter;

        //function call 
        (collateralToLiquidate, debtToRepay, ltvAfter) = liquidationPreviewHarness(e, ltvBefore, sumOfCollateralAssets, sumOfCollateralValue, borrowerDebtAssets, borrowerDebtValue, _params);

        //check
        assert debtToRepay <= borrowerDebtAssets;
        
    }


//------------------------------- RULES OK END ------------------------------------

//------------------------------- INVARIENTS OK START-------------------------------

//------------------------------- INVARIENTS OK END-------------------------------

//------------------------------- ISSUES OK START-------------------------------

//------------------------------- ISSUES OK END-------------------------------
