/* Rules concerning state change (accruing interest) */

import "../setup/CompleteSiloSetup.spec";
import "./0base_Silo.spec";
import "../simplifications/_Oracle_call_before_quote_UNSAFE.spec";
import "../simplifications/Oracle_quote_one_UNSAFE.spec";
import "../simplifications/_flashloan_no_state_changes.spec";



definition FUNCTIONS_TO_EXCLUDE(method f) returns bool =
    f.selector == sig:Silo0.callOnBehalfOfSilo(address,uint256,ISilo.CallType,bytes).selector ||
    f.selector == sig:Silo0.flashLoan(address,address,uint256,bytes).selector || //@audit-issue remove this to proove that falsh loan chages some stuff
    f.selector == sig:updateHooks().selector ||
    f.selector == sig:ShareDebtToken0.callOnBehalfOfShareToken(address,uint256,ISilo.CallType,bytes).selector ||
    f.selector == sig:ShareProtectedCollateralToken0.permit(address,address,uint256,uint256,uint8,bytes32,bytes32).selector ||
f.selector == sig:Silo0.initialize(address).selector;

//--------------------------------- RULES OK START ---------------------------------

    // daoAndDeployerRevenue0:only specific functions can change it 
    rule daoAndDeployerRevenue0OnlySpecificFunctionsCanChangeIt(env e, method f, calldataarg args) filtered{ f-> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f)} {
        configForEightTokensSetupRequirements();

        //value to change
        uint256 daoAndDeployerRevenueBefore;
        (daoAndDeployerRevenueBefore, _, _, _, _) = silo0.getSiloStorage();

        //execute function
        f(e, args);

        //value after
        uint256 daoAndDeployerRevenueAfter;
        (daoAndDeployerRevenueAfter, _, _, _, _) = silo0.getSiloStorage();

        //only specific functions can change it
        assert (daoAndDeployerRevenueBefore != daoAndDeployerRevenueAfter => 
            f.selector == sig:transfer(address,uint256).selector ||
            f.selector == sig:transferFrom(address,address,uint256).selector ||
            f.selector == sig:Silo0.accrueInterestForConfig(address,uint256,uint256).selector ||
            f.selector == sig:Silo0.withdraw(uint256,address,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.redeem(uint256,address,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.transfer(address,uint256).selector ||
            f.selector == sig:Silo0.borrowSameAsset(uint256,address,address).selector ||
            f.selector == sig:Silo0.borrow(uint256,address,address).selector ||
            f.selector == sig:Silo0.redeem(uint256,address,address).selector ||
            f.selector == sig:Silo0.withdraw(uint256,address,address).selector ||
            f.selector == sig:Silo0.borrowShares(uint256,address,address).selector ||
            f.selector == sig:Silo0.accrueInterest().selector ||
            f.selector == sig:Silo0.switchCollateralToThisSilo().selector ||
            f.selector == sig:Silo0.withdrawFees().selector ||
            f.selector == sig:Silo0.deposit(uint256,address).selector ||
            f.selector == sig:Silo0.repayShares(uint256,address).selector ||
            f.selector == sig:Silo0.repay(uint256,address).selector ||
            f.selector == sig:Silo0.mint(uint256,address).selector ||
            f.selector == sig:Silo0.deposit(uint256,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.transitionCollateral(uint256,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.mint(uint256,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.transferFrom(address,address,uint256).selector ||
            f.selector == sig:Silo0.withdrawFees().selector 
        );
    }
    
    // interestRateTimestamp:only specific functions can change it
    rule interestRateTimestampOnlySpecificFunctionsCanChangeIt(env e, method f, calldataarg args) filtered{ f-> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f)} {
        configForEightTokensSetupRequirements();

        //value to change
        uint256 interestRateTimestampBefore;
        (_, interestRateTimestampBefore, _, _, _) = silo0.getSiloStorage();


        //execute function
        f(e, args);

        //value after
        uint256 interestRateTimestampAfter;
        (_, interestRateTimestampAfter, _, _, _) = silo0.getSiloStorage();

        //only specific functions can change it
        assert (interestRateTimestampBefore != interestRateTimestampAfter => 
            f.selector == sig:transfer(address,uint256).selector ||
            f.selector == sig:transferFrom(address,address,uint256).selector ||
            f.selector == sig:Silo0.accrueInterestForConfig(address,uint256,uint256).selector ||
            f.selector == sig:Silo0.withdraw(uint256,address,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.redeem(uint256,address,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.transfer(address,uint256).selector ||
            f.selector == sig:Silo0.borrowSameAsset(uint256,address,address).selector ||
            f.selector == sig:Silo0.borrow(uint256,address,address).selector ||
            f.selector == sig:Silo0.redeem(uint256,address,address).selector ||
            f.selector == sig:Silo0.withdraw(uint256,address,address).selector ||
            f.selector == sig:Silo0.borrowShares(uint256,address,address).selector ||
            f.selector == sig:Silo0.accrueInterest().selector ||
            f.selector == sig:Silo0.switchCollateralToThisSilo().selector ||
            f.selector == sig:Silo0.withdrawFees().selector ||
            f.selector == sig:Silo0.deposit(uint256,address).selector ||
            f.selector == sig:Silo0.repayShares(uint256,address).selector ||
            f.selector == sig:Silo0.repay(uint256,address).selector ||
            f.selector == sig:Silo0.mint(uint256,address).selector ||
            f.selector == sig:Silo0.deposit(uint256,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.transitionCollateral(uint256,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.mint(uint256,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.transferFrom(address,address,uint256).selector
        );
    }

//--------------------------------- RULES OK END ---------------------------------