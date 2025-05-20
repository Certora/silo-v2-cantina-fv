/* The specification of the Silo configs */
import "../setup/CompleteSiloSetup.spec";
import "../setup/summaries/siloconfig_dispatchers.spec";
import "../setup/ERC20/erc20cvl.spec";
import "../setup/StorageHooks/hook_all.spec";

import "../simplifications/priceOracle_UNSAFE.spec";
import "../simplifications/SiloMathLib_SAFE.spec";
import "../simplifications/SiloMathLib_UNSAFE.spec";
import "../simplifications/SiloStdLib_UNSAFE.spec";
import "../simplifications/ignore_hooks_simplification.spec";

// using InterestRateModelV2_0 as interest_silo0;
// using InterestRateModelV2_1 as interest_silo1;

methods{
    function _.beforeAction(address, uint256, bytes) external => NONDET;
    function _.afterAction(address, uint256, bytes) external => NONDET;
    function _.reentrancyGuardEntered()external => NONDET;
    function _.nonReentrant(address)external  =>NONDET;

    function _.isSolvent(address) external => DISPATCHER(true) ;
    function _.synchronizeHooks(uint24,uint24) external => DISPATCHER(true);
    function _.hookReceiverConfig(address) external => DISPATCHER(true);
    function _.getCompoundInterestRateAndUpdate(
        uint256 _collateralAssets,
        uint256 _debtAssets,
        uint256 _interestRateTimestamp
    ) external =>  DISPATCHER(true);
    
    function _.getCompoundInterestRate(
        address _silo,
        uint256 _blockTimestamp
    ) external =>   DISPATCHER(true);
}

/// @title Methods that will be used in parametric rules (e.g. non-view methods)
definition isParametricMethod(method f) returns bool = (
    !f.isView &&
    // `callOnBehalfOfSilo` uses a `delegatecall`
    f.selector != sig:silo0.callOnBehalfOfSilo(address,uint256,ISilo.CallType,bytes).selector &&
    // TODO: `decimals` fails sanity
    f.selector != sig:silo0.decimals().selector &&
    // NOTE: Inside `flashLoan` can call any other method, so it should be added to all
    // the definitions here. But in order to save time, we simply skip it.
    f.selector != sig:silo0.flashLoan(address,address,uint256,bytes).selector
);

// ---- Rules and Invariants ----------------------------------------------------

// use builtin rule sanity;


/// @dev rule 109 :
//       calling accrueInterestForBothSilos() should be equal to
//       calling silo0.accrueInterest() and silo1.accrueInterest()
/// @status Done

rule accrueInterestConsistency() {
    storage initial = lastStorage;
    
    env e ;

    // call accrueInterestForBothSilos()
    siloConfig.accrueInterestForBothSilos(e) ;

    storage single_call = lastStorage ;

    // call silo1.accrueInterest() then silo0.accrueInterest()
    silo1.accrueInterest(e) at initial ;
    silo0.accrueInterest(e) ;

    storage separate_calls_10 = lastStorage ;
    
    // call silo0.accrueInterest() then silo1.accrueInterest()
    silo0.accrueInterest(e) at initial ;
    silo1.accrueInterest(e) ;

    storage separate_calls_01 = lastStorage ;

    // compare assets in both silos to ensure they are equal 
    assert (
        separate_calls_10 == single_call &&
        separate_calls_01 == single_call
    ) ;
}


/// @dev rule 13 :
//       `accrueInterest()` calling twice is the same as calling once (in a single block)
//       calling accrueInterest multiple times should be equal to
//       calling accrueInterest() one time in the same time range
/// @status Done

rule accrueInterest_multiple_one() {
    storage initial = lastStorage;

    env e1;
    env e2;
    
    require e1.block.timestamp == e2.block.timestamp;
    require silo0.getSiloDataInterestRateTimestamp(e1) != 0;


    silo0.accrueInterest(e1) at initial;
    require e1.block.timestamp == e1.block.timestamp + 10;
    silo0.accrueInterest(e1);

    storage multiple_times = lastStorage;
    
    require e2.block.timestamp == e2.block.timestamp + 10;
    silo0.accrueInterest(e2) at initial;

    storage one_time = lastStorage;

    assert (
        multiple_times == one_time 
    ) ;
}

