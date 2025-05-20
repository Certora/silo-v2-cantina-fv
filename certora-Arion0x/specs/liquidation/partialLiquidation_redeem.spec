import "./partialLiquidation_functions.spec";
import "../setup/ERC20/erc20cvl.spec";
import "../setup/StorageHooks/hook_all.spec";
import "../setup/CompleteSiloSetup.spec";
import "../simplifications/SiloSolvencyLib_UNSAFE.spec";
import "../setup/summaries/siloconfig_summaries.spec";

// import "../setup/single_silo_tokens_requirements.spec";
// import "../setup/summaries/silo0_summaries.spec";
// import "../setup/summaries/siloconfig_summaries_for_two.spec";
// import "../setup/summaries/config_for_one_in_cvl.spec";
// import "../setup/summaries/safe-approximations.spec";

import "../simplifications/priceOracle_UNSAFE.spec";
import "../simplifications/SiloMathLib_SAFE.spec";
import "../simplifications/SiloMathLib_UNSAFE.spec";
import "../simplifications/SiloStdLib_UNSAFE.spec";
import "../simplifications/Silo_isSolvent_ghost_UNSAFE.spec";
import "../simplifications/PartialLiquidationExecLib.spec";
import "../simplifications/ignore_hooks_simplification.spec";

// import "../simplifications/PartialLiquidationLib_UNSAVE.spec";

methods {
    function PartialLiquidationHarness.liquidationPreviewHarness(uint256,uint256,uint256,uint256,uint256,PartialLiquidationLib.LiquidationPreviewParams)
    external returns(uint256,uint256,uint256) envfree;

    // function _.isSolvent(address) external => DISPATCHER(true) ;
    // Dispatchers to Silos
    function _.repay(uint256, address) external => NONDET;
    function _.callOnBehalfOfSilo(address, uint256, ISilo.CallType, bytes) external => NONDET;


    function _.redeem(uint256 shares, address receiver, address owner, ISilo.CollateralType type) external with (env e) => CVLExpectedRedeem(e,shares,receiver,owner,type) expect uint256;
    function _.previewRedeem(uint256) external => NONDET;
    function _.previewRedeem(uint256, ISilo.CollateralType) external => NONDET;
    function _.getLiquidity() external => DISPATCHER(true);
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
    // function _.forwardTransferFromNoChecks(address _from, address _to, uint256 _amount) external => DISPATCHER(true);
    function _._callShareTokenForwardTransferNoChecks(
        address _silo,
        address _borrower,
        address _receiver,
        uint256 _withdrawAssets,
        address _shareToken,
        ISilo.AssetType _assetType
    ) internal => ForwardTransferCVL(_silo,_borrower,_receiver,_withdrawAssets,_shareToken,_assetType) expect (uint256);
    function _.callSolvencyOracleBeforeQuote(ISiloConfig.ConfigData memory) internal => NONDET;
    function _.callMaxLtvOracleBeforeQuote(ISiloConfig.ConfigData memory) internal => NONDET;

    // unresolved external in PartialLiquidation.liquidationCall(address, address, address, uint256, bool) 
    //     => DISPATCH(use_fallback=true) [ silo0._ ] default NONDET;
    // unresolved external in PartialLiquidation.maxLiquidation(address) 
    //     => DISPATCH(use_fallback=true) [ silo0._ ] default NONDET;
}

function ForwardTransferCVL(address silo,address borrower,address receiver,uint256 withdrawAssets,address shareToken ,ISilo.AssetType assetType) returns uint256{
    uint256 shares;
    if(assetType == ISilo.AssetType.Collateral){

    shares = assetsToSharesApprox(withdrawAssets, require_uint256(ghostTotalAssets[silo][COLLATERAL_ASSET_TYPE()]),
     totalSupplyCVL(shareToken), Math.Rounding.Floor, ISilo.AssetType.Collateral);
     require forwardCollateralSharesGhost == shares;
     return shares;
    }else{
    shares = assetsToSharesApprox(withdrawAssets, require_uint256(ghostTotalAssets[silo][PROTECTED_ASSET_TYPE()]),
    totalSupplyCVL(shareToken), Math.Rounding.Floor, ISilo.AssetType.Protected);
    require forwardProtectedSharesGhost == shares;
    return shares;
    }
}

