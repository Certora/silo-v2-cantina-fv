
//---------------------- DEFINITIONS -----------------------------

definition PRECISION_DECIMALS() returns uint256 = 10^18; 
definition DEBT_DUST_LEVEL() returns uint256 = 9*10^17;


//------------------------------- RULES TEST START ----------------------------------

    // estimateMaxRepayValue() returns 0 if user has not debt _totalBorrowerDebtValue == 0
    rule returnZeroIfNoDebt(env e) {
        uint256 totalBorrowerDebtValue; 
        uint256 totalBorrowerCollateralValue;
        uint256 ltvAfterLiquidation;
        uint256 liquidationFee;
        require(totalBorrowerDebtValue == 0);

        //function call
        uint256 returnValue = estimateMaxRepayValueHarness(e, totalBorrowerDebtValue, totalBorrowerCollateralValue, ltvAfterLiquidation, liquidationFee);

        assert(returnValue == 0);
    }

    // estimateMaxRepayValue() returns 0 if liquidation fee is to high _liquidationFee >= _PRECISION_DECIMALS
    rule returnZeroIfFeeToHigh(env e) {
        uint256 totalBorrowerDebtValue; 
        uint256 totalBorrowerCollateralValue;
        uint256 ltvAfterLiquidation;
        uint256 liquidationFee;
        require(liquidationFee >= PRECISION_DECIMALS());

        //function call
        uint256 returnValue = estimateMaxRepayValueHarness(e, totalBorrowerDebtValue, totalBorrowerCollateralValue, ltvAfterLiquidation, liquidationFee);

        assert(returnValue == 0);
    }

    // estimateMaxRepayValue() returns _totalBorrowerDebtValue if debtValue is bigger that collateralValue
    rule returnDebtIfDebtBiggerThanCollateral(env e) {
        uint256 totalBorrowerDebtValue; 
        uint256 totalBorrowerCollateralValue;
        uint256 ltvAfterLiquidation;
        uint256 liquidationFee;
        //prevent earlier returns
        require(totalBorrowerDebtValue > 0);
        require(liquidationFee < PRECISION_DECIMALS());
        //requirement
        require(totalBorrowerDebtValue > totalBorrowerCollateralValue);

        //function call
        uint256 returnValue = estimateMaxRepayValueHarness(e, totalBorrowerDebtValue, totalBorrowerCollateralValue, ltvAfterLiquidation, liquidationFee);

        assert(returnValue == totalBorrowerDebtValue);
    }

    // estimateMaxRepayValue() returns _totalBorrowerDebtValue for full liquidation (_ltvAfterLiquidation == 0)
    rule returnDebtIfFullLiquidation(env e) {
        uint256 totalBorrowerDebtValue; 
        uint256 totalBorrowerCollateralValue;
        uint256 ltvAfterLiquidation;
        uint256 liquidationFee;
        //prevent earlier returns
        require(totalBorrowerDebtValue > 0);
        require(liquidationFee < PRECISION_DECIMALS());
        require(totalBorrowerDebtValue < totalBorrowerCollateralValue);
        //requirement
        require(ltvAfterLiquidation == 0);

        //function call
        uint256 returnValue = estimateMaxRepayValueHarness(e, totalBorrowerDebtValue, totalBorrowerCollateralValue, ltvAfterLiquidation, liquidationFee);

        assert(returnValue == totalBorrowerDebtValue);
    }

    // estimateMaxRepayValue() returns 0 if current LTV lower than target LTV (ltCv >= _totalBorrowerDebtValue)
    rule returnZeroIfLtvLowerThanTarget(env e) {
        uint256 totalBorrowerDebtValue; 
        uint256 totalBorrowerCollateralValue;
        uint256 ltvAfterLiquidation;
        uint256 liquidationFee;
        //prevent earlier returns
        require(totalBorrowerDebtValue > 0);
        require(liquidationFee < PRECISION_DECIMALS());
        require(totalBorrowerDebtValue < totalBorrowerCollateralValue);
        require(ltvAfterLiquidation != 0);
        //requirement
        mathint ltCv = ltvAfterLiquidation * totalBorrowerCollateralValue;
        mathint adjustedBorrowerDebtValue = totalBorrowerDebtValue * PRECISION_DECIMALS();
        require(ltCv >= adjustedBorrowerDebtValue);

        //function call
        uint256 returnValue = estimateMaxRepayValueHarness(e, totalBorrowerDebtValue, totalBorrowerCollateralValue, ltvAfterLiquidation, liquidationFee);

        assert(returnValue == 0);
    }

    // estimateMaxRepayValue() returns _totalBorrowerValue if it is not possible to reach the targetVTL ratio (dividerR >= _PRECISION_DECIMALS)
    rule returnDebtIfNotPossibleToReachTarget(env e) {
        uint256 totalBorrowerDebtValue; 
        uint256 totalBorrowerCollateralValue;
        uint256 ltvAfterLiquidation;
        uint256 liquidationFee;
        //prevent earlier returns
        require(totalBorrowerDebtValue > 0);
        require(liquidationFee < PRECISION_DECIMALS());
        require(totalBorrowerDebtValue < totalBorrowerCollateralValue);
        require(ltvAfterLiquidation != 0);
        mathint ltCv = ltvAfterLiquidation * totalBorrowerCollateralValue;
        mathint adjustedBorrowerDebtValue = totalBorrowerDebtValue * PRECISION_DECIMALS();
        require(ltCv < adjustedBorrowerDebtValue);
        //requirement
        mathint dividerR = ltvAfterLiquidation + ltvAfterLiquidation * liquidationFee / PRECISION_DECIMALS();
        require(dividerR >= PRECISION_DECIMALS());

        //function call
        uint256 returnValue = estimateMaxRepayValueHarness(e, totalBorrowerDebtValue, totalBorrowerCollateralValue, ltvAfterLiquidation, liquidationFee);

        assert(returnValue == totalBorrowerDebtValue);
    }

    // estimateMaxRepayValue() return value is never bigger than _totalBorrowerDebtValue
    rule returnValueNeverBiggerThanDebt(env e) {
        uint256 totalBorrowerDebtValue; 
        uint256 totalBorrowerCollateralValue;
        uint256 ltvAfterLiquidation;
        uint256 liquidationFee;
        
        //function call
        uint256 returnValue = estimateMaxRepayValueHarness(e, totalBorrowerDebtValue, totalBorrowerCollateralValue, ltvAfterLiquidation, liquidationFee);

        assert(returnValue <= totalBorrowerDebtValue);
    }

    // estimateMaxRepayValue() returns totalBorrowerDebtValue if calculated repay value is bigger than totalBorrowerDebtValue
    rule returnDebtIfCalculatedValueBiggerThanDebt(env e) {
        uint256 totalBorrowerDebtValue; 
        uint256 totalBorrowerCollateralValue;
        uint256 ltvAfterLiquidation;
        uint256 liquidationFee;
        //prevent earlier returns
        require(totalBorrowerDebtValue > 0);
        require(liquidationFee < PRECISION_DECIMALS());
        require(totalBorrowerDebtValue < totalBorrowerCollateralValue);
        require(ltvAfterLiquidation != 0);
        mathint ltCv = ltvAfterLiquidation * totalBorrowerCollateralValue;
        mathint adjustedBorrowerDebtValue = totalBorrowerDebtValue * PRECISION_DECIMALS();
        require(ltCv < adjustedBorrowerDebtValue);
        mathint dividerR = ltvAfterLiquidation + ltvAfterLiquidation * liquidationFee / PRECISION_DECIMALS();
        require(dividerR >= PRECISION_DECIMALS());
        //requirement
        mathint repayValue = totalBorrowerDebtValue - ltCv;
        require(repayValue > totalBorrowerDebtValue);

        //function call
        uint256 returnValue = estimateMaxRepayValueHarness(e, totalBorrowerDebtValue, totalBorrowerCollateralValue, ltvAfterLiquidation, liquidationFee);

        assert(returnValue == totalBorrowerDebtValue);
    } 

    // estimateMaxRepayValue() return value does not allow for dust 
    rule returnValueDoesNotAllowForDust(env e) {
        uint256 totalBorrowerDebtValue; 
        uint256 totalBorrowerCollateralValue;
        uint256 ltvAfterLiquidation;
        uint256 liquidationFee;
        require(totalBorrowerDebtValue > 0);
        
        //function call
        uint256 returnValue = estimateMaxRepayValueHarness(e, totalBorrowerDebtValue, totalBorrowerCollateralValue, ltvAfterLiquidation, liquidationFee);

        mathint repayRatio = returnValue * PRECISION_DECIMALS() / totalBorrowerDebtValue;        
        assert(returnValue != 0 => repayRatio <= DEBT_DUST_LEVEL() || repayRatio == PRECISION_DECIMALS());
    }


    // valueToAssetsByRatio() reverts if totalValue == 0
    rule revertIfTotalValueZero(env e) {
        uint256 value;
        uint256 totalAssets;
        uint256 totalValue;
        require(totalValue == 0);

        //function call
        valueToAssetsByRatioHarness@withrevert(e, value, totalAssets, totalValue);

        assert lastReverted;
    }

    // valueToAssetsByRatio() returns the ratio between the given parameters
    rule returnRatio(env e) {
        uint256 value;
        uint256 totalAssets;
        uint256 totalValue;
        require(totalValue > 0);

        //function call
        uint256 returnValue = valueToAssetsByRatioHarness(e, value, totalAssets, totalValue);

        assert returnValue == value * totalAssets / totalValue;
    }

    // calculateCollateralToLiquidate() never returns more than sumOfCollateral
    rule neverReturnMoreThanCollateralSum(env e) {
        uint256 debtToCover;
        uint256 sumOfCollateral;
        uint256 fees;

        //function call
        uint256 returnValue = calculateCollateralToLiquidateHarness(e, debtToCover, sumOfCollateral, fees);

        assert returnValue <= sumOfCollateral;
    }

    // calculateCollateralToLiquidate() returns debtToCover + fees
    rule returnDebtPlusFees(env e) {
        uint256 debtToCover;
        uint256 sumOfCollateral;
        uint256 fees;
        require (fees < PRECISION_DECIMALS());

        //function call
        uint256 returnValue = calculateCollateralToLiquidateHarness(e, debtToCover, sumOfCollateral, fees);
        mathint debtPlusFees = debtToCover + (debtToCover * fees)/PRECISION_DECIMALS();

        assert returnValue != sumOfCollateral => returnValue == debtPlusFees;
    }