// prove that (accrueInterest; f();) has the same effect as f()
// afterwards add require that accrueInterest was already called before.
// It will simplify some methods, save runtime

// rule accrueInterest_test(method f,calldataarg args)
// filtered{ f-> isParametricMethod(f)} {

//     env e1;
//     require silo0.getSiloDataInterestRateTimestamp(e1) == e1.block.timestamp;

//     storage initial = lastStorage;

//     silo0.accrueInterest(e1) at initial;
//     f(e1,args);

//     storage accrue_f = lastStorage;
    
//     f(e1,args) at initial;

//     storage only_f   = lastStorage;

//     assert (
//        (f.selector != sig:withdrawFees().selector) => accrue_f == only_f 
//     ) ;
// }

// *73 `accrueInterestForConfig()` is equal to `accrueInterest()`. All storage should be equally updated.

rule accrueInterestForConfigIntegrity() {
    storage initial = lastStorage;

    env e;
    require silo0.getSiloDataInterestRateTimestamp(e) > 0;
    // address interestRateModel;
    // uint256 daoFee;
    // uint256 deployerFee;
    ISiloConfig.ConfigData config = silo0.getConfig(e);
    // require interestRateModel == config.interestRateModel;
    // require daoFee == config.daoFee;
    // require deployerFee == config.deployerFee;

    silo0.accrueInterest(e) at initial;

    storage accureInterest = lastStorage;
    
    silo0.accrueInterestForConfig(e,config.interestRateModel,config.daoFee,config.deployerFee) at initial;

    storage accrue_for_config = lastStorage;

    assert (
        accureInterest == accrue_for_config 
    );
}


rule interestRateTimestampOnlyDecreased(method f, calldataarg args)
filtered{ f-> isParametricMethod(f)}{
    env e;

    mathint timestampBefore = ghostInterestRateTimestamp[currentContract];

    f(e,args);

    mathint timestampAfter = ghostInterestRateTimestamp[currentContract];

    assert timestampAfter >= timestampBefore;
}


rule revenueGoesUp(method f) filtered {
    f -> isParametricMethod(f) && f.selector != sig:Silo0.initialize(address).selector
} {

    mathint daoAndDeployerRevenuePre = ghostDaoAndDeployerRevenue[currentContract];
    mathint interestRateTimestampPre = ghostInterestRateTimestamp[currentContract];

    env e;
    calldataarg args;
    f(e, args);

    mathint daoAndDeployerRevenuePost = ghostDaoAndDeployerRevenue[currentContract];
    mathint interestRateTimestampPost = ghostInterestRateTimestamp[currentContract];

    assert (
        f.selector != sig:withdrawFees().selector => (
            daoAndDeployerRevenuePre >= daoAndDeployerRevenuePost
        ),
        "daoAndDeployerRevenue only goes up (excluding withdrawFees())"
    );
}

rule cantAccrueInTheSameBlock(method f) filtered {
    f-> isParametricMethod(f) && f.selector != sig:Silo0.initialize(address).selector
}{
    env e;

    mathint daoAndDeployerRevenuePre = ghostDaoAndDeployerRevenue[currentContract];
    mathint interestRateTimestampPre = ghostInterestRateTimestamp[currentContract];
    require interestRateTimestampPre == e.block.timestamp;

    calldataarg args;
    f(e, args);

    mathint daoAndDeployerRevenuePost = ghostDaoAndDeployerRevenue[currentContract];
    mathint interestRateTimestampPost = ghostInterestRateTimestamp[currentContract];

    assert (
        f.selector != sig:withdrawFees().selector => (
            daoAndDeployerRevenuePre == daoAndDeployerRevenuePost &&
            interestRateTimestampPre == interestRateTimestampPost
        ),
        "cant accrue interest if the last checkpoint is the current block.timestamp"
    );
    assert (
        f.selector == sig:withdrawFees().selector => (
            daoAndDeployerRevenuePost <= daoAndDeployerRevenuePre
        ),
        " `withdrawFees()` never increases daoAndDeployerRevenue in the same block"
    );
}

// rule withdrawFeesWithdrawAllRevenue(env e){

