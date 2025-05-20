import "../setup/CompleteSiloSetup.spec";
import "../setup/ERC20/erc20cvl.spec";
import "../setup/StorageHooks/hook_all.spec";
import "../setup/Hook/HookLib.spec";

// import "../setup/StorageHooks/shareTokenStorage.spec";
// import "../setup/summaries/config_for_two_in_cvl.spec";
import "../setup/summaries/siloconfig_dispatchers.spec";

// import "../setup/summaries/tokens_dispatchers.spec";
// import "unresolved.spec";

import "../simplifications/priceOracle_UNSAFE.spec";
import "../simplifications/SiloMathLib_SAFE.spec";
import "../simplifications/SiloMathLib_UNSAFE.spec";
import "../simplifications/SiloStdLib_UNSAFE.spec";
// import "../simplifications/ignore_hooks_simplification.spec";

//ignore interest for this rules
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";
import "../simplifications/zero_compound_interest.spec";

using EmptyHookReceiver as hookReceiver;

methods{
    function _.onFlashLoan(address _initiator, address _token, uint256 _amount, uint256 _fee, bytes _data) external => NONDET;
    function SiloERC4626Lib.deposit(address _token,address _depositor,uint256 _assets,
    uint256 _shares,address _receiver,address _collateralShareToken,
    ISilo.CollateralType _collateralType)internal returns(uint256,uint256) => NONDET; 
    function SiloERC4626Lib.withdraw(address _asset,address _shareToken,
    ISilo.WithdrawArgs memory _args) internal returns(uint256,uint256) => NONDET;
    function SiloLendingLib.repay(
        address _debtShareToken,
        address _debtAsset,
        uint256 _assets,
        uint256 _shares,
        address _borrower,
        address _repayer
    ) internal returns (uint256,uint256) => NONDET;
    function SiloLendingLib.borrow(
        address _debtShareToken,
        address _token,
        address _spender,
        ISilo.BorrowArgs memory _args
    ) internal returns (uint256,uint256) => NONDET;

    function _.hookReceiverConfig(address) external => DISPATCHER(true);
    function _.reentrancyGuardEntered()external => NONDET;
    function _.synchronizeHooks(uint24,uint24) external => DISPATCHER(true);
    function _.beforeAction(address Receiver,uint256 action,bytes data) external => CVLBeforeAction(Receiver,action) expect void;
    function _.afterAction(address Receiver,uint256 action,bytes data) external => CVLAfterAction(Receiver,action) expect void;
}

persistent ghost mapping(address => mapping(uint256 => mathint)) beforeActionGhost{
    init_state axiom forall address i. forall uint256 j. beforeActionGhost[i][j] == 0;
}
persistent ghost mapping(address => mapping(uint256 => mathint)) afterActionGhost{
    init_state axiom forall address i. forall uint256 j. afterActionGhost[i][j] == 0;
}

function CVLBeforeAction(address Receiver,uint256 action){
    beforeActionGhost[Receiver][action] = beforeActionGhost[Receiver][action] + 1;
}
function CVLAfterAction(address Receiver,uint256 action){
    afterActionGhost[Receiver][action] = afterActionGhost[Receiver][action] + 1;
}

// use builtin rule sanity;

rule storage_check(env e){

    IShareToken.HookSetup hookSetup = getHookSetup(e);
    bool transferWithChecks = getTransferWithChecks(e);

    assert transferWithChecks == ghostTransferWithChecks[currentContract];
    assert hookSetup.hookReceiver == ghostHookReceiver[currentContract];
    assert hookSetup.hooksBefore == ghostHooksBefore[currentContract];
    assert hookSetup.hooksAfter == ghostHooksAfter[currentContract];
    assert hookSetup.tokenType == ghostTokenType[currentContract];
}

rule updateHooksIntegrity(env e){
    ISiloConfig.ConfigData config_0 = silo0.getConfig(e);
    ISiloConfig.ConfigData config_1 = silo1.getConfig(e);
    storage initState = lastStorage;

    silo0.updateHooks(e);
    storage state_0 = lastStorage;

    silo1.updateHooks(e) at initState;
    storage state_1 = lastStorage;

    assert (
        config_0.hookReceiver == 0 => state_0 == initState
    );
    assert (
        config_1.hookReceiver ==0  => state_1 == initState
    );
}

