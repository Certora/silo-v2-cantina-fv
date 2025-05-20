/* Integrity of main methods */

import "../setup/CompleteSiloSetup.spec";
import "../setup/StorageHooks/hook_all.spec";
import "../setup/summaries/siloconfig_dispatchers.spec";


import "../simplifications/priceOracle_UNSAFE.spec";
import "../simplifications/SiloMathLib_SAFE.spec";
import "../simplifications/SiloMathLib_UNSAFE.spec";
import "../simplifications/ignore_hooks_simplification.spec";
import "../simplifications/zero_compound_interest.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";



import "../setup/ERC20/erc20cvl.spec";

methods{
    //ignore calling hooks 
    function _.matchAction(uint256 _action, uint256 _expectedHook) internal => ALWAYS(false);

    function _.onFlashLoan(address _initiator, address _token, uint256 _amount, uint256 _fee, bytes _data) external => CVLOnFlashLoan(calledContract,_token) expect bytes32;

        //------------DISPATCHERS-------------//
    function _.isSolvent(address) external => DISPATCHER(true);
    function _.hookReceiverConfig(address) external => DISPATCHER(true);

        //--------------NONDET---------------//

    function _.synchronizeHooks(uint24,uint24) external => NONDET;
    function _.beforeAction(address, uint256, bytes) external => NONDET;
    function _.afterAction(address, uint256, bytes) external => NONDET;
}

function CVLOnFlashLoan(address receiver,address token) returns bytes32 {
    bytes32 data;
    require ghostTokenBalanceOnFlashLoan[token][receiver] == balanceOfCVL(token,receiver);
    require ghostOnFlashLoanResult == data;
    require onFlashLoanCalled == true;
    return data;
}

persistent ghost mapping(address => mapping(address => mathint)) ghostTokenBalanceOnFlashLoan;
persistent ghost bytes32 ghostOnFlashLoanResult;
persistent ghost bool onFlashLoanCalled{
    init_state axiom onFlashLoanCalled == false;
}

// rule maxFlashLoanIntegrity(env e,method f,calldataarg args)
// filtered{f-> !ignoredFunction(f)}{

//     synchronous_siloStorage_erc20cvl(e);
//     uint256 maxFlashLoanBefore = maxFlashLoan(e,token0);

//     f(e,args);

//     uint256 maxFlashLoanAfter = maxFlashLoan(e,token0);


//     assert canChangeProtectedAssets(f) => maxFlashLoanBefore == maxFlashLoanAfter;
// }

rule flashLoanDontChangeStorage(env e){
    address _receiver;
    address _token;
    uint256 _amount;
    bytes _data;
    mathint daoAndDeployerRevenueBefore = ghostDaoAndDeployerRevenue[silo0];
    require getFlashFee(e,siloConfig,_token,_amount) > 0;
    storage before_storage = lastStorage;

    flashLoan(e,_receiver,_token,_amount,_data);

    mathint daoAndDeployerRevenueAfter = ghostDaoAndDeployerRevenue[silo0];
    storage after_storage = lastStorage;

    assert daoAndDeployerRevenueBefore == daoAndDeployerRevenueAfter => before_storage == after_storage;
}
rule flashFeeCorrectness(env e){
    address _token;
    uint256 _amount;
    require _amount !=0;
    require _token == token0;   
    uint256 flashFee = getFlashFee(e,siloConfig,_token,_amount);
    uint256 flashLoanFee;
    _,_,flashLoanFee,_ = CVLGetFeesWithAsset(silo0);
    
    assert flashLoanFee != 0 => flashFee !=0;

}

// `flashLoan()` daoAndDeployerRevenue and Silo asset balance should increase by flashFee()
rule BalancesAfterFlashLoan(env e){
    address _receiver;
    address _token;
    require _token == token0;
    uint256 _amount;
    bytes _data;
    mathint daoAndDeployerRevenueBefore = ghostDaoAndDeployerRevenue[silo0];
    mathint siloBalanceBefore = balanceOfCVL(token0,silo0);
    mathint receiverBalanceBefore = balanceOfCVL(token0,_receiver);
    nonSceneAddressRequirements(_receiver);

    uint256 flashFee = getFlashFee(e,siloConfig,_token,_amount);
    bool success = flashLoan(e,_receiver,_token,_amount,_data);

    mathint daoAndDeployerRevenueAfter = ghostDaoAndDeployerRevenue[silo0];
    mathint siloBalanceAfter = balanceOfCVL(token0,silo0);
    mathint receiverBalanceAfter = balanceOfCVL(token0,_receiver);


    assert success <=> daoAndDeployerRevenueAfter == daoAndDeployerRevenueBefore + flashFee;
    assert success <=> siloBalanceAfter == siloBalanceBefore + flashFee;
    assert success <=> receiverBalanceAfter == receiverBalanceBefore - flashFee;
    assert success <=> ghostTokenBalanceOnFlashLoan[_token][_receiver] == receiverBalanceBefore + _amount;
}

rule siloBalanceIncrease(env e){
    address _receiver;
    address _token;
    require _token == token0;
    uint256 _amount;
    bytes _data;

    mathint siloBalanceBefore = balanceOfCVL(token0,silo0);
    mathint receiverBalanceBefore = balanceOfCVL(token0,_receiver);

    flashLoan(e,_receiver,_token,_amount,_data);
    mathint siloBalanceAfter = balanceOfCVL(token0,silo0);

    assert siloBalanceAfter >= siloBalanceBefore;
}


rule invalidFlashLoan(env e){
    address _receiver;
    address _token;
    require _token == token0;
    uint256 _amount;
    bytes _data;
    uint256 flashFee = getFlashFee(e,siloConfig,_token,_amount);
    uint256 maxFlashLoan = maxFlashLoan(e,token0);

    flashLoan@withrevert(e,_receiver,_token,_amount,_data);
    bool lastRevertedBool = lastReverted;

    assert ghostOnFlashLoanResult != FLASHLOAN_CALLBACK_HARNESS(e) => lastRevertedBool;
    assert flashFee > max_uint192 => lastRevertedBool;
    assert _amount  > maxFlashLoan => lastRevertedBool; 
    assert _amount == 0 => lastRevertedBool;
    assert !onFlashLoanCalled => lastRevertedBool;
}

definition canChangeProtectedAssets(method f) returns bool =
    f.selector == sig:Silo0.deposit(uint256,address,ISilo.CollateralType).selector ||
    f.selector == sig:Silo0.mint(uint256,address,ISilo.CollateralType).selector ||
    f.selector == sig:Silo0.transitionCollateral(uint256,address,ISilo.CollateralType).selector||
    f.selector == sig:Silo0.redeem(uint256,address,address,ISilo.CollateralType).selector ||
    f.selector == sig:Silo0.withdraw(uint256,address,address,ISilo.CollateralType).selector ||
    f.selector == sig:Silo0.transitionCollateral(uint256,address,ISilo.CollateralType).selector;


function synchronous_siloStorage_erc20cvl(env e){
    mathint totalDebt;
    mathint totalCollateral;
    mathint totalProtected;
    totalProtected =  ghostTotalAssets[silo0][PROTECTED_ASSET_TYPE()];
    totalCollateral = ghostTotalAssets[silo0][COLLATERAL_ASSET_TYPE()];
    totalDebt = ghostTotalAssets[silo0][DEBT_ASSET_TYPE()]; 
    require totalProtected  == totalSupplyCVL(shareProtectedCollateralToken0);
    require totalCollateral == totalSupplyCVL(silo0);
    require totalDebt == totalSupplyCVL(shareDebtToken0);
}