//     mathint daoAndDeployerRevenuePre = ghostDaoAndDeployerRevenue[currentContract];
//     uint256 daoFee;
//     uint256 deployerFee;
//     address asset;
//     address daoFeeReceiver;
//     address deployerFeeReceiver;

//     daoFeeReceiver,deployerFeeReceiver,daoFee,deployerFee,asset = getFeesAndFeeReceiverWithAssetCVL(silo0);

//     uint256 _siloBalance = balanceOfCVL(asset,silo0);
//     uint256 _daoFeeReceiverBalance = balanceOfCVL(asset,daoFeeReceiver);
//     uint256 _deployerFeeReceiverBalance = balanceOfCVL(asset,deployerFeeReceiver);

//     uint256 totalProtected = ghostTotalAssets[silo0][PROTECTED_ASSET_TYPE()];

//     uint256 availableLiquidity;
//     if( totalProtected > siloBalance){
//         availableLiquidity = 0;
//     }else{
//         availableLiquidity = require_uint256(siloBalance - protectedAssets);
//     }

//     withdrawFees(e);

//     uint256 siloBalance_ = balanceOfCVL(asset,silo0);
//     uint256 daoFeeReceiverBalance_ = balanceOfCVL(asset,daoFeeReceiver);
//     uint256 deployerFeeReceiverBalance_ = balanceOfCVL(asset,deployerFeeReceiver);

//     assert (
//        (deployerFeeReceiver == 0) =>  ,
//         "daoAndDeployerRevenue should be set to 0 after withdrawing fees"
//     );
// }

rule daoAndDeployerGainDontExceedLiquidity(env e){
    uint256 daoFee;
    uint256 deployerFee;
    address asset;
    address daoFeeReceiver;
    address deployerFeeReceiver;
    daoFeeReceiver,deployerFeeReceiver,daoFee,deployerFee,asset = getFeesAndFeeReceiverWithAssetCVL(silo0);

    uint256 siloBalancePre = balanceOfCVL(asset,silo0);
    uint256 _daoFeeReceiverBalance = balanceOfCVL(asset,daoFeeReceiver);
    uint256 _deployerFeeReceiverBalance = balanceOfCVL(asset,deployerFeeReceiver);
    
    mathint daoAndDeployerRevenuePre = ghostDaoAndDeployerRevenue[silo0];
    mathint totalProtected = ghostTotalAssets[silo0][PROTECTED_ASSET_TYPE()];

    uint256 availableLiquidity;
    if( totalProtected > siloBalancePre){
        availableLiquidity = 0;
    }else{
        availableLiquidity = require_uint256(siloBalancePre - totalProtected);
    }

    withdrawFees(e);

    uint256 daoGain = require_uint256(balanceOfCVL(asset,daoFeeReceiver) - _daoFeeReceiverBalance);
    uint256 deployerGain = require_uint256(balanceOfCVL(asset,deployerFeeReceiver) - _deployerFeeReceiverBalance);


    assert to_mathint(daoGain + deployerGain) <= availableLiquidity;
    assert (daoGain + deployerGain) <= daoAndDeployerRevenuePre;//proved
}

rule FeesSplitCorrectlyAfterWithdrawal(env e,uint256 availableLiquidity,uint256 earnedFees){
    uint256 daoFee;
    uint256 deployerFee;
    address asset;
    address daoFeeReceiver;
    address deployerFeeReceiver;
    daoFeeReceiver,deployerFeeReceiver,daoFee,deployerFee,asset = getFeesAndFeeReceiverWithAssetCVL(silo0);

    uint256 siloBalancePre = balanceOfCVL(asset,silo0);
    uint256 _daoFeeReceiverBalance = balanceOfCVL(asset,daoFeeReceiver);

    mathint daoAndDeployerRevenuePre = ghostDaoAndDeployerRevenue[silo0];
    mathint totalProtected = ghostTotalAssets[silo0][PROTECTED_ASSET_TYPE()];

    if( totalProtected > siloBalancePre){
        require availableLiquidity == 0;
    }else{
        require availableLiquidity == require_uint256(siloBalancePre - totalProtected);
    }

    if(daoAndDeployerRevenuePre > availableLiquidity){
        require earnedFees == availableLiquidity;
    }else{
        require earnedFees == daoAndDeployerRevenuePre;
    }

    withdrawFees(e);

    uint256 daoGain = require_uint256(balanceOfCVL(asset,daoFeeReceiver) - _daoFeeReceiverBalance);

    assert ghostDaoAndDeployerRevenue[silo0] == (daoAndDeployerRevenuePre - (earnedFees));//proved
    assert deployerFeeReceiver == 0 => (daoGain == earnedFees);//proved
    assert deployerFeeReceiver != 0 => (daoGain == cvlMulDiv(earnedFees, daoFee, require_uint256(daoFee + deployerFee)));
}