rule updateHooksCorrectness(env e){
    uint24 hooksBefore;
    uint24 hooksAfter;
    hooksBefore,hooksAfter = hookReceiver.hookReceiverConfig(e,silo0);
    ISiloConfig.ConfigData cfg = CVLGetConfig(silo0);
    require cfg.hookReceiver != 0;

    updateHooks(e);

    assert ghostHooksBefore[silo0] == hooksBefore;
    assert ghostHooksAfter[silo0]  == hooksAfter;
    assert ghostHooksBefore[shareDebtToken0]==hooksBefore;
    assert ghostHooksAfter[shareDebtToken0] == hooksAfter;
    assert ghostHooksBefore[shareProtectedCollateralToken0] == hooksBefore;
    assert ghostHooksAfter[shareProtectedCollateralToken0] == hooksAfter;
}

rule invalidHookReceiver(env e){
    uint24 hooksBefore;
    uint24 hooksAfter;
    mathint siloBefore = ghostHooksBefore[silo0];
    mathint siloAfter  = ghostHooksAfter[silo0];
    mathint debtBefore =  ghostHooksBefore[shareDebtToken0];
    mathint debtAfter  =  ghostHooksAfter[shareDebtToken0];
    mathint protectedBefore = ghostHooksBefore[shareProtectedCollateralToken0];
    mathint protectedAfter  = ghostHooksAfter[shareProtectedCollateralToken0];

    hooksBefore,hooksAfter = hookReceiver.hookReceiverConfig(e,silo0);
    ISiloConfig.ConfigData cfg = CVLGetConfig(silo0);
    require cfg.hookReceiver == 0;

    updateHooks(e);

    assert ghostHooksBefore[silo0] == siloBefore;
    assert ghostHooksAfter[silo0]  == siloAfter;
    assert ghostHooksBefore[shareDebtToken0]==debtBefore;
    assert ghostHooksAfter[shareDebtToken0] == debtAfter;
    assert ghostHooksBefore[shareProtectedCollateralToken0] == protectedBefore;
    assert ghostHooksAfter[shareProtectedCollateralToken0] == protectedAfter;
}

rule switchCollateralHooks(env e){
    IShareToken.HookSetup hookSetup = getHookSetup(e);
    uint256 action = SWITCH_COLLATERAL();
    uint256 otherActions;
    require otherActions != action;

    mathint beforeActionCounterPre = beforeActionGhost[hookSetup.hookReceiver][action];
    mathint afterActionCounterPre = afterActionGhost[hookSetup.hookReceiver][action];

    mathint beforeOtherCounterPre = beforeActionGhost[hookSetup.hookReceiver][otherActions];
    mathint afterOtherCounterPre = afterActionGhost[hookSetup.hookReceiver][otherActions];

    switchCollateralToThisSilo(e);

    mathint beforeOtherCounterPost = beforeActionGhost[hookSetup.hookReceiver][otherActions];
    mathint afterOtherCounterPost = afterActionGhost[hookSetup.hookReceiver][otherActions];

    assert(
     CVLMatchAction(require_uint256(ghostHooksBefore[currentContract]),action) <=>
     beforeActionGhost[hookSetup.hookReceiver][action] == beforeActionCounterPre + 1
    );
    assert(
     CVLMatchAction(require_uint256(ghostHooksAfter[currentContract]),action) <=>
     afterActionGhost[hookSetup.hookReceiver][action] == afterActionCounterPre + 1
    );
    assert (
        beforeOtherCounterPre == beforeOtherCounterPost
    );
    assert (
        afterOtherCounterPre == afterOtherCounterPost
    );
}

rule repayHooks(env e,uint256 assets ,address borrower){
    IShareToken.HookSetup hookSetup = getHookSetup(e);
    uint256 action = REPAY();
    uint256 otherActions;
    require otherActions != action;

    mathint beforeActionCounterPre = beforeActionGhost[hookSetup.hookReceiver][action];
    mathint afterActionCounterPre = afterActionGhost[hookSetup.hookReceiver][action];

    mathint beforeOtherCounterPre = beforeActionGhost[hookSetup.hookReceiver][otherActions];
    mathint afterOtherCounterPre = afterActionGhost[hookSetup.hookReceiver][otherActions];

    repay(e,assets,borrower);

    mathint beforeOtherCounterPost = beforeActionGhost[hookSetup.hookReceiver][otherActions];
    mathint afterOtherCounterPost = afterActionGhost[hookSetup.hookReceiver][otherActions];

    assert(
     CVLMatchAction(require_uint256(ghostHooksBefore[currentContract]),action) <=>
     beforeActionGhost[hookSetup.hookReceiver][action] == beforeActionCounterPre + 1
    );
    assert(
     CVLMatchAction(require_uint256(ghostHooksAfter[currentContract]),action) <=>
     afterActionGhost[hookSetup.hookReceiver][action] == afterActionCounterPre + 1
    );
    assert (
        beforeOtherCounterPre == beforeOtherCounterPost
    );
    assert (
        afterOtherCounterPre == afterOtherCounterPost
    );
}

