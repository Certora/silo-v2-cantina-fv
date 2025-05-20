/** 
@title Direct test of the solvency function

*/
import "./0base_Silo.spec";
import "../setup/CompleteSiloSetup.spec";
import "../simplifications/SiloMathLib_SAFE.spec";
import "../simplifications/Oracle_quote_one_UNSAFE.spec";
import "../simplifications/SimplifiedGetCompoundInterestRateAndUpdate_SAFE.spec";

import "../setup/meta/authorized_functions.spec";
import "unresolved.spec";


methods{
    function _.getDebtSilo(address user) external => DISPATCHER(true);
}

//setup 
// no interest accrual => version with interest accrual (??)
// 1 share = 1 asset
function OneToOneAndNoOraclesSetup(env e) {
    uint256 totalProtectedAssetsSilo0;
    uint256 totalCollateralAssetsSilo0;
    uint256 totalDebtAssetsSilo0;
    (totalProtectedAssetsSilo0, totalCollateralAssetsSilo0, totalDebtAssetsSilo0) = silo0.totalAssetsHarness(e);
    uint256 totalProtectedSharesSilo0 = shareProtectedCollateralToken0.totalSupply();
    uint256 totalCollateralSharesSilo0 = silo0.totalSupply();
    uint256 totalDebtSharesSilo0 = shareDebtToken0.totalSupply();

    require(totalProtectedAssetsSilo0 == totalProtectedSharesSilo0);
    require(totalCollateralAssetsSilo0 == totalCollateralSharesSilo0);
    require(totalDebtAssetsSilo0 == totalDebtSharesSilo0);

    uint256 totalProtectedAssetsSilo1;
    uint256 totalCollateralAssetsSilo1;
    uint256 totalDebtAssetsSilo1;
    (totalProtectedAssetsSilo1, totalCollateralAssetsSilo1, totalDebtAssetsSilo1) = silo1.totalAssetsHarness(e);
    uint256 totalProtectedSharesSilo1 = shareProtectedCollateralToken1.totalSupply();
    uint256 totalCollateralSharesSilo1 = silo1.totalSupply();
    uint256 totalDebtSharesSilo1 = shareDebtToken1.totalSupply();
    
    require(totalProtectedAssetsSilo1 == totalProtectedSharesSilo1);
    require(totalCollateralAssetsSilo1 == totalCollateralSharesSilo1);
    require(totalDebtAssetsSilo1 == totalDebtSharesSilo1);

    // no oracles set => no calls to oracles
    address silo0SolvencyOracle = siloConfig.getConfig(e, silo0).solvencyOracle;
    require(silo0SolvencyOracle == 0);
    address silo1SolvencyOracle = siloConfig.getConfig(e, silo1).solvencyOracle;
    require(silo1SolvencyOracle == 0);
    address silo0MaxLtvOracle = siloConfig.getConfig(e, silo0).maxLtvOracle;
    require(silo0MaxLtvOracle == 0);
    address silo1MaxLtvOracle = siloConfig.getConfig(e, silo1).maxLtvOracle;
    require(silo1MaxLtvOracle == 0);
}






