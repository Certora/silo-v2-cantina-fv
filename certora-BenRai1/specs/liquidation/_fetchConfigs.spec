import "../setup/CompleteSiloSetup.spec";

//----------------------------SETUP---------------------------------
    methods{
        function _._accrueInterest() internal => accrueInterestCVL(calledContract) expect void;
        function _.callSolvencyOracleBeforeQuote(ISiloConfig.ConfigData memory _config) internal => callSolvencyOracleBeforeQuoteCVL(_config) expect void;
    }

    //contract to times called
    ghost mapping (address => mathint) interestAccrued;
    ghost mapping (address => mathint) solvencyOracleCalls;

    function accrueInterestCVL(address contract) {
        interestAccrued[contract] = interestAccrued[contract] + 1;
    }

    function callSolvencyOracleBeforeQuoteCVL(ISiloConfig.ConfigData _config) {
        address solvencyOracle = _config.solvencyOracle;
        solvencyOracleCalls[solvencyOracle] = solvencyOracleCalls[solvencyOracle] + 1;
    }



//------------------------------- RULES TEST START ----------------------------------

// _fetchConfig() reverts if debtSilo == 0
rule revertsIfDebtSiloIsZero(env e) {
    configForEightTokensSetupRequirements();
    address siloConfigCached = siloConfig;
    address collateralAsset;
    address debtAsset;
    address borrower;
    address borrowerDebtSilo = siloConfigCached.getDebtSilo(e, borrower);
    //require
    require(borrowerDebtSilo == 0);
    
    //function call
    _fetchConfigsHarness@withrevert(e, siloConfigCached, collateralAsset, debtAsset, borrower);

    assert lastReverted;
}

// _fetchConfig() reverts if _collateralAsset != collateraConfig.token
rule revertsIfCollateralAssetIsNotCollateralConfigToken(env e) {
    configForEightTokensSetupRequirements();
    address siloConfigCached = siloConfig;
    address collateralAsset;
    address debtAsset;
    address borrower;
    address borrowerCollateralSilo = siloConfig.borrowerCollateralSilo(e, borrower);
    address collateralToken = siloConfig.getConfig(e, borrowerCollateralSilo).token;
    //require
    require(collateralToken != collateralAsset);
    //function call
    _fetchConfigsHarness@withrevert(e, siloConfigCached, collateralAsset, debtAsset, borrower);

    assert lastReverted;
}

// _fetchConfig() reverts if _debtAsset != debtConfig.token
rule revertsIfDebtAssetIsNotDebtConfigToken(env e) {
    configForEightTokensSetupRequirements();
    address siloConfigCached = siloConfig;
    address collateralAsset;
    address debtAsset;
    address borrower;
    address borrowerDebtSilo = siloConfig.getDebtSilo(e, borrower);
    address debtToken = siloConfig.getConfig(e, borrowerDebtSilo).token;
    //require
    require(debtToken != debtAsset);
    //function call
    _fetchConfigsHarness@withrevert(e, siloConfigCached, collateralAsset, debtAsset, borrower);

    assert lastReverted;
}

// _fetchConfig() debtSilo == collateralSilo => accruesInterst for debtSilo
rule accruesInterestForDebtSiloIfDebtSiloEqualsCollateralSilo(env e) {
    configForEightTokensSetupRequirements();
    address siloConfigCached = siloConfig;
    address collateralAsset;
    address debtAsset;
    address borrower;
    address borrowerCollateralSilo = siloConfig.borrowerCollateralSilo(e, borrower);
    address collateralToken = siloConfig.getConfig(e, borrowerCollateralSilo).token;
    address borrowerDebtSilo = siloConfig.getDebtSilo(e, borrower);
    address debtToken = siloConfig.getConfig(e, borrowerDebtSilo).token;
    address otherSilo;
    nonSceneAddressRequirements(otherSilo);
    //prevent reverts
    require(borrowerDebtSilo != 0);
    require(collateralToken == collateralAsset);
    require(debtToken == debtAsset);

    //require
    require(borrowerDebtSilo == borrowerCollateralSilo);

    //values before
    mathint interestBeforeDebtSilo = interestAccrued[borrowerDebtSilo];
    mathint interestBeforeOtherSilo = interestAccrued[otherSilo];

    //function call
    _fetchConfigsHarness(e, siloConfigCached, collateralAsset, debtAsset, borrower);

    //values after
    mathint interestAfterDebtSilo = interestAccrued[borrowerDebtSilo];
    mathint interestAfterOtherSilo = interestAccrued[otherSilo];

    //assert
    assert interestAfterDebtSilo == interestBeforeDebtSilo + 1;
    assert interestAfterOtherSilo == interestBeforeOtherSilo;
}