rule unavailableLiquidity(env e,uint256 availableLiquidity){
    address asset;
    _,_,_,_,asset = getFeesAndFeeReceiverWithAssetCVL(silo0);

    uint256 siloBalancePre = balanceOfCVL(asset,silo0);
    mathint totalProtected = ghostTotalAssets[silo0][PROTECTED_ASSET_TYPE()];

    if( totalProtected > siloBalancePre){
        require availableLiquidity == 0;
    }else{
        require availableLiquidity == require_uint256(siloBalancePre - totalProtected);
    }
    withdrawFees@withrevert(e);
    
    assert availableLiquidity == 0 => lastReverted; 
}    

rule protectedAssetsSafeAfterWithdrawFees(env e){
    // uint256 totalProtectedBefore = ghostTotalAssets[silo0][PROTECTED_ASSET_TYPE()];
    uint256 daoFee;
    uint256 deployerFee;
    address asset;
    address daoFeeReceiver;
    address deployerFeeReceiver;

    daoFeeReceiver,deployerFeeReceiver,daoFee,deployerFee,asset = getFeesAndFeeReceiverWithAssetCVL(silo0);
    withdrawFees(e);

    uint256 siloBalanceAfter = balanceOfCVL(asset,silo0);
    mathint totalProtected = ghostTotalAssets[silo0][PROTECTED_ASSET_TYPE()];

    assert totalProtected <= siloBalanceAfter;
}

//"borrow/withdraw/transitionCollateral/ should accrue interest for both silos"
rule FunctionsShouldAccrueForBoth(method f,calldataarg args)
filtered{f-> FunctionsAccrueInterestForBoth(f)}{
    env e;
    silo0.getSiloDataInterestRateTimestamp(e);
    silo1.getSiloDataInterestRateTimestamp(e);
    require (ghostInterestRateTimestamp[silo0] > 0 && ghostInterestRateTimestamp[silo0] < e.block.timestamp );
    require (ghostInterestRateTimestamp[silo0] > 0 && ghostInterestRateTimestamp[silo0] < e.block.timestamp );

    mathint InterestRateTimestampPre_0 = ghostInterestRateTimestamp[silo0];
    mathint InterestRateTimestampPre_1 = ghostInterestRateTimestamp[silo1];

    f(e, args);

    mathint InterestRateTimestampPost_0 = ghostInterestRateTimestamp[silo0];
    mathint InterestRateTimestampPost_1 = ghostInterestRateTimestamp[silo1];

    assert (
        (InterestRateTimestampPost_0 == e.block.timestamp &&
        InterestRateTimestampPost_1  == e.block.timestamp)
    );
}

rule switchCollateralShouldAccrueForBoth(env e)
{
    require (ghostInterestRateTimestamp[silo0] > 0 && ghostInterestRateTimestamp[silo0] < e.block.timestamp );
    require (ghostInterestRateTimestamp[silo1] > 0 && ghostInterestRateTimestamp[silo1] < e.block.timestamp );

    mathint InterestRateTimestampPre_0 = ghostInterestRateTimestamp[silo0];
    mathint InterestRateTimestampPre_1 = ghostInterestRateTimestamp[silo1];

    ISiloConfig.ConfigData debtConfig;
    _,debtConfig = getConfigsForSolvencyHarness(e,e.msg.sender);
    require debtConfig.silo != 0;

    switchCollateralToThisSilo(e);

    mathint InterestRateTimestampPost_0 = ghostInterestRateTimestamp[silo0];
    mathint InterestRateTimestampPost_1 = ghostInterestRateTimestamp[silo1];

    assert (
        (InterestRateTimestampPost_0 == e.block.timestamp &&
        InterestRateTimestampPost_1  == e.block.timestamp)
    );
}

