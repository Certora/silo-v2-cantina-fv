methods{
    function SiloConfigHarness.accrueInterestForSilo(address) external envfree;
    function SiloConfigHarness.getBorrowerCollateral(address) external returns(address) envfree;
    function SiloConfigHarness.getCollateralShareTokenAndAsset(
        address,
        ISilo.CollateralType
    ) external returns (address, address) envfree;

    function _.getConfigsForWithdraw(address _silo,address _borrower) external => CVLGetConfigsForWithdraw(_silo,_borrower) expect(ISiloConfig.DepositConfig,ISiloConfig.ConfigData,ISiloConfig.ConfigData);
    function _.getConfigsForBorrow(address) external  => DISPATCHER(true);
    function _.getConfigsForSolvency(address _borrower) external  => CVLGetConfigsForSolvency(_borrower) expect(ISiloConfig.ConfigData,ISiloConfig.ConfigData);

    // ---- Dispatcher ---------------------------------------------------------
    function _.setThisSiloAsCollateralSilo(address) external  => DISPATCHER(true);
    function _.setOtherSiloAsCollateralSilo(address) external  => DISPATCHER(true);
    function _.borrowerCollateralSilo(address) external  => DISPATCHER(true);
    function _.onDebtTransfer(address,address) external  => DISPATCHER(true);
    function _.hasDebtInOtherSilo(address,address) external => DISPATCHER(true);

    function _.accrueInterestForSilo(address) external => NONDET;
    function _.accrueInterestForBothSilos() external => NONDET;

    // `CrossReentrancyGuard`
    function _.turnOnReentrancyProtection() external => NONDET;
    function _.turnOffReentrancyProtection() external => NONDET;
}

function CVLGetConfigsForSolvency(address borrower) returns (ISiloConfig.ConfigData,ISiloConfig.ConfigData){
    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;
    address debtSilo;
    uint256 debtBal0 = balanceOfCVL(shareDebtToken0, borrower);
    if(debtBal0 != 0){
        require debtSilo == silo0; 
    }

    if(debtSilo ==0){
        return (collateralConfig,debtConfig);
    }
    address collateralSilo = siloConfig.getBorrowerCollateral(borrower);

    require collateralConfig == CVLGetConfig(collateralSilo);
    require debtConfig == CVLGetConfig(debtSilo);
    return (collateralConfig,debtConfig);
}

function CVLGetConfigsForWithdraw(address silo, address borrower) returns (ISiloConfig.DepositConfig,ISiloConfig.ConfigData,ISiloConfig.ConfigData){
        ISiloConfig.DepositConfig depositConfig;
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        collateralConfig,debtConfig = CVLGetConfigsForSolvency(borrower);
        depositConfig = CVLGetDepositConfig(silo);
        return (depositConfig,collateralConfig,debtConfig);

}
function CVLGetDepositConfig (address silo) returns ISiloConfig.DepositConfig{
    ISiloConfig.DepositConfig config;
    if(silo == silo0){
        require config.silo == silo0_CC;
        require config.token == token0_CC;
        require config.collateralShareToken == silo0_CC;
        require config.protectedShareToken ==shareProtectedCollateralToken0_CC;
        require config.daoFee == siloConfig_CC._DAO_FEE;
        require config.deployerFee == siloConfig_CC._DEPLOYER_FEE;
        require config.interestRateModel == siloConfig_CC._INTEREST_RATE_MODEL0;
    }else {
        require config.silo == 0;
        require config.token == 0;
        require config.collateralShareToken == 0;
        require config.protectedShareToken == 0;
        require config.daoFee == 0;
        require config.deployerFee == 0;
        require config.interestRateModel == 0;
    }
    return config;
}

function SiloConfigCVL() returns address{
    return siloConfig;
}
