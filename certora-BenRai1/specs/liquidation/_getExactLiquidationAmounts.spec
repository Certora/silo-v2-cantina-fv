import "../setup/CompleteSiloSetup.spec";


//----------------------------SETUP START ---------------------------------
    methods{
        function _.getAssetsDataForLtvCalculations( 
        ISiloConfig.ConfigData memory _collateralConfig, ISiloConfig.ConfigData memory _debtConfig, address _borrower, ISilo.OracleType _oracleType, ISilo.AccrueInterestInMemory _accrueInMemory, uint256 _debtShareBalanceCached) internal with (env e) => getAssetsDataForLtvCalculationsCVL(e, _collateralConfig, _debtConfig, _borrower, _oracleType, _accrueInMemory, _debtShareBalanceCached) expect (SiloSolvencyLib.LtvData memory);

        function _.liquidationPreview(SiloSolvencyLib.LtvData memory _ltvData, PartialLiquidationLib.LiquidationPreviewParams memory _params) internal => liquidationPreviewCVL(_ltvData, _params) expect (uint256, uint256, bytes4);
    }

    //used calculation Data
    ghost bool usedAccrueInMemory; 
    ghost uint256 usedDebtShareBalanceCached;

    // used ltvData
    ghost address usedCollateralOracle;
    ghost address usedDebtOracle;
    ghost uint256 usedBorrowerProtectedAssets;
    ghost uint256 usedBorrowerCollateralAssets;
    ghost uint256 usedBorrowerDebtAssets;

    //used params
    ghost uint256 usedCollateralLt;
    ghost address usedCollateralConfigAsset;
    ghost address usedDebtConfigAsset;
    ghost uint256 usedMaxDebtToCover;
    ghost uint256 usedLiquidationFee;
    ghost uint256 usedLiquidationTargetLtv;


    function getAssetsDataForLtvCalculationsCVL(
        env e,
        ISiloConfig.ConfigData _collateralConfig, 
        ISiloConfig.ConfigData _debtConfig, 
        address _borrower, 
        ISilo.OracleType _oracleType, 
        ISilo.AccrueInterestInMemory _accrueInMemory, 
        uint256 _debtShareBalanceCached
    ) returns SiloSolvencyLib.LtvData 
    {   
        usedAccrueInMemory = _accrueInMemory == ISilo.AccrueInterestInMemory.Yes; 
        usedDebtShareBalanceCached = _debtShareBalanceCached;

        SiloSolvencyLib.LtvData ReturnLtvData;
        address collateralOracel;
        address debtOracle;
        if(_oracleType == ISilo.OracleType.Solvency){
            collateralOracel = _collateralConfig.solvencyOracle;
            debtOracle = _debtConfig.solvencyOracle;
        }else {
            collateralOracel = _collateralConfig.maxLtvOracle;
            debtOracle = _debtConfig.maxLtvOracle;
        }

        require(ReturnLtvData.collateralOracle == collateralOracel);
        require(ReturnLtvData.debtOracle == debtOracle);
        require(ReturnLtvData.borrowerProtectedAssets == _collateralConfig.protectedShareToken.balanceOf(e,_borrower));
        require(ReturnLtvData.borrowerCollateralAssets == _collateralConfig.collateralShareToken.balanceOf(e,_borrower));
        require(ReturnLtvData.borrowerDebtAssets == _debtConfig.debtShareToken.balanceOf(e,_borrower));

        return ReturnLtvData;
    }

    function liquidationPreviewCVL(SiloSolvencyLib.LtvData _ltvData, PartialLiquidationLib.LiquidationPreviewParams _params) returns (uint256, uint256, bytes4) {
        //set ghost variables
        usedCollateralOracle = _ltvData.collateralOracle;
        usedDebtOracle = _ltvData.debtOracle;
        usedBorrowerProtectedAssets = _ltvData.borrowerProtectedAssets;
        usedBorrowerCollateralAssets = _ltvData.borrowerCollateralAssets;
        usedBorrowerDebtAssets = _ltvData.borrowerDebtAssets;
        usedCollateralLt = _params.collateralLt;
        usedCollateralConfigAsset = _params.collateralConfigAsset;
        usedDebtConfigAsset = _params.debtConfigAsset;
        usedMaxDebtToCover = _params.maxDebtToCover;
        usedLiquidationFee = _params.liquidationFee;
        usedLiquidationTargetLtv = _params.liquidationTargetLtv;

        uint256 borrowerCollateralToLiquidate = 10000;
        uint256 repayDebtAssets = 1000;
        bytes4 customError = to_bytes4(11);
        return (borrowerCollateralToLiquidate, repayDebtAssets, customError);
    }

