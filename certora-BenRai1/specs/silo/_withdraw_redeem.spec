/* Rules concerning withdraw and redeem  */

import "../setup/CompleteSiloSetup.spec";
import "./0base_Silo.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";
import "../simplifications/_Oracle_call_before_quote_UNSAFE.spec";
import "../simplifications/Oracle_quote_one_UNSAFE.spec";


//------------------------------- RULES TEST START ----------------------------------



    //------------------------- REDEEM SAME AS WITHDRAW ------------------------------

        // // withdraw / redeem: same assets 
        // rule withdrawRedeemSameAssets(env e){ //@audit timed out, running again
        //     configForEightTokensSetupRequirements();
        //     uint256 range = 3;
        //     uint256 assets;
        //     address receiver;
        //     address owner;
        //     address otherUser;
        //     threeUsersNotEqual(owner, receiver, otherUser);

        //     //init state
        //     storage init = lastStorage;

        //     //withdraw
        //     uint256 shares = withdraw(e, assets, receiver, owner) at init;

        //     //state after withdraw
        //     uint256 protectedAssetsBalanceOwnerAfterWithdraw;
        //     uint256 collateralAssetsBalanceOwnerAfterWithdraw;
        //     uint256 debtAssetsBalanceOwnerAfterWithdraw;
        //     (protectedAssetsBalanceOwnerAfterWithdraw, collateralAssetsBalanceOwnerAfterWithdraw, debtAssetsBalanceOwnerAfterWithdraw) = silo0.totalAssetsHarness(e);

        //     //redeem
        //     redeem(e, shares, receiver, owner) at init;

        //     //state after redeem
        //     uint256 protectedAssetsBalanceOwnerAfterRedeem;
        //     uint256 collateralAssetsBalanceOwnerAfterRedeem;
        //     uint256 debtAssetsBalanceOwnerAfterRedeem;
        //     (protectedAssetsBalanceOwnerAfterRedeem, collateralAssetsBalanceOwnerAfterRedeem, debtAssetsBalanceOwnerAfterRedeem) = silo0.totalAssetsHarness(e);

        //     //withdraw and redeem: same assets
        //     assert protectedAssetsBalanceOwnerAfterWithdraw == protectedAssetsBalanceOwnerAfterRedeem;
        //     assert cvlApproxSameWithRange(collateralAssetsBalanceOwnerAfterWithdraw, collateralAssetsBalanceOwnerAfterRedeem, range);
        //     assert debtAssetsBalanceOwnerAfterWithdraw == debtAssetsBalanceOwnerAfterRedeem;
        // }

        // // withdraw / redeem PROTECTED: same assets 
        // rule withdrawRedeemProtectedSameAssets(env e){ //@audit timed out, running again
        //     configForEightTokensSetupRequirements();
        //     uint256 range = 3;
        //     uint256 assets;
        //     address receiver;
        //     address owner;
        //     address otherUser;
        //     threeUsersNotEqual(owner, receiver, otherUser);

        //     //init state
        //     storage init = lastStorage;

        //     //withdraw
        //     uint256 shares = withdraw(e, assets, receiver, owner, ISilo.CollateralType.Protected) at init;

        //     //state after withdraw
        //     uint256 protectedAssetsAfterWithdraw;
        //     uint256 collateralAssetsAfterWithdraw;
        //     uint256 debtAssetsAfterWithdraw;
        //     (protectedAssetsAfterWithdraw, collateralAssetsAfterWithdraw, debtAssetsAfterWithdraw) = silo0.totalAssetsHarness(e);

        //     //redeem
        //     redeem(e, shares, receiver, owner, ISilo.CollateralType.Protected) at init;

        //     //state after redeem
        //     uint256 protectedAssetsAfterRedeem;
        //     uint256 collateralAssetsAfterRedeem;
        //     uint256 debtAssetsAfterRedeem;
        //     (protectedAssetsAfterRedeem, collateralAssetsAfterRedeem, debtAssetsAfterRedeem) = silo0.totalAssetsHarness(e);

        //     //withdraw and redeem: same assets
        //     assert cvlApproxSameWithRange(protectedAssetsAfterWithdraw, protectedAssetsAfterRedeem, range);
        //     assert collateralAssetsAfterWithdraw == collateralAssetsAfterRedeem;
        //     assert debtAssetsAfterWithdraw == debtAssetsAfterRedeem;
        // }

    //---------------------------------------------------------------------------------------
        


    // // withdraw( protected) should never revert because of to little liquidity
    // rule withdrawProtectedDoesNotRevertWithoutDebt(env e){
    //     configForEightTokensSetupRequirements();
    //     uint256 assets;
    //     address receiver;
    //     address owner;

    //     uint256 protectedAssetsBefore;
    //     uint256 collateralAssetsBefore;
    //     uint256 debtAssetsBefore;
    //     (protectedAssetsBefore, collateralAssetsBefore, debtAssetsBefore) = silo0.totalAssetsHarness(e);
        
    //     //protectedShares owner
    //     address collateralSiloOwner = borrowerCollateralSiloHarness(owner);
    //     //owner has no debt
    //     require (collateralSiloOwner == 0);
        
    //     //debt of owner
    //     uint256 debtShares0BalanceOwnerBefore = shareDebtToken0.balanceOf(owner);
    //     uint256 debtShares1BalanceOwnerBefore = shareDebtToken1.balanceOf(owner);



    //     //withdraw
    //     withdraw@withrevert(e, assets, receiver, owner, ISilo.CollateralType.Protected);

    //     //did not revert
    //     assert !lastReverted;
    // }

    // // * result of `maxWithdraw()` should never be more than liquidity of the Silo  //@audit timed out, running again
    rule maxWithdrawAssetsDoesNotExceedLiquidity(env e){
        configForEightTokensSetupRequirements();
        address owner;

        uint256 liquidity = silo0.getLiquidity(e);
        uint256 maxWithdraw = silo0.maxWithdraw(e, owner);

        assert maxWithdraw <= liquidity;
    }

   

    // * `withdraw()` should never revert if liquidity for a user and a silo is sufficient even if oracle reverts
    // * result of `maxWithdraw()` used as input to withdraw() should never revert
    // * if user has no debt and liquidity is available, shareToken.balanceOf(user) used as input to redeem(), assets from redeem() should be equal to maxWithdraw()
    // borrowerCollateralSiloHarness is not 0 if user has debtShareTokens
    // if borrowerCollateralSiloHarness is not 0 is silo0 or silo1 
    // if borrowerCollateralSiloHarness is not 0, user has some debtShareTokens 
    // protectedAsset are always bigger than 0 if there are protectedCollateralShares (where are they changed?)
    //maxRedeem is never bigger than shares of the owner (protected and normal collateral shares)






