/** 
@title Verify that for all function the solvency check is applied on any increases of debt or decrease of collateral 

*/
import "./0base_Silo.spec";
import "../setup/CompleteSiloSetup.spec";
import "../simplifications/SiloMathLib_SAFE.spec";
import "../simplifications/Oracle_quote_one_UNSAFE.spec";
import "../simplifications/SimplifiedGetCompoundInterestRateAndUpdate_SAFE.spec";

import "../setup/meta/authorized_functions.spec";
import "unresolved.spec";



methods {

     unresolved external in Silo0.callOnBehalfOfSilo(address,uint256,uint8,bytes) => DISPATCH(use_fallback=true) [
        
    ] default NONDET;

    function silo0.getTransferWithChecks() external  returns (bool) envfree;
    function silo1.getTransferWithChecks() external  returns (bool) envfree;
    function shareDebtToken0.getTransferWithChecks() external  returns (bool) envfree;
    function shareDebtToken1.getTransferWithChecks() external  returns (bool) envfree;
    function shareProtectedCollateralToken0.getTransferWithChecks() external  returns (bool) envfree;
    function shareProtectedCollateralToken1.getTransferWithChecks() external  returns (bool) envfree;
    function siloConfig.getDebtSilo(address) external returns (address) envfree;
    function _.isSolvent(address) external => DISPATCHER(true);

    
    
    // summary for the solvent check functions 
    function SiloSolvencyLib.isSolvent(
        ISiloConfig.ConfigData memory _collateralConfig,
        ISiloConfig.ConfigData memory _debtConfig,
        address borrower,
        ISilo.AccrueInterestInMemory _accrueInMemory
    )  internal returns (bool) => updateSolvent(borrower);

    function SiloSolvencyLib.isBelowMaxLtv(
        ISiloConfig.ConfigData memory _collateralConfig,
        ISiloConfig.ConfigData memory _debtConfig,
        address borrower,
        ISilo.AccrueInterestInMemory _accrueInMemory
    ) internal returns (bool) => updateSolvent(borrower);

    function ShareCollateralTokenLib.isSolventAfterCollateralTransfer(address _sender) external returns (bool) => updateSolvent(_sender);    

}



ghost mapping(address => bool) solventCalled;

function updateSolvent(address user) returns bool {
    return solventCalled[user];
}

function allTransferWithChecks() returns bool
{
        return  silo0.getTransferWithChecks() &&
                silo1.getTransferWithChecks() &&
                shareDebtToken0.getTransferWithChecks() &&
                shareDebtToken1.getTransferWithChecks() && 
                shareProtectedCollateralToken0.getTransferWithChecks() && 
                shareProtectedCollateralToken1.getTransferWithChecks();
        
}


//------------------------------- RULES TEST START ----------------------------------


//------------------------------- RULES TEST END ----------------------------------

//------------------------------- RULES PROBLEMS START ----------------------------------

//------------------------------- RULES PROBLEMS START ----------------------------------

