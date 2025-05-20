/* Rules concerning callst to hook  */

import "../setup/CompleteSiloSetup.spec";
import "./0base_Silo.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";
import "../simplifications/_Oracle_call_before_quote_UNSAFE.spec";
import "../simplifications/Oracle_quote_one_UNSAFE.spec";
import  "../simplifications/SiloMathLib_SAFE.spec";

using EmptyHookReceiver as hookReceiver;
using EmptyFlashloanReceiver as flashLoanReceiver;

methods{
    function _.onFlashLoan(address, address, uint256, uint256, bytes) external => DISPATCHER(true);
    function _.reentrancyGuardEntered() external => DISPATCHER(true);
    function _.synchronizeHooks(uint24, uint24) external => DISPATCHER(true);
    function _.hookReceiverConfig(address) external => DISPATCHER(true);
       
    function hookReceiver.sumOfCountersBefore() external returns (uint256) envfree;
    function hookReceiver.sumOfCountersAfter() external returns (uint256) envfree;
}
//------------------------------ FUNCTIONS START----------------------------------
    //all hook counters are set to 0
    function hookCountersAreZero() {
        require(hookReceiver.sumOfCountersBefore() == 0);
        require(hookReceiver.sumOfCountersAfter() == 0);
    }

    function setupHookRules(env e) {
        hookCountersAreZero();
        requireInvariant sameHookSetupSameForAllTokens(e);
        //hookReceiver is the hook receiver
        require hookReceiver == silo0.hookReceiver(e);
        require hookReceiver == shareProtectedCollateralToken0.hookReceiver(e);
        require hookReceiver == shareDebtToken0.hookReceiver(e);
        require silo0.hookSetup(e).tokenType == COLLATERAL_TOKEN();
        require shareProtectedCollateralToken0.hookSetup(e).tokenType == PROTECTED_TOKEN();
        require shareDebtToken0.hookSetup(e).tokenType == DEBT_TOKEN();
    }

//----------------------------- FUNCTIONS END----------------------------------
//----------------------------- DEFINITIONS START----------------------------------
        definition BEFORE() returns bool = true;
        definition AFTER() returns bool = false;
        definition NONE() returns uint256 = 0;
        definition DEPOSIT() returns uint256 = 2 ^ 1;
        definition DEPOSIT_COLLATERAL() returns uint256 = DEPOSIT() | COLLATERAL_TOKEN();
        definition DEPOSIT_PROTECTED() returns uint256 = DEPOSIT() | PROTECTED_TOKEN();
        definition BORROW() returns uint256 = 2 ^ 2;
        definition BORROW_SAME_ASSET() returns uint256 = 2 ^ 3;
        definition REPAY() returns uint256 = 2 ^ 4;
        definition WITHDRAW() returns uint256 = 2 ^ 5;
        definition WITHDRAW_COLLATERAL() returns uint256 = WITHDRAW() | COLLATERAL_TOKEN();
        definition WITHDRAW_PROTECTED() returns uint256 = WITHDRAW() | PROTECTED_TOKEN();
        definition FLASH_LOAN() returns uint256 = 2 ^ 6;
        definition TRANSITION_COLLATERAL() returns uint256 = 2 ^ 7;
        definition TRANSITION_COLLATERAL_COLLATERAL() returns uint256 = TRANSITION_COLLATERAL() | COLLATERAL_TOKEN();
        definition TRANSITION_PROTECTED_COLLATERAL() returns uint256 = TRANSITION_COLLATERAL() | PROTECTED_TOKEN();
        definition SWITCH_COLLATERAL() returns uint256 = 2 ^ 8;
        definition LIQUIDATION() returns uint256 = 2 ^ 9;
        definition SHARE_TOKEN_TRANSFER() returns uint256 = 2 ^ 10;
        definition TRANSFER_COLLATERAL() returns uint256 = SHARE_TOKEN_TRANSFER() | COLLATERAL_TOKEN();
        definition TRANSFER_PROTECTED() returns uint256 = SHARE_TOKEN_TRANSFER() | PROTECTED_TOKEN();
        definition TRANSFER_DEBT() returns uint256 = SHARE_TOKEN_TRANSFER() | DEBT_TOKEN();
        definition COLLATERAL_TOKEN() returns uint256 = 2 ^ 11;
        definition PROTECTED_TOKEN() returns uint256 = 2 ^ 12;
        definition DEBT_TOKEN() returns uint256 = 2 ^ 13;