function CVLExpectedRedeem(env e, uint256 shares ,address receiver,address owner,ISilo.CollateralType type) returns uint256{
    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;
    ISiloConfig.DepositConfig depositConfig;

    collateralConfig,debtConfig = CVLGetConfigsForSolvency(borrowerInput);
    depositConfig = CVLGetDepositConfig(collateralConfig.silo);
    uint256 withdrawAssetsFromCollateral;uint256 withdrawAssetsFromProtected;
    withdrawAssetsFromCollateral, withdrawAssetsFromProtected,_,_
    = CVLGetExactLiquidationAmounts(collateralConfig,debtConfig,borrowerInput,maxDebtToCoverInput,collateralConfig.liquidationFee); 

    if(type == ISilo.CollateralType.Collateral){
        if(forwardCollateralSharesGhost == 0) {
            return 0;
        }
    uint256 collateralShares;
    collateralShares = assetsToSharesApprox(withdrawAssetsFromCollateral, require_uint256(ghostTotalAssets[collateralConfig.silo][COLLATERAL_ASSET_TYPE()]),
     totalSupplyCVL(collateralConfig.collateralShareToken), Math.Rounding.Floor, ISilo.AssetType.Collateral);


    uint256 totalAssetsCollateral;uint256 totalSharesCollateral;

    totalAssetsCollateral,totalSharesCollateral = getTotalAssetsAndTotalSharesCVL(collateralConfig,ISilo.AssetType.Collateral);
    uint256 expectedCollateral = sharesToAssetsApprox(collateralShares,totalAssetsCollateral,totalSharesCollateral,Math.Rounding.Floor,ISilo.AssetType.Collateral);

    burnCVL(depositConfig.collateralShareToken,owner,currentContract,collateralShares);
    transferCVL(depositConfig.token,currentContract,receiver,expectedCollateral);
    require redeemCollateralShares == collateralShares;
    require expectedCollateralRedeemGhost == expectedCollateral;
    return expectedCollateral;
    }
    else{
        if(forwardProtectedSharesGhost == 0) {
            return 0;
        }
    uint256 protectedShares;
    protectedShares = assetsToSharesApprox(withdrawAssetsFromProtected, require_uint256(ghostTotalAssets[collateralConfig.silo][PROTECTED_ASSET_TYPE()]),
     totalSupplyCVL(collateralConfig.protectedShareToken), Math.Rounding.Floor, ISilo.AssetType.Protected);


    uint256 totalAssetsProtected;uint256 totalSharesProtected;
    totalAssetsProtected,totalSharesProtected = getTotalAssetsAndTotalSharesCVL(collateralConfig,ISilo.AssetType.Protected);
    uint256 expectedProtected = sharesToAssetsApprox(protectedShares,totalAssetsProtected,totalSharesProtected,Math.Rounding.Floor,ISilo.AssetType.Protected);

    burnCVL(depositConfig.protectedShareToken,owner,currentContract,protectedShares);
    transferCVL(depositConfig.token,currentContract,receiver,expectedProtected);
    require redeemProtectedShares == protectedShares;
    require expectedProtectedRedeemGhost == expectedProtected;
    return expectedProtected;
    }
}
persistent ghost uint256 expectedCollateralRedeemGhost{
    init_state axiom expectedCollateralRedeemGhost == 0;
}
persistent ghost uint256 expectedProtectedRedeemGhost{
    init_state axiom expectedProtectedRedeemGhost == 0;
}
persistent ghost uint256 redeemCollateralShares{
    init_state axiom redeemCollateralShares == 0;
}
persistent ghost uint256 redeemProtectedShares{
    init_state axiom redeemProtectedShares == 0;
}
persistent ghost uint256 forwardCollateralSharesGhost{
    init_state axiom forwardCollateralSharesGhost ==0;
}
persistent ghost uint256 forwardProtectedSharesGhost{
    init_state axiom forwardProtectedSharesGhost ==0;
}

persistent ghost address borrowerInput{
    init_state axiom borrowerInput == 0;
}
persistent ghost uint256 maxDebtToCoverInput{
    init_state axiom maxDebtToCoverInput == 0;
}

rule liquidationBalanceRedeem(env e,address collateralAsset,address debtAsset,
    address borrower,uint256 maxDebtToCover){

    require borrowerInput == borrower;
    require maxDebtToCoverInput == maxDebtToCover;

    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;
    ISiloConfig.DepositConfig depositConfig;

    collateralConfig,debtConfig = CVLGetConfigsForSolvency(borrowerInput);
    depositConfig = CVLGetDepositConfig(collateralConfig.silo);

    mathint receiverTokenBalancePre = balanceOfCVL(depositConfig.token,e.msg.sender);
    mathint contractCollateralBalancePre = balanceOfCVL(depositConfig.collateralShareToken,currentContract);
    mathint contractProtectedBalancePre = balanceOfCVL(depositConfig.protectedShareToken,currentContract);


    uint256 withdrawCollateral;
    withdrawCollateral ,_ =liquidationCall(e,collateralAsset,debtAsset,borrower,maxDebtToCover,false);

    mathint receiverTokenBalancePost = balanceOfCVL(depositConfig.token,e.msg.sender);
    mathint contractCollateralBalancePost = balanceOfCVL(depositConfig.collateralShareToken,currentContract);
    mathint contractProtectedBalancePost = balanceOfCVL(depositConfig.protectedShareToken,currentContract);

    assert (
        (forwardCollateralSharesGhost == 0 && forwardProtectedSharesGhost != 0) => (withdrawCollateral == expectedProtectedRedeemGhost
        && 
        contractProtectedBalancePost == contractProtectedBalancePre - redeemProtectedShares
        // &&
        // receiverTokenBalancePost == receiverTokenBalancePre - expectedProtectedRedeemGhost
        )
    );
    assert (
        (forwardProtectedSharesGhost == 0 && forwardCollateralSharesGhost != 0)  => (withdrawCollateral == expectedCollateralRedeemGhost
        && 
        contractCollateralBalancePost == contractCollateralBalancePre - redeemCollateralShares
        // &&
        // receiverTokenBalancePost == receiverTokenBalancePre - expectedCollateralRedeemGhost 
        )
    );
    assert (
        (forwardCollateralSharesGhost != 0 && forwardProtectedSharesGhost != 0) =>
         (to_mathint(withdrawCollateral) == expectedProtectedRedeemGhost + expectedCollateralRedeemGhost
         && (contractProtectedBalancePost == contractProtectedBalancePre - redeemProtectedShares)
         && (contractCollateralBalancePost == contractCollateralBalancePre - redeemCollateralShares)
        //  && (receiverTokenBalancePost == receiverTokenBalancePre - expectedProtectedRedeemGhost)
        //  && (receiverTokenBalancePost == receiverTokenBalancePre - expectedCollateralRedeemGhost)
         )
    );
}