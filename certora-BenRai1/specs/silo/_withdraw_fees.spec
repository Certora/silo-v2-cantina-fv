/* Rules concerning withdraw and redeem  */

import "../setup/CompleteSiloSetup.spec";
import "./0base_Silo.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";
import "../simplifications/_Oracle_call_before_quote_UNSAFE.spec";
import "../simplifications/Oracle_quote_one_UNSAFE.spec";
import "../simplifications/_flashloan_no_state_changes.spec";
// import "../simplifications/_accrueInteres_fixed_UNSAFE.spec"; // accrueInterest is fixed to 100

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


//------------------------------- RULES START ------------------------------------


    
    // INVARIANT: collateralAssets - debtAssets == siloBalance - protectedAssets - daoAndDeployerRevenue
    invariant twoWayLiquidityInvariant(env e)
        totalCollateralAssetsHarness(e) - totalDebtAssetsHarness(e) == token0.balanceOf(silo0) - totalProtectedAssetsHarness(e) - getSiloDataDaoAndDeployerRevenue(e) 
        filtered { f -> 
            f.selector != sig:updateHooks().selector &&
            f.selector != sig:callOnBehalfOfSilo(address,uint256,ISilo.CallType,bytes).selector &&
            f.selector != sig:mint(uint256,address).selector

        }
        {
            preserved withdraw(uint256 assets, address receiver, address owner, ISilo.CollateralType collateralType) with (env e1) {
                    require(receiver != silo0);
            }

            preserved withdraw(uint256 assets, address receiver, address owner)  with (env e1) {
                    require(receiver != silo0);
            }

            preserved redeem(uint256 shares, address receiver, address owner, ISilo.CollateralType collateralType) with (env e1) {
                    require(receiver != silo0);
            }

            
            preserved redeem(uint256 shares, address receiver, address owner)  with (env e1) {
                    require(receiver != silo0);
            }

            preserved borrowSameAsset(uint256 asset, address receiver, address borrower) with (env e1) {
                    require(receiver != silo0);
            }
            
            preserved borrow(uint256 asset, address receiver, address borrower) with (env e1) {
                    require(receiver != silo0);
            }
            
            preserved borrowShares(uint256 shares, address receiver, address borrower) with (env e1) {
                    require(receiver != silo0);
            }

            preserved deposit(uint256 asset, address receiver) with(env e1) {
                    require(e1.msg.sender != silo0);
                    totalSuppliesMoreThanBalances(e1.msg.sender, silo0);
            }

            preserved deposit(uint256 asset, address receiver, ISilo.CollateralType collateralType) with(env e1) {
                    require(e1.msg.sender != silo0);
                    totalSuppliesMoreThanBalances(e1.msg.sender, silo0);
            }

            preserved mint(uint256 shares, address receiver) with(env e1) {
                    require(e1.msg.sender != silo0);
                    totalSuppliesMoreThanBalances(e1.msg.sender, silo0);
            }

            preserved mint(uint256 asset, address receiver, ISilo.CollateralType collateralType) with(env e1) {
                    require(e1.msg.sender != silo0);
                    totalSuppliesMoreThanBalances(e1.msg.sender, silo0);
            }

            preserved repayShares(uint256 shares, address borrower) with(env e1) {
                    require(e1.msg.sender != silo0);
                    totalSuppliesMoreThanBalances(e1.msg.sender, silo0);
            }

            preserved repay(uint256 asset, address borrower) with(env e1) {
                    require(e1.msg.sender != silo0);
                    totalSuppliesMoreThanBalances(e1.msg.sender, silo0);
            }
    }
  
    // * `withdrawFees()` always reverts in a second call in the same block
    rule revertSecondCallInSameBlock(env e) {
        SafeAssumptionsEnv_simple(e);
        //call withdrawFees() once to accrue interest
        withdrawFees(e);

        //call withdrawFees() again
        withdrawFees@withrevert(e);

        //last call has reverted
        assert lastReverted;
    }

    // withDrawFees() if deployer is set, fees are split between dao and deployer using daoFee and deployerFee
    rule feesAreSplitBetweenDaoAndDeployer(env e) {
        SafeAssumptionsEnv_simple(e);
        address daoFeeReceiver;
        address deployerFeeReceiver;
        (daoFeeReceiver, deployerFeeReceiver) = cvlGetFeeReceivers();
        require(deployerFeeReceiver != 0);
        require(daoFeeReceiver != deployerFeeReceiver);
        totalSuppliesMoreThanThreeBalances(daoFeeReceiver, deployerFeeReceiver, silo0);

        //values before
        uint256 deployerFee;
        uint256 daoFee;
        (daoFee, deployerFee, _, _) = siloConfig.getFeesWithAsset(e,silo0);
        require(daoFee + deployerFee < 10^18);
        uint256 blanceDaoBefore = token0.balanceOf(daoFeeReceiver);
        uint256 blanceDeployerBefore = token0.balanceOf(deployerFeeReceiver);
        uint256 silo0BalanceBefore = token0.balanceOf(silo0);


        //function call
        withdrawFees(e);

        //values after
        uint256 blanceDaoAfter = token0.balanceOf(daoFeeReceiver);
        uint256 blanceDeployerAfter = token0.balanceOf(deployerFeeReceiver);
        uint256 silo0BalanceAfter = token0.balanceOf(silo0);
        mathint withdrawnFees = silo0BalanceBefore - silo0BalanceAfter;

        mathint feesForDao = withdrawnFees * daoFee / (daoFee + deployerFee);
        mathint feesForDeployer = withdrawnFees - feesForDao;

        //fees are split between dao and deployer
        assert blanceDaoAfter == blanceDaoBefore + feesForDao;
        assert blanceDeployerAfter == blanceDeployerBefore + feesForDeployer;
    }
    

    // * `withdrawFees()` always increases dao and/or deployer (can be empty address) balances
    rule withdrawFeesIncreasesDaoAndOrDeployerBalances(env e) {
        SafeAssumptionsEnv_simple(e);
        address daoFeeReceiver;
        address deployerFeeReceiver;
        (daoFeeReceiver, deployerFeeReceiver) = cvlGetFeeReceivers();
        require(deployerFeeReceiver != 0);
        totalSuppliesMoreThanThreeBalances(daoFeeReceiver, deployerFeeReceiver, silo0);

        //values before
        uint256 daoFee;
        uint256 deployerFee;
        (daoFee, deployerFee, _, _) = siloConfig.getFeesWithAsset(e,silo0);
        //positive fees are set
        require(daoFee == 0);
        require(deployerFee == 0);

        uint256 blanceDaoBefore = token0.balanceOf(daoFeeReceiver);
        uint256 blanceDeployerBefore = token0.balanceOf(deployerFeeReceiver);
        uint256 balanceOfSilo0Before = token0.balanceOf(silo0);

        //function call
        withdrawFees(e);

        //values after
        uint256 blanceDaoAfter = token0.balanceOf(daoFeeReceiver);
        uint256 blanceDeployerAfter = token0.balanceOf(deployerFeeReceiver);
        uint256 balanceOfSilo0After = token0.balanceOf(silo0);

        //earnedFees is increased by withdrawnFees
        assert blanceDaoAfter > blanceDaoBefore;
        assert blanceDeployerAfter > blanceDeployerBefore;
        assert balanceOfSilo0After < balanceOfSilo0Before;
    }
    
    // withDrawFees() if liquidity is 0 the function reverts
    rule revertIfLiquidityIsZero(env e) {
        SafeAssumptionsEnv_simple(e);

        //values before
        uint256 balanceSilo = token0.balanceOf(silo0);
        uint256 protectedAssets = totalProtectedAssetsHarness(e);
        mathint liquidity = balanceSilo - protectedAssets;
        require(liquidity == 0);

        //function call
        withdrawFees@withrevert(e);

        //last call has reverted
        assert lastReverted;
    }

    // withDrawFees() if liquidity is smaller than daoAndDeployerRevenue, only liquidity is withdrawn
    rule withdrawOnlyLiquidityIfLiquidityIsSmallerThanEarnedFees(env e) {
        SafeAssumptionsEnv_simple(e);

        //values before
        uint256 balanceSilo = token0.balanceOf(silo0);
        uint256 protectedAssets = totalProtectedAssetsHarness(e);
        mathint liquidityBefore = balanceSilo - protectedAssets;
        uint256 daoAndDeployerRevenueBefore;
        (daoAndDeployerRevenueBefore, _, _, _, _) = getSiloStorage(e);
        require(liquidityBefore < daoAndDeployerRevenueBefore);

        //function call
        withdrawFees(e);

        //values after
        uint256 balanceSiloAfter = token0.balanceOf(silo0);
        uint256 protectedAssetsAfter = totalProtectedAssetsHarness(e);
        mathint liquidityAfter = balanceSiloAfter - protectedAssetsAfter;
        uint256 daoAndDeployerRevenueAfter;
        (daoAndDeployerRevenueAfter, _, _, _, _) = getSiloStorage(e);

        //liquidity is 0
        assert liquidityAfter == 0;
        //earnedFees is decreased by liquidity
        assert daoAndDeployerRevenueAfter == daoAndDeployerRevenueBefore - liquidityBefore;
    }
   
    // withDrawFees() daoAndDeployerRevenue is reduced by the withdrawn assets
    rule daoAndDeployerRevenueIsReducedByWithdrawnAssets(env e) {
        SafeAssumptionsEnv_simple(e);

        //values before
        uint256 daoAndDeployerRevenueBefore;
        (daoAndDeployerRevenueBefore, _, _, _, _) = getSiloStorage(e);
        uint256 blanceSiloBefore = token0.balanceOf(silo0);

        //function call
        withdrawFees(e);

        //values after
        uint256 daoAndDeployerRevenueAfter;
        (daoAndDeployerRevenueAfter, _, _, _, _) = getSiloStorage(e);
        uint256 balanceSiloAfter = token0.balanceOf(silo0);
        mathint withdrawnFees = blanceSiloBefore - balanceSiloAfter;

        //earnedFees is decreased by withdrawnFees
        assert daoAndDeployerRevenueAfter == daoAndDeployerRevenueBefore - withdrawnFees;
    }
   
    // withDrawFees() if deployerFeeReceiver = 0 all fees go to the dao
    rule allFeesGoToDaoIfDeployerFeeReceiverIsZero(env e) {
        SafeAssumptionsEnv_simple(e);
        address daoFeeReceiver;
        address deployerFeeReceiver;
        (daoFeeReceiver, deployerFeeReceiver) = cvlGetFeeReceivers();
        require(deployerFeeReceiver == 0);

        //values before
        uint256 blanceDaoBefore = token0.balanceOf(daoFeeReceiver);
        uint256 blanceDeployerBefore = token0.balanceOf(deployerFeeReceiver);
        uint256 balanceOfSilo0Before = token0.balanceOf(silo0);
        totalSuppliesMoreThanThreeBalances(daoFeeReceiver, deployerFeeReceiver, silo0);

        //function call
        withdrawFees(e);

        //values after
        uint256 blanceDaoAfter = token0.balanceOf(daoFeeReceiver);
        uint256 blanceDeployerAfter = token0.balanceOf(deployerFeeReceiver);
        uint256 balanceOfSilo0After = token0.balanceOf(silo0);
        mathint withdrawnFees = balanceOfSilo0Before - balanceOfSilo0After;

        //all fees go do the dao
        assert blanceDaoAfter == blanceDaoBefore + withdrawnFees;
        assert blanceDeployerAfter == blanceDeployerBefore;
    }

    // withDrawFees() silo0 balance is decreased by the withdrawn fees
    rule silo0BalanceIsDecreasedByWithdrawnFees(env e) {
        SafeAssumptionsEnv_simple(e);

        //values before
        uint256 daoAndDeployerRevenueBefore;
        (daoAndDeployerRevenueBefore, _, _, _, _) = getSiloStorage(e);
        uint256 balanceOfSilo0Before = token0.balanceOf(silo0);

        //function call
        withdrawFees(e);

        //values after
        uint256 daoAndDeployerRevenueAfter;
        (daoAndDeployerRevenueAfter, _, _, _, _) = getSiloStorage(e);
        uint256 balanceOfSilo0After = token0.balanceOf(silo0);
        mathint withdrawnFees = daoAndDeployerRevenueBefore - daoAndDeployerRevenueAfter;

        //silo0 balance is decreased by withdrawnFees
        assert balanceOfSilo0After == balanceOfSilo0Before - withdrawnFees;
    }

    // withDrawFees() if daoAndDeployerRevenue are 0 function reverts
    rule revertIfDaoAndDeployerRevenueIsZero(env e) {
        SafeAssumptionsEnv_simple(e);
        //call withdrawFees() once to accrue interest
        withdrawFees(e);

        //make sure the daoAndDeployerRevenue is 0
        uint256 daoAndDeployerRevenue;
        (daoAndDeployerRevenue, _, _, _, _) = getSiloStorage(e);
        require(daoAndDeployerRevenue == 0);

        //call withdrawFees() again
        withdrawFees@withrevert(e);

        //last call has reverted
        assert lastReverted;
    }


//------------------------------- RULES OK END ------------------------------------