// _fetchConfig() debtSilo != collateralSilo => accrues interest for both silos
rule accruesInterestForBothSilosIfDebtSiloNotEqualsCollateralSilo(env e) {
    configForEightTokensSetupRequirements();
    address siloConfigCached = siloConfig;
    address collateralAsset;
    address debtAsset;
    address borrower;
    address borrowerCollateralSilo = siloConfig.borrowerCollateralSilo(e, borrower);
    address collateralToken = siloConfig.getConfig(e, borrowerCollateralSilo).token;
    address borrowerDebtSilo = siloConfig.getDebtSilo(e, borrower);
    address debtToken = siloConfig.getConfig(e, borrowerDebtSilo).token;
    address otherSilo;
    nonSceneAddressRequirements(otherSilo);
    //prevent reverts
    require(borrowerDebtSilo != 0);
    require(collateralToken == collateralAsset);
    require(debtToken == debtAsset);
    //require
    require(borrowerDebtSilo != borrowerCollateralSilo);

    //values before
    mathint interestBeforeCollateralSilo = interestAccrued[borrowerCollateralSilo];
    mathint interestBeforeDebtSilo = interestAccrued[borrowerDebtSilo];
    mathint interestBeforeOtherSilo = interestAccrued[otherSilo];

    //function call
    _fetchConfigsHarness(e, siloConfigCached, collateralAsset, debtAsset, borrower);

    //values after
    mathint interestAfterCollateralSilo = interestAccrued[borrowerCollateralSilo];
    mathint interestAfterDebtSilo = interestAccrued[borrowerDebtSilo];
    mathint interestAfterOtherSilo = interestAccrued[otherSilo];

    //assert
    assert interestAfterCollateralSilo == interestBeforeCollateralSilo + 1;
    assert interestAfterDebtSilo == interestBeforeDebtSilo + 1;
    assert interestAfterOtherSilo == interestBeforeOtherSilo;
}

// _fetchConfig()  debtSilo != collateralSilo => calls callSolvancyOracleBeforeQuote
rule callsCallSolvencyOracleBeforeQuoteIfDebtSiloNotEqualsCollateralSilo(env e) {
    configForEightTokensSetupRequirements();
    address siloConfigCached = siloConfig;
    address collateralAsset;
    address debtAsset;
    address borrower;
    address borrowerCollateralSilo = siloConfig.borrowerCollateralSilo(e, borrower);
    address collateralToken = siloConfig.getConfig(e, borrowerCollateralSilo).token;
    address borrowerDebtSilo = siloConfig.getDebtSilo(e, borrower);
    address debtToken = siloConfig.getConfig(e, borrowerDebtSilo).token;
    //prevent reverts
    require(borrowerDebtSilo != 0);
    require(collateralToken == collateralAsset);
    require(debtToken == debtAsset);
    //require
    require(borrowerDebtSilo != borrowerCollateralSilo);
    address solvencyOracleDebtSilo = siloConfig.getConfig(e, borrowerDebtSilo).solvencyOracle;
    address solvencyOracleCollateralSilo = siloConfig.getConfig(e, borrowerCollateralSilo).solvencyOracle;
    address otherOracle;
    require(solvencyOracleDebtSilo != otherOracle);
    require(solvencyOracleCollateralSilo != otherOracle);
    require(solvencyOracleDebtSilo != solvencyOracleCollateralSilo);

    //values before
    mathint callsBeforeCollateralSilo = solvencyOracleCalls[solvencyOracleCollateralSilo];
    mathint callsBeforeDebtSilo = solvencyOracleCalls[solvencyOracleDebtSilo];
    mathint callsBeforeOtherSilo = solvencyOracleCalls[otherOracle];

    //function call
    _fetchConfigsHarness(e, siloConfigCached, collateralAsset, debtAsset, borrower);

    //values after
    mathint callsAfterCollateralSilo = solvencyOracleCalls[solvencyOracleCollateralSilo];
    mathint callsAfterDebtSilo = solvencyOracleCalls[solvencyOracleDebtSilo];
    mathint callsAfterOtherSilo = solvencyOracleCalls[otherOracle];

    //assert
    assert callsAfterCollateralSilo == callsBeforeCollateralSilo + 1;
    assert callsAfterDebtSilo == callsBeforeDebtSilo + 1;
    assert callsAfterOtherSilo == callsBeforeOtherSilo;
}

// _fetchConfig()  returned configs depend on the debt and collateralSilo of the user
rule returnedConfigsDependOnDebtAndCollateralSiloOfUser(env e) {
    configForEightTokensSetupRequirements();
    address siloConfigCached = siloConfig;
    address collateralAsset;
    address debtAsset;
    address borrower;
    address borrowerCollateralSilo = siloConfig.borrowerCollateralSilo(e, borrower);
    address collateralSiloToken = siloConfig.getConfig(e, borrowerCollateralSilo).token;
    address borrowerDebtSilo = siloConfig.getDebtSilo(e, borrower);
    address debtSiloToken = siloConfig.getConfig(e, borrowerDebtSilo).token;
    //prevent reverts
    require(borrowerDebtSilo != 0);
    require(borrowerCollateralSilo != 0);
    
    ISiloConfig.ConfigData collateralConfigResult;
    ISiloConfig.ConfigData debtConfigResult;

    //function call
    (collateralConfigResult, debtConfigResult) = _fetchConfigsHarness(e, siloConfigCached, collateralAsset, debtAsset, borrower);

    //assert
    assert collateralConfigResult.token == collateralSiloToken;
    assert debtConfigResult.token == debtSiloToken;
}