//------------------------------- RULES TEST START ----------------------------------

    // // solvent if debtAssets/collateralAssets <= _collateralConfig.lt
    // rule isBelowMaxLtv(env e) {
    //     configForEightTokensSetupRequirements();
    //     OneToOneAndNoOraclesSetup(e);
    //     address user;
    //     totalSuppliesMoreThanBalance(user);
    //     address debtSilo = siloConfig.getDebtSilo(e, user);
    //     address shareDebtToken = siloConfig.getConfig(e, debtSilo).debtShareToken;
    //     uint256 userBalanceDebtShares = shareDebtToken.balanceOf(e, user);
    //     address collateralSilo = siloConfig.borrowerCollateralSilo(e, user);
    //     address shareProtectedToken = siloConfig.getConfig(e, collateralSilo).protectedShareToken;
    //     uint256 userBalanceProtectedShares = shareProtectedToken.balanceOf(e, user);
    //     uint256 userBalanceCollateralShares = collateralSilo.balanceOf(e, user);
    //     require(userBalanceProtectedShares + userBalanceCollateralShares < max_uint256);
    //     uint256 totalCollateralAssets = sumHarness(userBalanceProtectedShares, userBalanceCollateralShares);
    //     uint256 userLtv = userLTVHarness(e, userBalanceDebtShares, totalCollateralAssets);
    //     uint256 liquidationThreshold = siloConfig.getConfig(e, collateralSilo).lt;
    //     require(liquidationThreshold < max_uint256);


    //     //function call
    //     bool isSolvent = isSolventHarness(e, user, ISilo.AccrueInterestInMemory.No);

    //     //solvent if userLtv <= liquidationThreshold
    //     assert(userLtv <= liquidationThreshold => isSolvent);
    // }






// SiloSolvencyLib.ltvInDp = _totalBorrowerDebtValue.mulDiv(_PRECISION_DECIMALS, _sumOfBorrowerCollateralValue, Rounding.LTV);
// _PRECISION_DECIMALS = 1e18; 

//------------------------------- RULES TEST END ----------------------------------

//------------------------------- RULES PROBLEMS START ----------------------------------

//------------------------------- RULES PROBLEMS START ----------------------------------

