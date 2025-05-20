/* Rules concerning withdraw and redeem  */

import "../setup/CompleteSiloSetup.spec";
import "./0base_Silo.spec";
// import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";
import "../simplifications/_Oracle_call_before_quote_UNSAFE.spec";
import "../simplifications/Oracle_quote_one_UNSAFE.spec";
import "../simplifications/_flashloan_no_state_changes.spec";
import "../simplifications/_accrueInteres_fixed_UNSAFE.spec"; // accrueInterest is fixed to 100


//----------------------------- METHODES AND FUNCTIONS START ------------------------

    methods {
        function _.getFeeReceivers(address) external => cvlGetFeeReceivers() expect (address, address);
    }

    ghost address dao;
    ghost address deployer;

    function cvlGetFeeReceivers() returns (address, address) {
        nonSceneAddressRequirements(dao);
        nonSceneAddressRequirements(deployer);
        return (dao, deployer);
    }
//----------------------------- METHODES AND FUNCTIONS END --------------------------  



//----------------------------- Rules OK ------------------------
    // withDrawFees() accrues interest before withdrawing fees
    rule accrueInterestBeforeWithdrawingFees(env e) {
        SafeAssumptionsEnv_simple(e);
        //make sure interest is accrued
        mathint interestRateTimestamp = getSiloDataInterestRateTimestamp();
        require(e.block.timestamp > interestRateTimestamp);  

        //liquidity is 0
        uint256 balanceSilo = token0.balanceOf(silo0);
        uint256 totalProtectedAssets = totalProtectedAssetsHarness(e);
        mathint liquidity = balanceSilo - totalProtectedAssets;
        require(liquidity == 0); //noPayout is happening
        //daoFee and deployerFee are a total of 0.8 * 10^18
        uint256 deployerFee;
        uint256 daoFee;
        (daoFee, deployerFee, _, _) = siloConfig.getFeesWithAsset(e,silo0);
        require(daoFee + deployerFee == (10^18/2));

        //values before
        uint256 daoAndDeployerRevenueBefore;
        (daoAndDeployerRevenueBefore, _, _, _, _) = getSiloStorage(e);

        //withdraw fees
        withdrawFees(e);

        //values after
        uint256 daoAndDeployerRevenueAfter;
        (daoAndDeployerRevenueAfter, _, _, _, _) = getSiloStorage(e);

        //daoAndDeployerRevenue has increased by 50 (fixed interst returns 100, fees are 50%)
        assert(daoAndDeployerRevenueAfter == daoAndDeployerRevenueBefore + 50);
    }

        
