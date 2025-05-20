import "./partialLiquidation_functions.spec";

import "../setup/ERC20/erc20cvl.spec";
import "../setup/StorageHooks/hook_all.spec";
import "../setup/CompleteSiloSetup.spec";

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
import "../simplifications/SiloSolvencyLib_UNSAFE.spec";
import "../simplifications/PartialLiquidationExecLib.spec";
// import "../simplifications/PartialLiquidationLib_UNSAVE.spec";

methods {
    function PartialLiquidationHarness.liquidationPreviewHarness(uint256,uint256,uint256,uint256,uint256,PartialLiquidationLib.LiquidationPreviewParams)
    external returns(uint256,uint256,uint256) envfree;

    // function _.isSolvent(address) external => DISPATCHER(true) ;
    // Dispatchers to Silos
    function _.repay(uint256, address) external => NONDET;
    function _.callOnBehalfOfSilo(address, uint256, ISilo.CallType, bytes) external => NONDET;
    function _.redeem(uint256, address, address, ISilo.CollateralType) external => NONDET;
    function _.previewRedeem(uint256) external => NONDET;
    function _.previewRedeem(uint256, ISilo.CollateralType) external => NONDET;
    function _.getLiquidity() external => DISPATCHER(true);
    function _.forwardTransferFromNoChecks(address _from, address _to, uint256 _amount) external => DISPATCHER(true);
    // function _._callShareTokenForwardTransferNoChecks(
    //     address,
    //     address,
    //     address,
    //     uint256,
    //     address,
    //     ISilo.AssetType
    // ) internal => NONDET;
    function _.callSolvencyOracleBeforeQuote(ISiloConfig.ConfigData memory config) internal => NONDET;
    function _.callMaxLtvOracleBeforeQuote(ISiloConfig.ConfigData memory config) internal => NONDET;


    function _.getCompoundInterestRateAndUpdate(
        uint256 _collateralAssets,
        uint256 _debtAssets,
        uint256 _interestRateTimestamp
    ) external =>  DISPATCHER(true);
    
    function _.getCompoundInterestRate(
        address _silo,
        uint256 _blockTimestamp
    ) external =>   DISPATCHER(true);
    // unresolved external in PartialLiquidation.liquidationCall(address, address, address, uint256, bool) 
    //     => DISPATCH(use_fallback=true) [ silo0._ ] default NONDET;
    // unresolved external in PartialLiquidation.maxLiquidation(address) 
    //     => DISPATCH(use_fallback=true) [ silo0._ ] default NONDET;
}

rule liquidationCallShouldAccrueInterest(env e,address collateralAsset,address debtAsset,
    address borrower,uint256 maxDebtToCover,bool receiveSToken){

    configForEightTokensSetupRequirements();
    nonSceneAddressRequirements(e.msg.sender);
    synchronous_siloStorage_erc20cvl(silo0);
    synchronous_siloStorage_erc20cvl(silo1);
    require balanceOfCVL(shareDebtToken0, borrower) >0 ;

    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;

    collateralConfig,debtConfig = CVLGetConfigsForSolvency(borrower);

    require (ghostInterestRateTimestamp[collateralConfig.silo] > 0 && ghostInterestRateTimestamp[collateralConfig.silo] < e.block.timestamp );
    require (ghostInterestRateTimestamp[debtConfig.silo] > 0 && ghostInterestRateTimestamp[debtConfig.silo] < e.block.timestamp );

    mathint InterestRateTimestampPre_Collateral = ghostInterestRateTimestamp[collateralConfig.silo];
    mathint InterestRateTimestampPre_debt = ghostInterestRateTimestamp[debtConfig.silo];

    liquidationCall(e,collateralAsset,debtAsset,borrower,maxDebtToCover,receiveSToken);

    mathint InterestRateTimestampPost_Collateral = ghostInterestRateTimestamp[collateralConfig.silo];
    mathint InterestRateTimestampPost_debt = ghostInterestRateTimestamp[debtConfig.silo];

    assert (
        InterestRateTimestampPost_debt  == e.block.timestamp
    );
    assert (
        debtConfig.silo != collateralConfig.silo <=> 
        InterestRateTimestampPost_Collateral == e.block.timestamp
    );
}