//------------------------------- RULES TEST END ----------------------------------

//------------------------------- RULES PROBLEMS START ----------------------------------







        
      
    // // * result of `previewWithdraw()` should be equal to result of `withdraw()` //@audit fails
    // rule previewWithdrawIsEqualToWithdraw(env e){
    //     configForEightTokensSetupRequirements();
    //     uint256 assets;
    //     address receiver;
    //     address owner = e.msg.sender;

    //     uint256 previewWithdrawShares = previewWithdraw(e, assets);
    //     uint256 withdrawShares = withdraw(e, assets, receiver, owner);
    //     assert previewWithdrawShares == withdrawShares;
    // }
  
    // // withdraw / redeem: same underlyingToken
    // rule withdrawRedeemSameUnderlyingToken(env e){ //@audit aproximation does not work
    //     configForEightTokensSetupRequirements();
    //     uint256 range = 3;
    //     uint256 assets;
    //     address receiver;
    //     address owner;
    //     address otherUser;
    //     threeUsersNotEqual(owner, receiver, otherUser);

    //     //values before
    //     uint256 receiverUnderlyingTokenBalance = token0.balanceOf(receiver);
    //     require(receiverUnderlyingTokenBalance + assets >= max_uint256 - 50);

    //     //init state
    //     storage init = lastStorage;

    //     //withdraw
    //     uint256 shares = withdraw(e, assets, receiver, owner) at init;

    //     //state after withdraw
    //     uint256 underlyingTokenBalanceOwnerAfterWithdraw = token0.balanceOf(owner);
    //     uint256 underlyingTokenBalanceReceiverAfterWithdraw = token0.balanceOf(receiver);
    //     uint256 underlyingTokenBalanceOtherUserAfterWithdraw = token0.balanceOf(otherUser);
    //     uint256 underlyingTokenBalanceSiloAfterWithdraw = token0.balanceOf(silo0);

    //     //redeem
    //     redeem(e, shares, receiver, owner) at init;

    //     //state after redeem
    //     uint256 underlyingTokenBalanceOwnerAfterRedeem = token0.balanceOf(owner);
    //     uint256 underlyingTokenBalanceReceiverAfterRedeem = token0.balanceOf(receiver);
    //     uint256 underlyingTokenBalanceOtherUserAfterRedeem = token0.balanceOf(otherUser);
    //     uint256 underlyingTokenBalanceSiloAfterRedeem = token0.balanceOf(silo0);

    //     //withdraw and redeem: same underlyingToken
    //     assert underlyingTokenBalanceOwnerAfterWithdraw == underlyingTokenBalanceOwnerAfterRedeem;
    //     assert cvlApproxSameWithRange(underlyingTokenBalanceReceiverAfterWithdraw, underlyingTokenBalanceReceiverAfterRedeem, range);
    //     assert underlyingTokenBalanceOtherUserAfterWithdraw == underlyingTokenBalanceOtherUserAfterRedeem;
    //     assert cvlApproxSameWithRange(underlyingTokenBalanceSiloAfterWithdraw, underlyingTokenBalanceSiloAfterRedeem, range);
    // }

    // // withdraw / redeem PROTECTED: same underlyingToken
    // rule withdrawRedeemProtectedSameUnderlyingToken(env e){ //@audit overflow and a range of 5 would be needed
    //     configForEightTokensSetupRequirements();
    //     uint256 range = 2;
    //     uint256 assets;
    //     address receiver;
    //     address owner;
    //     address otherUser;
    //     threeUsersNotEqual(owner, receiver, otherUser);

    //     //values before
    //     uint256 receiverUnderlyingTokenBalance = token0.balanceOf(receiver);
    //     require(receiverUnderlyingTokenBalance + assets >= max_uint256 - 50);

    //     //init state
    //     storage init = lastStorage;

    //     //withdraw
    //     uint256 shares = withdraw(e, assets, receiver, owner, ISilo.CollateralType.Protected) at init;

    //     //state after withdraw
    //     uint256 underlyingTokenBalanceOwnerAfterWithdraw = token0.balanceOf(owner);
    //     uint256 underlyingTokenBalanceReceiverAfterWithdraw = token0.balanceOf(receiver);
    //     uint256 underlyingTokenBalanceOtherUserAfterWithdraw = token0.balanceOf(otherUser);
    //     uint256 underlyingTokenBalanceSiloAfterWithdraw = token0.balanceOf(silo0);

    //     //redeem
    //     redeem(e, shares, receiver, owner, ISilo.CollateralType.Protected) at init;

    //     //state after redeem
    //     uint256 underlyingTokenBalanceOwnerAfterRedeem = token0.balanceOf(owner);
    //     uint256 underlyingTokenBalanceReceiverAfterRedeem = token0.balanceOf(receiver);
    //     uint256 underlyingTokenBalanceOtherUserAfterRedeem = token0.balanceOf(otherUser);
    //     uint256 underlyingTokenBalanceSiloAfterRedeem = token0.balanceOf(silo0);

    //     //withdraw and redeem: same underlyingToken
    //     assert underlyingTokenBalanceOwnerAfterWithdraw == underlyingTokenBalanceOwnerAfterRedeem;
    //     assert cvlApproxSameWithRange(underlyingTokenBalanceReceiverAfterWithdraw, underlyingTokenBalanceReceiverAfterRedeem, range);
    //     assert underlyingTokenBalanceOtherUserAfterWithdraw == underlyingTokenBalanceOtherUserAfterRedeem;
    //     assert cvlApproxSameWithRange(underlyingTokenBalanceSiloAfterWithdraw, underlyingTokenBalanceSiloAfterRedeem, range);
    // }

    // //withdraw if insolvent, no withdraw possible //@audit time out
    rule ifInsolventNoWithdrawPossible(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;

        bool solventBefore = silo0.isSolvent(e,owner);
        require(!solventBefore);
        address collateralSiloOwner = siloConfig.borrowerCollateralSilo(e, owner);
        //called silo must be collateralSilo
        require(collateralSiloOwner == silo0);

        //withdraw
        withdraw@withrevert(e, assets, receiver, owner);

        //reverted
        assert lastReverted;
    }

    // //withdraw Protected if insolvent, no withdraw possible
    rule ifInsolventNoProtectedWithdrawPossible(env e){ //@audit timeout
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;

        bool solventBefore = silo0.isSolvent(e,owner);
        require(!solventBefore);
        address collateralSiloOwner = siloConfig.borrowerCollateralSilo(e, owner);
        //called silo must be collateralSilo
        require(collateralSiloOwner == silo0);

        //withdraw
        withdraw@withrevert(e, assets, receiver, owner, ISilo.CollateralType.Protected);

        //reverted
        assert lastReverted;
    }

