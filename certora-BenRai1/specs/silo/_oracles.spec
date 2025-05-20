import "../setup/CompleteSiloSetup.spec";
import "./0base_Silo.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";
// import "../simplifications/_Oracle_call_before_quote_UNSAFE.spec"; //i: summarizes before the call to beforeQuote
import "../simplifications/Oracle_quote_one_UNSAFE.spec";
import "../simplifications/_flashloan_no_state_changes.spec";
import "../simplifications/SiloMathLib_SAFE.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec"; //accrueInterest does not change state
// import "../simplifications/_Oracle_call_before_quote_UNSAFE.spec"; //to avoide DEFAUL HAVOC for oracle calls
// import "../simplifications/SimplifiedGetCompoundInterestRateAndUpdate_SAFE.spec";
// import "../simplifications/_hooks_no_state_change.spec"; //calls to hooks do not change state

//---------------------- METHODES, FUNCTIONS, GHOSTS START----------------------
    methods{

    function _.beforeQuote(address) external => beforeQuote__noStateChange(calledContract) expect void;
    }

    //number of calls to the oracle
    persistent ghost mapping(address => mathint) callCountBeforeQuote{
        //all runs starts with the value 0
        init_state axiom forall address a. callCountBeforeQuote[a] == 0;
        // init_state axiom forall uint256 p. tracked_weight(p) == 0;
    }

    //oracle calls
    function beforeQuote__noStateChange(address _calledContract) {
        callCountBeforeQuote[_calledContract] = callCountBeforeQuote[_calledContract] + 1;
    }

    //setup for the maxLtvOracles
    function maxLtvOracleRulesSetup(env e, address otherOracle) {
        address silo0MaxLtvOracle = siloConfig.getConfig(e, silo0).maxLtvOracle;
        address silo1MaxLtvOracle = siloConfig.getConfig(e, silo1).maxLtvOracle;
        //oracle addresses are different
        require(silo0MaxLtvOracle != silo1MaxLtvOracle);
        require(silo0MaxLtvOracle != otherOracle);
        require(silo1MaxLtvOracle != otherOracle);
    }

    //setup for the solvencyOracles
    function solvencyOracleRulesSetup(env e, address otherOracle) {
        address silo0SolvencyOracle = siloConfig.getConfig(e, silo0).solvencyOracle;
        address silo1SolvencyOracle = siloConfig.getConfig(e, silo1).solvencyOracle;
        //oracle addresses are different
        require(silo0SolvencyOracle != silo1SolvencyOracle);
        require(silo0SolvencyOracle != otherOracle);
        require(silo1SolvencyOracle != otherOracle);
    }

    function allOraclesDifferent(env e, address otherOracle) {
        address silo0MaxLtvOracle = siloConfig.getConfig(e, silo0).maxLtvOracle;
        address silo0SolvencyOracle = siloConfig.getConfig(e, silo0).solvencyOracle;
        address silo1MaxLtvOracle = siloConfig.getConfig(e, silo1).maxLtvOracle;
        address silo1SolvencyOracle = siloConfig.getConfig(e, silo1).solvencyOracle;

        //oracle addresses are different
        require(silo0MaxLtvOracle != silo0SolvencyOracle);
        require(silo0MaxLtvOracle != silo1MaxLtvOracle);
        require(silo0MaxLtvOracle != silo1SolvencyOracle);
        require(silo0MaxLtvOracle != otherOracle);
        require(silo0SolvencyOracle != silo1MaxLtvOracle);
        require(silo0SolvencyOracle != silo1SolvencyOracle);
        require(silo0SolvencyOracle != otherOracle);
        require(silo1MaxLtvOracle != silo1SolvencyOracle);
        require(silo1MaxLtvOracle != otherOracle);
        require(silo1SolvencyOracle != otherOracle);
    }
//---------------------- METHODES, FUNCTIONS, GHOSTS END----------------------


//------------------------------- RULES TEST START ----------------------------------    
    


//------------------------------- RULES TEST END ----------------------------------

//------------------------------- RULES PROBLEMS START ----------------------------------
//  // transitionCollateral() call to collateralSolvancyOracle and debtSolvalncyOracle if collateralSolvancyOracle != 0 (collateralSilo = silo0) (with requirements) //@audit-issue did pass but does not pass anymore
//     rule callToSolvencyOraclesIfSolvencyOraclesNot0TRANSITION(env e){
//         uint256 shares;
//         address owner;
//         ISilo.CollateralType transitionType;
//         address anyOracle;
//         address debtSilo = siloConfig.getDebtSilo(e, owner);
//         address collateralSilo = siloConfig.borrowerCollateralSilo(e, owner);
//         require(collateralSilo == silo0);
//         require(debtSilo == silo1);

//         address collateralSolvencyOracle = siloConfig.getConfig(e, collateralSilo).solvencyOracle;
//         address debtSolvencyOracle = siloConfig.getConfig(e, debtSilo).solvencyOracle;
//         require(collateralSolvencyOracle != 0);
//         require(debtSolvencyOracle != 0);

//         //debtShare owner
//         address debtShareToken = siloConfig.getConfig(e, debtSilo).debtShareToken;
//         uint256 ownerBalanceDebtShareToken = debtShareToken.balanceOf(e, owner);
//         require(ownerBalanceDebtShareToken != 0); //to reach getPositionValues

//         //borrowerDebtAssets owner
//         uint256 borrowerProtectedAssets;
//         uint256 borrowerDebtAssets;
//         uint256 borrowerCollateralAssets;
//         (borrowerProtectedAssets, borrowerCollateralAssets, borrowerDebtAssets) = 
//             assetsBorrowerForLTVHarness( 
//                 e,  
//                 siloConfig.getConfig(e, collateralSilo),
//                 siloConfig.getConfig(e, debtSilo),
//                 owner,  
//                 ISilo.OracleType.Solvency,
//                 ISilo.AccrueInterestInMemory.No
//             );
//         require(borrowerProtectedAssets != 0);
//         require(borrowerCollateralAssets != 0);
//         require(borrowerProtectedAssets + borrowerCollateralAssets < max_uint256 - 500); //prevent overflow
//         require(borrowerDebtAssets != 0);

//         //setup
//         solvencyOracleRulesSetup(e, anyOracle);

//         //values before
//         mathint debtSiloSolvencyOracleCountBefore = callCountQuote[debtSolvencyOracle];
//         mathint collateralSiloSolvencyOracleCountBefore = callCountQuote[collateralSolvencyOracle];
//         mathint anyOracleCountBefore = callCountQuote[anyOracle];

//         //function call
//         transitionCollateral(e, shares, owner, transitionType);

//         //values after
//         mathint debtSiloSolvencyOracleCountAfter = callCountQuote[debtSolvencyOracle];
//         mathint collateralSiloSolvencyOracleCountAfter = callCountQuote[collateralSolvencyOracle];
//         mathint anyOracleCountAfter = callCountQuote[anyOracle];