//------------------------------- RULES TEST END ----------------------------------

//------------------------------- RULES PROBLEMS START ----------------------------------


    // // estimateMaxRepayValue() ltvAfter is never overshot with return values
    // rule ltvAfterIsNeverOvershotWithReturnValues(env e) { //@audit-issue  does not add up, dont know why => check closer if I have time
    //     uint256 totalBorrowerDebtValue; 
    //     uint256 totalBorrowerCollateralValue;
    //     uint256 ltvAfterLiquidation;
    //     uint256 liquidationFee;
    //     require(totalBorrowerDebtValue > 0);
    //     uint256 targetLTV = ltvAfterLiquidation;


    //     //function call
    //     uint256 returnValue = estimateMaxRepayValueHarness(e, totalBorrowerDebtValue, totalBorrowerCollateralValue, ltvAfterLiquidation, liquidationFee);

    //     mathint borrowerDebtAfter = totalBorrowerDebtValue - returnValue;
    //     mathint borrowerCollateralAfter = totalBorrowerCollateralValue - returnValue * (PRECISION_DECIMALS() + liquidationFee) / PRECISION_DECIMALS();
    //     mathint ltvAfter = borrowerCollateralAfter == 0 ? ltvAfterLiquidation : borrowerDebtAfter * PRECISION_DECIMALS() / borrowerCollateralAfter;
    //     assert(borrowerDebtAfter != 0 && returnValue != 0 => ltvAfter >= targetLTV);
    // }


//------------------------------- RULES PROBLEMS START ----------------------------------

