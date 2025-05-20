using SiloConfig as siloConfig;

//------------------------------------ SETUP START --------------------------------------

    methods {
        function _.accrueInterestForConfig(address, uint256, uint256) external => accrueInterestForSiloCVL(calledContract) expect void;
    }

    function accrueInterestForSiloCVL(address silo) {
        accrueInterestCalled[silo] = accrueInterestCalled[silo] + 1;
    }


    ghost mapping (address => mathint) accrueInterestCalled;

 
//------------------------------------ SETUP END --------------------------------------
// accrueInterestForSilo() calls accrueInterest for the provided silo 
    rule accrueInterestForSiloCallsAccrueInterestForProvidedSilo(env e) {
        address silo;

        address silo0;
        address silo1;
        (silo0, silo1) = siloConfig.getSilos(e);

        //values before
        mathint callsSilo0 = accrueInterestCalled[silo0];
        mathint callsSilo1 = accrueInterestCalled[silo1];

        //function call
        siloConfig.accrueInterestForSilo(e, silo);

        //values after
        mathint callsSilo0After = accrueInterestCalled[silo0];
        mathint callsSilo1After = accrueInterestCalled[silo1];

        //assert
        assert silo == silo0 => callsSilo0After == callsSilo0 + 1 && callsSilo1After == callsSilo1;
        assert silo == silo1 => callsSilo1After == callsSilo1 + 1 && callsSilo0After == callsSilo0;
    }


    //  // accrueInterestForBothSilos() calls accrueInterest for both silos 
    // rule accrueInterestForBothSilosCallsAccrueInterestForBothSilos(env e) {
    //     address silo0;
    //     address silo1;
    //     (silo0, silo1) = siloConfig.getSilos(e);

    //     //values before
    //     mathint callsSilo0 = accrueInterestCalled[silo0];
    //     mathint callsSilo1 = accrueInterestCalled[silo1];

    //     //function call
    //     siloConfig.accrueInterestForBothSilos(e);

    //     //values after
    //     mathint callsSilo0After = accrueInterestCalled[silo0];
    //     mathint callsSilo1After = accrueInterestCalled[silo1];

    //     //assert
    //     assert callsSilo0After == callsSilo0 + 1 && callsSilo1After == callsSilo1 + 1;
    // }