//         //no oracle is called before the quote
//         assert (debtSiloSolvencyOracleCountAfter == debtSiloSolvencyOracleCountBefore + 1);
//         assert (collateralSiloSolvencyOracleCountAfter == collateralSiloSolvencyOracleCountBefore + 1);
//         assert (anyOracleCountAfter == anyOracleCountBefore);
//     }
    
    // // withdraw() no call to solvancyOracles if debtShareBalance of owner is 0 //@audit-issue sanity failed, not sure why
    // rule noCallToSolvencyOraclesIfDebtShareBalance0(env e){
    //     configForEightTokensSetupRequirements();
    //     uint256 assets;
    //     address receiver;
    //     address owner;
    //     address anyOracle;
    //     address debtSilo = siloConfig.getDebtSilo(e, owner);
    //     address collateralSilo = siloConfig.borrowerCollateralSilo(e, owner);
        
    //     address debtSiloSolvencyOracle = siloConfig.getConfig(e, debtSilo).solvencyOracle;
    //     address collateralSiloSolvencyOracle = siloConfig.getConfig(e, collateralSilo).solvencyOracle;

    //     //debtShare owner
    //     address debtShareToken = siloConfig.getConfig(e, debtSilo).debtShareToken;
    //     uint256 ownerBalanceDebtShareToken = debtShareToken.balanceOf(e, owner);
    //     // require(ownerBalanceDebtShareToken == 0); //@audit-issue Commented out to see if sanity works => this is the reason for sanity failure

    //     //values before
    //     mathint countBefore = callCountQuote[anyOracle];

    //     //function call
    //     withdraw(e, assets, receiver, owner);

    //     satisfy(true); ////@audit-issue is the call even possible?

    //     // //values after
    //     // mathint countAfter = callCountQuote[anyOracle];

    //     // //no oracle is called before the quote
    //     // assert (countAfter == countBefore);
    // }
    
    // // withdraw() no call to solvancyOracles if borrowerDebtAssets of owner is 0 //@audit-issue sanity failed, not sure why
    // rule noCallToSolvencyOraclesIfBorrowerDebtAssets0(env e){
    //     configForEightTokensSetupRequirements();
    //     uint256 assets;
    //     address receiver;
    //     address owner;
    //     address anyOracle;
    //     address debtSilo = siloConfig.getDebtSilo(e, owner);
    //     address collateralSilo = siloConfig.borrowerCollateralSilo(e, owner);
    //     require(debtSilo == silo0 || debtSilo == silo1 || debtSilo == 0);
    //     require(collateralSilo == silo0 || collateralSilo == silo1 || collateralSilo == 0); 
        
    //     address debtSiloSolvencyOracle = siloConfig.getConfig(e, debtSilo).solvencyOracle;
    //     address collateralSiloSolvencyOracle = siloConfig.getConfig(e, collateralSilo).solvencyOracle;

    //     //borrowerDebtAssets owner
    //     uint256 borrowerDebtAssets;
    //     (_, _, borrowerDebtAssets) = 
    //         assetsBorrowerForLTVHarness( 
    //             e,  
    //             siloConfig.getConfig(e, collateralSilo),
    //             siloConfig.getConfig(e, debtSilo),
    //             owner,  
    //             ISilo.OracleType.Solvency,
    //             ISilo.AccrueInterestInMemory.No
    //         );  
    //     require(borrowerDebtAssets == 0);

    //     //values before
    //     mathint countBefore = callCountQuote[anyOracle];

    //     //function call
    //     withdraw(e, assets, receiver, owner);

    //     //values after
    //     mathint countAfter = callCountQuote[anyOracle];

    //     //no oracle is called before the quote
    //     assert (countAfter == countBefore);
    // }
    
    // // withdraw() call only to collateralSolvancyOracle when collateralSolvancyOracle != 0 (collateralSilo = silo0) (with requirements) //@audit-issue sanity failed, not sure why
    // rule callToCollateralSolvencyOracleIfCollateralSolvencyOracleNot0(env e){
    //     uint256 assets;
    //     address receiver;
    //     address owner;
    //     address anyOracle;
    //     address debtSilo = siloConfig.getDebtSilo(e, owner);
    //     address collateralSilo = siloConfig.borrowerCollateralSilo(e, owner);
    //     require(collateralSilo == silo0);
    //     require(debtSilo != collateralSilo);

    //     address debtSiloSolvencyOracle = siloConfig.getConfig(e, debtSilo).solvencyOracle;
    //     address collateralSiloSolvencyOracle = siloConfig.getConfig(e, collateralSilo).solvencyOracle;
    //     require(debtSiloSolvencyOracle == 0);
    //     require(collateralSiloSolvencyOracle != 0);

    //     //debtShare owner
    //     address debtShareToken = siloConfig.getConfig(e, debtSilo).debtShareToken;
    //     uint256 ownerBalanceDebtShareToken = debtShareToken.balanceOf(e, owner);
    //     require(ownerBalanceDebtShareToken != 0);

    //     //borrowerDebtAssets owner
    //     uint256 borrowerProtectedAssets;
    //     uint256 borrowerDebtAssets;
    //     uint256 borrowerCollateralAssets;
    //     (borrowerProtectedAssets, borrowerCollateralAssets, borrowerDebtAssets)= 
    //         assetsBorrowerForLTVHarness( 
    //             e,  
    //             siloConfig.getConfig(e, collateralSilo),
    //             siloConfig.getConfig(e, debtSilo),
    //             owner,  
    //             ISilo.OracleType.Solvency,
    //             ISilo.AccrueInterestInMemory.No
    //         );
    //     require(borrowerDebtAssets != 0);
    //     //to ensuer that there are still collateral assest left after withdraw
    //     require(borrowerProtectedAssets != 0); 
    //     require(borrowerCollateralAssets != 0);
    //     require(borrowerProtectedAssets + borrowerCollateralAssets != 0);

    //     //setup
    //     allOraclesDifferent(e, anyOracle);

    //     //values before
    //     mathint debtSiloSolvencyOracleCountBefore = callCountQuote[debtSiloSolvencyOracle];
    //     mathint collateralSiloSolvencyOracleCountBefore = callCountQuote[collateralSiloSolvencyOracle];
    //     mathint anyOracleCountBefore = callCountQuote[anyOracle];

    //     //function call
    //     withdraw(e, assets, receiver, owner);

    //     //values after
    //     mathint debtSiloSolvencyOracleCountAfter = callCountQuote[debtSiloSolvencyOracle];
    //     mathint collateralSiloSolvencyOracleCountAfter = callCountQuote[collateralSiloSolvencyOracle];
    //     mathint anyOracleCountAfter = callCountQuote[anyOracle];

    //     //no oracle is called before the quote
    //     assert (debtSiloSolvencyOracleCountAfter == debtSiloSolvencyOracleCountBefore);
    //     assert (collateralSiloSolvencyOracleCountAfter == collateralSiloSolvencyOracleCountBefore + 1);
    //     assert (anyOracleCountAfter == anyOracleCountBefore);
    // }


//------------------------------- RULES PROBLEMS START ----------------------------------