//------------------------------- RULES OK START ------------------------------------


    //onlySpecific functions should call solvancy
    rule onlySpecificFunctionsCallSolvency(env e, method f, calldataarg args) filtered {f-> !HARNESS_METHODS(f) &&
        f.selector != sig:permit(address,address,uint256,uint256,uint8,bytes32,bytes32).selector &&
        f.selector != sig:updateHooks().selector &&
        f.selector != sig:approve(address,uint256).selector &&
        f.selector != sig:ShareDebtToken0.callOnBehalfOfShareToken(address,uint256,ISilo.CallType,bytes).selector &&
        f.selector != sig:ShareDebtToken0.decreaseReceiveAllowance(address,uint256).selector &&
        f.selector != sig:ShareDebtToken0.increaseReceiveAllowance(address,uint256).selector &&
        f.selector != sig:ShareDebtToken0.setReceiveApproval(address,uint256).selector       
        }{
        address user;

        //value before
        bool userSolventCalledBefore = solventCalled[user];
        require userSolventCalledBefore == false;

        //call the function
        f(e,args);

        //value after
        bool userSolventAfter = solventCalled[user];

        //check if the value has changed
        assert (userSolventAfter == true => 
                    f.selector == sig:transferFrom(address,address,uint256).selector ||
                    f.selector == sig:transfer(address,uint256).selector ||
                    f.selector == sig:borrow(uint256,address,address).selector ||
                    f.selector == sig:borrowSameAsset(uint256,address,address).selector ||
                    f.selector == sig:borrowShares(uint256,address,address).selector ||
                    f.selector == sig:redeem(uint256,address,address).selector ||
                    f.selector == sig:redeem(uint256,address,address,ISilo.CollateralType).selector ||
                    f.selector == sig:transitionCollateral(uint256,address,ISilo.CollateralType).selector ||
                    f.selector == sig:withdraw(uint256,address,address).selector ||
                    f.selector == sig:withdraw(uint256,address,address,ISilo.CollateralType).selector ||
                    f.selector == sig:switchCollateralToThisSilo().selector
        );

    }

    // transferFrom() CollateralToken solvancyCheck on owner
    rule transferFromCollateralTokenSolvencyCheck(env e) {
        configForEightTokensSetupRequirements();
        address from;
        address to;
        uint256 amount;
        address otherUser;
        threeUsersNotEqual(from,to,otherUser);
        address fromCollateralSilo = siloConfig.borrowerCollateralSilo(e, from);
        require fromCollateralSilo == silo0; //transfer from the relevant silo
        bool transferWithChecks = shareProtectedCollateralToken0.getTransferWithChecks();
        require transferWithChecks == true;

        //value before
        bool fromSolventCalledBefore = solventCalled[from];
        bool toSolventCalledBefore = solventCalled[to];
        bool otherUserSolventCalledBefore = solventCalled[otherUser];
        require fromSolventCalledBefore == false;
        require toSolventCalledBefore == false;
        require otherUserSolventCalledBefore == false;

        //call the function
        shareProtectedCollateralToken0.transferFrom(e,from,to,amount);

        //value after
        bool fromSolventCalledAfter = solventCalled[from];
        bool toSolventCalledAfter = solventCalled[to];
        bool otherUserSolventCalledAfter = solventCalled[otherUser];

        //check if the value has changed
        assert (fromSolventCalledAfter == true);
        assert (toSolventCalledAfter == false);
        assert (otherUserSolventCalledAfter == false);
    }
    
    // transfer() CollateralToken solvancyCheck on msg.sender
    rule transferCollateralTokenSolvencyCheck(env e) {
        configForEightTokensSetupRequirements();
        address to;
        uint256 amount;
        address sender = e.msg.sender;
        address otherUser;
        threeUsersNotEqual(sender,to,otherUser);
        address fromCollateralSilo = siloConfig.borrowerCollateralSilo(e, e.msg.sender);
        require fromCollateralSilo == silo0; //transfer from the relevant silo
        bool transferWithChecks = shareProtectedCollateralToken0.getTransferWithChecks();
        require transferWithChecks == true;

        //value before
        bool toSolventCalledBefore = solventCalled[to];
        bool senderSolventCalledBefore = solventCalled[sender];
        bool otherUserSolventCalledBefore = solventCalled[otherUser];
        require toSolventCalledBefore == false;
        require senderSolventCalledBefore == false;
        require otherUserSolventCalledBefore == false;

        //call the function
        shareProtectedCollateralToken0.transfer(e,to,amount);

        //value after
        bool toSolventCalledAfter = solventCalled[to];
        bool senderSolventCalledAfter = solventCalled[sender];
        bool otherUserSolventCalledAfter = solventCalled[otherUser];

        //check if the value has changed
        assert (toSolventCalledAfter == false);
        assert (senderSolventCalledAfter == true);
        assert (otherUserSolventCalledAfter == false);
    }
    
    // redeem() solvancy is checked on owner
    rule redeemSolvencyCheck(env e) {
        configForEightTokensSetupRequirements();
        uint256 shares;
        address receiver;
        address owner;
        address otherUser;
        threeUsersNotEqual(receiver,owner,otherUser);
        address ownerCollateralSilo = siloConfig.borrowerCollateralSilo(e, owner);
        require ownerCollateralSilo == silo0; //withdraw from the relevant silo
        address ownerDebtSilo = siloConfig.getDebtSilo(owner);
        require ownerDebtSilo != 0; //user has debt 

        //value before
        bool receiverSolventCalledBefore = solventCalled[receiver];
        bool ownerSolventCalledBefore = solventCalled[owner];
        bool otherUserSolventCalledBefore = solventCalled[otherUser];
        require receiverSolventCalledBefore == false;
        require ownerSolventCalledBefore == false;
        require otherUserSolventCalledBefore == false;

        //call the function
        redeem(e, shares, receiver, owner);

        //value after
        bool receiverSolventCalledAfter = solventCalled[receiver];
        bool ownerSolventCalledAfter = solventCalled[owner];
        bool otherUserSolventCalledAfter = solventCalled[otherUser];

        //check if the value has changed
        assert (receiverSolventCalledAfter == false);
        assert (ownerSolventCalledAfter == true);
        assert (otherUserSolventCalledAfter == false);
    }

    // redeem(CollateralType) solvancy is checked on owner
    rule redeemCollateralTypeSolvencyCheck(env e) {
        configForEightTokensSetupRequirements();
        uint256 shares;
        address receiver;
        address owner;
        ISilo.CollateralType collateralType;
        address otherUser;
        threeUsersNotEqual(receiver,owner,otherUser);
        address ownerCollateralSilo = siloConfig.borrowerCollateralSilo(e, owner);
        require ownerCollateralSilo == silo0; //withdraw from the relevant silo
        address ownerDebtSilo = siloConfig.getDebtSilo(owner);
        require ownerDebtSilo != 0; //user has debt 

        //value before
        bool receiverSolventCalledBefore = solventCalled[receiver];
        bool ownerSolventCalledBefore = solventCalled[owner];
        bool otherUserSolventCalledBefore = solventCalled[otherUser];
        require receiverSolventCalledBefore == false;
        require ownerSolventCalledBefore == false;
        require otherUserSolventCalledBefore == false;

        //call the function
        redeem(e, shares, receiver, owner, collateralType);

        //value after
        bool receiverSolventCalledAfter = solventCalled[receiver];
        bool ownerSolventCalledAfter = solventCalled[owner];
        bool otherUserSolventCalledAfter = solventCalled[otherUser];

        //check if the value has changed
        assert (receiverSolventCalledAfter == false);
        assert (ownerSolventCalledAfter == true);
        assert (otherUserSolventCalledAfter == false);
    }

    // transitionCollateral() solvancy is checked on owner
    rule transitionCollateralSolvencyCheck(env e) {
        configForEightTokensSetupRequirements();
        uint256 shares;
        address owner;
        ISilo.CollateralType collateralType;
        address otherUser;
        require(owner != otherUser);
        address ownerCollateralSilo = siloConfig.borrowerCollateralSilo(e, owner);
        require ownerCollateralSilo == silo0; //trnasfering in the relevant silo
        address ownerDebtSilo = siloConfig.getDebtSilo(owner);
        require ownerDebtSilo != 0; //user has debt

        //value before
        bool ownerSolventCalledBefore = solventCalled[owner];
        bool otherUserSolventCalledBefore = solventCalled[otherUser];
        require ownerSolventCalledBefore == false;
        require otherUserSolventCalledBefore == false;

        //call the function
        transitionCollateral(e, shares, owner, collateralType);

        //value after
        bool ownerSolventCalledAfter = solventCalled[owner];
        bool otherUserSolventCalledAfter = solventCalled[otherUser];

        //check if the value has changed
        assert (ownerSolventCalledAfter == true);
        assert (otherUserSolventCalledAfter == false);
    }

    // withdraw() solvancy is checked on owner
    rule withdrawSolvencyCheck(env e) {
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;
        address otherUser;
        threeUsersNotEqual(receiver,owner,otherUser);
        address ownerCollateralSilo = siloConfig.borrowerCollateralSilo(e, owner);
        require ownerCollateralSilo == silo0; //withdraw from the relevant silo
        address ownerDebtSilo = siloConfig.getDebtSilo(owner);
        require ownerDebtSilo != 0; //user has debt 

        //value before
        bool receiverSolventCalledBefore = solventCalled[receiver];
        bool ownerSolventCalledBefore = solventCalled[owner];
        bool otherUserSolventCalledBefore = solventCalled[otherUser];
        require receiverSolventCalledBefore == false;
        require ownerSolventCalledBefore == false;
        require otherUserSolventCalledBefore == false;

        //call the function
        withdraw(e, assets, receiver, owner);

        //value after
        bool receiverSolventCalledAfter = solventCalled[receiver];
        bool ownerSolventCalledAfter = solventCalled[owner];
        bool otherUserSolventCalledAfter = solventCalled[otherUser];

        //check if the value has changed
        assert (receiverSolventCalledAfter == false);
        assert (ownerSolventCalledAfter == true);
        assert (otherUserSolventCalledAfter == false);
    }

    // withdraw(CollateralType) solvancy is checked on owner
    rule withdrawCollateralTypeSolvencyCheck(env e) {
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;
        ISilo.CollateralType collateralType;
        address otherUser;
        threeUsersNotEqual(receiver,owner,otherUser);
        address ownerCollateralSilo = siloConfig.borrowerCollateralSilo(e, owner);
        require ownerCollateralSilo == silo0; //withdraw from the relevant silo
        address ownerDebtSilo = siloConfig.getDebtSilo(owner);
        require ownerDebtSilo != 0; //user has debt 

        //value before
        bool receiverSolventCalledBefore = solventCalled[receiver];
        bool ownerSolventCalledBefore = solventCalled[owner];
        bool otherUserSolventCalledBefore = solventCalled[otherUser];
        require receiverSolventCalledBefore == false;
        require ownerSolventCalledBefore == false;
        require otherUserSolventCalledBefore == false;

        //call the function
        withdraw(e, assets, receiver, owner, collateralType);

        //value after
        bool receiverSolventCalledAfter = solventCalled[receiver];
        bool ownerSolventCalledAfter = solventCalled[owner];
        bool otherUserSolventCalledAfter = solventCalled[otherUser];

        //check if the value has changed
        assert (receiverSolventCalledAfter == false);
        assert (ownerSolventCalledAfter == true);
        assert (otherUserSolventCalledAfter == false);
    }
    
    // transfer() DebtToken solvancyCheck on receiver
    rule transferDebtTokenSolvencyCheck(env e) {
        configForEightTokensSetupRequirements();
        address to;
        uint256 amount;
        address otherUser;
        require(to != otherUser);
        require(e.msg.sender != 0 && to != 0);
        bool transferWithChecks = shareDebtToken0.getTransferWithChecks();
        require transferWithChecks == true;

        //value before
        bool toSolventCalledBefore = solventCalled[to];
        bool otherUserSolventCalledBefore = solventCalled[otherUser];
        require toSolventCalledBefore == false;
        require otherUserSolventCalledBefore == false;

        //call the function
        shareDebtToken0.transfer(e,to,amount);

        //value after
        bool toSolventCalledAfter = solventCalled[to];
        bool otherUserSolventCalledAfter = solventCalled[otherUser];

        //check if the value has changed
        assert (toSolventCalledAfter == true);
        assert (otherUserSolventCalledAfter == false);
    }
    
    // transferFrom() DebtToken solvancyCheck on receiver
    rule transferFromDebtTokenSolvencyCheck(env e) {
        configForEightTokensSetupRequirements();
        address from;
        address to;
        uint256 amount;
        address otherUser;
        threeUsersNotEqual(from,to,otherUser);
        require(from != 0 && to != 0);
        bool transferWithChecks = shareDebtToken0.getTransferWithChecks();
        require transferWithChecks == true;

        //value before
        bool fromSolventCalledBefore = solventCalled[from];
        bool toSolventCalledBefore = solventCalled[to];
        bool otherUserSolventCalledBefore = solventCalled[otherUser];
        require fromSolventCalledBefore == false;
        require toSolventCalledBefore == false;
        require otherUserSolventCalledBefore == false;

        //call the function
        shareDebtToken0.transferFrom(e,from,to,amount);

        //value after
        bool fromSolventCalledAfter = solventCalled[from];
        bool toSolventCalledAfter = solventCalled[to];
        bool otherUserSolventCalledAfter = solventCalled[otherUser];

        //check if the value has changed
        assert (fromSolventCalledAfter == false);
        assert (toSolventCalledAfter == true);
        assert (otherUserSolventCalledAfter == false);
    }
    
    // withdraw() no solvancy check if collateralSilo is not silo0
    rule noSolvencyCheckIfCollateralSiloIsNotSilo0(env e) {
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;
        address otherUser;
        threeUsersNotEqual(receiver,owner,otherUser);
        address ownerCollateralSilo = siloConfig.borrowerCollateralSilo(e, owner);
        require ownerCollateralSilo != silo0; //withdraw from the wrong silo

        //value before
        bool receiverSolventCalledBefore = solventCalled[receiver];
        bool ownerSolventCalledBefore = solventCalled[owner];
        bool otherUserSolventCalledBefore = solventCalled[otherUser];
        require receiverSolventCalledBefore == false;
        require ownerSolventCalledBefore == false;
        require otherUserSolventCalledBefore == false;

        //call the function
        withdraw(e, assets, receiver, owner);

        //value after
        bool receiverSolventCalledAfter = solventCalled[receiver];
        bool ownerSolventCalledAfter = solventCalled[owner];
        bool otherUserSolventCalledAfter = solventCalled[otherUser];

        //check if the value has changed
        assert (receiverSolventCalledAfter == false);
        assert (ownerSolventCalledAfter == false);
        assert (otherUserSolventCalledAfter == false);
    }

    // switchCollateralToThisSilo() solvancy is checked on msg.sender
    rule switchCollateralToThisSiloSolvencyCheck(env e) {
        configForEightTokensSetupRequirements();
        address sender = e.msg.sender;
        address otherUser;
        require(sender != otherUser);
        address senderDebtSilo = siloConfig.getDebtSilo(sender);
        require senderDebtSilo != 0;

        //value before
        bool senderSolventCalledBefore = solventCalled[sender];
        bool otherUserSolventCalledBefore = solventCalled[otherUser];
        require senderSolventCalledBefore == false;
        require otherUserSolventCalledBefore == false;

        //call the function
        switchCollateralToThisSilo(e);

        //value after
        bool senderSolventCalledAfter = solventCalled[sender];
        bool otherUserSolventCalledAfter = solventCalled[otherUser];

        //check if the value has changed
        assert (senderSolventCalledAfter == true);
        assert (otherUserSolventCalledAfter == false);
    }

    //switchCollateralToThisSilo() no solvancy check if debtSilo is 0
    rule noSolvencyCheckIfDebtSiloIs0(env e) {
        configForEightTokensSetupRequirements();
        address sender = e.msg.sender;
        address otherUser;
        threeUsersNotEqual(sender,otherUser,otherUser);
        address senderDebtSilo = siloConfig.getDebtSilo(sender);
        require senderDebtSilo == 0;

        //value before
        bool senderSolventCalledBefore = solventCalled[sender];
        bool otherUserSolventCalledBefore = solventCalled[otherUser];
        require senderSolventCalledBefore == false;
        require otherUserSolventCalledBefore == false;

        //call the function
        switchCollateralToThisSilo(e);

        //value after
        bool senderSolventCalledAfter = solventCalled[sender];
        bool otherUserSolventCalledAfter = solventCalled[otherUser];

        //check if the value has changed
        assert (senderSolventCalledAfter == false);
        assert (otherUserSolventCalledAfter == false);
    }

    // borrow() solvancy is checked on borrower
    rule borrowSolvencyCheck(env e) {
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address borrower;
        address otherUser;
        threeUsersNotEqual(receiver,borrower,otherUser);

        //value before
        bool receiverSolventCalledBefore = solventCalled[receiver];
        bool borrowerSolventCalledBefore = solventCalled[borrower];
        bool otherUserSolventCalledBefore = solventCalled[otherUser];
        require receiverSolventCalledBefore == false;
        require borrowerSolventCalledBefore == false;
        require otherUserSolventCalledBefore == false;

        //call the function
        borrow(e, assets, receiver, borrower);

        //value after
        bool receiverSolventCalledAfter = solventCalled[receiver];
        bool borrowerSolventCalledAfter = solventCalled[borrower];
        bool otherUserSolventCalledAfter = solventCalled[otherUser];

        //check if the value has changed
        assert (receiverSolventCalledAfter == false);
        assert (borrowerSolventCalledAfter == true);
        assert (otherUserSolventCalledAfter == false);
    }
    
    // borrowSameAsset() solvancy is checked on borrower
    rule borrowSameAssetSolvencyCheck(env e) {
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address borrower;
        address otherUser;
        threeUsersNotEqual(receiver,borrower,otherUser);

        //value before
        bool receiverSolventCalledBefore = solventCalled[receiver];
        bool borrowerSolventCalledBefore = solventCalled[borrower];
        bool otherUserSolventCalledBefore = solventCalled[otherUser];
        require receiverSolventCalledBefore == false;
        require borrowerSolventCalledBefore == false;
        require otherUserSolventCalledBefore == false;

        //call the function
        borrowSameAsset(e, assets, receiver, borrower);

        //value after
        bool receiverSolventCalledAfter = solventCalled[receiver];
        bool borrowerSolventCalledAfter = solventCalled[borrower];
        bool otherUserSolventCalledAfter = solventCalled[otherUser];

        //check if the value has changed
        assert (receiverSolventCalledAfter == false);
        assert (borrowerSolventCalledAfter == true);
        assert (otherUserSolventCalledAfter == false);
    }
    
    // borrowShares() solvancy is checked on borrower
    rule borrowSharesSolvencyCheck(env e) {
        configForEightTokensSetupRequirements();
        uint256 shares;
        address receiver;
        address borrower;
        address otherUser;
        threeUsersNotEqual(receiver,borrower,otherUser);

        //value before
        bool receiverSolventCalledBefore = solventCalled[receiver];
        bool borrowerSolventCalledBefore = solventCalled[borrower];
        bool otherUserSolventCalledBefore = solventCalled[otherUser];
        require receiverSolventCalledBefore == false;
        require borrowerSolventCalledBefore == false;
        require otherUserSolventCalledBefore == false;

        //call the function
        borrowShares(e, shares, receiver, borrower);

        //value after
        bool receiverSolventCalledAfter = solventCalled[receiver];
        bool borrowerSolventCalledAfter = solventCalled[borrower];
        bool otherUserSolventCalledAfter = solventCalled[otherUser];

        //check if the value has changed
        assert (receiverSolventCalledAfter == false);
        assert (borrowerSolventCalledAfter == true);
        assert (otherUserSolventCalledAfter == false);
    }
    

