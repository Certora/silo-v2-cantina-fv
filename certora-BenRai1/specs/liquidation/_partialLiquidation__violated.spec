import "./_partialLiquidationSetup.spec";

//liquidationCall() should revert if the caller does not get any collateral tokens (@audit-issue added)
// rule revertIfReceivedCollateralAssetsAre0(env e)  {
//     configForEightTokensSetupRequirements();
//     address collateralAsset;
//     address debtAsset;
//     address borrower;
//     uint256 maxDebtToCover;
//     bool receiveSToken;

//     //setup
//     require(receiveSToken == false); //liquidated collateral tokens are sent to the caller
//     address collateralSilo;
//     address debtSilo;
//     ISiloConfig.ConfigData collateralConfig;
//     ISiloConfig.ConfigData debtConfig;
//     (collateralSilo, debtSilo, collateralConfig, debtConfig) = setupLiquidationRules(e, borrower);
//     uint256 withdrawAssetsFromCollateral;
//     uint256 withdrawAssetsFromProtected;
//     uint256 repayDebtAssets;
//     bytes4 customError;
//     (withdrawAssetsFromCollateral, withdrawAssetsFromProtected, repayDebtAssets, customError) = 
//     getExactLiquidationAmountsCVL(collateralConfig, debtConfig, borrower, maxDebtToCover, collateralConfig.liquidationFee); 
//     require(withdrawAssetsFromCollateral == 0);
//     require(withdrawAssetsFromProtected == 0);

//     //values before
//     uint256 receivedAssetsProtectedCaller = receivedRedeemedAssets[collateralSilo][false][e.msg.sender];
//     uint256 receivedAssetsCollateralCaller = receivedRedeemedAssets[collateralSilo][true][e.msg.sender];

//     liquidationCall@withrevert(e, collateralAsset, debtAsset, borrower, maxDebtToCover, receiveSToken);
//     bool reverted = lastReverted;

//     uint256 receivedAssetsProtectedCallerAfter = receivedRedeemedAssets[collateralSilo][false][e.msg.sender];
//     uint256 receivedAssetsCollateralCallerAfter = receivedRedeemedAssets[collateralSilo][true][e.msg.sender];

//     //assert
//     assert(receivedAssetsProtectedCaller == receivedAssetsProtectedCallerAfter => reverted);
//     assert(receivedAssetsCollateralCaller == receivedAssetsCollateralCallerAfter => reverted);
// }

//FIXED liquidationCall() should revert if the caller does not get any collateral tokens
rule FIXEDrevertIfReceivedCollateralAssetsAre0(env e)  {
    configForEightTokensSetupRequirements();
    address collateralAsset;
    address debtAsset;
    address borrower;
    uint256 maxDebtToCover;
    bool receiveSToken;
    bool liquidateBadDebt;

    //setup
    require(receiveSToken == false); //liquidated collateral tokens are sent to the caller
    require(liquidateBadDebt == false); //liquidated collateral tokens are sent to the
    address collateralSilo;
    address debtSilo;
    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;
    (collateralSilo, debtSilo, collateralConfig, debtConfig) = setupLiquidationRules(e, borrower);
    uint256 withdrawAssetsFromCollateral;
    uint256 withdrawAssetsFromProtected;
    uint256 repayDebtAssets;
    bytes4 customError;
    (withdrawAssetsFromCollateral, withdrawAssetsFromProtected, repayDebtAssets, customError) = 
    getExactLiquidationAmountsCVL(collateralConfig, debtConfig, borrower, maxDebtToCover, collateralConfig.liquidationFee); 

    //values before
    uint256 receivedAssetsProtectedCaller = receivedRedeemedAssets[collateralSilo][false][e.msg.sender];
    uint256 receivedAssetsCollateralCaller = receivedRedeemedAssets[collateralSilo][true][e.msg.sender];

    liquidationCall@withrevert(e, collateralAsset, debtAsset, borrower, maxDebtToCover, receiveSToken, false);
    bool reverted = lastReverted;

    //values after
    uint256 receivedAssetsProtectedCallerAfter = receivedRedeemedAssets[collateralSilo][false][e.msg.sender];
    uint256 receivedAssetsCollateralCallerAfter = receivedRedeemedAssets[collateralSilo][true][e.msg.sender];

    //assert
    assert(receivedAssetsProtectedCaller == receivedAssetsProtectedCallerAfter => reverted);
    assert(receivedAssetsCollateralCaller == receivedAssetsCollateralCallerAfter => reverted);
}