//------------------------------- RULES OK START ------------------------------------



    // withdraw() call only to debtSolvancyOracle when debtSolvancyOracle != 0 (collateralSilo = silo0) (with requirements)
    rule callToDebtSolvencyOracleIfDebtSolvencyOracleNot0(env e){
        uint256 assets;
        address receiver;
        address owner;
        address anyOracle;
        address debtSilo = siloConfig.getDebtSilo(e, owner);
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, owner);
        require(collateralSilo == silo0);
        require(debtSilo != collateralSilo);

        address debtSiloSolvencyOracle = siloConfig.getConfig(e, debtSilo).solvencyOracle;
        address collateralSiloSolvencyOracle = siloConfig.getConfig(e, collateralSilo).solvencyOracle;
        require(debtSiloSolvencyOracle != 0);
        require(collateralSiloSolvencyOracle == 0);

        //debtShare owner
        address debtShareToken = siloConfig.getConfig(e, debtSilo).debtShareToken;
        uint256 ownerBalanceDebtShareToken = debtShareToken.balanceOf(e, owner);
        require(ownerBalanceDebtShareToken != 0);

        //borrowerDebtAssets owner
        uint256 borrowerProtectedAssets;
        uint256 borrowerDebtAssets;
        uint256 borrowerCollateralAssets;
        (borrowerProtectedAssets, borrowerCollateralAssets, borrowerDebtAssets)= 
            assetsBorrowerForLTVHarness( 
                e,  
                siloConfig.getConfig(e, collateralSilo),
                siloConfig.getConfig(e, debtSilo),
                owner,  
                ISilo.OracleType.Solvency,
                ISilo.AccrueInterestInMemory.No
            );
        require(borrowerDebtAssets != 0);
        //to ensuer that there are still collateral assest left after withdraw
        require(borrowerProtectedAssets != 0); 
        require(borrowerCollateralAssets != 0);
        require(borrowerProtectedAssets + borrowerCollateralAssets != 0);

        //setup
        allOraclesDifferent(e, anyOracle);

        //values before
        mathint debtSiloSolvencyOracleCountBefore = callCountQuote[debtSiloSolvencyOracle];
        mathint collateralSiloSolvencyOracleCountBefore = callCountQuote[collateralSiloSolvencyOracle];
        mathint anyOracleCountBefore = callCountQuote[anyOracle];

        //function call
        withdraw(e, assets, receiver, owner);

        //values after
        mathint debtSiloSolvencyOracleCountAfter = callCountQuote[debtSiloSolvencyOracle];
        mathint collateralSiloSolvencyOracleCountAfter = callCountQuote[collateralSiloSolvencyOracle];
        mathint anyOracleCountAfter = callCountQuote[anyOracle];

        //no oracle is called before the quote
        assert (debtSiloSolvencyOracleCountAfter == debtSiloSolvencyOracleCountBefore + 1);
        assert (collateralSiloSolvencyOracleCountAfter == collateralSiloSolvencyOracleCountBefore);
        assert (anyOracleCountAfter == anyOracleCountBefore);
    }

   

    //switchCollateralToThisSilo() call to collateralSolvancyOracle newCollateralSolvancyOracle != 0 (with requirements)
    rule callToCollateralSolvencyOraclesIfCollateralSolvencyOraclesNot0SWITCHCOLLATERAL(env e){
        configForEightTokensSetupRequirements();
        address sender = e.msg.sender;
        address anyOracle;
        address debtSilo = siloConfig.getDebtSilo(e, sender);
        require(debtSilo == silo1);
        address collateralSiloBefore = siloConfig.borrowerCollateralSilo(e, sender);
        require(collateralSiloBefore == silo1);
        address collateralSiloAfter = silo0;

        address debtSiloSolvencyOracle = siloConfig.getConfig(e, debtSilo).solvencyOracle;
        address collateralAfterSolvencyOracle = siloConfig.getConfig(e, collateralSiloAfter).solvencyOracle;
        require(collateralAfterSolvencyOracle != 0);
        require(debtSiloSolvencyOracle == 0);

        //setup
        solvencyOracleRulesSetup(e, anyOracle);
        address debtShareToken = siloConfig.getConfig(e, debtSilo).debtShareToken;
        uint256 senderBalanceDebtShareToken = debtShareToken.balanceOf(e, sender);
        require(senderBalanceDebtShareToken != 0); //to reach getPositionValues

        uint256 borrowerProtectedAssetsAfter;
        uint256 borrowerCollateralAssetsAfter;
        uint256 borrowerDebtAssets;
        (borrowerProtectedAssetsAfter, borrowerCollateralAssetsAfter, borrowerDebtAssets) = 
            assetsBorrowerForLTVHarness( 
                e,  
                siloConfig.getConfig(e, collateralSiloAfter),
                siloConfig.getConfig(e, debtSilo),
                sender,  
                ISilo.OracleType.Solvency,
                ISilo.AccrueInterestInMemory.No
            );
        require(borrowerProtectedAssetsAfter != 0);
        require(borrowerCollateralAssetsAfter != 0);
        require(borrowerProtectedAssetsAfter + borrowerCollateralAssetsAfter < max_uint256 - 500); //prevent overflow
        require(borrowerDebtAssets != 0);

        //values before
        mathint debtSiloSolvencyOracleCountBefore = callCountQuote[debtSiloSolvencyOracle];
        mathint collateralSiloSolvencyOracleCountBefore = callCountQuote[collateralAfterSolvencyOracle];
        mathint anyOracleCountBefore = callCountQuote[anyOracle];

        //function call
        switchCollateralToThisSilo(e);

        //values after
        mathint debtSiloSolvencyOracleCountAfter = callCountQuote[debtSiloSolvencyOracle];
        mathint collateralSiloSolvencyOracleCountAfter = callCountQuote[collateralAfterSolvencyOracle];
        mathint anyOracleCountAfter = callCountQuote[anyOracle];

        //no oracle is called before the quote
        assert (debtSiloSolvencyOracleCountAfter == debtSiloSolvencyOracleCountBefore);
        assert (collateralSiloSolvencyOracleCountAfter == collateralSiloSolvencyOracleCountBefore + 1);
        assert (anyOracleCountAfter == anyOracleCountBefore);
    }

    //switchCollateralToThisSilo() call to debtSolvancyOracle debtSolvancyOracle != 0 (with requirements)
    rule callToDebtSolvencyOraclesIfDebtSolvencyOraclesNot0SWITCHCOLLATERAL(env e){
        configForEightTokensSetupRequirements();
        address sender = e.msg.sender;
        address anyOracle;
        address debtSilo = siloConfig.getDebtSilo(e, sender);
        require(debtSilo == silo1);
        address collateralSiloBefore = siloConfig.borrowerCollateralSilo(e, sender);
        require(collateralSiloBefore == silo1);
        address collateralSiloAfter = silo0;

        address debtSiloSolvencyOracle = siloConfig.getConfig(e, debtSilo).solvencyOracle;
        address collateralAfterSolvencyOracle = siloConfig.getConfig(e, collateralSiloAfter).solvencyOracle;
        require(collateralAfterSolvencyOracle == 0);
        require(debtSiloSolvencyOracle != 0);

        //setup
        solvencyOracleRulesSetup(e, anyOracle);
        address debtShareToken = siloConfig.getConfig(e, debtSilo).debtShareToken;
        uint256 senderBalanceDebtShareToken = debtShareToken.balanceOf(e, sender);
        require(senderBalanceDebtShareToken != 0); //to reach getPositionValues

        uint256 borrowerProtectedAssetsAfter;
        uint256 borrowerCollateralAssetsAfter;
        uint256 borrowerDebtAssets;
        (borrowerProtectedAssetsAfter, borrowerCollateralAssetsAfter, borrowerDebtAssets) = 
            assetsBorrowerForLTVHarness( 
                e,  
                siloConfig.getConfig(e, collateralSiloAfter),
                siloConfig.getConfig(e, debtSilo),
                sender,  
                ISilo.OracleType.Solvency,
                ISilo.AccrueInterestInMemory.No
            );
        require(borrowerProtectedAssetsAfter != 0);
        require(borrowerCollateralAssetsAfter != 0);
        require(borrowerProtectedAssetsAfter + borrowerCollateralAssetsAfter < max_uint256 - 500); //prevent overflow
        require(borrowerDebtAssets != 0);

        //values before
        mathint debtSiloSolvencyOracleCountBefore = callCountQuote[debtSiloSolvencyOracle];
        mathint collateralSiloSolvencyOracleCountBefore = callCountQuote[collateralAfterSolvencyOracle];
        mathint anyOracleCountBefore = callCountQuote[anyOracle];

        //function call
        switchCollateralToThisSilo(e);

        //values after
        mathint debtSiloSolvencyOracleCountAfter = callCountQuote[debtSiloSolvencyOracle];
        mathint collateralSiloSolvencyOracleCountAfter = callCountQuote[collateralAfterSolvencyOracle];
        mathint anyOracleCountAfter = callCountQuote[anyOracle];

        //no oracle is called before the quote
        assert (debtSiloSolvencyOracleCountAfter == debtSiloSolvencyOracleCountBefore + 1);
        assert (collateralSiloSolvencyOracleCountAfter == collateralSiloSolvencyOracleCountBefore);
        assert (anyOracleCountAfter == anyOracleCountBefore);
    }

    //switchCollateralToThisSilo() call to collateralSolvancyOracle and debtSolvalncyOracle if collateralSolvancyOracle != 0 (collateralSilo = silo0) (with requirements)
    rule callToSolvencyOraclesIfSolvencyOraclesNot0SWITCHCOLLATERAL(env e){
        configForEightTokensSetupRequirements();
        address sender = e.msg.sender;
        address anyOracle;
        address debtSilo = siloConfig.getDebtSilo(e, sender);
        require(debtSilo == silo1);
        address collateralSiloBefore = siloConfig.borrowerCollateralSilo(e, sender);
        require(collateralSiloBefore == silo1);
        address collateralSiloAfter = silo0;

        address debtSiloSolvencyOracle = siloConfig.getConfig(e, debtSilo).solvencyOracle;
        address collateralAfterSolvencyOracle = siloConfig.getConfig(e, collateralSiloAfter).solvencyOracle;
        require(collateralAfterSolvencyOracle != 0);
        require(debtSiloSolvencyOracle != 0);

        //setup
        solvencyOracleRulesSetup(e, anyOracle);
        address debtShareToken = siloConfig.getConfig(e, debtSilo).debtShareToken;
        uint256 senderBalanceDebtShareToken = debtShareToken.balanceOf(e, sender);
        require(senderBalanceDebtShareToken != 0); //to reach getPositionValues

        uint256 borrowerProtectedAssetsAfter;
        uint256 borrowerCollateralAssetsAfter;
        uint256 borrowerDebtAssets;
        (borrowerProtectedAssetsAfter, borrowerCollateralAssetsAfter, borrowerDebtAssets) = 
            assetsBorrowerForLTVHarness( 
                e,  
                siloConfig.getConfig(e, collateralSiloAfter),
                siloConfig.getConfig(e, debtSilo),
                sender,  
                ISilo.OracleType.Solvency,
                ISilo.AccrueInterestInMemory.No
            );
        require(borrowerProtectedAssetsAfter != 0);
        require(borrowerCollateralAssetsAfter != 0);
        require(borrowerProtectedAssetsAfter + borrowerCollateralAssetsAfter < max_uint256 - 500); //prevent overflow
        require(borrowerDebtAssets != 0);

        //values before
        mathint debtSiloSolvencyOracleCountBefore = callCountQuote[debtSiloSolvencyOracle];
        mathint collateralSiloSolvencyOracleCountBefore = callCountQuote[collateralAfterSolvencyOracle];
        mathint anyOracleCountBefore = callCountQuote[anyOracle];

        //function call
        switchCollateralToThisSilo(e);

        //values after
        mathint debtSiloSolvencyOracleCountAfter = callCountQuote[debtSiloSolvencyOracle];
        mathint collateralSiloSolvencyOracleCountAfter = callCountQuote[collateralAfterSolvencyOracle];
        mathint anyOracleCountAfter = callCountQuote[anyOracle];

        //no oracle is called before the quote
        assert (debtSiloSolvencyOracleCountAfter == debtSiloSolvencyOracleCountBefore + 1);
        assert (collateralSiloSolvencyOracleCountAfter == collateralSiloSolvencyOracleCountBefore + 1);
        assert (anyOracleCountAfter == anyOracleCountBefore);
    }

    // withdraw() call to collateralSolvancyOracle and debtSolvalncyOracle if oracles != 0 (with requirements)
    rule callToSolvencyOraclesIfSolvencyOracleNot0WITHDRAW(env e){
        uint256 assets;
        address receiver;
        address owner;
        address anyOracle;
        address debtSilo = siloConfig.getDebtSilo(e, owner);
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, owner);
        require(collateralSilo == silo0);
        require(debtSilo != collateralSilo);

        address debtSiloSolvencyOracle = siloConfig.getConfig(e, debtSilo).solvencyOracle;
        address collateralSiloSolvencyOracle = siloConfig.getConfig(e, collateralSilo).solvencyOracle;
        require(debtSiloSolvencyOracle != 0);
        require(collateralSiloSolvencyOracle != 0);

        //debtShare owner
        address debtShareToken = siloConfig.getConfig(e, debtSilo).debtShareToken;
        uint256 ownerBalanceDebtShareToken = debtShareToken.balanceOf(e, owner);
        require(ownerBalanceDebtShareToken != 0);

        //borrowerDebtAssets owner
        uint256 borrowerProtectedAssets;
        uint256 borrowerDebtAssets;
        uint256 borrowerCollateralAssets;
        (borrowerProtectedAssets, borrowerCollateralAssets, borrowerDebtAssets)= 
            assetsBorrowerForLTVHarness( 
                e,  
                siloConfig.getConfig(e, collateralSilo),
                siloConfig.getConfig(e, debtSilo),
                owner,  
                ISilo.OracleType.Solvency,
                ISilo.AccrueInterestInMemory.No
            );
        require(borrowerDebtAssets != 0);
        //to ensuer that there are still collateral assest left after withdraw
        require(borrowerProtectedAssets != 0); 
        require(borrowerCollateralAssets != 0);
        require(borrowerProtectedAssets + borrowerCollateralAssets != 0);

        //setup
        allOraclesDifferent(e, anyOracle);

        //values before
        mathint debtSiloSolvencyOracleCountBefore = callCountQuote[debtSiloSolvencyOracle];
        mathint collateralSiloSolvencyOracleCountBefore = callCountQuote[collateralSiloSolvencyOracle];
        mathint anyOracleCountBefore = callCountQuote[anyOracle];

        //function call
        withdraw(e, assets, receiver, owner);

        //values after
        mathint debtSiloSolvencyOracleCountAfter = callCountQuote[debtSiloSolvencyOracle];
        mathint collateralSiloSolvencyOracleCountAfter = callCountQuote[collateralSiloSolvencyOracle];
        mathint anyOracleCountAfter = callCountQuote[anyOracle];

        //no oracle is called before the quote
        assert (debtSiloSolvencyOracleCountAfter == debtSiloSolvencyOracleCountBefore + 1);
        assert (collateralSiloSolvencyOracleCountAfter == collateralSiloSolvencyOracleCountBefore + 1);
        assert (anyOracleCountAfter == anyOracleCountBefore);
    }

    //switchCollateralToThisSilo() no call to SolvancyOracle if newCollateralSilo == debtSilo
    rule noCallToSolvencyOraclesIfDebtSiloEqualCollateralSiloAfterSWITCHCOLLATERAL(env e){
        configForEightTokensSetupRequirements();
        address sender = e.msg.sender;
        address anyOracle;
        address debtSilo = siloConfig.getDebtSilo(e, sender);
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, sender);
        require(debtSilo == silo0 && collateralSilo == silo1);

        //values before
        mathint countBefore = callCountQuote[anyOracle];

        //function call
        switchCollateralToThisSilo(e);

        //values after
        mathint countAfter = callCountQuote[anyOracle];

        //no oracle is called before the quote
        assert (countAfter == countBefore);
    }

        //switchCollateralToThisSilo() no call to SolvancyOracle if debtSilo == 0
    rule noCallToSolvencyOraclesIfDebtSiloEqualZeroSWITCHCOLLATERAL(env e){
        configForEightTokensSetupRequirements();
        address sender = e.msg.sender;
        address anyOracle;
        address debtSilo = siloConfig.getDebtSilo(e, sender);
        require(debtSilo == 0);
        
        //values before
        mathint countBefore = callCountQuote[anyOracle];

        //function call
        switchCollateralToThisSilo(e);

        //values after
        mathint countAfter = callCountQuote[anyOracle];

        //no oracle is called before the quote
        assert (countAfter == countBefore);
    }

    // borrowSameAsset() maxLtvOracle quote never calls oracles becasue of same asset
    rule maxLtvCallQuoteIfOraclesSetSameAsset(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address borrower;
        address anyOracle;
        address debtSilo = siloConfig.getDebtSilo(e, borrower);
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, borrower);
        // require(debtSilo == silo0);
        // require(collateralSilo == silo0);
        // totalSuppliesMoreThanThreeBalances(e, debtSilo, collateralSilo, borrower); //i: added

        // address debtSiloMaxLtvOracle = siloConfig.getConfig(e, debtSilo).maxLtvOracle;
        // address collateralSiloMaxLtvOracle = siloConfig.getConfig(e, collateralSilo).maxLtvOracle;
        // require(debtSiloMaxLtvOracle != 0);
        // require(collateralSiloMaxLtvOracle != 0);

        // uint256 borrowerProtectedAssets;
        // uint256 borrowerCollateralAssets;
        // uint256 borrowerDebtAssets;
        // (borrowerProtectedAssets, borrowerCollateralAssets,borrowerDebtAssets) = //returns: 2 , 0 , 7
        //     assetsBorrowerForLTVHarness( 
        //         e,  
        //         siloConfig.getConfig(e, collateralSilo),
        //         siloConfig.getConfig(e, debtSilo),
        //         borrower,  
        //         ISilo.OracleType.Solvency,
        //         ISilo.AccrueInterestInMemory.No
        //     );
        // require(borrowerProtectedAssets + borrowerCollateralAssets > 0);
        // require(borrowerDebtAssets > 0);
        // require(borrowDebtAsset + assets < max_uint256)

        // //setup
        // maxLtvOracleRulesSetup(e, anyOracle);

        //values before
        // address shareDebtTokenSilo0 = siloConfig.getConfig(e, silo0).debtShareToken;
        // uint256 borrowerBalanceDebtShareTokenBefore = shareDebtTokenSilo0.balanceOf(e, borrower);
        mathint otherOracleCountBefore = callCountQuote[anyOracle];
        // mathint debtSiloMaxLtvOracleCountBefore = callCountQuote[debtSiloMaxLtvOracle];
        // mathint collateralSiloMaxLtvOracleCountBefore = callCountQuote[collateralSiloMaxLtvOracle];

        //function call
        borrowSameAsset(e, assets, receiver, borrower);

        //values after
        // uint256 borrowerBalanceDebtShareTokenAfter = shareDebtTokenSilo0.balanceOf(e, borrower);
        // require(borrowerBalanceDebtShareTokenAfter >= borrowerBalanceDebtShareTokenBefore); //prevent overflow when minting debtShareToken
        mathint otherOraclecountAfter = callCountQuote[anyOracle];
        // mathint debtSiloMaxLtvOracleCountAfter = callCountQuote[debtSiloMaxLtvOracle];
        // mathint collateralSiloMaxLtvOracleCountAfter = callCountQuote[collateralSiloMaxLtvOracle];

        //no oracle is called before the quote
        // assert (debtSiloMaxLtvOracleCountAfter == debtSiloMaxLtvOracleCountBefore + 2); //becasue the oracel for debt and collatearl is the same
        // assert (collateralSiloMaxLtvOracleCountAfter == collateralSiloMaxLtvOracleCountBefore + 2); //becasue the oracel for debt and collatearl is the same
        assert (otherOracleCountBefore == otherOraclecountAfter);
    }

    // borrow() maxLtvOracle quote must be called if oracles !=  0 because after borrow one has collateral and debt assets
    rule maxLtvCallQuoteIfOraclesSetBorrow(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address borrower;
        address anyOracle;
        address debtSilo = siloConfig.getDebtSilo(e, borrower);
        require(debtSilo == silo0); //prevent cases where debtSilo changes during the function call
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, borrower);
        require(collateralSilo == silo1); //prevent cases where collateralSilo changes during the function call

        address debtSiloMaxLtvOracle = siloConfig.getConfig(e, debtSilo).maxLtvOracle;
        address collateralSiloMaxLtvOracle = siloConfig.getConfig(e, collateralSilo).maxLtvOracle;
        require(debtSiloMaxLtvOracle != 0);
        require(collateralSiloMaxLtvOracle != 0);

        //setup
        maxLtvOracleRulesSetup(e, anyOracle);

        //values before
        address shareDebtTokenSilo0 = siloConfig.getConfig(e, silo0).debtShareToken;
        uint256 borrowerBalanceDebtShareTokenBefore = shareDebtTokenSilo0.balanceOf(e, borrower);
        uint256 borrowerProtectedAssets;
        uint256 borrowerCollateralAssets;
        uint256 borrowerDebtAssets;
        (borrowerProtectedAssets, borrowerCollateralAssets,borrowerDebtAssets) = 
            assetsBorrowerForLTVHarness( 
                e,  
                siloConfig.getConfig(e, collateralSilo),
                siloConfig.getConfig(e, debtSilo),
                borrower,  
                ISilo.OracleType.Solvency,
                ISilo.AccrueInterestInMemory.No
            );
        require(borrowerProtectedAssets + borrowerCollateralAssets > 0);
        require(borrowerDebtAssets > 0);

        mathint otherOracleCountBefore = callCountQuote[anyOracle];
        mathint debtSiloMaxLtvOracleCountBefore = callCountQuote[debtSiloMaxLtvOracle];
        mathint collateralSiloMaxLtvOracleCountBefore = callCountQuote[collateralSiloMaxLtvOracle];

        //function call
        borrow(e, assets, receiver, borrower);

        //values after
        uint256 borrowerBalanceDebtShareTokenAfter = shareDebtTokenSilo0.balanceOf(e, borrower);
        require(borrowerBalanceDebtShareTokenAfter >= borrowerBalanceDebtShareTokenBefore); //prevent overflow when minting debtShareToken
        mathint countAfter = callCountQuote[anyOracle];
        mathint debtSiloMaxLtvOracleCountAfter = callCountQuote[debtSiloMaxLtvOracle];
        mathint collateralSiloMaxLtvOracleCountAfter = callCountQuote[collateralSiloMaxLtvOracle];

        //no oracle is called before the quote
        assert (debtSiloMaxLtvOracleCountAfter == debtSiloMaxLtvOracleCountBefore + 1);
        assert (collateralSiloMaxLtvOracleCountAfter == collateralSiloMaxLtvOracleCountBefore + 1);
        assert (otherOracleCountBefore == countAfter);
    }

    // switchCollateralToThisSilo() no call to collateralSolvancyOracles if debtSilo = 0
    rule noCallToSolvencyOraclesIfDebtSilo0SWITCHCOLLATERAL(env e){
        configForEightTokensSetupRequirements();
        address sender = e.msg.sender;
        address anyOracle;
        address debtSiloBefore = siloConfig.getDebtSilo(e, sender);
        require(debtSiloBefore == 0);


        //valeus before
        mathint countBefore = callCountQuote[anyOracle];
    
        //function call
        switchCollateralToThisSilo(e);

        //values after
        mathint countAfter = callCountQuote[anyOracle];

        //no oracle is called before the quote
        assert (countAfter == countBefore);
    }

    //only specific functions should call quote for solvencyOracle
    rule onlySpecificFunctionsCallQuoteSolvancyOracle(env e, method f, calldataarg args) 
            filtered{f-> !HARNESS_METHODS(f) &&
            f.selector != sig:decimals().selector &&
            f.selector != sig:flashLoan(address,address,uint256,bytes).selector

        } {
        address silo0SolvencyOracle = siloConfig.getConfig(e, silo0).solvencyOracle;
        address silo1SolvencyOracle = siloConfig.getConfig(e, silo1).solvencyOracle;
        address otherOracle;

        //setup
        allOraclesDifferent(e, otherOracle);

        //values before
        mathint silo0SolvencyOracleCountBefore = callCountQuote[silo0SolvencyOracle];
        mathint silo1SolvencyOracleCountBefore = callCountQuote[silo1SolvencyOracle];

        //function call
        f(e, args);

        //values after
        mathint silo0SolvencyOracleCountAfter = callCountQuote[silo0SolvencyOracle];
        mathint silo1SolvencyOracleCountAfter = callCountQuote[silo1SolvencyOracle];

        //only specific functions should call quote
        assert (silo0SolvencyOracleCountAfter != silo0SolvencyOracleCountBefore || silo1SolvencyOracleCountAfter != silo1SolvencyOracleCountBefore => 
                    f.selector != sig:transfer(address,uint256).selector ||
                    f.selector != sig:transferFrom(address,address,uint256).selector ||
                    f.selector != sig:withdraw(uint256,address,address).selector ||
                    f.selector != sig:withdraw(uint256,address,address,ISilo.CollateralType).selector ||
                    f.selector != sig:redeem(uint256,address,address).selector ||
                    f.selector != sig:redeem(uint256,address,address,ISilo.CollateralType).selector ||
                    f.selector != sig:switchCollateralToThisSilo().selector ||
                    f.selector != sig:isSolvent(address).selector ||
                    f.selector != sig:maxRedeem(address).selector ||
                    f.selector != sig:maxWithdraw(address).selector ||
                    f.selector != sig:maxBorrow(address).selector ||
                    f.selector != sig:maxBorrowShares(address).selector ||
                    f.selector != sig:maxRedeem(address,ISilo.CollateralType).selector ||
                    f.selector != sig:maxWithdraw(address,ISilo.CollateralType).selector ||
                    f.selector != sig:transitionCollateral(uint256,address,ISilo.CollateralType).selector
                );
    }

    // withdraw() no call to solvancyOracles if oracles are 0
    rule noCallToSolvencyOraclesIfOracles0(env e){
        uint256 assets;
        address receiver;
        address owner;
        address anyOracle;
        address debtSilo = siloConfig.getDebtSilo(e, owner);
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, owner);

        address debtSiloSolvencyOracle = siloConfig.getConfig(e, debtSilo).solvencyOracle;
        address collateralSiloSolvencyOracle = siloConfig.getConfig(e, collateralSilo).solvencyOracle;
        require(debtSiloSolvencyOracle == 0);
        require(collateralSiloSolvencyOracle == 0);

        //values before
        mathint countBefore = callCountQuote[anyOracle];

        //function call
        withdraw(e, assets, receiver, owner);

        //values after
        mathint countAfter = callCountQuote[anyOracle];

        //no oracle is called before the quote
        assert (countAfter == countBefore);
    }
    
    // withdraw() no call to solvancyOracles if collateralSilo != silo0
    rule noCallToSolvencyOraclesIfCollateralSiloNotSilo0(env e){
        uint256 assets;
        address receiver;
        address owner;
        address anyOracle;
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, owner);
        require(collateralSilo != silo0);

        //values before
        mathint countBefore = callCountQuote[anyOracle];

        //function call
        withdraw(e, assets, receiver, owner);

        //values after
        mathint countAfter = callCountQuote[anyOracle];

        //no oracle is called before the quote
        assert (countAfter == countBefore);
    }
        
    // onlySpecific functions should call the maxLTVOracle beforeQuote
    rule onlySpecificFunctionsCallMaxLtvOracleBeforeCall (env e, method f, calldataarg args) 
        filtered {f-> 
            !f.isView && 
            !HARNESS_METHODS(f) && 
            f.selector != sig:decimals().selector &&
            f.selector != sig:flashLoan(address,address,uint256,bytes).selector
    } {
        address silo0MaxLtvOracle = siloConfig.getConfig(e, silo0).maxLtvOracle;
        address silo1MaxLtvOracle = siloConfig.getConfig(e, silo1).maxLtvOracle;
        address otherOracle;

        //setup
        allOraclesDifferent(e, otherOracle);

        //valus before
        mathint silo0MaxLtvOracleCountBefore = callCountBeforeQuote[silo0MaxLtvOracle];
        mathint silo1MaxLtvOracleCountBefore = callCountBeforeQuote[silo1MaxLtvOracle];

        //function call
        f(e, args);

        //values after
        mathint silo0MaxLtvOracleCountAfter = callCountBeforeQuote[silo0MaxLtvOracle];
        mathint silo1MaxLtvOracleCountAfter = callCountBeforeQuote[silo1MaxLtvOracle];


        //only specific functions should call the maxLTVOracle
        assert (silo0MaxLtvOracleCountAfter != silo0MaxLtvOracleCountBefore || silo1MaxLtvOracleCountAfter != silo1MaxLtvOracleCountBefore => 
                    f.selector == sig:borrow(uint256,address,address).selector ||
                    f.selector == sig:borrowSameAsset(uint256,address,address).selector ||
                    f.selector == sig:borrowShares(uint256,address,address).selector
                );
    }

    // borrow() no quote call to maxLtvOracle (maxLTV oracles are 0)
    rule maxLtvNoCallQuoteIfOracles0Borrow(env e){
        uint256 assets;
        address receiver;
        address borrower;
        address anyOracle;
        address debtSilo = siloConfig.getDebtSilo(e, borrower);
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, borrower);
        require(collateralSilo == silo1); //prevent cases where collateralSilo changes during the function call

        address debtSiloMaxLtvOracle = siloConfig.getConfig(e, debtSilo).maxLtvOracle;
        address collateralSiloMaxLtvOracle = siloConfig.getConfig(e, collateralSilo).maxLtvOracle;
        require(debtSiloMaxLtvOracle == 0);
        require(collateralSiloMaxLtvOracle == 0);

        

        //values before
        mathint countBefore = callCountQuote[anyOracle];

        //function call
        borrow(e, assets, receiver, borrower);

        //values after
        mathint countAfter = callCountQuote[anyOracle];

        //no oracle is called before the quote
        assert (countAfter == countBefore);
    }


    //only specific functions should call quote for maxLtvOracle
    rule onlySpecificFunctionsCallQuoteMaxTvlOracle(env e, method f, calldataarg args) 
        filtered{f-> !HARNESS_METHODS(f) &&
                f.selector != sig:decimals().selector &&
                f.selector != sig:flashLoan(address,address,uint256,bytes).selector

            } {
        address silo0MaxLtvOracle = siloConfig.getConfig(e, silo0).maxLtvOracle;
        address silo1MaxLtvOracle = siloConfig.getConfig(e, silo1).maxLtvOracle;
        address otherOracle;

        //setup
        allOraclesDifferent(e, otherOracle);

        //values before
        mathint silo0MaxLtvOracleCountBefore = callCountQuote[silo0MaxLtvOracle];
        mathint silo1MaxLtvOracleCountBefore = callCountQuote[silo1MaxLtvOracle];

        //function call
        f(e, args);

        //values after
        mathint silo0MaxLtvOracleCountAfter = callCountQuote[silo0MaxLtvOracle];
        mathint silo1MaxLtvOracleCountAfter = callCountQuote[silo1MaxLtvOracle];

        //only specific functions should call quote
        assert (silo0MaxLtvOracleCountAfter != silo0MaxLtvOracleCountBefore || silo1MaxLtvOracleCountAfter != silo1MaxLtvOracleCountBefore => 
                    f.selector != sig:borrowShares(uint256,address,address).selector ||
                    f.selector != sig:borrowSameAsset(uint256,address,address).selector ||
                    f.selector != sig:borrow(uint256,address,address).selector
                );
    }

    rule onlySolvencyOraclesCalledBeforeQuote(env e) {
        uint256 assets;
        address receiver;
        address owner;
        address otherOracle;
        address debtSilo = siloConfig.getDebtSilo(e, owner);
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, owner);
        require(collateralSilo == silo0);
        require(debtSilo != collateralSilo);

        address debtSiloSolvencyOracle = siloConfig.getConfig(e, debtSilo).solvencyOracle;
        address collateralSiloSolvencyOracle = siloConfig.getConfig(e, collateralSilo).solvencyOracle;
        bool debtSiloCallBeforeQuote = siloConfig.getConfig(e, debtSilo).callBeforeQuote;
        bool collateralSiloCallBeforeQuote = siloConfig.getConfig(e, collateralSilo).callBeforeQuote;
        require(debtSiloSolvencyOracle != 0 && collateralSiloSolvencyOracle != 0);
        require(debtSiloCallBeforeQuote == true && collateralSiloCallBeforeQuote == true);
        
        //setup
        allOraclesDifferent(e, otherOracle);

        //values before
        mathint debtSiloSolvencyOracleCountBefore = callCountBeforeQuote[debtSiloSolvencyOracle];
        mathint collateralSiloSolvencyOracleCountBefore = callCountBeforeQuote[collateralSiloSolvencyOracle];
        mathint otherOracleCountBefore = callCountBeforeQuote[otherOracle];

        //function call
        withdraw(e, assets, receiver, owner);

        //values after
        mathint debtSiloSolvencyOracleCountAfter = callCountBeforeQuote[debtSiloSolvencyOracle];
        mathint collateralSiloSolvencyOracleCountAfter = callCountBeforeQuote[collateralSiloSolvencyOracle];
        mathint otherOracleCountAfter = callCountBeforeQuote[otherOracle];

        //only the solvancyOracles are called once before the quote
        assert (debtSiloSolvencyOracleCountAfter == debtSiloSolvencyOracleCountBefore + 1);
        assert (collateralSiloSolvencyOracleCountAfter == collateralSiloSolvencyOracleCountBefore + 1);
        assert (otherOracleCountAfter == otherOracleCountBefore);
    }

    //borrowSameAsset() no quote call to maxLtvOracle (maxLTV oracles are 0)
    rule maxLtvNoCallQuoteIfOracles0SameAsset(env e){
        uint256 assets;
        address receiver;
        address borrower;
        address anyOracle;
        address debtSilo = siloConfig.getDebtSilo(e, borrower);
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, borrower);

        address debtSiloMaxLtvOracle = siloConfig.getConfig(e, debtSilo).maxLtvOracle;
        address collateralSiloMaxLtvOracle = siloConfig.getConfig(e, collateralSilo).maxLtvOracle;
        require(debtSiloMaxLtvOracle == 0);
        require(collateralSiloMaxLtvOracle == 0);

        //values before
        mathint countBefore = callCountQuote[anyOracle];

        //function call
        borrowSameAsset(e, assets, receiver, borrower);

        //values after
        mathint countAfter = callCountQuote[anyOracle];

        //no oracle is called before the quote
        assert (countAfter == countBefore);
    }

    // onlySpecific functions should call the solvancyOracle beforeQuote
    rule onlySpecificFunctionsCallSolvalcyOracleBeforeQuote(env e, method f, calldataarg args) 
        filtered {f-> 
            !HARNESS_METHODS(f) && 
            f.selector != sig:decimals().selector &&
            f.selector != sig:flashLoan(address,address,uint256,bytes).selector
            } {
        address silo0SolvencyOracle = siloConfig.getConfig(e, silo0).solvencyOracle;
        address silo1SolvencyOracle = siloConfig.getConfig(e, silo1).solvencyOracle;
        address otherOracle;

        //setup
        allOraclesDifferent(e, otherOracle);

        //valus before
        mathint silo0SolvencyOracleCountBefore = callCountBeforeQuote[silo0SolvencyOracle];
        mathint silo1SolvencyOracleCountBefore = callCountBeforeQuote[silo1SolvencyOracle];

        //function call
        f(e, args);

        //values after
        mathint silo0SolvencyOracleCountAfter = callCountBeforeQuote[silo0SolvencyOracle];
        mathint silo1SolvencyOracleCountAfter = callCountBeforeQuote[silo1SolvencyOracle];

        //only specific functions should call the solvancyOracle
        assert (silo0SolvencyOracleCountAfter > silo0SolvencyOracleCountBefore || silo1SolvencyOracleCountAfter > silo1SolvencyOracleCountBefore => 
                    f.selector == sig:redeem(uint256,address,address).selector ||
                    f.selector == sig:redeem(uint256,address,address, ISilo.CollateralType).selector ||
                    f.selector == sig:withdraw(uint256,address,address).selector ||
                    f.selector == sig:withdraw(uint256,address,address, ISilo.CollateralType).selector ||
                    f.selector == sig:transitionCollateral(uint256,address,ISilo.CollateralType).selector ||
                    f.selector == sig:switchCollateralToThisSilo().selector ||
                    f.selector == sig:transfer(address,uint256).selector ||
                    f.selector == sig:transferFrom(address,address,uint256).selector ||
                    f.selector == sig:mint(uint256,address).selector ||
                    f.selector == sig:mint(address,address,uint256).selector ||
                    f.selector == sig:burn(address,address,uint256).selector

                );
    }

    // withdraw() if solvancyOracle != 0 && _config.callBeforeQuote == true for debtSilo, no oracle is called before the quote (only collateralSilo is checked)
    rule onlySolvencyOracleDebtSiloCalledBeforeQuote(env e) {
        uint256 assets;
        address receiver;
        address owner;
        address otherOracle;
        address debtSilo = siloConfig.getDebtSilo(e, owner);
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, owner);
        require(collateralSilo == silo0);
        require(debtSilo != collateralSilo);

        address debtSiloSolvencyOracle = siloConfig.getConfig(e, debtSilo).solvencyOracle;
        address collateralSiloSolvencyOracle = siloConfig.getConfig(e, collateralSilo).solvencyOracle;
        bool debtSiloCallBeforeQuote = siloConfig.getConfig(e, debtSilo).callBeforeQuote;
        bool collateralSiloCallBeforeQuote = siloConfig.getConfig(e, collateralSilo).callBeforeQuote;
        require(debtSiloSolvencyOracle != 0 && collateralSiloSolvencyOracle == 0);
        require(debtSiloCallBeforeQuote == true && collateralSiloCallBeforeQuote == false);
        
        //setup
        solvencyOracleRulesSetup(e, otherOracle);

        //values before
        mathint debtSiloSolvencyOracleCountBefore = callCountBeforeQuote[debtSiloSolvencyOracle];
        mathint collateralSiloSolvencyOracleCountBefore = callCountBeforeQuote[collateralSiloSolvencyOracle];
        mathint otherOracleCountBefore = callCountBeforeQuote[otherOracle];


        //function call
        withdraw(e, assets, receiver, owner);

        //values after
        mathint debtSiloSolvencyOracleCountAfter = callCountBeforeQuote[debtSiloSolvencyOracle];
        mathint collateralSiloSolvencyOracleCountAfter = callCountBeforeQuote[collateralSiloSolvencyOracle];
        mathint otherOracleCountAfter = callCountBeforeQuote[otherOracle];

        //only the solvancyOracles are called once before the quote
        assert (debtSiloSolvencyOracleCountAfter == debtSiloSolvencyOracleCountBefore +1);
        assert (collateralSiloSolvencyOracleCountAfter == collateralSiloSolvencyOracleCountBefore);
        assert (otherOracleCountAfter == otherOracleCountBefore);
    }

    // withdraw() if solvancyOracle != 0 && _config.callBeforeQuote == true for collateralSilo, only the solvancyOracle of collateralSilo is called once before the quote
    rule onlySolvencyOracleCollateralSiloCalledBeforeQuote(env e) {
        uint256 assets;
        address receiver;
        address owner;
        address otherOracle;
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, owner);
        address debtSilo = siloConfig.getDebtSilo(e, owner);
        require(collateralSilo == silo0);
        require(collateralSilo != debtSilo);

        address collateralSiloSolvencyOracle = siloConfig.getConfig(e, collateralSilo).solvencyOracle;
        address debtSiloSolvencyOracle = siloConfig.getConfig(e, debtSilo).solvencyOracle;
        bool collateralSiloCallBeforeQuote = siloConfig.getConfig(e, collateralSilo).callBeforeQuote;
        bool debtSiloCallBeforeQuote = siloConfig.getConfig(e, debtSilo).callBeforeQuote;
        require(collateralSiloSolvencyOracle != 0 && debtSiloSolvencyOracle == 0);
        require(collateralSiloCallBeforeQuote == true && debtSiloCallBeforeQuote == false);

        //setup
        solvencyOracleRulesSetup(e, otherOracle);

        //values before
        mathint collateralSiloSolvencyOracleCountBefore = callCountBeforeQuote[collateralSiloSolvencyOracle];
        mathint debtSiloSolvencyOracleCountBefore = callCountBeforeQuote[debtSiloSolvencyOracle];
        mathint otherOracleCountBefore = callCountBeforeQuote[otherOracle];

        //function call
        withdraw(e, assets, receiver, owner);

        //values after
        mathint collateralSiloSolvencyOracleCountAfter = callCountBeforeQuote[collateralSiloSolvencyOracle];
        mathint debtSiloSolvencyOracleCountAfter = callCountBeforeQuote[debtSiloSolvencyOracle];
        mathint otherOracleCountAfter = callCountBeforeQuote[otherOracle];

        //only the solvancyOracles are called once before the quote
        assert (collateralSiloSolvencyOracleCountAfter == collateralSiloSolvencyOracleCountBefore + 1);
        assert (debtSiloSolvencyOracleCountAfter == debtSiloSolvencyOracleCountBefore);
        assert (otherOracleCountAfter == otherOracleCountBefore);
    }
       
    //withdwar() if collateralSilo != silo0 no oracle is called before the quote
    rule noCallBeforeIfCollateralSiloNotSilo0(env e){
        uint256 assets;
        address receiver;
        address owner;
        address anyOracle;
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, owner);
        require(collateralSilo != silo0);

        //values before
        mathint countBefore = callCountBeforeQuote[anyOracle];

        //function call
        withdraw(e, assets, receiver, owner);

        //values after
        mathint countAfter = callCountBeforeQuote[anyOracle];

        //no oracle is called before the quote
        assert (countAfter == countBefore);
    }

    // withdraw() if  _config.solvencyOracle == address(0) no oracle is called before the quote
    rule noCallBeforeIfSolvencyOracles0(env e){
        uint256 assets;
        address receiver;
        address owner;
        address anyOracle;
        address debtSilo = siloConfig.getDebtSilo(e, owner);
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, owner);
        require(debtSilo != collateralSilo);

        address debtSiloSolvencyOracle = siloConfig.getConfig(e, debtSilo).solvencyOracle;
        address collateralSiloSolvencyOracle = siloConfig.getConfig(e, collateralSilo).solvencyOracle;
        require(debtSiloSolvencyOracle == 0);
        require(collateralSiloSolvencyOracle == 0);

        //values before
        mathint countBefore = callCountBeforeQuote[anyOracle];

        //function call
        withdraw(e, assets, receiver, owner);

        //values after
        mathint countAfter = callCountBeforeQuote[anyOracle];

        //no oracle is called before the quote
        assert (countAfter == countBefore);
    }

    // withdraw() if callBeforeQuote == false no oracle is called before the quote
    rule noCallBeforeQuoteIfFalseSolvancyOracle(env e) {
        uint256 assets;
        address receiver;
        address owner;
        address anyOracle;
        address debtSilo = siloConfig.getDebtSilo(e, owner);
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, owner);
        require(debtSilo != collateralSilo);

        bool callBeforeQuoteDebtSilo = siloConfig.getConfig(e, debtSilo).callBeforeQuote;
        bool callBeforeQuoteCollateralSilo = siloConfig.getConfig(e, collateralSilo).callBeforeQuote;
        require(callBeforeQuoteDebtSilo == false);
        require(callBeforeQuoteCollateralSilo == false);

        //values before
        mathint countBefore = callCountBeforeQuote[anyOracle];

        //function call
        withdraw(e, assets, receiver, owner);

        //values after
        mathint countAfter = callCountBeforeQuote[anyOracle];

        //no oracle is called before the quote
        assert (countAfter == countBefore);
    }

    // borrow() if  _config.maxLtvOracle == address(0) no oracle is called before the quote
    rule noCallBeforeIfOracles0(env e){
        uint256 assets;
        address receiver;
        address borrower;
        address anyOracle;
        address debtSilo = siloConfig.getDebtSilo(e, borrower);
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, borrower);
        require(debtSilo != collateralSilo);

        address debtSiloMaxLtvOracle = siloConfig.getConfig(e, debtSilo).maxLtvOracle;
        address collateralSiloMaxLtvOracle = siloConfig.getConfig(e, collateralSilo).maxLtvOracle;
        require(debtSiloMaxLtvOracle == 0);
        require(collateralSiloMaxLtvOracle == 0);

        //values before
        mathint countBefore = callCountBeforeQuote[anyOracle];

        //function call
        borrow(e, assets, receiver, borrower);

        //values after
        mathint countAfter = callCountBeforeQuote[anyOracle];

        //no oracle is called before the quote
        assert (countAfter == countBefore);
    }

    // borrow() if maxLtvOracle != 0 && _config.callBeforeQuote == true for collateralSilo, only the maxLtvOracle of collateralSilo is called once before the quote
    rule onlyCollateralSiloMaxLtvOracleCalledBeforeQuote(env e) {
        uint256 assets;
        address receiver;
        address borrower;
        address otherOracle;
        address debtSilo = siloConfig.getDebtSilo(e, borrower);
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, borrower);
        require(debtSilo != collateralSilo);

        address debtSiloMaxLtvOracle = siloConfig.getConfig(e, debtSilo).maxLtvOracle;
        address collateralSiloMaxLtvOracle = siloConfig.getConfig(e, collateralSilo).maxLtvOracle;
        bool debtSiloCallBeforeQuote = siloConfig.getConfig(e, debtSilo).callBeforeQuote;
        bool collateralSiloCallBeforeQuote = siloConfig.getConfig(e, collateralSilo).callBeforeQuote;
        require(debtSiloMaxLtvOracle == 0 && collateralSiloMaxLtvOracle != 0);
        require(debtSiloCallBeforeQuote == false && collateralSiloCallBeforeQuote == true);
        
        //setup
        maxLtvOracleRulesSetup(e, otherOracle);

        //values before
        mathint debtSiloMaxLtvOracleCountBefore = callCountBeforeQuote[debtSiloMaxLtvOracle];
        mathint collateralSiloMaxLtvOracleCountBefore = callCountBeforeQuote[collateralSiloMaxLtvOracle];
        mathint otherOracleCountBefore = callCountBeforeQuote[otherOracle];

        //function call
        borrow(e, assets, receiver, borrower);

        //values after
        mathint debtSiloMaxLtvOracleCountAfter = callCountBeforeQuote[debtSiloMaxLtvOracle];
        mathint collateralSiloMaxLtvOracleCountAfter = callCountBeforeQuote[collateralSiloMaxLtvOracle];
        mathint otherOracleCountAfter = callCountBeforeQuote[otherOracle];

        //only the maxLtvOracles are called once before the quote
        assert (debtSiloMaxLtvOracleCountAfter == debtSiloMaxLtvOracleCountBefore);
        assert (collateralSiloMaxLtvOracleCountAfter == collateralSiloMaxLtvOracleCountBefore + 1);
        assert (otherOracleCountAfter == otherOracleCountBefore);
    }

    // borrow() if maxLtvOracle != 0 && _config.callBeforeQuote == true, only the maxLtvOracles are called once before the quote
    rule onlyMaxLtvOraclesCalledBeforeQuote(env e) {
        uint256 assets;
        address receiver;
        address borrower;
        address otherOracle;
        address debtSilo = siloConfig.getDebtSilo(e, borrower);
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, borrower);
        require(debtSilo != collateralSilo);

        address debtSiloMaxLtvOracle = siloConfig.getConfig(e, debtSilo).maxLtvOracle;
        address collateralSiloMaxLtvOracle = siloConfig.getConfig(e, collateralSilo).maxLtvOracle;
        bool debtSiloCallBeforeQuote = siloConfig.getConfig(e, debtSilo).callBeforeQuote;
        bool collateralSiloCallBeforeQuote = siloConfig.getConfig(e, collateralSilo).callBeforeQuote;
        require(debtSiloMaxLtvOracle != 0 && collateralSiloMaxLtvOracle != 0);
        require(debtSiloCallBeforeQuote == true && collateralSiloCallBeforeQuote == true);
        
        //setup
        maxLtvOracleRulesSetup(e, otherOracle);

        //values before
        mathint debtSiloMaxLtvOracleCountBefore = callCountBeforeQuote[debtSiloMaxLtvOracle];
        mathint collateralSiloMaxLtvOracleCountBefore = callCountBeforeQuote[collateralSiloMaxLtvOracle];
        mathint otherOracleCountBefore = callCountBeforeQuote[otherOracle];

        //function call
        borrow(e, assets, receiver, borrower);

        //values after
        mathint debtSiloMaxLtvOracleCountAfter = callCountBeforeQuote[debtSiloMaxLtvOracle];
        mathint collateralSiloMaxLtvOracleCountAfter = callCountBeforeQuote[collateralSiloMaxLtvOracle];
        mathint otherOracleCountAfter = callCountBeforeQuote[otherOracle];

        //only the maxLtvOracles are called once before the quote
        assert (debtSiloMaxLtvOracleCountAfter == debtSiloMaxLtvOracleCountBefore + 1);
        assert (collateralSiloMaxLtvOracleCountAfter == collateralSiloMaxLtvOracleCountBefore + 1);
        assert (otherOracleCountAfter == otherOracleCountBefore);
    }

    // borrow() if maxLtvOracle != 0 && _config.callBeforeQuote == true for debtSilo, only the maxLtvOracle of debtSilo is called once before the quote
    rule onlyDebtSiloMaxLtvOracleCalledBeforeQuote(env e) {
        uint256 assets;
        address receiver;
        address borrower;
        address otherOracle;
        address debtSilo = siloConfig.getDebtSilo(e, borrower);
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, borrower);
        require(debtSilo != collateralSilo);

        address debtSiloMaxLtvOracle = siloConfig.getConfig(e, debtSilo).maxLtvOracle;
        address collateralSiloMaxLtvOracle = siloConfig.getConfig(e, collateralSilo).maxLtvOracle;
        bool debtSiloCallBeforeQuote = siloConfig.getConfig(e, debtSilo).callBeforeQuote;
        bool collateralSiloCallBeforeQuote = siloConfig.getConfig(e, collateralSilo).callBeforeQuote;
        require(debtSiloMaxLtvOracle != 0 && collateralSiloMaxLtvOracle == 0);
        require(debtSiloCallBeforeQuote == true && collateralSiloCallBeforeQuote == false);
        
        //setup
        maxLtvOracleRulesSetup(e, otherOracle);

        //values before
        mathint debtSiloMaxLtvOracleCountBefore = callCountBeforeQuote[debtSiloMaxLtvOracle];
        mathint collateralSiloMaxLtvOracleCountBefore = callCountBeforeQuote[collateralSiloMaxLtvOracle];
        mathint otherOracleCountBefore = callCountBeforeQuote[otherOracle];

        //function call
        borrow(e, assets, receiver, borrower);

        //values after
        mathint debtSiloMaxLtvOracleCountAfter = callCountBeforeQuote[debtSiloMaxLtvOracle];
        mathint collateralSiloMaxLtvOracleCountAfter = callCountBeforeQuote[collateralSiloMaxLtvOracle];
        mathint otherOracleCountAfter = callCountBeforeQuote[otherOracle];

        //only the maxLtvOracles are called once before the quote
        assert (debtSiloMaxLtvOracleCountAfter == debtSiloMaxLtvOracleCountBefore + 1);
        assert (collateralSiloMaxLtvOracleCountAfter == collateralSiloMaxLtvOracleCountBefore);
        assert (otherOracleCountAfter == otherOracleCountBefore);
    }

    //borrowSameAsset() no oracle is called before quote
    rule noOracleCalledBeforeQuote(env e) {
        uint256 assets;
        address receiver;
        address borrower;
        address anyOracle;

        //values before
        mathint countBefore = callCountBeforeQuote[anyOracle];

        //function call
        borrowSameAsset(e, assets, receiver, borrower);

        //values after
        mathint countAfter = callCountBeforeQuote[anyOracle];

        //no oracle is called before the quote
        assert (countAfter == countBefore);
    }
    
    // borrow() if callBeforeQuote == false no oracle is called before the quote
    rule noCallBeforeQuoteIfFalse(env e) {
        uint256 assets;
        address receiver;
        address borrower;
        address anyOracle;
        address debtSilo = siloConfig.getDebtSilo(e, borrower);
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, borrower);
        require(debtSilo != collateralSilo);

        bool callBeforeQuoteDebtSilo = siloConfig.getConfig(e, debtSilo).callBeforeQuote;
        bool callBeforeQuoteCollateralSilo = siloConfig.getConfig(e, collateralSilo).callBeforeQuote;
        require(callBeforeQuoteDebtSilo == false);
        require(callBeforeQuoteCollateralSilo == false);

        //values before
        mathint countBefore = callCountBeforeQuote[anyOracle];

        //function call
        borrow(e, assets, receiver, borrower);

        //values after
        mathint countAfter = callCountBeforeQuote[anyOracle];

        //no oracle is called before the quote
        assert (countAfter == countBefore);
    }
//------------------------------- RULES OK END ------------------------------------

//------------------------------- INVARIENTS OK START-------------------------------

//------------------------------- INVARIENTS OK END-------------------------------

//------------------------------- ISSUES OK START-------------------------------

//------------------------------- ISSUES OK END-------------------------------