//------------------------------- RULES OK END ------------------------------------

//------------------------------- INVARIENTS OK START-------------------------------

//------------------------------- INVARIENTS OK END-------------------------------

//------------------------------- ISSUES OK START-------------------------------

//------------------------------- ISSUES OK END-------------------------------

//-------------------------------OLD RULES START----------------------------------
    //@title The flag transferWithChecks is always on at then end of all public methods  
    rule transferWithChecksAlwaysOn(method f)  filtered {f-> !onlySiloContractsMethods(f) && !f.isView &&
        f.selector != sig:ShareDebtToken0.callOnBehalfOfShareToken(address,uint256,ISilo.CallType,bytes).selector &&
        f.selector != sig:assetsBorrowerForLTVHarness(ISiloConfig.ConfigData,ISiloConfig.ConfigData,address,ISilo.OracleType,ISilo.AccrueInterestInMemory).selector
        }
    {
        env e;
        calldataarg args;
        configForEightTokensSetupRequirements();
        nonSceneAddressRequirements(e.msg.sender);
        silosTimestampSetupRequirements(e);

        require allTransferWithChecks();
        f(e,args);
        assert allTransferWithChecks();
    }

    //@title Solvency check has been performed on the correct user 
    rule solventChecked(method f)  filtered {f-> !onlySiloContractsMethods(f) && !f.isView &&
        f.selector != sig:ShareDebtToken0.callOnBehalfOfShareToken(address,uint256,ISilo.CallType,bytes).selector &&
        f.selector != sig:assetsBorrowerForLTVHarness(ISiloConfig.ConfigData,ISiloConfig.ConfigData,address,ISilo.OracleType,ISilo.AccrueInterestInMemory).selector
        }
    {
        env e;
        address user; 
        SafeAssumptions_withInvariants(e, user);
        completeSiloSetupForEnv(e);
        require silo0.getSiloFromStorage(e) == silo0;
        require silo1.getSiloFromStorage(e) == silo1;

        accrueHasBeenCalled(e);

        require allTransferWithChecks(); 

        require silo0 == siloConfig.borrowerCollateralSilo[user];
        
        uint256 userCollateralBalancePre = silo0.balanceOf(e,user);
        uint256 userDebt0BalancePre = shareDebtToken0.balanceOf(user);
        uint256 userDebt1BalancePre = shareDebtToken1.balanceOf(user);
        
        if (f.selector == sig:Silo0.transferFrom(address,address,uint256).selector) {
            address from;
            address to;
            uint256 amount;
            totalSuppliesMoreThanThreeBalances(from,to,silo0);
            silo0.transferFrom(e,from,to,amount);
        }
        else {
            calldataarg args;
            f(e,args);
        }
        uint256 userCollateralBalancePost = silo0.balanceOf(e,user);
        uint256 userDebt0BalancePost = shareDebtToken0.balanceOf(user);
        uint256 userDebt1BalancePost = shareDebtToken1.balanceOf(user);
        

        assert  ( ( userCollateralBalancePre > userCollateralBalancePost && (userDebt0BalancePost!=0 || userDebt1BalancePost!=0)) || 
                    userDebt0BalancePre < userDebt0BalancePost ||
                    userDebt1BalancePre < userDebt1BalancePost ) =>

                solventCalled[user]; 
    }
//-------------------------------OLD RULES END----------------------------------
