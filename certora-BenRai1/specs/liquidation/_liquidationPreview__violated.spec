//------------------------- Defintions --------------------------
definition _BAD_DEBT() returns uint256 = 10^18;


//------------------------------- RULES TEST START ----------------------------------


// ISSUE: dust level does not work //@audit-issue changed for issue
rule borrowerIsNeverLeftWithDustAfterLiquidation(env e) {
    //the amount of toknes/ value that should not be left after liquidation
    uint256 dustLevel = 9*10^17;
    //function call parameters
    uint256 ltvBefore;
    uint256 sumOfCollateralAssets;
    uint256 sumOfCollateralValue;
    uint256 borrowerDebtAssets; 
    uint256 borrowerDebtValue;
    PartialLiquidationLib.LiquidationPreviewParams params;

    //prevent earlier reverts
    require(ltvBefore < 10^18);

    //setup
    require(borrowerDebtAssets > dustLevel);
    require(sumOfCollateralValue == require_uint256(2 * borrowerDebtValue)); //have enough collateral to cover the debt


    //exchangerate 1 to 1 for simplicity
    require(sumOfCollateralAssets == sumOfCollateralValue);
    require(borrowerDebtAssets == borrowerDebtValue);

    //require to reduce the run time
    require(params.liquidationFee == 5 * 10^16); //5% liquidation fee
    require(params.maxDebtToCover == 890 * borrowerDebtAssets / 1000);

    //requires ensure that the borrower can be liquidated and reduce the run time
    //         uint256 collateralLt;
    //     address collateralConfigAsset;
    //     address debtConfigAsset;
    // require(_params.maxDebtToCover == 950);
    // require(_params.liquidationFee;
    //     uint256 liquidationTargetLtv;



    //get the borrowers debtAssetsBefore
    uint256 borrowerDebtAssetsBefore = borrowerDebtAssets;

    //call the function and get the returned debtToRepay
    uint256 debtToRepay;
    (_, debtToRepay, _) = liquidationPreviewHarness(e, ltvBefore, sumOfCollateralAssets, sumOfCollateralValue, borrowerDebtAssets, borrowerDebtValue, params);

    //if the functin call can go through in liquidationCall (debtToRepay <= maxDebtToCover) the remainting debt will not be less than the dust level
    assert debtToRepay <= params.maxDebtToCover => borrowerDebtAssetsBefore - debtToRepay >= dustLevel; 
}
