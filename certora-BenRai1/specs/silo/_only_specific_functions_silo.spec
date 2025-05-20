/* Rules concerning state change  */

import "../setup/CompleteSiloSetup.spec";
import "./0base_Silo.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";
import "../simplifications/_Oracle_call_before_quote_UNSAFE.spec";
import "../simplifications/Oracle_quote_one_UNSAFE.spec";
import "../simplifications/_flashloan_no_state_changes.spec";


//------------------------------- RULES TEST START ----------------------------------



    //--------------------- Definitions ---------------------

    definition FUNCTIONS_TO_EXCLUDE(method f) returns bool =
        f.selector == sig:Silo0.flashLoan(address,address,uint256,bytes).selector || 
        f.selector == sig:Silo0.callOnBehalfOfSilo(address,uint256,ISilo.CallType,bytes).selector ||
        f.selector == sig:updateHooks().selector ||
        f.selector == sig:ShareDebtToken0.callOnBehalfOfShareToken(address,uint256,ISilo.CallType,bytes).selector ||
        f.selector == sig:ShareProtectedCollateralToken0.permit(address,address,uint256,uint256,uint8,bytes32,bytes32).selector ||
        f.selector == sig:Silo0.initialize(address).selector ||
    f.selector == sig:ShareDebtToken0.initialize(address,address,uint24).selector;

    //invariant borrowerCollateralSilo can only be 0, silo0 or silo1
    invariant borrowerCollateralSiloCanOnlyBe0Silo0OrSilo1(env e, address user, address owner) 
     (siloConfig.borrowerCollateralSilo(user) == 0 || siloConfig.borrowerCollateralSilo(user) == silo0 || siloConfig.borrowerCollateralSilo(user) == silo1) &&
     (siloConfig.borrowerCollateralSilo(owner) == 0 || siloConfig.borrowerCollateralSilo(owner) == silo0 || siloConfig.borrowerCollateralSilo(owner) == silo1)
        filtered { 
            f -> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f)
        }

        { 
                preserved transfer(address to, uint256 amount) with (env e1) {
                    require siloConfig.borrowerCollateralSilo(e.msg.sender) == 0 || siloConfig.borrowerCollateralSilo(e.msg.sender) == silo0 || siloConfig.borrowerCollateralSilo(e1.msg.sender) == silo1;
                }

                preserved transferFrom(address from, address to, uint256 amount) with (env e2) {
                    require siloConfig.borrowerCollateralSilo(from) == 0 || siloConfig.borrowerCollateralSilo(from) == silo0 || siloConfig.borrowerCollateralSilo(from) == silo1;
                }
                
                preserved forwardTransferFromNoChecks(address from, address to, uint256 amount) with (env e3) {
                    require siloConfig.borrowerCollateralSilo(from) == 0 || siloConfig.borrowerCollateralSilo(from) == silo0 || siloConfig.borrowerCollateralSilo(from) == silo1;
                }
    }

    // //INVARIANT: if debt tokens, borrowerCollateralSilo must be silo0 or silo1 
    invariant ifDebtTokensBorrowerCollateralSiloMustBeSilo0OrSilo1(address user)
        (shareDebtToken0.balanceOf(user) != 0 || shareDebtToken1.balanceOf(user) != 0) => 
        (siloConfig.borrowerCollateralSilo(user) == silo0 || siloConfig.borrowerCollateralSilo(user) == silo1)
        filtered { 
            f -> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f) &&
            f.selector != sig:ShareDebtToken0.mint(address,address,uint256).selector //can only be called by silo and not directly
        }
        {
            preserved transfer(address to, uint256 amount) with (env e){
                require siloConfig.borrowerCollateralSilo(e.msg.sender) == silo0 || siloConfig.borrowerCollateralSilo(e.msg.sender) == silo1;
            }

            preserved transferFrom(address from, address to, uint256 amount) with (env e1){
                require siloConfig.borrowerCollateralSilo(from) == silo0 || siloConfig.borrowerCollateralSilo(from) == silo1;
            }

            preserved forwardTransferFromNoChecks(address from, address to, uint256 amount) with (env e2){
                require siloConfig.borrowerCollateralSilo(from) == silo0 || siloConfig.borrowerCollateralSilo(from) == silo1;
            }        
            preserved mint(address owner, address spender, uint256 amount) with (env e3){
                require siloConfig.borrowerCollateralSilo(owner) == silo0 || siloConfig.borrowerCollateralSilo(owner) == silo1;
            }        
    }

    // //INVARIANT: user can only have debtToken0 or debtToken1
    // invariant userCanOnlyHaveDebtToken0OrDebtToken1(address user)
    //     (shareDebtToken0.balanceOf(user) != 0 && shareDebtToken1.balanceOf(user) == 0) || 
    //     (shareDebtToken0.balanceOf(user) == 0 && shareDebtToken1.balanceOf(user) != 0) ||
    //     (shareDebtToken0.balanceOf(user) == 0 && shareDebtToken1.balanceOf(user) == 0) 
    //     filtered {
    //         f -> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f)
    // }


    // //INVARIANT siloBalance token0 alway bigger or equal to sprotectedAssets
    // invariant siloBalanceToken0AlwaysBiggerOrEqualThanSprotectedAssets()
    //     token0.balanceOf(silo0) >= totalProtectedAssetsHarness()
    //     filtered { 
    //         f -> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f)
    //     }

    // //INVARIANT: liquidity can never be bigger than balance of silo0
    // invariant liquidityNeverBiggerThanBalanceOfSilo0(env e)  
    //     token0.balanceOf(silo0) >= getLiquidity(e);