//------------------------------- RULES OK START ------------------------------------

    

    // user has no assets => insolvent
    rule ifNoAssetsButDebtThenInsolvent(env e) {
        configForEightTokensSetupRequirements();
        OneToOneAndNoOraclesSetup(e);
        address user;
        totalSuppliesMoreThanBalance(user);
        address debtSilo = siloConfig.getDebtSilo(e, user);
        address shareDebtToken = siloConfig.getConfig(e, debtSilo).debtShareToken;
        uint256 userBalanceDebtShares = shareDebtToken.balanceOf(e, user);
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, user);
        address shareProtectedToken = siloConfig.getConfig(e, collateralSilo).protectedShareToken;
        uint256 userBalanceProtectedShares = shareProtectedToken.balanceOf(e, user);
        uint256 userBalanceCollateralShares = collateralSilo.balanceOf(e, user);
        require(userBalanceProtectedShares + userBalanceCollateralShares == 0);
        require(userBalanceDebtShares != 0);
        uint256 liquidationThreshold = siloConfig.getConfig(e, collateralSilo).lt;
        require(liquidationThreshold < max_uint256);
        

        //function call
        bool isSolvent = isSolventHarness(e, user, ISilo.AccrueInterestInMemory.No);

        //if user has no assets, user must be insolvent
        assert !isSolvent;
    }
    
    // insolvent if debtAssets/collateralAssets > _collateralConfig.lt
    rule isAboveMaxLtv(env e) {
        configForEightTokensSetupRequirements();
        OneToOneAndNoOraclesSetup(e);
        address user;
        totalSuppliesMoreThanBalance(user);
        address debtSilo = siloConfig.getDebtSilo(e, user);
        address shareDebtToken = siloConfig.getConfig(e, debtSilo).debtShareToken;
        uint256 userBalanceDebtShares = shareDebtToken.balanceOf(e, user);
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, user);
        address shareProtectedToken = siloConfig.getConfig(e, collateralSilo).protectedShareToken;
        uint256 userBalanceProtectedShares = shareProtectedToken.balanceOf(e, user);
        uint256 userBalanceCollateralShares = collateralSilo.balanceOf(e, user);
        require(userBalanceProtectedShares + userBalanceCollateralShares < max_uint256);
        uint256 totalCollateralAssets = sumHarness(userBalanceProtectedShares, userBalanceCollateralShares);
        uint256 userLtv = userLTVHarness(e, userBalanceDebtShares, totalCollateralAssets);
        uint256 liquidationThreshold = siloConfig.getConfig(e, collateralSilo).lt;


        //function call
        bool isSolvent = isSolventHarness(e, user, ISilo.AccrueInterestInMemory.No);

        //insolvent if userLtv > liquidationThreshold
        assert(userLtv > liquidationThreshold => !isSolvent);
    }

    // if user has no debtAssets, should always be solvent
    rule ifNoDebtAssetsThenSolvent(env e) {
        configForEightTokensSetupRequirements();
        OneToOneAndNoOraclesSetup(e);
        address user;
        totalSuppliesMoreThanBalance(user);
        address debtSilo = siloConfig.getDebtSilo(e, user);
        address shareDebtToken = siloConfig.getConfig(e, debtSilo).debtShareToken;
        uint256 userBalanceDebtShares = shareDebtToken.balanceOf(e, user);


        //function call
        bool isSolvent = isSolventHarness(e, user, ISilo.AccrueInterestInMemory.No);

        //if user has no debt assets, user must be solvent
        assert(userBalanceDebtShares == 0 => isSolvent);
    }
    
    //* if user has no debt, should always be ltv == 0
    rule ifNoDebtThenLtvZero(env e) {
        configForEightTokensSetupRequirements();
        OneToOneAndNoOraclesSetup(e);
        address user;
        totalSuppliesMoreThanBalance(user);
        address debtSilo = siloConfig.getDebtSilo(e, user);
        address shareDebtToken = siloConfig.getConfig(e, debtSilo).debtShareToken;
        uint256 userBalanceDebtShares = shareDebtToken.balanceOf(e, user);
        require(userBalanceDebtShares == 0);

        //function call
        uint256 userLtv = getLTV(e,user);

        //if user has no debt, user must have ltv == 0
        assert userLtv == 0;
    }

    // isBelowMaxLtv and isSolvent should be the same
    rule isSolventAndBelowMaxLtvTheSame(env e) {
        configForEightTokensSetupRequirements();
        OneToOneAndNoOraclesSetup(e);
        address user;
        
        //function call
        bool isSolvent = isSolventHarness(e, user, ISilo.AccrueInterestInMemory.No);
        bool isBelowLtv = ltvBelowMaxLtvHarness(e, user);

        //if user has no assets, user must be insolvent
        assert(isSolvent == isBelowLtv);
    }

    // insolvent => user must have debt shares
    rule ifInsolventThenDebtShares(env e) {
        configForEightTokensSetupRequirements();
        OneToOneAndNoOraclesSetup(e);
        address user;
        address debtSilo = siloConfig.getDebtSilo(e, user);
        address shareDebtToken = siloConfig.getConfig(e, debtSilo).debtShareToken;
        uint256 userBalanceDebtShares = shareDebtToken.balanceOf(e, user);

        //function call
        bool isSolvent = isSolventHarness(e, user, ISilo.AccrueInterestInMemory.No);

        //if isSolvent is false, user must have debt shares
        assert(!isSolvent => userBalanceDebtShares > 0);
    }

    // no debtShares => solvent
    rule ifNoDebtSharesThenSolvent(env e) {
        configForEightTokensSetupRequirements();
        OneToOneAndNoOraclesSetup(e);
        address user;
        address debtSilo = siloConfig.getDebtSilo(e, user);
        address shareDebtToken = siloConfig.getConfig(e, debtSilo).debtShareToken;
        uint256 userBalanceDebtShares = shareDebtToken.balanceOf(e, user);

        //function call
        bool isSolvent = isSolventHarness(e, user, ISilo.AccrueInterestInMemory.No);

        //if user has no debt shares, user must be solvent
        assert(userBalanceDebtShares == 0 => isSolvent);
    }
    

//------------------------------- RULES OK END ------------------------------------

//------------------------------- INVARIENTS OK START-------------------------------

//------------------------------- INVARIENTS OK END-------------------------------

//------------------------------- ISSUES OK START-------------------------------

//------------------------------- ISSUES OK END-------------------------------
