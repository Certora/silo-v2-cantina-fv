/* Rules concerning function with "modifiers"  */

import "../setup/CompleteSiloSetup.spec";
import "./0base_Silo.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";
import "../simplifications/_Oracle_call_before_quote_UNSAFE.spec";
import "../simplifications/Oracle_quote_one_UNSAFE.spec";
import "../simplifications/_flashloan_no_state_changes.spec";


    // only one of the silos can call specific functions
    rule onlyOneOfTheSilosCanCallSpecificFunctions(env e, method f, calldataarg args) filtered { f->
        f.selector == sig:siloConfig.setOtherSiloAsCollateralSilo(address).selector ||
        f.selector == sig:siloConfig.setThisSiloAsCollateralSilo(address).selector 

    }{
        configForEightTokensSetupRequirements();
        address sender = e.msg.sender;
        require(sender != silo0 && sender != silo1);

        f@withrevert(e, args);

        assert lastReverted;
    }

    // only silo0 can call specific functions
    rule onlySilo0CanCallSpecificFunctions(env e, method f, calldataarg args) filtered { f->
        f.selector == sig:ShareDebtToken0.mint(address , address , uint256 ).selector ||
        f.selector == sig:ShareDebtToken0.burn(address,address,uint256).selector ||
        f.selector == sig:Silo0.burn(address,address,uint256).selector ||
        f.selector == sig:Silo0.mint(address,address,uint256).selector ||
        f.selector == sig:synchronizeHooks(uint24,uint24).selector
    }{
        configForEightTokensSetupRequirements();
        address sender = e.msg.sender;
        require(sender != silo0);

        f@withrevert(e, args);

        assert lastReverted;
    }

    // only hookReceiver can call specific functions
    rule onlyHookReceiverCanCallSpecificFunctions(env e, method f, calldataarg args) filtered { f->
        f.selector == sig:Silo0.callOnBehalfOfSilo(address,uint256,ISilo.CallType,bytes).selector ||
        f.selector == sig:shareDebtToken0.callOnBehalfOfShareToken(address,uint256,ISilo.CallType,bytes).selector ||
        f.selector == sig:Silo0.forwardTransferFromNoChecks(address,address,uint256).selector
    }{
        configForEightTokensSetupRequirements();
        address sender = e.msg.sender;
        address hookreceiverSilo = hookReceiver(e);
        address hookreceiverShareDebtToken = shareDebtToken0.hookReceiver(e);
        address hookreceiverShareProtectedCollateralToken = shareProtectedCollateralToken0.hookReceiver(e);
        require(sender != hookreceiverSilo && sender != hookreceiverShareDebtToken && sender != hookreceiverShareProtectedCollateralToken);

        f@withrevert(e, args);

        assert lastReverted;
    }