//------------------------------- RULES PROBLEMS START ----------------------------------

//------------------------------- RULES OK START ------------------------------------


    // withdraw() can not withdraw more than liquidity 
    rule withdrawCanNotWithdrawMoreThanLiquidity(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;

        uint256 liquidity = getLiquidity(e);
        require(assets > liquidity);

        //withdraw
        withdraw@withrevert(e, assets, receiver, owner);

        //reverted if assest > liquidity
        assert lastReverted;
    }


    // withdraw( protected) can not make owner insolvent
    rule withdrawProtectedCanNotMakeOwnerInSolvent(env e){ 
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;

        bool solventBefore = silo0.isSolvent(e,owner);
        require(solventBefore);


        //withdraw
        withdraw(e, assets, receiver, owner, ISilo.CollateralType.Protected);

        bool solventAfter = silo0.isSolvent(e,owner);

        //owner is still solvent
        assert solventAfter == true;
    }

    //reddeem is the same as redeem (collateralAssets)
    rule redeemIsTheSameAsRedeemCollateralAssets(env e){ 
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;

        storage init = lastStorage;
        
        //redeem
        redeem(e, assets, receiver, owner);

        storage afterRedeem = lastStorage;

        redeem(e, assets, receiver, owner, ISilo.CollateralType.Collateral) at init;

        storage afterRedeemCollateral = lastStorage;

        assert afterRedeem == afterRedeemCollateral;
    }

    // withdraw / redeem: same collateralShare
    rule withdrawRedeemSameCollateralShares(env e){
        configForEightTokensSetupRequirements();
        uint256 range = 2;
        uint256 assets;
        address receiver;
        address owner;
        address otherUser;
        threeUsersNotEqual(owner, receiver, otherUser);

        //init state
        storage init = lastStorage;

        //balances before
        uint256 collateralSharesBalanceOwnerBefore = silo0.balanceOf(owner);
        totalSuppliesMoreThanBalance(owner);

        //withdraw
        uint256 shares = withdraw(e, assets, receiver, owner) at init;
        require(collateralSharesBalanceOwnerBefore >= shares);

        //state after withdraw
        uint256 collateralSharesBalanceOwnerAfterWithdraw = silo0.balanceOf(owner);
        uint256 collateralSharesBalanceReceiverAfterWithdraw = silo0.balanceOf(receiver);
        uint256 collateralSharesBalanceOtherUserAfterWithdraw = silo0.balanceOf(otherUser);
        uint256 collateralSharesTotalSupplyAfterWithdraw = silo0.totalSupply();

        //redeem
        redeem(e, shares, receiver, owner) at init;

        //state after redeem
        uint256 collateralSharesBalanceOwnerAfterRedeem = silo0.balanceOf(owner);
        uint256 collateralSharesBalanceReceiverAfterRedeem = silo0.balanceOf(receiver);
        uint256 collateralSharesBalanceOtherUserAfterRedeem = silo0.balanceOf(otherUser);
        uint256 collateralSharesTotalSupplyAfterRedeem = silo0.totalSupply();

        //withdraw and redeem: same collateralShares
        assert cvlApproxSameWithRange(collateralSharesBalanceOwnerAfterWithdraw, collateralSharesBalanceOwnerAfterRedeem, range);
        assert collateralSharesBalanceReceiverAfterWithdraw == collateralSharesBalanceReceiverAfterRedeem;
        assert collateralSharesBalanceOtherUserAfterWithdraw == collateralSharesBalanceOtherUserAfterRedeem;
        assert cvlApproxSameWithRange(collateralSharesTotalSupplyAfterWithdraw, collateralSharesTotalSupplyAfterRedeem, range);
    }

    // withdraw can not make owner insolvent
    rule withdrawCanNotMakeOwnerInSolvent(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;

        bool solventBefore = silo0.isSolvent(e,owner);
        require(solventBefore);


        //withdraw
        withdraw(e, assets, receiver, owner);

        bool solventAfter = silo0.isSolvent(e,owner);

        //owner is still solvent
        assert solventAfter == true;
    }

    // withdraw / redeem: same protectedCollateralShare
    rule withdrawRedeemSameProtectedCollateralShares(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;
        address otherUser;
        threeUsersNotEqual(owner, receiver, otherUser);

        //init state
        storage init = lastStorage;

        //withdraw
        uint256 shares = withdraw(e, assets, receiver, owner) at init;

        //state after withdraw
        uint256 protectedSharesBalanceOwnerAfterWithdraw = shareProtectedCollateralToken0.balanceOf(owner);
        uint256 protectedSharesBalanceReceiverAfterWithdraw = shareProtectedCollateralToken0.balanceOf(receiver);
        uint256 protectedSharesBalanceOtherUserAfterWithdraw = shareProtectedCollateralToken0.balanceOf(otherUser);
        uint256 protectedSharesTotalSupplyAfterWithdraw = shareProtectedCollateralToken0.totalSupply();

        //redeem
        redeem(e, shares, receiver, owner) at init;

        //state after redeem
        uint256 protectedSharesBalanceOwnerAfterRedeem = shareProtectedCollateralToken0.balanceOf(owner);
        uint256 protectedSharesBalanceReceiverAfterRedeem = shareProtectedCollateralToken0.balanceOf(receiver);
        uint256 protectedSharesBalanceOtherUserAfterRedeem = shareProtectedCollateralToken0.balanceOf(otherUser);
        uint256 protectedSharesTotalSupplyAfterRedeem = shareProtectedCollateralToken0.totalSupply();

        //withdraw and redeem: same protectedCollateralShares
        assert protectedSharesBalanceOwnerAfterWithdraw == protectedSharesBalanceOwnerAfterRedeem;
        assert protectedSharesBalanceReceiverAfterWithdraw == protectedSharesBalanceReceiverAfterRedeem;
        assert protectedSharesBalanceOtherUserAfterWithdraw == protectedSharesBalanceOtherUserAfterRedeem;
        assert protectedSharesTotalSupplyAfterWithdraw == protectedSharesTotalSupplyAfterRedeem;
    }

    // withdraw / redeem PROTECTED: same debtShare
    rule withdrawRedeemProtectedSameDebtShares(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;
        address otherUser;
        threeUsersNotEqual(owner, receiver, otherUser);

        //init state
        storage init = lastStorage;

        //withdraw
        uint256 shares = withdraw(e, assets, receiver, owner, ISilo.CollateralType.Protected) at init;

        //state after withdraw
        uint256 debtSharesBalanceOwnerAfterWithdraw = shareDebtToken0.balanceOf(owner);
        uint256 debtSharesBalanceReceiverAfterWithdraw = shareDebtToken0.balanceOf(receiver);
        uint256 debtSharesBalanceOtherUserAfterWithdraw = shareDebtToken0.balanceOf(otherUser);
        uint256 debtSharesTotalSupplyAfterWithdraw = shareDebtToken0.totalSupply();

        //redeem
        redeem(e, shares, receiver, owner, ISilo.CollateralType.Protected) at init;

        //state after redeem
        uint256 debtSharesBalanceOwnerAfterRedeem = shareDebtToken0.balanceOf(owner);
        uint256 debtSharesBalanceReceiverAfterRedeem = shareDebtToken0.balanceOf(receiver);
        uint256 debtSharesBalanceOtherUserAfterRedeem = shareDebtToken0.balanceOf(otherUser);
        uint256 debtSharesTotalSupplyAfterRedeem = shareDebtToken0.totalSupply();

        //withdraw and redeem: same debtShares
        assert debtSharesBalanceOwnerAfterWithdraw == debtSharesBalanceOwnerAfterRedeem;
        assert debtSharesBalanceReceiverAfterWithdraw == debtSharesBalanceReceiverAfterRedeem;
        assert debtSharesBalanceOtherUserAfterWithdraw == debtSharesBalanceOtherUserAfterRedeem;
        assert debtSharesTotalSupplyAfterWithdraw == debtSharesTotalSupplyAfterRedeem;
    }


    // withdraw / redeem PROTECTED: same collateralShare
    rule withdrawRedeemProtectedSameCollateralShares(env e){
        configForEightTokensSetupRequirements();
        uint256 range = 2;
        uint256 assets;
        address receiver;
        address owner;
        address otherUser;
        threeUsersNotEqual(owner, receiver, otherUser);

        //init state
        storage init = lastStorage;

        //withdraw
        uint256 shares = withdraw(e, assets, receiver, owner, ISilo.CollateralType.Protected) at init;

        //state after withdraw
        uint256 collateralSharesBalanceOwnerAfterWithdraw = silo0.balanceOf(owner);
        uint256 collateralSharesBalanceReceiverAfterWithdraw = silo0.balanceOf(receiver);
        uint256 collateralSharesBalanceOtherUserAfterWithdraw = silo0.balanceOf(otherUser);
        uint256 collateralSharesTotalSupplyAfterWithdraw = silo0.totalSupply();

        //redeem
        redeem(e, shares, receiver, owner, ISilo.CollateralType.Protected) at init;
        
        //state after redeem
        uint256 collateralSharesBalanceOwnerAfterRedeem = silo0.balanceOf(owner);
        uint256 collateralSharesBalanceReceiverAfterRedeem = silo0.balanceOf(receiver);
        uint256 collateralSharesBalanceOtherUserAfterRedeem = silo0.balanceOf(otherUser);
        uint256 collateralSharesTotalSupplyAfterRedeem = silo0.totalSupply();

        //withdraw and redeem: same collateralShares
        assert collateralSharesBalanceOwnerAfterWithdraw == collateralSharesBalanceOwnerAfterRedeem;
        assert collateralSharesBalanceReceiverAfterWithdraw == collateralSharesBalanceReceiverAfterRedeem;
        assert collateralSharesBalanceOtherUserAfterWithdraw == collateralSharesBalanceOtherUserAfterRedeem;
        assert collateralSharesTotalSupplyAfterWithdraw == collateralSharesTotalSupplyAfterRedeem;
    }

    // withdraw / redeem: same debtShare
    rule withdrawRedeemSameDebtShares(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;
        address otherUser;
        threeUsersNotEqual(owner, receiver, otherUser);

        //init state
        storage init = lastStorage;

        //withdraw
        uint256 shares = withdraw(e, assets, receiver, owner) at init;

        //state after withdraw
        uint256 debtSharesBalanceOwnerAfterWithdraw = shareDebtToken0.balanceOf(owner);
        uint256 debtSharesBalanceReceiverAfterWithdraw = shareDebtToken0.balanceOf(receiver);
        uint256 debtSharesBalanceOtherUserAfterWithdraw = shareDebtToken0.balanceOf(otherUser);
        uint256 debtSharesTotalSupplyAfterWithdraw = shareDebtToken0.totalSupply();

        //redeem
        redeem(e, shares, receiver, owner) at init;

        //state after redeem
        uint256 debtSharesBalanceOwnerAfterRedeem = shareDebtToken0.balanceOf(owner);
        uint256 debtSharesBalanceReceiverAfterRedeem = shareDebtToken0.balanceOf(receiver);
        uint256 debtSharesBalanceOtherUserAfterRedeem = shareDebtToken0.balanceOf(otherUser);
        uint256 debtSharesTotalSupplyAfterRedeem = shareDebtToken0.totalSupply();

        //withdraw and redeem: same debtShares
        assert debtSharesBalanceOwnerAfterWithdraw == debtSharesBalanceOwnerAfterRedeem;
        assert debtSharesBalanceReceiverAfterWithdraw == debtSharesBalanceReceiverAfterRedeem;
        assert debtSharesBalanceOtherUserAfterWithdraw == debtSharesBalanceOtherUserAfterRedeem;
        assert debtSharesTotalSupplyAfterWithdraw == debtSharesTotalSupplyAfterRedeem;
    }

    // withdraw / redeem PROTECTED: same protectedCollateralShare
    rule withdrawRedeemProtectedSameProtectedCollateralShares(env e){
        configForEightTokensSetupRequirements();
        uint256 range = 2;
        uint256 assets;
        address receiver;
        address owner;
        address otherUser;
        threeUsersNotEqual(owner, receiver, otherUser);

        //init state
        storage init = lastStorage;

        //withdraw
        uint256 shares = withdraw(e, assets, receiver, owner, ISilo.CollateralType.Protected) at init;

        //state after withdraw
        uint256 protectedSharesBalanceOwnerAfterWithdraw = shareProtectedCollateralToken0.balanceOf(owner);
        uint256 protectedSharesBalanceReceiverAfterWithdraw = shareProtectedCollateralToken0.balanceOf(receiver);
        uint256 protectedSharesBalanceOtherUserAfterWithdraw = shareProtectedCollateralToken0.balanceOf(otherUser);
        uint256 protectedSharesTotalSupplyAfterWithdraw = shareProtectedCollateralToken0.totalSupply();

        //redeem
        redeem(e, shares, receiver, owner, ISilo.CollateralType.Protected) at init;

        //state after redeem
        uint256 protectedSharesBalanceOwnerAfterRedeem = shareProtectedCollateralToken0.balanceOf(owner);
        uint256 protectedSharesBalanceReceiverAfterRedeem = shareProtectedCollateralToken0.balanceOf(receiver);
        uint256 protectedSharesBalanceOtherUserAfterRedeem = shareProtectedCollateralToken0.balanceOf(otherUser);
        uint256 protectedSharesTotalSupplyAfterRedeem = shareProtectedCollateralToken0.totalSupply();

        //withdraw and redeem: same protectedCollateralShares
        assert cvlApproxSameWithRange(protectedSharesBalanceOwnerAfterWithdraw, protectedSharesBalanceOwnerAfterRedeem, range);
        assert protectedSharesBalanceReceiverAfterWithdraw == protectedSharesBalanceReceiverAfterRedeem;
        assert protectedSharesBalanceOtherUserAfterWithdraw == protectedSharesBalanceOtherUserAfterRedeem;
        assert cvlApproxSameWithRange(protectedSharesTotalSupplyAfterWithdraw, protectedSharesTotalSupplyAfterRedeem, range);
    }

    // withdraw() is the same as withdraw(collateralAssets)
    rule withdrawIsTheSameAsWithdrawCollateralAssets(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;

        storage init = lastStorage;
        
        //withdraw
        withdraw(e, assets, receiver, owner);

        storage afterWithdraw = lastStorage;

        withdraw(e, assets, receiver, owner, ISilo.CollateralType.Collateral) at init;

        storage afterWithdrawCollateral = lastStorage;

        assert afterWithdraw == afterWithdrawCollateral;
    }

    // withdraw() decreases collateralAssets by assets, debtAssets and protectedCollateralAssets stay the same
    rule withdrawDecreasesCollateralAssets(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;

        // assets before withdraw
        uint256 collateralAssetsBefore;
        uint256 protectedCollateralAssetsBefore;
        uint256 debtAssetsBefore;
        (protectedCollateralAssetsBefore, collateralAssetsBefore, debtAssetsBefore) = silo0.totalAssetsHarness(e);

        //withdraw
        withdraw(e, assets, receiver, owner);

        // assets after withdraw
        uint256 collateralAssetsAfter;
        uint256 protectedCollateralAssetsAfter;
        uint256 debtAssetsAfter;
        (protectedCollateralAssetsAfter, collateralAssetsAfter, debtAssetsAfter) = silo0.totalAssetsHarness(e);

        //collateralAssets decreased by assets
        assert collateralAssetsAfter == collateralAssetsBefore - assets;
        //protectedCollateralAssets did not change
        assert protectedCollateralAssetsBefore == protectedCollateralAssetsAfter;
        //debtAssets did not change
        assert debtAssetsBefore == debtAssetsAfter;
    }

    // withdraw( protected) decreases totalSupply of protected shares by dif for owner
    rule withdrawProtectedReducesTotalSupplyOfProtectedShares(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;

        //totalSupply of protected shares before withdraw
        uint256 protectedSharesTotalSupplyBefore = shareProtectedCollateralToken0.totalSupply();
        uint256 protectedSharesBalanceOwnerBefore = shareProtectedCollateralToken0.balanceOf(owner);
        require(protectedSharesTotalSupplyBefore >= protectedSharesBalanceOwnerBefore);

        //withdraw
        withdraw(e, assets, receiver, owner, ISilo.CollateralType.Protected);

        //totalSupply of protected shares after withdraw
        uint256 protectedSharesTotalSupplyAfter = shareProtectedCollateralToken0.totalSupply();
        uint256 protectedSharesBalanceOwnerAfter = shareProtectedCollateralToken0.balanceOf(owner);

        //totalSupply of protected shares decreased by dif
        assert protectedSharesTotalSupplyAfter == protectedSharesTotalSupplyBefore + protectedSharesBalanceOwnerAfter - protectedSharesBalanceOwnerBefore;
    }


    // withdraw( protected) increases underlyingToken for receiver by assets, decreases the balance of silo accordingly and does not change for owner or receiver
    rule withdrawProtectedIncreasesUnderlyingTokenForReceiver(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        nonSceneAddressRequirements(receiver);
        address owner;
        nonSceneAddressRequirements(owner);
        address otherUser;
        nonSceneAddressRequirements(otherUser);
        require(owner != receiver);
        require(otherUser != receiver);

        //underlyingToken balances before 
        uint256 underlyingTokenBalanceReceiverBefore = token0.balanceOf(receiver);
        uint256 underlyingTokenBalanceOwnerBefore = token0.balanceOf(owner);
        uint256 underlyingTokenBalanceOtherUserBefore = token0.balanceOf(otherUser);
        uint256 underlyingTokenBalanceSiloBefore = token0.balanceOf(silo0);
        totalSuppliesMoreThanBalances(receiver, silo0);

        //withdraw
        withdraw(e, assets, receiver, owner, ISilo.CollateralType.Protected);

        //underlyingToken balances after
        uint256 underlyingTokenBalanceReceiverAfter = token0.balanceOf(receiver);
        uint256 underlyingTokenBalanceOwnerAfter = token0.balanceOf(owner);
        uint256 underlyingTokenBalanceOtherUserAfter = token0.balanceOf(otherUser);
        uint256 underlyingTokenBalanceSiloAfter = token0.balanceOf(silo0);

        //underlyingToken of receiver increased by assets
        assert underlyingTokenBalanceReceiverAfter == underlyingTokenBalanceReceiverBefore + assets;
        //underlyingToken of owner did not change
        assert underlyingTokenBalanceOwnerBefore == underlyingTokenBalanceOwnerAfter;
        //underlyingToken of other user did not change
        assert underlyingTokenBalanceOtherUserBefore == underlyingTokenBalanceOtherUserAfter;
        //underlyingToken of silo decreased by assets
        assert underlyingTokenBalanceSiloAfter == underlyingTokenBalanceSiloBefore - assets;
    }
    
    // withdraw( protected) does not change totalSupply or balance for borrower for debt and Collateral shares
    rule withdrawProtectedDoesNotChangeDebtOrCollateralShares(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;

        //totalSupply and balance of owner before withdraw
        uint256 debtSharesTotalBalanceBefore = shareDebtToken0.totalSupply();
        uint256 collateralSharesTotalBalanceBefore = silo0.totalSupply();
        uint256 debtSharesBalanceOwnerBefore = shareDebtToken0.balanceOf(owner);
        uint256 collateralSharesBalanceOwnerBefore = silo0.balanceOf(owner);

        //withdraw
        withdraw(e, assets, receiver, owner, ISilo.CollateralType.Protected);

        //totalSupply and balance of owner after withdraw
        uint256 debtSharesTotalBalanceAfter = shareDebtToken0.totalSupply();
        uint256 collateralSharesTotalBalanceAfter = silo0.totalSupply();
        uint256 debtSharesBalanceOwnerAfter = shareDebtToken0.balanceOf(owner);
        uint256 collateralSharesBalanceOwnerAfter = silo0.balanceOf(owner);

        //totalSupply and balance of owner did not change
        assert debtSharesTotalBalanceBefore == debtSharesTotalBalanceAfter;
        assert collateralSharesTotalBalanceBefore == collateralSharesTotalBalanceAfter;
        assert debtSharesBalanceOwnerBefore == debtSharesBalanceOwnerAfter;
        assert collateralSharesBalanceOwnerBefore == collateralSharesBalanceOwnerAfter;
    }

    // withdraw( protected) does not change any shares for other user or receiver
    rule withdrawProtectedDoesNotChangeSharesOfOthers(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;
        address otherUser;
        require(owner != otherUser);
        require(owner != receiver);

        //shares of other user and receiver before withdraw
        uint256 debtSharesOtherUserBefore = shareDebtToken0.balanceOf(otherUser);
        uint256 collateralSharesOtherUserBefore = silo0.balanceOf(otherUser);
        uint256 protectedSharesOtherUserBefore = shareProtectedCollateralToken0.balanceOf(otherUser);
        uint256 debtSharesReceiverBefore = shareDebtToken0.balanceOf(receiver);
        uint256 collateralSharesReceiverBefore = silo0.balanceOf(receiver);
        uint256 protectedSharesReceiverBefore = shareProtectedCollateralToken0.balanceOf(receiver);

        //withdraw
        withdraw(e, assets, receiver, owner, ISilo.CollateralType.Protected);

        //shares of other user and receiver after withdraw
        uint256 debtSharesOtherUserAfter = shareDebtToken0.balanceOf(otherUser);
        uint256 collateralSharesOtherUserAfter = silo0.balanceOf(otherUser);
        uint256 protectedSharesOtherUserAfter = shareProtectedCollateralToken0.balanceOf(otherUser);
        uint256 debtSharesReceiverAfter = shareDebtToken0.balanceOf(receiver);
        uint256 collateralSharesReceiverAfter = silo0.balanceOf(receiver);
        uint256 protectedSharesReceiverAfter = shareProtectedCollateralToken0.balanceOf(receiver);

        //shares of other user and receiver did not change
        assert debtSharesOtherUserBefore == debtSharesOtherUserAfter;
        assert collateralSharesOtherUserBefore == collateralSharesOtherUserAfter;
        assert protectedSharesOtherUserBefore == protectedSharesOtherUserAfter;
        assert debtSharesReceiverBefore == debtSharesReceiverAfter;
        assert collateralSharesReceiverBefore == collateralSharesReceiverAfter;
        assert protectedSharesReceiverBefore == protectedSharesReceiverAfter;
    }


    // withdraw( protected) always decreases protectedShares for owner
    rule withdrawProtectedDecreasesProtectedSharesForOwner(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;

        //protectedShares of owner before withdraw
        uint256 protectedSharesBalanceOwnerBefore = shareProtectedCollateralToken0.balanceOf(owner);

        //withdraw
        withdraw(e, assets, receiver, owner, ISilo.CollateralType.Protected);

        //protectedShares of owner after withdraw
        uint256 protectedSharesBalanceOwnerAfter = shareProtectedCollateralToken0.balanceOf(owner);

        //protectedShares of owner decreased
        assert protectedSharesBalanceOwnerBefore > protectedSharesBalanceOwnerAfter;
    }
    
    // withdraw( protected) decreases protectedAssets by assets, debtAssets and CollateralAssets stay the same
    rule withdrawProtectedDecreasesProtectedAssets(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;

        // assets before withdraw
        uint256 protectedAssetsBefore;
        uint256 collateralAssetsBefore;
        uint256 debtAssetsBefore;
        (protectedAssetsBefore, collateralAssetsBefore, debtAssetsBefore) = silo0.totalAssetsHarness(e);

        //withdraw
        withdraw(e, assets, receiver, owner, ISilo.CollateralType.Protected);

        // assets after withdraw
        uint256 protectedAssetsAfter;
        uint256 collateralAssetsAfter;
        uint256 debtAssetsAfter;
        (protectedAssetsAfter, collateralAssetsAfter, debtAssetsAfter) = silo0.totalAssetsHarness(e);

        //protectedAssets decreased by assets
        assert protectedAssetsAfter == protectedAssetsBefore - assets;
        //collateralAssets did not change
        assert collateralAssetsBefore == collateralAssetsAfter;
        //debtAssets did not change
        assert debtAssetsBefore == debtAssetsAfter;
    }

    // withdraw() increases underlyingToken for receiver by assets, decreases the balance of silo accordingly and does not change for owner or receiver
    rule withdrawIncreasesUnderlyingTokenForReceiver(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        nonSceneAddressRequirements(receiver);
        address owner;
        nonSceneAddressRequirements(owner);
        address otherUser;
        nonSceneAddressRequirements(otherUser);
        require(owner != receiver);
        require(otherUser != receiver);

        //underlyingToken balances before 
        uint256 underlyingTokenBalanceReceiverBefore = token0.balanceOf(receiver);
        uint256 underlyingTokenBalanceOwnerBefore = token0.balanceOf(owner);
        uint256 underlyingTokenBalanceOtherUserBefore = token0.balanceOf(otherUser);
        uint256 underlyingTokenBalanceSiloBefore = token0.balanceOf(silo0);
        totalSuppliesMoreThanBalances(receiver, silo0);


        //withdraw
        withdraw(e, assets, receiver, owner);

        //underlyingToken balances after
        uint256 underlyingTokenBalanceReceiverAfter = token0.balanceOf(receiver);
        uint256 underlyingTokenBalanceOwnerAfter = token0.balanceOf(owner);
        uint256 underlyingTokenBalanceOtherUserAfter = token0.balanceOf(otherUser);
        uint256 underlyingTokenBalanceSiloAfter = token0.balanceOf(silo0);

        //underlyingToken of receiver increased by assets
        assert underlyingTokenBalanceReceiverAfter == underlyingTokenBalanceReceiverBefore + assets;
        //underlyingToken of owner did not change
        assert underlyingTokenBalanceOwnerBefore == underlyingTokenBalanceOwnerAfter;
        //underlyingToken of other user did not change
        assert underlyingTokenBalanceOtherUserBefore == underlyingTokenBalanceOtherUserAfter;
        //underlyingToken of silo decreased by assets
        assert underlyingTokenBalanceSiloAfter == underlyingTokenBalanceSiloBefore - assets;
    }

    // withdraw() and redeem can only be called by owner or allowance
    rule onlyUserOrAllowanceCanRedeemOrWithdrawShares(env e, method f, calldataarg args) filtered{f-> 
        f.selector == sig:redeem(uint256,address,address).selector ||
        f.selector == sig:redeem(uint256,address,address,ISilo.CollateralType).selector ||
        f.selector == sig:withdraw(uint256,address,address).selector ||
        f.selector == sig:withdraw(uint256,address,address,ISilo.CollateralType).selector        
    } {
        address amountAsset;
        address owner;
        uint256 allowanceMsgSender = silo0.allowance(e, owner, e.msg.sender);
        uint256 sharesBefore = silo0.balanceOf(owner);        

        f(e, args);

        uint256 sharesAfter = silo0.balanceOf(owner);
        mathint redeemedShares = sharesBefore - sharesAfter;

        assert(sharesBefore != sharesAfter => e.msg.sender == owner || allowanceMsgSender >= redeemedShares);
    }


    // withdraw() decreases totalSupply of collateral shares by dif for owner
    rule withdrawReducesTotalSupplyOfCollateralShares(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;

        //totalSupply of collateral shares before withdraw
        uint256 collateralSharesTotalSupplyBefore = silo0.totalSupply();
        uint256 collateralSharesBalanceOwnerBefore = silo0.balanceOf(owner);
        require(collateralSharesTotalSupplyBefore >= collateralSharesBalanceOwnerBefore);

        //withdraw
        uint256 burnedShares = withdraw(e, assets, receiver, owner);

        //totalSupply of collateral shares after withdraw
        uint256 collateralSharesTotalSupplyAfter = silo0.totalSupply();
        uint256 collateralSharesBalanceOwnerAfter = silo0.balanceOf(owner);

        //totalSupply of collateral shares decreased by dif
        assert collateralSharesTotalSupplyAfter == collateralSharesTotalSupplyBefore + collateralSharesBalanceOwnerAfter - collateralSharesBalanceOwnerBefore;
    }
    // withdraw() does not change any shares for other user or receiver
    rule withdrawDoesNotChangeSharesOfOthers(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;
        address otherUser;
        require(owner != otherUser);
        require(owner != receiver);

        //shares of other user and receiver before withdraw
        uint256 debtSharesOtherUserBefore = shareDebtToken0.balanceOf(otherUser);
        uint256 collateralSharesOtherUserBefore = silo0.balanceOf(otherUser);
        uint256 protectedSharesOtherUserBefore = shareProtectedCollateralToken0.balanceOf(otherUser);
        uint256 debtSharesReceiverBefore = shareDebtToken0.balanceOf(receiver);
        uint256 collateralSharesReceiverBefore = silo0.balanceOf(receiver);
        uint256 protectedSharesReceiverBefore = shareProtectedCollateralToken0.balanceOf(receiver);

        //withdraw
        withdraw(e, assets, receiver, owner);

        //shares of other user and receiver after withdraw
        uint256 debtSharesOtherUserAfter = shareDebtToken0.balanceOf(otherUser);
        uint256 collateralSharesOtherUserAfter = silo0.balanceOf(otherUser);
        uint256 protectedSharesOtherUserAfter = shareProtectedCollateralToken0.balanceOf(otherUser);
        uint256 debtSharesReceiverAfter = shareDebtToken0.balanceOf(receiver);
        uint256 collateralSharesReceiverAfter = silo0.balanceOf(receiver);
        uint256 protectedSharesReceiverAfter = shareProtectedCollateralToken0.balanceOf(receiver);

        //shares of other user and receiver did not change
        assert debtSharesOtherUserBefore == debtSharesOtherUserAfter;
        assert collateralSharesOtherUserBefore == collateralSharesOtherUserAfter;
        assert protectedSharesOtherUserBefore == protectedSharesOtherUserAfter;
        assert debtSharesReceiverBefore == debtSharesReceiverAfter;
        assert collateralSharesReceiverBefore == collateralSharesReceiverAfter;
        assert protectedSharesReceiverBefore == protectedSharesReceiverAfter;
    }

    // withdraw() does not change totalSupply or balance for borrower for debt and protectedCollateral shares
    rule withdrawDoesNotChangeDebtOrProtectedShares(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;

        //totalSupply and balance of owner before withdraw
        uint256 debtSharesTotalBalanceBefore = shareDebtToken0.totalSupply();
        uint256 protectedSharesTotalBalanceBefore = shareProtectedCollateralToken0.totalSupply();
        uint256 debtSharesBalanceOwnerBefore = shareDebtToken0.balanceOf(owner);
        uint256 protectedSharesBalanceOwnerBefore = shareProtectedCollateralToken0.balanceOf(owner);

        //withdraw
        withdraw(e, assets, receiver, owner);

        //totalSupply and balance of owner after withdraw
        uint256 debtSharesTotalBalanceAfter = shareDebtToken0.totalSupply();
        uint256 protectedSharesTotalBalanceAfter = shareProtectedCollateralToken0.totalSupply();
        uint256 debtSharesBalanceOwnerAfter = shareDebtToken0.balanceOf(owner);
        uint256 protectedSharesBalanceOwnerAfter = shareProtectedCollateralToken0.balanceOf(owner);

        //totalSupply and balance of owner did not change
        assert debtSharesTotalBalanceBefore == debtSharesTotalBalanceAfter;
        assert protectedSharesTotalBalanceBefore == protectedSharesTotalBalanceAfter;
        assert debtSharesBalanceOwnerBefore == debtSharesBalanceOwnerAfter;
        assert protectedSharesBalanceOwnerBefore == protectedSharesBalanceOwnerAfter;
    }

    // withdraw() always decreases collateralShares for owner
    rule withdrawDecreasesCollateralSharesForOwner(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address owner;

        //collateralShares of owner before withdraw
        uint256 collateralSharesBalanceOwnerBefore = silo0.balanceOf(owner);

        //withdraw
        withdraw(e, assets, receiver, owner);

        //collateralShares of owner after withdraw
        uint256 collateralSharesBalanceOwnerAfter = silo0.balanceOf(owner);

        //collateralShares of owner decreased
        assert collateralSharesBalanceOwnerBefore > collateralSharesBalanceOwnerAfter;
    }

//------------------------------- RULES OK END ------------------------------------

//------------------------------- INVARIENTS OK START-------------------------------

//------------------------------- INVARIENTS OK END-------------------------------

//------------------------------- ISSUES OK START-------------------------------

//------------------------------- ISSUES OK END-------------------------------

//-------------------------------OLD RULES START----------------------------------

//-------------------------------OLD RULES END----------------------------------