//------------------------------- RULES TEST END ----------------------------------

//------------------------------- RULES PROBLEMS START ----------------------------------

//------------------------------- RULES PROBLEMS START ----------------------------------

//------------------------------- RULES OK START ------------------------------------

    
    // borrowerCollateralSilo:only specific functions can change it
    rule borrowerCollateralSiloOnlySpecificFunctionsCanChangeIt(env e, method f, calldataarg args) filtered{ f-> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f)} {
        configForEightTokensSetupRequirements();
        address user;

        //value to change
        address borrowerCollateralSiloBefore = siloConfig.borrowerCollateralSilo(e, user);

        //execute function
        f(e, args);

        //value after
        address borrowerCollateralSiloAfter = siloConfig.borrowerCollateralSilo(e, user);

        //only specific functions can change it
        assert (borrowerCollateralSiloBefore != borrowerCollateralSiloAfter => 
            f.selector == sig:ShareDebtToken0.transfer(address,uint256).selector ||
            f.selector == sig:ShareDebtToken0.transferFrom(address,address,uint256).selector ||
            f.selector == sig:ShareDebtToken0.forwardTransferFromNoChecks(address,address,uint256).selector ||
            f.selector == sig:Silo0.switchCollateralToThisSilo().selector ||
            f.selector == sig:Silo0.flashLoan(address,address,uint256,bytes).selector || // because of DEFAULT HAVOC
            f.selector == sig:Silo0.borrow(uint256,address,address).selector ||
            f.selector == sig:Silo0.borrowSameAsset(uint256,address,address).selector ||
            f.selector == sig:Silo0.borrowShares(uint256,address,address).selector ||
            f.selector == sig:Silo0.repay(uint256,address).selector ||
            f.selector == sig:Silo0.repayShares(uint256,address).selector
        );
    }

    // shareDebtToken0:only specific functions can change hookSetup
    rule shareDebtToken0OnlySpecificFunctionsCanChangeHookSetup(env e, method f, calldataarg args) filtered{ f-> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f)} {
        configForEightTokensSetupRequirements();

        //value to change
        IShareToken.HookSetup hookSetupBefore = shareDebtToken0.hookSetup(e);

        //execute function
        f(e, args);

        //value after
        IShareToken.HookSetup hookSetupAfter = shareDebtToken0.hookSetup(e);

        //only specific functions can change it
        assert (hookSetupBefore != hookSetupAfter => 
            f.selector == sig:ShareDebtToken0.synchronizeHooks(uint24,uint24).selector // will be false
        );
    }

    // shareProtectedCollateralToken0:only specific functions can change allowance
    rule shareProtectedTokenOnlySpecificFunctionsCanChangeAllowance(env e, method f, calldataarg args) filtered{ f-> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f)} {
        configForEightTokensSetupRequirements();
        address owner;
        address spender;

        //value to change
        uint256 allowanceBefore = shareProtectedCollateralToken0.allowance(owner, spender);

        //execute function
        f(e, args);

        //value after
        uint256 allowanceAfter = shareProtectedCollateralToken0.allowance(owner, spender);

        //only specific functions can change it
        assert (allowanceBefore != allowanceAfter => 
            f.selector == sig:ShareProtectedCollateralToken0.burn(address,address,uint256).selector ||
            f.selector == sig:ShareProtectedCollateralToken0.approve(address,uint256).selector ||
            f.selector == sig:Silo0.transitionCollateral(uint256,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.withdraw(uint256,address,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.redeem(uint256,address,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.transferFrom(address,address,uint256).selector
        );
    }

    // silo0 (CollateralShares):only specific functions can change allowance
    rule silo0OnlySpecificFunctionsCanChangeAllowance(env e, method f, calldataarg args) filtered{ f-> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f)} {
        configForEightTokensSetupRequirements();
        address owner;
        address spender;

        //value to change
        uint256 allowanceBefore = silo0.allowance(owner, spender);

        //execute function
        f(e, args);

        //value after
        uint256 allowanceAfter = silo0.allowance(owner, spender);

        //only specific functions can change it
        assert (allowanceBefore != allowanceAfter => 
            f.selector == sig:Silo0.burn(address,address,uint256).selector ||
            f.selector == sig:Silo0.approve(address,uint256).selector ||
            f.selector == sig:Silo0.transferFrom(address,address,uint256).selector ||
            f.selector == sig:Silo0.permit(address,address,uint256,uint256,uint8,bytes32,bytes32).selector ||
            f.selector == sig:Silo0.redeem(uint256,address,address).selector ||
            f.selector == sig:Silo0.redeem(uint256,address,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.withdraw(uint256,address,address).selector ||
            f.selector == sig:Silo0.withdraw(uint256,address,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.transitionCollateral(uint256,address,ISilo.CollateralType).selector
        );
    }

    // shareDebtToken0:only specific functions can change allowance
    rule shareDebtToken0OnlySpecificFunctionsCanChangeAllowance(env e, method f, calldataarg args) filtered{ f-> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f)} {
        configForEightTokensSetupRequirements();
        address owner;
        address spender;

        //value to change
        uint256 allowanceBefore = shareDebtToken0.allowance(owner, spender);

        //execute function
        f(e, args);

        //value after
        uint256 allowanceAfter = shareDebtToken0.allowance(owner, spender);

        //only specific functions can change it
        assert (allowanceBefore != allowanceAfter => 
            f.selector == sig:ShareDebtToken0.permit(address,address,uint256,uint256,uint8,bytes32,bytes32).selector ||
            f.selector == sig:ShareDebtToken0.mint(address,address,uint256).selector ||
            f.selector == sig:ShareDebtToken0.approve(address,uint256).selector ||
            f.selector == sig:ShareDebtToken0.transferFrom(address,address,uint256).selector ||
            f.selector == sig:Silo0.borrowSameAsset(uint256,address,address).selector ||
            f.selector == sig:Silo0.borrow(uint256,address,address).selector ||
            f.selector == sig:Silo0.borrowShares(uint256,address,address).selector
        );
    }

    // shareDebtToken0:only specific functions can change receiverAllowance
    rule shareDebtToken0OnlySpecificFunctionsCanChangeReceiverAllowance(env e, method f, calldataarg args) filtered{ f-> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f)} {
        configForEightTokensSetupRequirements();
        address owner;
        address spender;

        //value to change
        uint256 allowanceBefore = shareDebtToken0.receiveAllowance(owner, spender);

        //execute function
        f(e, args);

        //value after
        uint256 allowanceAfter = shareDebtToken0.receiveAllowance(owner, spender);

        //only specific functions can change it
        assert (allowanceBefore != allowanceAfter => 
            f.selector == sig:shareDebtToken0.setReceiveApproval(address,uint256).selector ||
            f.selector == sig:ShareDebtToken0.decreaseReceiveAllowance(address,uint256).selector ||
            f.selector == sig:ShareDebtToken0.increaseReceiveAllowance(address,uint256).selector ||
            f.selector == sig:ShareDebtToken0.transferFrom(address,address,uint256).selector ||
            f.selector == sig:shareDebtToken0.transfer(address,uint256).selector
        );
    }
    
    // shareProtectedCollateralToken0:only specific functions can change hookSetup
    rule shareProtectedToken0OnlySpecificFunctionsCanChangeHookSetup(env e, method f, calldataarg args) filtered{ f-> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f)} {
        configForEightTokensSetupRequirements();

        //value to change
        IShareToken.HookSetup hookSetupBefore = shareProtectedCollateralToken0.hookSetup(e);

        //execute function
        f(e, args);

        //value after
        IShareToken.HookSetup hookSetupAfter = shareProtectedCollateralToken0.hookSetup(e);

        //only specific functions can change it
        assert (hookSetupBefore != hookSetupAfter => 
            f.selector == sig:ShareProtectedCollateralToken0.synchronizeHooks(uint24,uint24).selector
        );
    }
    
    // silo0 (CollateralShares):only specific functions can change hookSetup
    rule silo0OnlySpecificFunctionsCanChangeHookSetup(env e, method f, calldataarg args) filtered{ f-> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f)} {
        configForEightTokensSetupRequirements();

        //value to change
        IShareToken.HookSetup hookSetupBefore = silo0.hookSetup(e);

        //execute function
        f(e, args);

        //value after
        IShareToken.HookSetup hookSetupAfter = silo0.hookSetup(e);

        //only specific functions can change it
        assert (hookSetupBefore != hookSetupAfter => 
            f.selector == sig:Silo0.synchronizeHooks(uint24,uint24).selector
        );
    }
    

    // totalAssets PROTECTED:only specific functions can change it
    rule totalAssetsProtectedOnlySpecificFunctionsCanChangeIt(env e, method f, calldataarg args) filtered{ f-> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f)} {
        configForEightTokensSetupRequirements();

        //value to change
        uint256 totalAssetsBefore;
        (_, _, totalAssetsBefore, _, _) = silo0.getSiloStorage();

        //execute function
        f(e, args);

        //value after
        uint256 totalAssetsAfter;
        (_, _, totalAssetsAfter, _, _) = silo0.getSiloStorage();

        //only specific functions can change it
        assert (totalAssetsBefore != totalAssetsAfter => 
            f.selector == sig:Silo0.deposit(uint256,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.mint(uint256,address, ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.redeem(uint256,address,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.withdraw(uint256,address,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.transitionCollateral(uint256,address,ISilo.CollateralType).selector 
        );
    }    
    
    // totalAssets COLLATERAL:only specific functions can change it
    rule totalAssetsCollateralOnlySpecificFunctionsCanChangeIt(env e, method f, calldataarg args) filtered{ f-> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f)} {
        configForEightTokensSetupRequirements();

        //value to change
        uint256 totalAssetsBefore;
        (_, _, _, totalAssetsBefore, _) = silo0.getSiloStorage();

        //execute function
        f(e, args);

        //value after
        uint256 totalAssetsAfter;
        (_, _, _, totalAssetsAfter, _) = silo0.getSiloStorage();

        //only specific functions can change it
        assert (totalAssetsBefore != totalAssetsAfter => 
            f.selector == sig:Silo0.deposit(uint256,address).selector ||
            f.selector == sig:Silo0.deposit(uint256,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.mint(uint256,address).selector ||
            f.selector == sig:Silo0.mint(uint256,address, ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.redeem(uint256,address,address).selector ||
            f.selector == sig:Silo0.redeem(uint256,address,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.withdraw(uint256,address,address).selector ||
            f.selector == sig:Silo0.withdraw(uint256,address,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.transitionCollateral(uint256,address,ISilo.CollateralType).selector // will be worng because accrue interest changes it
        );
    }

    // totalAssets DEBT:only specific functions can change it
    rule totalAssetsDebtOnlySpecificFunctionsCanChangeIt(env e, method f, calldataarg args) filtered{ f-> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f)} {
        configForEightTokensSetupRequirements();

        //value to change
        uint256 totalAssetsBefore;
        (_, _, _, _, totalAssetsBefore) = silo0.getSiloStorage();

        //execute function
        f(e, args);

        //value after
        uint256 totalAssetsAfter;
        (_, _, _, _, totalAssetsAfter) = silo0.getSiloStorage();

        //only specific functions can change it
        assert (totalAssetsBefore != totalAssetsAfter => 
            f.selector == sig:Silo0.borrow(uint256,address,address).selector ||
            f.selector == sig:Silo0.borrowSameAsset(uint256,address,address).selector ||
            f.selector == sig:Silo0.borrowShares(uint256,address,address).selector ||
            f.selector == sig:Silo0.repay(uint256,address).selector ||
            f.selector == sig:Silo0.repayShares(uint256,address).selector // will be wrong because accrue interest changes it
        );
    }

    // token0: only specific functions can change balances
    rule token0OnlySpecificFunctionsCanChangeBalances(env e, method f, calldataarg args) filtered{ f-> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f)} {
        configForEightTokensSetupRequirements();
        address user;

        //value to change
        uint256 balanceUserBefore = token0.balanceOf(user);

        //execute function
        f(e, args);

        //value after
        uint256 balanceUserAfter = token0.balanceOf(user);

        //only specific functions can change it
        assert (balanceUserBefore != balanceUserAfter => 
            f.selector == sig:Token0.transfer(address,uint256).selector ||
            f.selector == sig:Token0.transferFrom(address,address,uint256).selector ||
            f.selector == sig:Silo0.mint(address,address,uint256).selector ||
            f.selector == sig:Silo0.mint(uint256,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.mint(uint256,address).selector ||
            f.selector == sig:Silo0.burn(address,address,uint256).selector ||
            f.selector == sig:Silo0.borrow(uint256,address,address).selector ||
            f.selector == sig:Silo0.borrowSameAsset(uint256,address,address).selector ||
            f.selector == sig:Silo0.borrowShares(uint256,address,address).selector ||
            f.selector == sig:Silo0.deposit(uint256,address).selector ||
            f.selector == sig:Silo0.deposit(uint256,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.flashLoan(address,address,uint256,bytes).selector ||
            f.selector == sig:Silo0.redeem(uint256,address,address).selector ||
            f.selector == sig:Silo0.redeem(uint256,address,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.repay(uint256,address).selector ||
            f.selector == sig:Silo0.repayShares(uint256,address).selector ||
            f.selector == sig:Silo0.withdraw(uint256,address,address).selector ||
            f.selector == sig:Silo0.withdraw(uint256,address,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.withdrawFees().selector
        );
    }

    // shareProtectedCollateralToken0: only specific functions can change balances and totalSupply
    rule shareProtectedTokenOnlySpecificFunctions(env e, method f, calldataarg args) filtered{ f-> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f)} {
        configForEightTokensSetupRequirements();
        address user;

        //value to change
        uint256 balanceUserBefore = shareProtectedCollateralToken0.balanceOf(user);
        uint256 totalSupplyBefore = shareProtectedCollateralToken0.totalSupply();

        //execute function
        f(e, args);

        //value after
        uint256 balanceUserAfter = shareProtectedCollateralToken0.balanceOf(user);
        uint256 totalSupplyAfter = shareProtectedCollateralToken0.totalSupply();

        //only specific functions can change it
        assert (balanceUserBefore != balanceUserAfter || totalSupplyBefore != totalSupplyAfter => 
            f.selector == sig:ShareProtectedCollateralToken0.transfer(address,uint256).selector ||
            f.selector == sig:ShareProtectedCollateralToken0.transferFrom(address,address,uint256).selector ||
            f.selector == sig:ShareProtectedCollateralToken0.forwardTransferFromNoChecks(address,address,uint256).selector ||
            f.selector == sig:Silo0.mint(address,address,uint256).selector ||
            f.selector == sig:Silo0.mint(uint256,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.burn(address,address,uint256).selector ||
            f.selector == sig:Silo0.burn(address,address,uint256).selector ||
            f.selector == sig:Silo0.deposit(uint256,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.mint(uint256,address).selector ||
            f.selector == sig:Silo0.redeem(uint256,address,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.transitionCollateral(uint256,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.withdraw(uint256,address,address,ISilo.CollateralType).selector
        );
    }

    // silo0 (CollateralShares): only specific functions can change balances and totalSupply
    rule silo0OnlySpecificFunctionsCanChangeBalances(env e, method f, calldataarg args) filtered{ f-> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f)} {
        configForEightTokensSetupRequirements();
        address user;

        //value to change
        uint256 balanceUserBefore = silo0.balanceOf(user);
        uint256 totalSupplyBefore = silo0.totalSupply();

        //execute function
        f(e, args);

        //value after
        uint256 balanceUserAfter = silo0.balanceOf(user);
        uint256 totalSupplyAfter = silo0.totalSupply();

        //only specific functions can change it
        assert (balanceUserBefore != balanceUserAfter || totalSupplyBefore != totalSupplyAfter => 
            f.selector == sig:Silo0.mint(uint256,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.forwardTransferFromNoChecks(address,address,uint256).selector ||
            f.selector == sig:Silo0.transfer(address,uint256).selector ||
            f.selector == sig:Silo0.transferFrom(address,address,uint256).selector ||
            f.selector == sig:Silo0.burn(address,address,uint256).selector ||
            f.selector == sig:Silo0.mint(address,address,uint256).selector ||
            f.selector == sig:Silo0.deposit(uint256,address).selector ||
            f.selector == sig:Silo0.deposit(uint256,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.mint(address,address,uint256).selector ||
            f.selector == sig:Silo0.mint(uint256,address).selector ||
            f.selector == sig:Silo0.redeem(uint256,address,address).selector ||
            f.selector == sig:Silo0.redeem(uint256,address,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.transitionCollateral(uint256,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.withdraw(uint256,address,address).selector ||
            f.selector == sig:Silo0.withdraw(uint256,address,address,ISilo.CollateralType).selector
        );
    }

    // shareDebtToken0: only specific functions can change balances and totalSupply
    rule shareDebtToken0OnlySpecificFunctionsCanChangeBalances(env e, method f, calldataarg args) filtered{ f-> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f)} {
        configForEightTokensSetupRequirements();
        address user;

        //value to change
        uint256 balanceUserBefore = shareDebtToken0.balanceOf(user);
        uint256 totalSupplyBefore = shareDebtToken0.totalSupply();

        //execute function
        f(e, args);

        //value after
        uint256 balanceUserAfter = shareDebtToken0.balanceOf(user);
        uint256 totalSupplyAfter = shareDebtToken0.totalSupply();

        //only specific functions can change it
        assert (balanceUserBefore != balanceUserAfter || totalSupplyBefore != totalSupplyAfter => 
            f.selector == sig:shareDebtToken0.mint(address,address,uint256).selector ||
            f.selector == sig:shareDebtToken0.burn(address,address,uint256).selector ||
            f.selector == sig:shareDebtToken0.transfer(address,uint256).selector ||
            f.selector == sig:shareDebtToken0.transferFrom(address,address,uint256).selector ||
            f.selector == sig:shareDebtToken0.forwardTransferFromNoChecks(address,address,uint256).selector ||
            f.selector == sig:Silo0.borrow(uint256,address,address).selector ||
            f.selector == sig:Silo0.borrowSameAsset(uint256,address,address).selector ||
            f.selector == sig:Silo0.borrowShares(uint256,address,address).selector ||
            f.selector == sig:Silo0.repay(uint256,address).selector ||
            f.selector == sig:Silo0.repayShares(uint256,address).selector
        );
    }

    // token0: only specific functions can change allowance
    rule token0OnlySpecificFunctionsCanChangeAllowance(env e, method f, calldataarg args) filtered{ f-> !f.isView && !HARNESS_METHODS(f) && !FUNCTIONS_TO_EXCLUDE(f)} {
        configForEightTokensSetupRequirements();
        address owner;
        address spender;

        //value to change
        uint256 allowanceBefore = token0.allowance(owner, spender);

        //execute function
        f(e, args);

        //value after
        uint256 allowanceAfter = token0.allowance(owner, spender);

        //only specific functions can change it
        assert (allowanceBefore != allowanceAfter => 
            f.selector == sig:Silo0.mint(uint256,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.flashLoan(address,address,uint256,bytes).selector ||
            f.selector == sig:Silo0.approve(address,uint256).selector ||
            f.selector == sig:Silo0.deposit(uint256,address).selector ||
            f.selector == sig:Silo0.deposit(uint256,address,ISilo.CollateralType).selector ||
            f.selector == sig:Silo0.mint(address,address,uint256).selector ||
            f.selector == sig:Silo0.mint(uint256,address).selector ||
            f.selector == sig:Silo0.repay(uint256,address).selector ||
            f.selector == sig:Silo0.repayShares(uint256,address).selector ||
            f.selector == sig:Silo0.transferFrom(address,address,uint256).selector
        );
    }

//------------------------------- RULES OK END ------------------------------------

//------------------------------- INVARIENTS OK START-------------------------------

//------------------------------- INVARIENTS OK END-------------------------------

//------------------------------- ISSUES OK START-------------------------------

//------------------------------- ISSUES OK END-------------------------------