//----------------------------- DEFINITIONS END----------------------------------


    //INVARIANT: hookSetup (hooksBefore, hooksAfter) for all tokens is the same
    invariant sameHookSetupSameForAllTokens(env e) 
        silo0.hookSetup(e).hooksBefore == shareProtectedCollateralToken0.hookSetup(e).hooksBefore &&
        shareProtectedCollateralToken0.hookSetup(e).hooksBefore == shareDebtToken0.hookSetup(e).hooksBefore &&
        silo0.hookSetup(e).hooksAfter == shareProtectedCollateralToken0.hookSetup(e).hooksAfter &&
        shareProtectedCollateralToken0.hookSetup(e).hooksAfter == shareDebtToken0.hookSetup(e).hooksAfter
        filtered {f-> f.selector != sig:callOnBehalfOfSilo(address,uint256,ISilo.CallType,bytes).selector &&
                        f.selector != sig:initialize(address).selector &&
                        f.selector != sig:synchronizeHooks(uint24,uint24).selector //i: can only be called by silo which can not call it directly
                }
        {
            preserved {
                require (e.msg.sender != silo0); //to prevent syncronizeHooks to be called directly
                require hookReceiverHarness(silo0) != 0;
            }

    }

    // transitionCollateral(CollateralType.Protected) should call beforeAction() and afterAction() hooks if activated
    rule transitionCollateralProtectedHooks(env e) {
        configForEightTokensSetupRequirements();
        setupHookRules(e);
        uint256 shares;
        address owner;
        ISilo.CollateralType collateralType = ISilo.CollateralType.Protected;


        //is hook activated
        bool beforeTransitionCollateralActivated = hookCallActivatedHarness(TRANSITION_PROTECTED_COLLATERAL(), BEFORE());
        bool afterTransitionCollateralActivated = hookCallActivatedHarness(TRANSITION_PROTECTED_COLLATERAL(), AFTER());
        bool afterProtectedCounterActivated = hookCallActivatedHarness(TRANSFER_PROTECTED(), AFTER());
        bool afterCollateralCounterActivated = hookCallActivatedHarness(TRANSFER_COLLATERAL(), AFTER());

        //function call
        transitionCollateral(e, shares, owner, collateralType);

        //check if hooks were called
        uint256 beforeCounter = hookReceiver.sumOfCountersBefore();
        uint256 afterCounter = hookReceiver.sumOfCountersAfter();
        uint256 transitionCollateralCounterBefore = hookReceiver.TRANSITION_COLLATERAL_PROTECTED_COUNTER_BEFORE(e);
        uint256 transitionCollateralCounterAfter = hookReceiver.TRANSITION_COLLATERAL_PROTECTED_COUNTER_AFTER(e);
        uint256 protectedCounterAfter = hookReceiver.TRANSFER_PROTECTED_COUNTER_AFTER(e);
        uint256 collateralCounterAfter = hookReceiver.TRANSFER_COLLATERAL_COUNTER_AFTER(e);

        //beforeCounter
        assert beforeTransitionCollateralActivated == true => beforeCounter == 1;
        assert beforeTransitionCollateralActivated == false => beforeCounter == 0;

        //afterCounter
        assert afterTransitionCollateralActivated == true && afterProtectedCounterActivated == true && afterCollateralCounterActivated == true => afterCounter == 3;
        assert afterTransitionCollateralActivated == false && afterProtectedCounterActivated == true && afterCollateralCounterActivated == true => afterCounter == 2;
        assert afterTransitionCollateralActivated == true && afterProtectedCounterActivated == false && afterCollateralCounterActivated == true => afterCounter == 2;
        assert afterTransitionCollateralActivated == true && afterProtectedCounterActivated == true && afterCollateralCounterActivated == false => afterCounter == 2;
        assert afterTransitionCollateralActivated == false && afterProtectedCounterActivated == false && afterCollateralCounterActivated == true => afterCounter == 1;
        assert afterTransitionCollateralActivated == false && afterProtectedCounterActivated == true && afterCollateralCounterActivated == false => afterCounter == 1;
        assert afterTransitionCollateralActivated == true && afterProtectedCounterActivated == false && afterCollateralCounterActivated == false => afterCounter == 1;
        assert afterTransitionCollateralActivated == false && afterProtectedCounterActivated == false && afterCollateralCounterActivated == false => afterCounter == 0;

        //transitionCollateralCounterBefore
        assert beforeTransitionCollateralActivated == true => transitionCollateralCounterBefore == 1;
        assert beforeTransitionCollateralActivated == false => transitionCollateralCounterBefore == 0;

        //transitionCollateralCounterAfter
        assert afterTransitionCollateralActivated == true => transitionCollateralCounterAfter == 1;
        assert afterTransitionCollateralActivated == false => transitionCollateralCounterAfter == 0;

        //shareCounter
        assert afterProtectedCounterActivated == true => protectedCounterAfter == 1;
        assert afterCollateralCounterActivated == true => collateralCounterAfter == 1;
        assert afterProtectedCounterActivated == false => protectedCounterAfter == 0;
        assert afterCollateralCounterActivated == false => collateralCounterAfter == 0;
    }

    // after a call to `updateHooks()` all share tokens and silo should have the same values for hooksBefore and hooksAfter
    rule sameHookSetupForAllTokensAfterUpdateHooks(env e) {
        configForEightTokensSetupRequirements();

        //hookReceiver not 0
        require hookReceiverHarness(silo0) != 0;

        //function call
        updateHooks(e);

        //check if hooksBefore and hooksAfter are the same
        assert silo0.hookSetup(e).hooksBefore == shareProtectedCollateralToken0.hookSetup(e).hooksBefore; 
        assert shareProtectedCollateralToken0.hookSetup(e).hooksBefore == shareDebtToken0.hookSetup(e).hooksBefore;
        assert silo0.hookSetup(e).hooksAfter == shareProtectedCollateralToken0.hookSetup(e).hooksAfter;
        assert shareProtectedCollateralToken0.hookSetup(e).hooksAfter == shareDebtToken0.hookSetup(e).hooksAfter;
    }

    // redeem() should call beforeAction() and afterAction() hooks if activated
    rule redeemHooks(env e) {
        configForEightTokensSetupRequirements();
        setupHookRules(e);
        uint256 shares;
        address receiver;
        address owner;

        //is hook activated
        bool beforeRedeemActivated = hookCallActivatedHarness(WITHDRAW_COLLATERAL(), BEFORE());
        bool afterRedeemActivated = hookCallActivatedHarness(WITHDRAW_COLLATERAL(), AFTER());
        bool afterCollateralCounterActivated = hookCallActivatedHarness(TRANSFER_COLLATERAL(), AFTER());

        //function call
        redeem(e, shares, receiver, owner);

        //check if hooks were called
        uint256 beforeCounter = hookReceiver.sumOfCountersBefore();
        uint256 afterCounter = hookReceiver.sumOfCountersAfter();
        uint256 redeemCounterBefore = hookReceiver.WITHDRAW_COLLATERAL_COUNTER_BEFORE(e);
        uint256 redeemCounterAfter = hookReceiver.WITHDRAW_COLLATERAL_COUNTER_AFTER(e);
        uint256 collateralCounterAfter = hookReceiver.TRANSFER_COLLATERAL_COUNTER_AFTER(e);

        //beforeCounter
        assert beforeRedeemActivated == true => beforeCounter == 1;
        assert beforeRedeemActivated == false => beforeCounter == 0;

        //afterCounter
        assert afterRedeemActivated == true && afterCollateralCounterActivated == true => afterCounter == 2;
        assert afterRedeemActivated == false && afterCollateralCounterActivated == true => afterCounter == 1;
        assert afterRedeemActivated == true && afterCollateralCounterActivated == false => afterCounter == 1;
        assert afterRedeemActivated == false && afterCollateralCounterActivated == false => afterCounter == 0;

        //redeemCounterBefore
        assert beforeRedeemActivated == true => redeemCounterBefore == 1;
        assert beforeRedeemActivated == false => redeemCounterBefore == 0;

        //redeemCounterAfter
        assert afterRedeemActivated == true => redeemCounterAfter == 1;
        assert afterRedeemActivated == false => redeemCounterAfter == 0;

        //shareCounter
        assert afterCollateralCounterActivated == true => collateralCounterAfter == 1;
        assert afterCollateralCounterActivated == false => collateralCounterAfter == 0;
    }

    // deposit() should call beforeAction() and afterAction() hooks if activated
    rule depositHooks(env e) {
        configForEightTokensSetupRequirements();
        setupHookRules(e);
        uint256 assets;
        address receiver;

        //is hook activated
        bool beforeDepositActivated = hookCallActivatedHarness(DEPOSIT_COLLATERAL(), BEFORE());
        bool afterDepositActivated = hookCallActivatedHarness(DEPOSIT_COLLATERAL(), AFTER());
        bool afterCollateralCounterActivated = hookCallActivatedHarness(TRANSFER_COLLATERAL(), AFTER());

        //function call
        deposit(e, assets, receiver);

        //check if hooks were called
        uint256 beforeCounter = hookReceiver.sumOfCountersBefore();
        uint256 afterCounter = hookReceiver.sumOfCountersAfter();
        uint256 depositCounterBefore = hookReceiver.DEPOSIT_COLLATERAL_COUNTER_BEFORE(e);
        uint256 depositCounterAfter = hookReceiver.DEPOSIT_COLLATERAL_COUNTER_AFTER(e);
        uint256 collateralCounterAfter = hookReceiver.TRANSFER_COLLATERAL_COUNTER_AFTER(e);

        //beforeCounter
        assert beforeDepositActivated == true => beforeCounter == 1;
        assert beforeDepositActivated == false => beforeCounter == 0;

        //afterCounter
        assert afterDepositActivated == true && afterCollateralCounterActivated == true => afterCounter == 2;
        assert afterDepositActivated == false && afterCollateralCounterActivated == true => afterCounter == 1;
        assert afterDepositActivated == true && afterCollateralCounterActivated == false => afterCounter == 1;
        assert afterDepositActivated == false && afterCollateralCounterActivated == false => afterCounter == 0;

        //depositCounterBefore
        assert beforeDepositActivated == true => depositCounterBefore == 1;
        assert beforeDepositActivated == false => depositCounterBefore == 0;

        //depositCounterAfter
        assert afterDepositActivated == true => depositCounterAfter == 1;
        assert afterDepositActivated == false => depositCounterAfter == 0;

        //shareCounter
        assert afterCollateralCounterActivated == true => collateralCounterAfter == 1;
        assert afterCollateralCounterActivated == false => collateralCounterAfter == 0;
    }

    // deposit(CollateralTye.Collateral) should call beforeAction() and afterAction() hooks if activated
    rule depositCollateralHooks(env e) {
        configForEightTokensSetupRequirements();
        setupHookRules(e);
        uint256 assets;
        address receiver;
        ISilo.CollateralType collateralType = ISilo.CollateralType.Collateral;

        //is hook activated
        bool beforeDepositCollateralActivated = hookCallActivatedHarness(DEPOSIT_COLLATERAL(), BEFORE());
        bool afterDepositCollateralActivated = hookCallActivatedHarness(DEPOSIT_COLLATERAL(), AFTER());
        bool afterCollateralCounterActivated = hookCallActivatedHarness(TRANSFER_COLLATERAL(), AFTER());

        //function call
        deposit(e, assets, receiver, collateralType);

        //check if hooks were called
        uint256 beforeCounter = hookReceiver.sumOfCountersBefore();
        uint256 afterCounter = hookReceiver.sumOfCountersAfter();
        uint256 depositCollateralCounterBefore = hookReceiver.DEPOSIT_COLLATERAL_COUNTER_BEFORE(e);
        uint256 depositCollateralCounterAfter = hookReceiver.DEPOSIT_COLLATERAL_COUNTER_AFTER(e);
        uint256 collateralCounterAfter = hookReceiver.TRANSFER_COLLATERAL_COUNTER_AFTER(e);

        //beforeCounter
        assert beforeDepositCollateralActivated == true => beforeCounter == 1;
        assert beforeDepositCollateralActivated == false => beforeCounter == 0;

        //afterCounter
        assert afterDepositCollateralActivated == true && afterCollateralCounterActivated == true => afterCounter == 2;
        assert afterDepositCollateralActivated == false && afterCollateralCounterActivated == true => afterCounter == 1;
        assert afterDepositCollateralActivated == true && afterCollateralCounterActivated == false => afterCounter == 1;
        assert afterDepositCollateralActivated == false && afterCollateralCounterActivated == false => afterCounter == 0;

        //depositCollateralCounterBefore
        assert beforeDepositCollateralActivated == true => depositCollateralCounterBefore == 1;
        assert beforeDepositCollateralActivated == false => depositCollateralCounterBefore == 0;

        //depositCollateralCounterAfter
        assert afterDepositCollateralActivated == true => depositCollateralCounterAfter == 1;
        assert afterDepositCollateralActivated == false => depositCollateralCounterAfter == 0;

        //shareCounter
        assert afterCollateralCounterActivated == true => collateralCounterAfter == 1;
        assert afterCollateralCounterActivated == false => collateralCounterAfter == 0;
    }

    // deposit(CollateralTye.Protected) should call beforeAction() and afterAction() hooks if activated
    rule depositProtectedHooks(env e) {
        configForEightTokensSetupRequirements();
        setupHookRules(e);
        uint256 assets;
        address receiver;
        ISilo.CollateralType collateralType = ISilo.CollateralType.Protected;

        //is hook activated
        bool beforeDepositProtectedActivated = hookCallActivatedHarness(DEPOSIT_PROTECTED(), BEFORE());
        bool afterDepositProtectedActivated = hookCallActivatedHarness(DEPOSIT_PROTECTED(), AFTER());
        bool afterProtectedCounterActivated = hookCallActivatedHarness(TRANSFER_PROTECTED(), AFTER());  

        //function call
        deposit(e, assets, receiver, collateralType);

        //check if hooks were called
        uint256 beforeCounter = hookReceiver.sumOfCountersBefore();
        uint256 afterCounter = hookReceiver.sumOfCountersAfter();
        uint256 depositProtectedCounterBefore = hookReceiver.DEPOSIT_PROTECTED_COUNTER_BEFORE(e);
        uint256 depositProtectedCounterAfter = hookReceiver.DEPOSIT_PROTECTED_COUNTER_AFTER(e);
        uint256 protectedCounterAfter = hookReceiver.TRANSFER_PROTECTED_COUNTER_AFTER(e);

        //beforeCounter
        assert beforeDepositProtectedActivated == true => beforeCounter == 1;
        assert beforeDepositProtectedActivated == false => beforeCounter == 0;

        //afterCounter
        assert afterDepositProtectedActivated == true && afterProtectedCounterActivated == true => afterCounter == 2;
        assert afterDepositProtectedActivated == false && afterProtectedCounterActivated == true => afterCounter == 1;
        assert afterDepositProtectedActivated == true && afterProtectedCounterActivated == false => afterCounter == 1;
        assert afterDepositProtectedActivated == false && afterProtectedCounterActivated == false => afterCounter == 0;

        //depositProtectedCounterBefore
        assert beforeDepositProtectedActivated == true => depositProtectedCounterBefore == 1;
        assert beforeDepositProtectedActivated == false => depositProtectedCounterBefore == 0;

        //depositProtectedCounterAfter
        assert afterDepositProtectedActivated == true => depositProtectedCounterAfter == 1;
        assert afterDepositProtectedActivated == false => depositProtectedCounterAfter == 0;

        //shareCounter
        assert afterProtectedCounterActivated == true => protectedCounterAfter == 1;
        assert afterProtectedCounterActivated == false => protectedCounterAfter == 0;
    }

    // mint() should call beforeAction() and afterAction() hooks if activated
    rule mintHooks(env e) {
        configForEightTokensSetupRequirements();
        setupHookRules(e);
        uint256 shares;
        address receiver;

        //is hook activated
        bool beforeMintActivated = hookCallActivatedHarness(DEPOSIT_COLLATERAL(), BEFORE());
        bool afterMintActivated = hookCallActivatedHarness(DEPOSIT_COLLATERAL(), AFTER());
        bool afterCollateralCounterActivated = hookCallActivatedHarness(TRANSFER_COLLATERAL(), AFTER());

        //function call
        mint(e, shares, receiver);

        //check if hooks were called
        uint256 beforeCounter = hookReceiver.sumOfCountersBefore();
        uint256 afterCounter = hookReceiver.sumOfCountersAfter();
        uint256 mintCounterBefore = hookReceiver.DEPOSIT_COLLATERAL_COUNTER_BEFORE(e);
        uint256 mintCounterAfter = hookReceiver.DEPOSIT_COLLATERAL_COUNTER_AFTER(e);
        uint256 collateralCounterAfter = hookReceiver.TRANSFER_COLLATERAL_COUNTER_AFTER(e);

        //beforeCounter
        assert beforeMintActivated == true => beforeCounter == 1;
        assert beforeMintActivated == false => beforeCounter == 0;

        //afterCounter
        assert afterMintActivated == true && afterCollateralCounterActivated == true => afterCounter == 2;
        assert afterMintActivated == false && afterCollateralCounterActivated == true => afterCounter == 1;
        assert afterMintActivated == true && afterCollateralCounterActivated == false => afterCounter == 1;
        assert afterMintActivated == false && afterCollateralCounterActivated == false => afterCounter == 0;

        //mintCounterBefore
        assert beforeMintActivated == true => mintCounterBefore == 1;
        assert beforeMintActivated == false => mintCounterBefore == 0;

        //mintCounterAfter
        assert afterMintActivated == true => mintCounterAfter == 1;
        assert afterMintActivated == false => mintCounterAfter == 0;

        //shareCounter
        assert afterCollateralCounterActivated == true => collateralCounterAfter == 1;
        assert afterCollateralCounterActivated == false => collateralCounterAfter == 0;
    }

    // mint(CollateralTye.Collateral) should call beforeAction() and afterAction() hooks if activated
    rule mintCollateralHooks(env e) {
        configForEightTokensSetupRequirements();
        setupHookRules(e);
        uint256 shares;
        address receiver;
        ISilo.CollateralType collateralType = ISilo.CollateralType.Collateral;

        //is hook activated
        bool beforeMintCollateralActivated = hookCallActivatedHarness(DEPOSIT_COLLATERAL(), BEFORE());
        bool afterMintCollateralActivated = hookCallActivatedHarness(DEPOSIT_COLLATERAL(), AFTER());
        bool afterCollateralCounterActivated = hookCallActivatedHarness(TRANSFER_COLLATERAL(), AFTER());

        //function call
        mint(e, shares, receiver, collateralType);

        //check if hooks were called
        uint256 beforeCounter = hookReceiver.sumOfCountersBefore();
        uint256 afterCounter = hookReceiver.sumOfCountersAfter();
        uint256 mintCollateralCounterBefore = hookReceiver.DEPOSIT_COLLATERAL_COUNTER_BEFORE(e);
        uint256 mintCollateralCounterAfter = hookReceiver.DEPOSIT_COLLATERAL_COUNTER_AFTER(e);
        uint256 collateralCounterAfter = hookReceiver.TRANSFER_COLLATERAL_COUNTER_AFTER(e);

        //beforeCounter
        assert beforeMintCollateralActivated == true => beforeCounter == 1;
        assert beforeMintCollateralActivated == false => beforeCounter == 0;

        //afterCounter
        assert afterMintCollateralActivated == true && afterCollateralCounterActivated == true => afterCounter == 2;
        assert afterMintCollateralActivated == false && afterCollateralCounterActivated == true => afterCounter == 1;
        assert afterMintCollateralActivated == true && afterCollateralCounterActivated == false => afterCounter == 1;
        assert afterMintCollateralActivated == false && afterCollateralCounterActivated == false => afterCounter == 0;

        //mintCollateralCounterBefore
        assert beforeMintCollateralActivated == true => mintCollateralCounterBefore == 1;
        assert beforeMintCollateralActivated == false => mintCollateralCounterBefore == 0;

        //mintCollateralCounterAfter
        assert afterMintCollateralActivated == true => mintCollateralCounterAfter == 1;
        assert afterMintCollateralActivated == false => mintCollateralCounterAfter == 0;

        //shareCounter
        assert afterCollateralCounterActivated == true => collateralCounterAfter == 1;
        assert afterCollateralCounterActivated == false => collateralCounterAfter == 0;
    }

    // mint(CollateralTye.Protected) should call beforeAction() and afterAction() hooks if activated
    rule mintProtectedHooks(env e) {
        configForEightTokensSetupRequirements();
        setupHookRules(e);
        uint256 shares;
        address receiver;
        ISilo.CollateralType collateralType = ISilo.CollateralType.Protected;

        //is hook activated
        bool beforeMintProtectedActivated = hookCallActivatedHarness(DEPOSIT_PROTECTED(), BEFORE());
        bool afterMintProtectedActivated = hookCallActivatedHarness(DEPOSIT_PROTECTED(), AFTER());
        bool afterProtectedCounterActivated = hookCallActivatedHarness(TRANSFER_PROTECTED(), AFTER());

        //function call
        mint(e, shares, receiver, collateralType);

        //check if hooks were called
        uint256 beforeCounter = hookReceiver.sumOfCountersBefore();
        uint256 afterCounter = hookReceiver.sumOfCountersAfter();
        uint256 mintProtectedCounterBefore = hookReceiver.DEPOSIT_PROTECTED_COUNTER_BEFORE(e);
        uint256 mintProtectedCounterAfter = hookReceiver.DEPOSIT_PROTECTED_COUNTER_AFTER(e);
        uint256 protectedCounterAfter = hookReceiver.TRANSFER_PROTECTED_COUNTER_AFTER(e);   

        //beforeCounter
        assert beforeMintProtectedActivated == true => beforeCounter == 1;
        assert beforeMintProtectedActivated == false => beforeCounter == 0;

        //afterCounter
        assert afterMintProtectedActivated == true && afterProtectedCounterActivated == true => afterCounter == 2;
        assert afterMintProtectedActivated == false && afterProtectedCounterActivated == true => afterCounter == 1;
        assert afterMintProtectedActivated == true && afterProtectedCounterActivated == false => afterCounter == 1;
        assert afterMintProtectedActivated == false && afterProtectedCounterActivated == false => afterCounter == 0;

        //mintProtectedCounterBefore
        assert beforeMintProtectedActivated == true => mintProtectedCounterBefore == 1;
        assert beforeMintProtectedActivated == false => mintProtectedCounterBefore == 0;

        //mintProtectedCounterAfter
        assert afterMintProtectedActivated == true => mintProtectedCounterAfter == 1;
        assert afterMintProtectedActivated == false => mintProtectedCounterAfter == 0;

        //shareCounter
        assert afterProtectedCounterActivated == true => protectedCounterAfter == 1;
        assert afterProtectedCounterActivated == false => protectedCounterAfter == 0;
    }

    // transitionCollateral(CollateralType.Collateral) should call beforeAction() and afterAction() hooks if activated 
    rule transitionCollateralColateralHooks(env e) {
        configForEightTokensSetupRequirements();
        setupHookRules(e);
        uint256 shares;
        address owner;
        ISilo.CollateralType collateralType = ISilo.CollateralType.Collateral;


        //is hook activated
        bool beforeTransitionCollateralActivated = hookCallActivatedHarness(TRANSITION_COLLATERAL_COLLATERAL(), BEFORE());
        bool afterTransitionCollateralActivated = hookCallActivatedHarness(TRANSITION_COLLATERAL_COLLATERAL(), AFTER());
        bool afterProtectedCounterActivated = hookCallActivatedHarness(TRANSFER_PROTECTED(), AFTER());
        bool afterCollateralCounterActivated = hookCallActivatedHarness(TRANSFER_COLLATERAL(), AFTER());

        //function call
        transitionCollateral(e, shares, owner, collateralType);

        //check if hooks were called
        uint256 beforeCounter = hookReceiver.sumOfCountersBefore();
        uint256 afterCounter = hookReceiver.sumOfCountersAfter();
        uint256 transitionCollateralCounterBefore = hookReceiver.TRANSITION_COLLATERAL_COLLATERAL_COUNTER_BEFORE(e);
        uint256 transitionCollateralCounterAfter = hookReceiver.TRANSITION_COLLATERAL_COLLATERAL_COUNTER_AFTER(e);
        uint256 protectedCounterAfter = hookReceiver.TRANSFER_PROTECTED_COUNTER_AFTER(e);
        uint256 collateralCounterAfter = hookReceiver.TRANSFER_COLLATERAL_COUNTER_AFTER(e);

        //beforeCounter
        assert beforeTransitionCollateralActivated == true => beforeCounter == 1;
        assert beforeTransitionCollateralActivated == false => beforeCounter == 0;

        //afterCounter
        assert afterTransitionCollateralActivated == true && afterProtectedCounterActivated == true && afterCollateralCounterActivated == true => afterCounter == 3;
        assert afterTransitionCollateralActivated == false && afterProtectedCounterActivated == true && afterCollateralCounterActivated == true => afterCounter == 2;
        assert afterTransitionCollateralActivated == true && afterProtectedCounterActivated == false && afterCollateralCounterActivated == true => afterCounter == 2;
        assert afterTransitionCollateralActivated == true && afterProtectedCounterActivated == true && afterCollateralCounterActivated == false => afterCounter == 2;
        assert afterTransitionCollateralActivated == false && afterProtectedCounterActivated == false && afterCollateralCounterActivated == true => afterCounter == 1;
        assert afterTransitionCollateralActivated == false && afterProtectedCounterActivated == true && afterCollateralCounterActivated == false => afterCounter == 1;
        assert afterTransitionCollateralActivated == true && afterProtectedCounterActivated == false && afterCollateralCounterActivated == false => afterCounter == 1;
        assert afterTransitionCollateralActivated == false && afterProtectedCounterActivated == false && afterCollateralCounterActivated == false => afterCounter == 0;

        //transitionCollateralCounterBefore
        assert beforeTransitionCollateralActivated == true => transitionCollateralCounterBefore == 1;
        assert beforeTransitionCollateralActivated == false => transitionCollateralCounterBefore == 0;

        //transitionCollateralCounterAfter
        assert afterTransitionCollateralActivated == true => transitionCollateralCounterAfter == 1;
        assert afterTransitionCollateralActivated == false => transitionCollateralCounterAfter == 0;

        //shareCounter
        assert afterProtectedCounterActivated == true => protectedCounterAfter == 1;
        assert afterCollateralCounterActivated == true => collateralCounterAfter == 1;
        assert afterProtectedCounterActivated == false => protectedCounterAfter == 0;
        assert afterCollateralCounterActivated == false => collateralCounterAfter == 0;
    }

    // redeem(CollateralTye.Collateral) should call beforeAction() and afterAction() hooks if activated
    rule redeemCollateralHooks(env e) {
        configForEightTokensSetupRequirements();
        setupHookRules(e);
        uint256 shares;
        address receiver;
        address owner;
        ISilo.CollateralType collateralType = ISilo.CollateralType.Collateral;

        //is hook activated
        bool beforeRedeemCollateralActivated = hookCallActivatedHarness(WITHDRAW_COLLATERAL(), BEFORE());
        bool afterRedeemCollateralActivated = hookCallActivatedHarness(WITHDRAW_COLLATERAL(), AFTER());
        bool afterCollateralCounterActivated = hookCallActivatedHarness(TRANSFER_COLLATERAL(), AFTER());

        //function call
        redeem(e, shares, receiver, owner, collateralType);

        //check if hooks were called
        uint256 beforeCounter = hookReceiver.sumOfCountersBefore();
        uint256 afterCounter = hookReceiver.sumOfCountersAfter();
        uint256 redeemCollateralCounterBefore = hookReceiver.WITHDRAW_COLLATERAL_COUNTER_BEFORE(e);
        uint256 redeemCollateralCounterAfter = hookReceiver.WITHDRAW_COLLATERAL_COUNTER_AFTER(e);
        uint256 collateralCounterAfter = hookReceiver.TRANSFER_COLLATERAL_COUNTER_AFTER(e);

        //beforeCounter
        assert beforeRedeemCollateralActivated == true => beforeCounter == 1;
        assert beforeRedeemCollateralActivated == false => beforeCounter == 0;

        //afterCounter
        assert afterRedeemCollateralActivated == true && afterCollateralCounterActivated == true => afterCounter == 2;
        assert afterRedeemCollateralActivated == false && afterCollateralCounterActivated == true => afterCounter == 1;
        assert afterRedeemCollateralActivated == true && afterCollateralCounterActivated == false => afterCounter == 1;
        assert afterRedeemCollateralActivated == false && afterCollateralCounterActivated == false => afterCounter == 0;

        //redeemCollateralCounterBefore
        assert beforeRedeemCollateralActivated == true => redeemCollateralCounterBefore == 1;
        assert beforeRedeemCollateralActivated == false => redeemCollateralCounterBefore == 0;

        //redeemCollateralCounterAfter
        assert afterRedeemCollateralActivated == true => redeemCollateralCounterAfter == 1;
        assert afterRedeemCollateralActivated == false => redeemCollateralCounterAfter == 0;

        //shareCounter
        assert afterCollateralCounterActivated == true => collateralCounterAfter == 1;
        assert afterCollateralCounterActivated == false => collateralCounterAfter == 0;
    }

    // withdraw(CollateralTye.Collateral) should call beforeAction() and afterAction() hooks if activated 
    rule withdrawCollateralCollateralHooks(env e) {
        configForEightTokensSetupRequirements();
        setupHookRules(e);
        uint256 assets;
        address receiver;
        address owner;
        ISilo.CollateralType collateralType = ISilo.CollateralType.Collateral;

        //is hook activated
        bool beforeWithdrawCollateralActivated = hookCallActivatedHarness(WITHDRAW_COLLATERAL(), BEFORE());
        bool afterWithdrawCollateralActivated = hookCallActivatedHarness(WITHDRAW_COLLATERAL(), AFTER());
        bool afterTransferCollateralActivated = hookCallActivatedHarness(TRANSFER_COLLATERAL(), AFTER());

        //function call
        withdraw(e, assets, receiver, owner, collateralType);

        //check if hooks were called
        uint256 beforeCounter = hookReceiver.sumOfCountersBefore();
        uint256 afterCounter = hookReceiver.sumOfCountersAfter();
        uint256 withdrawCollateralCounterBefore = hookReceiver.WITHDRAW_COLLATERAL_COUNTER_BEFORE(e);
        uint256 withdrawCollateralCounterAfter = hookReceiver.WITHDRAW_COLLATERAL_COUNTER_AFTER(e);
        uint256 collateralCounterAfter = hookReceiver.TRANSFER_COLLATERAL_COUNTER_AFTER(e);

        //beforeCounter
        assert beforeWithdrawCollateralActivated == true => beforeCounter == 1;
        assert beforeWithdrawCollateralActivated == false => beforeCounter == 0;

        //afterCounter
        assert afterWithdrawCollateralActivated == true && afterTransferCollateralActivated == true => afterCounter == 2;
        assert afterWithdrawCollateralActivated == false && afterTransferCollateralActivated == true => afterCounter == 1;
        assert afterWithdrawCollateralActivated == true && afterTransferCollateralActivated == false => afterCounter == 1;
        assert afterWithdrawCollateralActivated == false && afterTransferCollateralActivated == false => afterCounter == 0;

        //withdrawCollateralCounterBefore
        assert beforeWithdrawCollateralActivated == true => withdrawCollateralCounterBefore == 1;
        assert beforeWithdrawCollateralActivated == false => withdrawCollateralCounterBefore == 0;

        //withdrawCollateralCounterAfter
        assert afterWithdrawCollateralActivated == true => withdrawCollateralCounterAfter == 1;
        assert afterWithdrawCollateralActivated == false => withdrawCollateralCounterAfter == 0;

        //shareCounter
        assert afterTransferCollateralActivated == true => collateralCounterAfter == 1;
        assert afterTransferCollateralActivated == false => collateralCounterAfter == 0;
    }

    // withdraw() should call beforeAction() and afterAction() hooks if activated 
    rule withdrawCollateralHooks(env e) {
        configForEightTokensSetupRequirements();
        setupHookRules(e);
        uint256 assets;
        address receiver;
        address owner;

        //is hook activated
        bool beforeWithdrawActivated = hookCallActivatedHarness(WITHDRAW_COLLATERAL(), BEFORE());
        bool afterWithdrawActivated = hookCallActivatedHarness(WITHDRAW_COLLATERAL(), AFTER());
        bool afterTransferCollateralActivated = hookCallActivatedHarness(TRANSFER_COLLATERAL(), AFTER());

        //function call
        withdraw(e, assets, receiver, owner);

        //check if hooks were called
        uint256 beforeCounter = hookReceiver.sumOfCountersBefore();
        uint256 afterCounter = hookReceiver.sumOfCountersAfter();
        uint256 withdrawCounterBefore = hookReceiver.WITHDRAW_COLLATERAL_COUNTER_BEFORE(e);
        uint256 withdrawCounterAfter = hookReceiver.WITHDRAW_COLLATERAL_COUNTER_AFTER(e);
        uint256 collateralCounterAfter = hookReceiver.TRANSFER_COLLATERAL_COUNTER_AFTER(e);

        //beforeCounter
        assert beforeWithdrawActivated == true => beforeCounter == 1;
        assert beforeWithdrawActivated == false => beforeCounter == 0;

        //afterCounter
        assert afterWithdrawActivated == true && afterTransferCollateralActivated == true => afterCounter == 2;
        assert afterWithdrawActivated == false && afterTransferCollateralActivated == true => afterCounter == 1;
        assert afterWithdrawActivated == true && afterTransferCollateralActivated == false => afterCounter == 1;
        assert afterWithdrawActivated == false && afterTransferCollateralActivated == false => afterCounter == 0;

        //withdrawCounterBefore
        assert beforeWithdrawActivated == true => withdrawCounterBefore == 1;
        assert beforeWithdrawActivated == false => withdrawCounterBefore == 0;

        //withdrawCounterAfter
        assert afterWithdrawActivated == true => withdrawCounterAfter == 1;
        assert afterWithdrawActivated == false => withdrawCounterAfter == 0;

        //shareCounter
        assert afterTransferCollateralActivated == true => collateralCounterAfter == 1;
        assert afterTransferCollateralActivated == false => collateralCounterAfter == 0;
    }

    // redeem(CollateralTye.Protected) should call beforeAction() and afterAction() hooks if activated
    rule redeemProtectedHooks(env e) {
        configForEightTokensSetupRequirements();
        setupHookRules(e);
        uint256 shares;
        address receiver;
        address owner;
        ISilo.CollateralType collateralType = ISilo.CollateralType.Protected;

        //is hook activated
        bool beforeRedeemProtectedActivated = hookCallActivatedHarness(WITHDRAW_PROTECTED(), BEFORE());
        bool afterRedeemProtectedActivated = hookCallActivatedHarness(WITHDRAW_PROTECTED(), AFTER());
        bool afterProtectedCounterActivated = hookCallActivatedHarness(TRANSFER_PROTECTED(), AFTER());

        //function call
        redeem(e, shares, receiver, owner, collateralType);

        //check if hooks were called
        uint256 beforeCounter = hookReceiver.sumOfCountersBefore();
        uint256 afterCounter = hookReceiver.sumOfCountersAfter();
        uint256 redeemProtectedCounterBefore = hookReceiver.WITHDRAW_PROTECTED_COUNTER_BEFORE(e);
        uint256 redeemProtectedCounterAfter = hookReceiver.WITHDRAW_PROTECTED_COUNTER_AFTER(e);
        uint256 protectedCounterAfter = hookReceiver.TRANSFER_PROTECTED_COUNTER_AFTER(e);

        //beforeCounter
        assert beforeRedeemProtectedActivated == true => beforeCounter == 1;
        assert beforeRedeemProtectedActivated == false => beforeCounter == 0;

        //afterCounter
        assert afterRedeemProtectedActivated == true && afterProtectedCounterActivated == true => afterCounter == 2;
        assert afterRedeemProtectedActivated == false && afterProtectedCounterActivated == true => afterCounter == 1;
        assert afterRedeemProtectedActivated == true && afterProtectedCounterActivated == false => afterCounter == 1;
        assert afterRedeemProtectedActivated == false && afterProtectedCounterActivated == false => afterCounter == 0;

        //redeemProtectedCounterBefore
        assert beforeRedeemProtectedActivated == true => redeemProtectedCounterBefore == 1;
        assert beforeRedeemProtectedActivated == false => redeemProtectedCounterBefore == 0;

        //redeemProtectedCounterAfter
        assert afterRedeemProtectedActivated == true => redeemProtectedCounterAfter == 1;
        assert afterRedeemProtectedActivated == false => redeemProtectedCounterAfter == 0;

        //shareCounter
        assert afterProtectedCounterActivated == true => protectedCounterAfter == 1;
        assert afterProtectedCounterActivated == false => protectedCounterAfter == 0;
    }

    // borrowShares() should call beforeAction() and afterAction() hooks if activated
    rule borrowSharesHooks(env e) {
        configForEightTokensSetupRequirements();
        setupHookRules(e);
        uint256 shares;
        address receiver;
        address borrower;

        //is hook activated
        bool beforeBorrowSharesActivated = hookCallActivatedHarness(BORROW(), BEFORE());
        bool afterBorrowSharesActivated = hookCallActivatedHarness(BORROW(), AFTER());
        bool afterTransferDebtActivated = hookCallActivatedHarness(TRANSFER_DEBT(), AFTER());

        //function call
        borrowShares(e, shares, receiver, borrower);

        //check if hooks were called
        uint256 beforeCounter = hookReceiver.sumOfCountersBefore();
        uint256 afterCounter = hookReceiver.sumOfCountersAfter();
        uint256 borrowCounterBefore = hookReceiver.BORROW_COUNTER_BEFORE(e);
        uint256 borrowCounterAfter = hookReceiver.BORROW_COUNTER_AFTER(e);
        uint256 debtCounterAfter = hookReceiver.TRANSFER_DEBT_COUNTER_AFTER(e);

        //beforeCounter
        assert beforeBorrowSharesActivated == true => beforeCounter == 1;
        assert beforeBorrowSharesActivated == false => beforeCounter == 0;

        //afterCounter
        assert afterBorrowSharesActivated == true && afterTransferDebtActivated == true => afterCounter == 2;
        assert afterBorrowSharesActivated == false && afterTransferDebtActivated == true => afterCounter == 1;
        assert afterBorrowSharesActivated == true && afterTransferDebtActivated == false => afterCounter == 1;
        assert afterBorrowSharesActivated == false && afterTransferDebtActivated == false => afterCounter == 0;

        //borrowCounterBefore
        assert beforeBorrowSharesActivated == true => borrowCounterBefore == 1;
        assert beforeBorrowSharesActivated == false => borrowCounterBefore == 0;

        //borrowCounterAfter
        assert afterBorrowSharesActivated == true => borrowCounterAfter == 1;
        assert afterBorrowSharesActivated == false => borrowCounterAfter == 0;

        //debtCounter
        assert afterTransferDebtActivated == true => debtCounterAfter == 1;
        assert afterTransferDebtActivated == false => debtCounterAfter == 0;
    }

    // borrowSameAsset() should call beforeAction() and afterAction() hooks if activated
    rule borrowSameAssetHooks(env e) {
        configForEightTokensSetupRequirements();
        setupHookRules(e);
        uint256 assets;
        address receiver;
        address borrower;

        //is hook activated
        bool beforeBorrowSameAssetActivated = hookCallActivatedHarness(BORROW_SAME_ASSET(), BEFORE());
        bool afterBorrowSameAssetActivated = hookCallActivatedHarness(BORROW_SAME_ASSET(), AFTER());
        bool afterTransferDebtActivated = hookCallActivatedHarness(TRANSFER_DEBT(), AFTER());

        //function call
        borrowSameAsset(e, assets, receiver, borrower);

        //check if hooks were called
        uint256 beforeCounter = hookReceiver.sumOfCountersBefore();
        uint256 afterCounter = hookReceiver.sumOfCountersAfter();
        uint256 borrowSameCounterBefore = hookReceiver.BORROW_SAME_ASSET_COUNTER_BEFORE(e);
        uint256 borrowSameCounterAfter = hookReceiver.BORROW_SAME_ASSET_COUNTER_AFTER(e);
        uint256 debtCounterAfter = hookReceiver.TRANSFER_DEBT_COUNTER_AFTER(e);

        //beforeCounter
        assert beforeBorrowSameAssetActivated == true => beforeCounter == 1;
        assert beforeBorrowSameAssetActivated == false => beforeCounter == 0;

        //afterCounter
        assert afterBorrowSameAssetActivated == true && afterTransferDebtActivated == true => afterCounter == 2;
        assert afterBorrowSameAssetActivated == false && afterTransferDebtActivated == true => afterCounter == 1;
        assert afterBorrowSameAssetActivated == true && afterTransferDebtActivated == false => afterCounter == 1;
        assert afterBorrowSameAssetActivated == false && afterTransferDebtActivated == false => afterCounter == 0;

        //borrowSameCounterBefore
        assert beforeBorrowSameAssetActivated == true => borrowSameCounterBefore == 1;
        assert beforeBorrowSameAssetActivated == false => borrowSameCounterBefore == 0;

        //borrowSameCounterAfter
        assert afterBorrowSameAssetActivated == true => borrowSameCounterAfter == 1;
        assert afterBorrowSameAssetActivated == false => borrowSameCounterAfter == 0;

        //debtCounter
        assert afterTransferDebtActivated == true => debtCounterAfter == 1;
        assert afterTransferDebtActivated == false => debtCounterAfter == 0;
    }

    // repay() should call beforeAction() and afterAction() hooks if activated
    rule repayHooks(env e) {
        configForEightTokensSetupRequirements();
        setupHookRules(e);
        uint256 assets;
        address borrower;

        //is hook activated
        bool beforeRepayActivated = hookCallActivatedHarness(REPAY(), BEFORE());    
        bool afterRepayActivated = hookCallActivatedHarness(REPAY(), AFTER());
        bool afterTransferDebtActivated = hookCallActivatedHarness(TRANSFER_DEBT(), AFTER());

        //function call
        repay(e, assets, borrower);

        //check if hooks were called
        uint256 beforeCounter = hookReceiver.sumOfCountersBefore();
        uint256 afterCounter = hookReceiver.sumOfCountersAfter();
        uint256 repayCounterBefore = hookReceiver.REPAY_COUNTER_BEFORE(e);
        uint256 repayCounterAfter = hookReceiver.REPAY_COUNTER_AFTER(e);
        uint256 debtCounterAfter = hookReceiver.TRANSFER_DEBT_COUNTER_AFTER(e);

        //beforeCounter
        assert beforeRepayActivated == true => beforeCounter == 1;
        assert beforeRepayActivated == false => beforeCounter == 0;

        //afterCounter
        assert afterRepayActivated == true && afterTransferDebtActivated == true => afterCounter == 2;
        assert afterRepayActivated == false && afterTransferDebtActivated == true => afterCounter == 1;
        assert afterRepayActivated == true && afterTransferDebtActivated == false => afterCounter == 1;
        assert afterRepayActivated == false && afterTransferDebtActivated == false => afterCounter == 0;

        //repayCounterBefore
        assert beforeRepayActivated == true => repayCounterBefore == 1;
        assert beforeRepayActivated == false => repayCounterBefore == 0;

        //repayCounterAfter
        assert afterRepayActivated == true => repayCounterAfter == 1;
        assert afterRepayActivated == false => repayCounterAfter == 0;

        //debtCounter
        assert afterTransferDebtActivated == true => debtCounterAfter == 1;
        assert afterTransferDebtActivated == false => debtCounterAfter == 0;
    }

    // repayShares() should call beforeAction() and afterAction() hooks if activated
    rule repaySharesHooks(env e) {
        configForEightTokensSetupRequirements();
        setupHookRules(e);
        uint256 shares;
        address borrower;

        //is hook activated
        bool beforeRepaySharesActivated = hookCallActivatedHarness(REPAY(), BEFORE());
        bool afterRepaySharesActivated = hookCallActivatedHarness(REPAY(), AFTER());
        bool afterTransferDebtActivated = hookCallActivatedHarness(TRANSFER_DEBT(), AFTER());

        //function call
        repayShares(e, shares, borrower);

        //check if hooks were called
        uint256 beforeCounter = hookReceiver.sumOfCountersBefore();
        uint256 afterCounter = hookReceiver.sumOfCountersAfter();
        uint256 repaySharesCounterBefore = hookReceiver.REPAY_COUNTER_BEFORE(e);
        uint256 repaySharesCounterAfter = hookReceiver.REPAY_COUNTER_AFTER(e);
        uint256 debtCounterAfter = hookReceiver.TRANSFER_DEBT_COUNTER_AFTER(e);

        //beforeCounter
        assert beforeRepaySharesActivated == true => beforeCounter == 1;
        assert beforeRepaySharesActivated == false => beforeCounter == 0;

        //afterCounter
        assert afterRepaySharesActivated == true && afterTransferDebtActivated == true => afterCounter == 2;
        assert afterRepaySharesActivated == false && afterTransferDebtActivated == true => afterCounter == 1;
        assert afterRepaySharesActivated == true && afterTransferDebtActivated == false => afterCounter == 1;
        assert afterRepaySharesActivated == false && afterTransferDebtActivated == false => afterCounter == 0;

        //repaySharesCounterBefore
        assert beforeRepaySharesActivated == true => repaySharesCounterBefore == 1;
        assert beforeRepaySharesActivated == false => repaySharesCounterBefore == 0;

        //repaySharesCounterAfter
        assert afterRepaySharesActivated == true => repaySharesCounterAfter == 1;
        assert afterRepaySharesActivated == false => repaySharesCounterAfter == 0;

        //debtCounter
        assert afterTransferDebtActivated == true => debtCounterAfter == 1;
        assert afterTransferDebtActivated == false => debtCounterAfter == 0;
    }

    // withdraw(CollateralTye.Protected) should call beforeAction() and afterAction() hooks if activated 
    rule withdrawCollateralProtectedHooks(env e) {
        configForEightTokensSetupRequirements();
        setupHookRules(e);
        uint256 assets;
        address receiver;
        address owner;
        ISilo.CollateralType collateralType = ISilo.CollateralType.Protected;

        //is hook activated
        bool beforeWithdrawProtectedActivated = hookCallActivatedHarness(WITHDRAW_PROTECTED(), BEFORE());
        bool afterWithdrawProtectedActivated = hookCallActivatedHarness(WITHDRAW_PROTECTED(), AFTER());
        bool afterTransferProtectedActivated = hookCallActivatedHarness(TRANSFER_PROTECTED(), AFTER());

        //function call
        withdraw(e, assets, receiver, owner, collateralType);

        //check if hooks were called
        uint256 beforeCounter = hookReceiver.sumOfCountersBefore();
        uint256 afterCounter = hookReceiver.sumOfCountersAfter();
        uint256 withdrawProtectedCounterBefore = hookReceiver.WITHDRAW_PROTECTED_COUNTER_BEFORE(e);
        uint256 withdrawProtectedCounterAfter = hookReceiver.WITHDRAW_PROTECTED_COUNTER_AFTER(e);
        uint256 protectedCounterAfter = hookReceiver.TRANSFER_PROTECTED_COUNTER_AFTER(e);

        //beforeCounter
        assert beforeWithdrawProtectedActivated == true => beforeCounter == 1;
        assert beforeWithdrawProtectedActivated == false => beforeCounter == 0;

        //afterCounter
        assert afterWithdrawProtectedActivated == true && afterTransferProtectedActivated == true => afterCounter == 2;
        assert afterWithdrawProtectedActivated == false && afterTransferProtectedActivated == true => afterCounter == 1;
        assert afterWithdrawProtectedActivated == true && afterTransferProtectedActivated == false => afterCounter == 1;
        assert afterWithdrawProtectedActivated == false && afterTransferProtectedActivated == false => afterCounter == 0;

        //withdrawProtectedCounterBefore
        assert beforeWithdrawProtectedActivated == true => withdrawProtectedCounterBefore == 1;
        assert beforeWithdrawProtectedActivated == false => withdrawProtectedCounterBefore == 0;

        //withdrawProtectedCounterAfter
        assert afterWithdrawProtectedActivated == true => withdrawProtectedCounterAfter == 1;
        assert afterWithdrawProtectedActivated == false => withdrawProtectedCounterAfter == 0;

        //shareCounter
        assert afterTransferProtectedActivated == true => protectedCounterAfter == 1;
        assert afterTransferProtectedActivated == false => protectedCounterAfter == 0;
    }

    // borrow() should call beforeAction() and afterAction() hooks if activated
    rule borrowHooks(env e) {
        configForEightTokensSetupRequirements();
        setupHookRules(e);
        uint256 assets;
        address receiver;
        address borrower;

        //is hook activated
        bool beforeBorrowActivated = hookCallActivatedHarness(BORROW(), BEFORE());
        bool afterBorrowActivated = hookCallActivatedHarness(BORROW(), AFTER());
        bool afterTransferDebtActivated = hookCallActivatedHarness(TRANSFER_DEBT(), AFTER());

        //function call
        borrow(e, assets, receiver, borrower);

        //check if hooks were called
        uint256 beforeCounter = hookReceiver.sumOfCountersBefore();
        uint256 afterCounter = hookReceiver.sumOfCountersAfter();
        uint256 borrowCounterBefore = hookReceiver.BORROW_COUNTER_BEFORE(e);
        uint256 borrowCounterAfter = hookReceiver.BORROW_COUNTER_AFTER(e);
        uint256 debtCounterAfter = hookReceiver.TRANSFER_DEBT_COUNTER_AFTER(e);

        //beforeCounter
        assert beforeBorrowActivated == true => beforeCounter == 1;
        assert beforeBorrowActivated == false => beforeCounter == 0;

        //afterCounter
        assert afterBorrowActivated == true && afterTransferDebtActivated == true => afterCounter == 2;
        assert afterBorrowActivated == true && afterTransferDebtActivated == false => afterCounter == 1;
        assert afterBorrowActivated == false && afterTransferDebtActivated == true => afterCounter == 1;
        assert afterBorrowActivated == false && afterTransferDebtActivated == false => afterCounter == 0;

        //borrowCounterBefore
        assert beforeBorrowActivated == true => borrowCounterBefore == 1;
        assert beforeBorrowActivated == false => borrowCounterBefore == 0;

        //borrowCounterAfter
        assert afterBorrowActivated == true => borrowCounterAfter == 1;
        assert afterBorrowActivated == false => borrowCounterAfter == 0;

        //debtCounter
        assert afterTransferDebtActivated == true => debtCounterAfter == 1;
        assert afterTransferDebtActivated == false => debtCounterAfter == 0;
    }  

    // switchCollateral() should call beforeAction() and afterAction() hooks if activated 
    rule switchCollateralHooks(env e) {
        configForEightTokensSetupRequirements();
        setupHookRules(e);

        //is hook activated
        bool beforeSwitchCollateralActivated = hookCallActivatedHarness(SWITCH_COLLATERAL(), BEFORE());
        bool afterSwitchCollateralActivated = hookCallActivatedHarness(SWITCH_COLLATERAL(), AFTER());

        //function call
        switchCollateralToThisSilo(e);

        //check if hooks were called
        uint256 beforeCounter = hookReceiver.sumOfCountersBefore();
        uint256 afterCounter = hookReceiver.sumOfCountersAfter();
        uint256 switchCollateralCounterBefore = hookReceiver.SWITCH_COLLATERAL_COUNTER_BEFORE(e);
        uint256 switchCollateralCounterAfter = hookReceiver.SWITCH_COLLATERAL_COUNTER_AFTER(e);

        //beforeCounter
        assert beforeSwitchCollateralActivated == true => beforeCounter == 1;
        assert beforeSwitchCollateralActivated == false => beforeCounter == 0;

        //afterCounter
        assert afterSwitchCollateralActivated == true => afterCounter == 1;
        assert afterSwitchCollateralActivated == false => afterCounter == 0;

        //switchCollateralCounterBefore
        assert beforeSwitchCollateralActivated == true => switchCollateralCounterBefore == 1;
        assert beforeSwitchCollateralActivated == false => switchCollateralCounterBefore == 0;

        //switchCollateralCounterAfter
        assert afterSwitchCollateralActivated == true => switchCollateralCounterAfter == 1;
        assert afterSwitchCollateralActivated == false => switchCollateralCounterAfter == 0;
    }

    // flashLoan() should call beforeAction() and afterAction() hooks if activated
    rule flashLoanHooks(env e) {
        configForEightTokensSetupRequirements();
        setupHookRules(e);
        address receiver;
        address token;
        uint256 amount;
        bytes data;

        //is hook activated
        bool beforeFlashLoanActivated = hookCallActivatedHarness(FLASH_LOAN(), BEFORE());
        bool afterFlashLoanActivated = hookCallActivatedHarness(FLASH_LOAN(), AFTER());

        //function call
        flashLoan(e, receiver, token, amount, data);

        //check if hooks were called
        uint256 beforeCounter = hookReceiver.sumOfCountersBefore();
        uint256 afterCounter = hookReceiver.sumOfCountersAfter();
        uint256 flashLoanCounterBefore = hookReceiver.FLASH_LOAN_COUNTER_BEFORE(e);
        uint256 flashLoanCounterAfter = hookReceiver.FLASH_LOAN_COUNTER_AFTER(e);

        //beforeCounter
        assert beforeFlashLoanActivated == true => beforeCounter == 1;
        assert beforeFlashLoanActivated == false => beforeCounter == 0;

        //afterCounter
        assert afterFlashLoanActivated == true => afterCounter == 1;
        assert afterFlashLoanActivated == false => afterCounter == 0;

        //flashLoanCounterBefore
        assert beforeFlashLoanActivated == true => flashLoanCounterBefore == 1;
        assert beforeFlashLoanActivated == false => flashLoanCounterBefore == 0;

        //flashLoanCounterAfter
        assert afterFlashLoanActivated == true => flashLoanCounterAfter == 1;
        assert afterFlashLoanActivated == false => flashLoanCounterAfter == 0;
    }