//----------------------------SETUP END ---------------------------------


//------------------------------- RULES TEST START ----------------------------------
    // getExactLiquidationAmounts() gets the right ltvData
    rule getsRightLtvData(env e) {
        configForEightTokensSetupRequirements();
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        address user;
        uint256 maxDebtToCover;
        uint256 liquidationFee;

        SiloSolvencyLib.LtvData ltvData = getAssetsDataForLtvCalculationsCVL(e, collateralConfig, debtConfig, user, ISilo.OracleType.Solvency, ISilo.AccrueInterestInMemory.No, 0);

        //function call
        getExactLiquidationAmountsHarness(e, collateralConfig, debtConfig, user, maxDebtToCover, liquidationFee);

        //used values are the same as the ltvData
        assert usedAccrueInMemory == false; 
        assert usedDebtShareBalanceCached == 0;
        assert usedCollateralOracle == ltvData.collateralOracle;
        assert usedDebtOracle == ltvData.debtOracle;
        assert usedBorrowerProtectedAssets == ltvData.borrowerProtectedAssets;
        assert usedBorrowerCollateralAssets == ltvData.borrowerCollateralAssets;
        assert usedBorrowerDebtAssets == ltvData.borrowerDebtAssets;
    }

    // getExactLiquidationAmounts() gets right values from the liquidation preview
    rule getsRightValuesFromLiquidationPreview(env e) {
        configForEightTokensSetupRequirements();
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        address user;
        uint256 maxDebtToCover;
        uint256 liquidationFee;

        //function call
        uint256 withdrawAssetsFromCollateralReturn;
        uint256 withdrawAssetsFromProtectedReturn;
        uint256 repayDebtAssetsReturn;
        bytes4 customErrorReturn;
        (withdrawAssetsFromCollateralReturn, withdrawAssetsFromProtectedReturn, repayDebtAssetsReturn, customErrorReturn) =
        getExactLiquidationAmountsHarness(e, collateralConfig, debtConfig, user, maxDebtToCover, liquidationFee);

        //used values are the same as the liquidation preview
        assert usedCollateralLt == collateralConfig.lt;
        assert usedCollateralConfigAsset == collateralConfig.token;
        assert usedDebtConfigAsset == debtConfig.token;
        assert usedMaxDebtToCover == maxDebtToCover;
        assert usedLiquidationFee == liquidationFee;
        assert usedLiquidationTargetLtv == collateralConfig.liquidationTargetLtv;
        assert withdrawAssetsFromCollateralReturn + withdrawAssetsFromProtectedReturn == 10000;
        assert repayDebtAssetsReturn == 1000;
        assert customErrorReturn == to_bytes4(11);
    }

    // getExactLiquidationAmounts() returns the right values for Collateral withdraw
    rule returnsRightValuesForCollateralWithdraw(env e) {
        configForEightTokensSetupRequirements();
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        address user;
        uint256 maxDebtToCover;
        uint256 liquidationFee;

        //function call
        uint256 withdrawAssetsFromCollateralReturn;
        uint256 withdrawAssetsFromProtectedReturn;
        uint256 repayDebtAssetsReturn;
        bytes4 customErrorReturn;
        (withdrawAssetsFromCollateralReturn, withdrawAssetsFromProtectedReturn, repayDebtAssetsReturn, customErrorReturn) =
        getExactLiquidationAmountsHarness(e, collateralConfig, debtConfig, user, maxDebtToCover, liquidationFee);

        uint256 borrowerProtectedAssets = usedBorrowerProtectedAssets;

        //return values are correct
        assert borrowerProtectedAssets >= 10000 => withdrawAssetsFromCollateralReturn == 0 && withdrawAssetsFromProtectedReturn == 10000;
        assert borrowerProtectedAssets < 10000 => withdrawAssetsFromCollateralReturn == 10000 - borrowerProtectedAssets && withdrawAssetsFromProtectedReturn == borrowerProtectedAssets;
    }