rule depositHooks(env e,uint256 assets ,address receiver,ISilo.CollateralType type){
    IShareToken.HookSetup hookSetup = getHookSetup(e);
    uint256 action = CVLDepositAction(type);
    uint256 otherActions;
    require otherActions != action;

    mathint beforeActionCounterPre = beforeActionGhost[hookSetup.hookReceiver][action];
    mathint afterActionCounterPre = afterActionGhost[hookSetup.hookReceiver][action];

    mathint beforeOtherCounterPre = beforeActionGhost[hookSetup.hookReceiver][otherActions];
    mathint afterOtherCounterPre = afterActionGhost[hookSetup.hookReceiver][otherActions];

    deposit(e,assets,receiver,type);

    mathint beforeOtherCounterPost = beforeActionGhost[hookSetup.hookReceiver][otherActions];
    mathint afterOtherCounterPost = afterActionGhost[hookSetup.hookReceiver][otherActions];

    assert(
     CVLMatchAction(require_uint256(ghostHooksBefore[currentContract]),action) <=>
     beforeActionGhost[hookSetup.hookReceiver][action] == beforeActionCounterPre + 1
    );
    assert(
     CVLMatchAction(require_uint256(ghostHooksAfter[currentContract]),action) <=>
     afterActionGhost[hookSetup.hookReceiver][action] == afterActionCounterPre + 1
    );

    assert (
        beforeOtherCounterPre == beforeOtherCounterPost
    );
    assert (
        afterOtherCounterPre == afterOtherCounterPost
    );
}

rule withdrawHooks(env e,uint256 assets ,address receiver,ISilo.CollateralType type){
    IShareToken.HookSetup hookSetup = getHookSetup(e);
    uint256 action = CVLWithdrawAction(type);
    uint256 otherActions;
    require otherActions != action;

    mathint beforeActionCounterPre = beforeActionGhost[hookSetup.hookReceiver][action];
    mathint afterActionCounterPre = afterActionGhost[hookSetup.hookReceiver][action];

    mathint beforeOtherCounterPre = beforeActionGhost[hookSetup.hookReceiver][otherActions];
    mathint afterOtherCounterPre = afterActionGhost[hookSetup.hookReceiver][otherActions];

    withdraw(e,assets,receiver,receiver,type);

    mathint beforeOtherCounterPost = beforeActionGhost[hookSetup.hookReceiver][otherActions];
    mathint afterOtherCounterPost = afterActionGhost[hookSetup.hookReceiver][otherActions];

    assert(
     CVLMatchAction(require_uint256(ghostHooksBefore[currentContract]),action) <=>
     beforeActionGhost[hookSetup.hookReceiver][action] == beforeActionCounterPre + 1
    );
    assert(
     CVLMatchAction(require_uint256(ghostHooksAfter[currentContract]),action) <=>
     afterActionGhost[hookSetup.hookReceiver][action] == afterActionCounterPre + 1
    );

    assert (
        beforeOtherCounterPre == beforeOtherCounterPost
    );
    assert (
        afterOtherCounterPre == afterOtherCounterPost
    );
}

rule borrowHooks(env e,uint256 assets ,address receiver,address borrower){
    IShareToken.HookSetup hookSetup = getHookSetup(e);
    uint256 action = BORROW();
    uint256 otherActions;
    require otherActions != action;

    mathint beforeActionCounterPre = beforeActionGhost[hookSetup.hookReceiver][action];
    mathint afterActionCounterPre = afterActionGhost[hookSetup.hookReceiver][action];

    mathint beforeOtherCounterPre = beforeActionGhost[hookSetup.hookReceiver][otherActions];
    mathint afterOtherCounterPre = afterActionGhost[hookSetup.hookReceiver][otherActions];

    borrow(e,assets,receiver,borrower);

    mathint beforeOtherCounterPost = beforeActionGhost[hookSetup.hookReceiver][otherActions];
    mathint afterOtherCounterPost = afterActionGhost[hookSetup.hookReceiver][otherActions];


    assert(
     CVLMatchAction(require_uint256(ghostHooksBefore[currentContract]),action) <=>
     beforeActionGhost[hookSetup.hookReceiver][action] == beforeActionCounterPre + 1
    );
    assert(
     CVLMatchAction(require_uint256(ghostHooksAfter[currentContract]),action) <=>
     afterActionGhost[hookSetup.hookReceiver][action] == afterActionCounterPre + 1
    );
    assert (
        beforeOtherCounterPre == beforeOtherCounterPost
    );
    assert (
        afterOtherCounterPre == afterOtherCounterPost
    );
}