//     "other silo revenue remains unchanged"
rule otherSiloDontAccrueInterest(method f,calldataarg args)
filtered{f-> !FunctionsAccrueInterestForBoth(f) && isParametricMethod(f)}{
    env e;

    require (ghostInterestRateTimestamp[silo0] > 0 && ghostInterestRateTimestamp[silo0] < e.block.timestamp );
    require (ghostInterestRateTimestamp[silo0] > 0 && ghostInterestRateTimestamp[silo0] < e.block.timestamp );

    mathint InterestRateTimestampPre_0 = ghostInterestRateTimestamp[silo0];
    mathint InterestRateTimestampPre_1 = ghostInterestRateTimestamp[silo1];

    f(e, args);

    mathint InterestRateTimestampPost_0 = ghostInterestRateTimestamp[silo0];
    mathint InterestRateTimestampPost_1 = ghostInterestRateTimestamp[silo1];

    assert (
        InterestRateTimestampPre_1 == InterestRateTimestampPost_1
    );
    assert (
        FunctionsAccrueInterestForSelf(f) => (
            InterestRateTimestampPost_0 == e.block.timestamp
        ),"Interst rate time stamp should be updated to bloc.timestamp"
    );
}

rule onlyConfigAccrueFunction(env e){
    require (ghostInterestRateTimestamp[silo0] > 0 && ghostInterestRateTimestamp[silo0] < e.block.timestamp );

    ISiloConfig.ConfigData config = silo0.getConfig(e);

    mathint InterestRateTimestampPre = ghostInterestRateTimestamp[silo0];
    
    silo0.accrueInterestForConfig(e,config.interestRateModel,config.daoFee,config.deployerFee);

    mathint InterestRateTimestampPost = ghostInterestRateTimestamp[silo0];

    assert InterestRateTimestampPost == e.block.timestamp <=> e.msg.sender == siloConfig;
}

rule accrueInterestValueIntegrity(env e){

    mathint daoAndDeployerRevenuePre = ghostDaoAndDeployerRevenue[currentContract];

    uint256 accruedInterestValue = accrueInterest(e);

    mathint daoAndDeployerRevenuePost = ghostDaoAndDeployerRevenue[currentContract];

    assert accruedInterestValue == daoAndDeployerRevenuePost - daoAndDeployerRevenuePre;
}

definition FunctionsAccrueInterestForBoth(method f) returns bool = 
    f.selector == sig:Silo0.withdraw(uint256,address,address).selector ||
    f.selector == sig:Silo1.withdraw(uint256,address,address).selector ||
    f.selector == sig:Silo0.withdraw(uint256,address,address,ISilo.CollateralType).selector||
    f.selector == sig:Silo1.withdraw(uint256,address,address,ISilo.CollateralType).selector||
    f.selector == sig:Silo0.borrowShares(uint256,address,address).selector ||
    f.selector == sig:Silo1.borrowShares(uint256,address,address).selector ||
    f.selector == sig:Silo0.borrow(uint256,address,address).selector ||
    f.selector == sig:Silo1.borrow(uint256,address,address).selector ||
    f.selector == sig:Silo0.transitionCollateral(uint256,address,ISilo.CollateralType).selector||
    f.selector == sig:Silo1.transitionCollateral(uint256,address,ISilo.CollateralType).selector;

definition FunctionsAccrueInterestForSelf(method f) returns bool = 
    f.selector == sig:Silo0.deposit(uint256,address,ISilo.CollateralType).selector ||
    f.selector == sig:Silo1.deposit(uint256,address,ISilo.CollateralType).selector ||
    f.selector == sig:Silo0.deposit(uint256,address).selector ||
    f.selector == sig:Silo1.deposit(uint256,address).selector ||
    f.selector == sig:Silo0.repay(uint256,address).selector ||
    f.selector == sig:Silo1.repay(uint256,address).selector ||
    f.selector == sig:Silo0.repayShares(uint256,address).selector||
    f.selector == sig:Silo1.repayShares(uint256,address).selector||
    f.selector == sig:Silo0.borrowSameAsset(uint256,address,address).selector||
    f.selector == sig:Silo1.borrowSameAsset(uint256,address,address).selector;