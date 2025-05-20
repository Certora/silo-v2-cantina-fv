import "./partialLiquidation_functions.spec";

import "../setup/ERC20/erc20cvl.spec";
import "../setup/StorageHooks/hook_all.spec";
import "../setup/CompleteSiloSetup.spec";
import "../setup/summaries/siloconfig_summaries.spec";

import "../simplifications/SiloSolvencyLib_UNSAFE.spec";
import "../simplifications/priceOracle_UNSAFE.spec";
import "../simplifications/SiloMathLib_SAFE.spec";
import "../simplifications/SiloMathLib_UNSAFE.spec";
import "../simplifications/SiloStdLib_UNSAFE.spec";
import "../simplifications/Silo_isSolvent_ghost_UNSAFE.spec";
import "../simplifications/PartialLiquidationExecLib.spec";
import "../simplifications/ignore_hooks_simplification.spec";


methods {
    function PartialLiquidationHarness.liquidationPreviewHarness(uint256,uint256,uint256,uint256,uint256,PartialLiquidationLib.LiquidationPreviewParams)
    external returns(uint256,uint256,uint256) envfree;

    // Dispatchers to Silos
    function _.redeem(uint256, address, address, ISilo.CollateralType) external => DISPATCHER(true);
    function _.previewRedeem(uint256) external => DISPATCHER(true);
    function _.previewRedeem(uint256, ISilo.CollateralType) external => DISPATCHER(true);
    function _.getLiquidity() external => DISPATCHER(true);
    function _.forwardTransferFromNoChecks(address _from, address _to, uint256 _amount) external => DISPATCHER(true);

    function _.repay(uint256, address) external => NONDET;
    function _.callOnBehalfOfSilo(address, uint256, ISilo.CallType, bytes) external => NONDET;


    function _.safeIncreaseAllowance(address,uint256) external => NONDET;
    function _.revertIfError(bytes4) internal => NONDET;
    function _._fetchConfigs(address config,address collateralAsset,address debtAsset,address  _borrower) external => CVLGetConfigsForSolvency(_borrower) expect (ISiloConfig.ConfigData,ISiloConfig.ConfigData);

    function PartialLiquidationLib.maxLiquidation(uint256,uint256,uint256,uint256,uint256,uint256) internal returns (uint256,uint256) => NONDET /* difficulty 72 */;
    function SiloLendingLib.maxBorrow(address,bool) internal returns (uint256,uint256) => NONDET /* difficulty 73 */;
    function SiloERC4626Lib.maxWithdraw(address,ISilo.CollateralType,uint256) internal returns (uint256,uint256) => NONDET /* difficulty 69 */;
    function _._checkSolvencyWithoutAccruingInterest(
        ISiloConfig.ConfigData calldata,
        ISiloConfig.ConfigData calldata,
        address _user
    ) internal => NONDET;
    
    function _.callSolvencyOracleBeforeQuote(ISiloConfig.ConfigData memory) internal => NONDET;
    function _.callMaxLtvOracleBeforeQuote(ISiloConfig.ConfigData memory) internal => NONDET;

}

rule liquidationPreviewRedeem(env e,address collateralAsset,address debtAsset,
    address borrower,uint256 maxDebtToCover){
    configForEightTokensSetupRequirements();
    nonSceneAddressRequirements(e.msg.sender);
    nonSceneAddressRequirements(borrower);
    silosTimestampSetupRequirements(e);
    synchronous_siloStorage_erc20cvl(silo0);
    synchronous_siloStorage_erc20cvl(silo1);
    require balanceOfCVL(shareDebtToken0, borrower) >0 ;

    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;

    collateralConfig,debtConfig = CVLGetConfigsForSolvency(borrower);
    uint256 withdrawAssetsFromCollateral;uint256 withdrawAssetsFromProtected;
    withdrawAssetsFromCollateral, withdrawAssetsFromProtected,_,_
    = CVLGetExactLiquidationAmounts(collateralConfig,debtConfig,borrower,maxDebtToCover,collateralConfig.liquidationFee); 
    uint256 collateralShares;
    uint256 protectedShares;
    collateralShares = assetsToSharesApprox(withdrawAssetsFromCollateral, require_uint256(ghostTotalAssets[collateralConfig.silo][COLLATERAL_ASSET_TYPE()]),
     totalSupplyCVL(collateralConfig.collateralShareToken), Math.Rounding.Floor, ISilo.AssetType.Collateral);
    protectedShares = assetsToSharesApprox(withdrawAssetsFromProtected, require_uint256(ghostTotalAssets[collateralConfig.silo][PROTECTED_ASSET_TYPE()]),
     totalSupplyCVL(collateralConfig.protectedShareToken), Math.Rounding.Floor, ISilo.AssetType.Protected);

    uint256 totalAssetsCollateral;uint256 totalSharesCollateral;
    totalAssetsCollateral,totalSharesCollateral = getTotalAssetsAndTotalSharesCVL(collateralConfig,ISilo.AssetType.Collateral);
    uint256 expectedCollateral = sharesToAssetsApprox(collateralShares,totalAssetsCollateral,totalSharesCollateral,Math.Rounding.Floor,ISilo.AssetType.Collateral);

    uint256 totalAssetsProtected;uint256 totalSharesProtected;
    totalAssetsProtected,totalSharesProtected = getTotalAssetsAndTotalSharesCVL(collateralConfig,ISilo.AssetType.Protected);
    uint256 expectedProtected = sharesToAssetsApprox(protectedShares,totalAssetsProtected,totalSharesProtected,Math.Rounding.Floor,ISilo.AssetType.Protected);

    uint256 withdrawCollateral;
    withdrawCollateral ,_ =liquidationCall(e,collateralAsset,debtAsset,borrower,maxDebtToCover,true);

    assert (
        collateralShares == 0 => withdrawCollateral == expectedProtected
    );
    assert (
        protectedShares == 0  => withdrawCollateral == expectedCollateral
    );
    assert (
        (collateralShares != 0 && protectedShares != 0) =>
         to_mathint(withdrawCollateral) == expectedCollateral + expectedProtected
    );
}