rule borrowSameHooks(env e,uint256 assets ,address receiver,address borrower){
    IShareToken.HookSetup hookSetup = getHookSetup(e);
    uint256 action = BORROW_SAME_ASSET();
    uint256 otherActions;
    require otherActions != action;
    
    mathint beforeActionCounterPre = beforeActionGhost[hookSetup.hookReceiver][action];
    mathint afterActionCounterPre = afterActionGhost[hookSetup.hookReceiver][action];

    mathint beforeOtherCounterPre = beforeActionGhost[hookSetup.hookReceiver][otherActions];
    mathint afterOtherCounterPre = afterActionGhost[hookSetup.hookReceiver][otherActions];

    borrowSameAsset(e,assets,receiver,borrower);

    mathint beforeOtherCounterPost = beforeActionGhost[hookSetup.hookReceiver][otherActions];
    mathint afterOtherCounterPost = afterActionGhost[hookSetup.hookReceiver][otherActions];

    assert(
     CVLMatchAction(require_uint256(ghostHooksBefore[currentContract]),action) <=>
     beforeActionGhost[hookSetup.hookReceiver][action] == beforeActionCounterPre + 1
    );
    assert(
     CVLMatchAction(require_uint256(ghostHooksAfter[currentContract]),action) <=>
     afterActionGhost[hookSetup.hookReceiver][action] == afterActionCounterPre + 1
    );
    assert (
        beforeOtherCounterPre == beforeOtherCounterPost
    );
    assert (
        afterOtherCounterPre == afterOtherCounterPost
    );
}

rule transitionCollateralHooks(env e,uint256 shares ,address owner,ISilo.CollateralType transitionFrom){
    IShareToken.HookSetup hookSetup = getHookSetup(e);
    uint256 action = CVLTransitionCollateralAction(transitionFrom);
    uint256 otherActions;
    require otherActions != action;

    mathint beforeActionCounterPre = beforeActionGhost[hookSetup.hookReceiver][action];
    mathint afterActionCounterPre = afterActionGhost[hookSetup.hookReceiver][action];

    mathint beforeOtherCounterPre = beforeActionGhost[hookSetup.hookReceiver][otherActions];
    mathint afterOtherCounterPre = afterActionGhost[hookSetup.hookReceiver][otherActions];

    transitionCollateral(e,shares,owner,transitionFrom);

    mathint beforeOtherCounterPost = beforeActionGhost[hookSetup.hookReceiver][otherActions];
    mathint afterOtherCounterPost = afterActionGhost[hookSetup.hookReceiver][otherActions];

    assert(
     CVLMatchAction(require_uint256(ghostHooksBefore[currentContract]),action) <=>
     beforeActionGhost[hookSetup.hookReceiver][action] == beforeActionCounterPre + 1
    );
    assert(
     CVLMatchAction(require_uint256(ghostHooksAfter[currentContract]),action) <=>
     afterActionGhost[hookSetup.hookReceiver][action] == afterActionCounterPre + 1
    );
    assert (
        beforeOtherCounterPre == beforeOtherCounterPost
    );
    assert (
        afterOtherCounterPre == afterOtherCounterPost
    );
}

rule flashLoanHooks(env e,address _receiver,address _token,uint256 _amount,bytes _data){
    IShareToken.HookSetup hookSetup = getHookSetup(e);
    uint256 action = FLASH_LOAN();
    uint256 otherActions;
    require otherActions != action;

    mathint beforeActionCounterPre = beforeActionGhost[hookSetup.hookReceiver][action];
    mathint afterActionCounterPre = afterActionGhost[hookSetup.hookReceiver][action];

    mathint beforeOtherCounterPre = beforeActionGhost[hookSetup.hookReceiver][otherActions];
    mathint afterOtherCounterPre = afterActionGhost[hookSetup.hookReceiver][otherActions];

    flashLoan(e,_receiver,_token,_amount,_data);

    mathint beforeOtherCounterPost = beforeActionGhost[hookSetup.hookReceiver][otherActions];
    mathint afterOtherCounterPost = afterActionGhost[hookSetup.hookReceiver][otherActions];

    assert(
     CVLMatchAction(require_uint256(ghostHooksBefore[currentContract]),action) <=>
     beforeActionGhost[hookSetup.hookReceiver][action] == beforeActionCounterPre + 1
    );
    assert(
     CVLMatchAction(require_uint256(ghostHooksAfter[currentContract]),action) <=>
     afterActionGhost[hookSetup.hookReceiver][action] == afterActionCounterPre + 1
    );
    assert (
        beforeOtherCounterPre == beforeOtherCounterPost
    );
    assert (
        afterOtherCounterPre == afterOtherCounterPost
    );
}