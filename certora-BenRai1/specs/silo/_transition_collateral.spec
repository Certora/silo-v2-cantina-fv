/* Rules concerning transition collateral */

import "../setup/CompleteSiloSetup.spec";
import "./0base_Silo.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";
import "../simplifications/_Oracle_call_before_quote_UNSAFE.spec";
import "../simplifications/Oracle_quote_one_UNSAFE.spec";

//------------------------------- RULES TEST START ----------------------------------



    

    


//------------------------------- RULES TEST END ----------------------------------

//------------------------------- RULES PROBLEMS START ----------------------------------

    //------------------------- transitionCollateral and user assets -------------------------

        // ////@audit what happens if you minting x shares and redeem x shares? Does it result in the same balance of token0? Strange behavior for transitionCollateralShouldNotIncreaseUserAssets
        // //minting and then redeeming the same amount of shares results in the same balance of token0
        // rule mintAndRedeemSameAmount(env e){    
        //     configForEightTokensSetupRequirements();
        //     uint256 range = 2;
        //     uint256 shares;
        //     address owner;
        //     address receiver = owner;
        //     require(owner == e.msg.sender);

        //     //values before
        //     uint256 ownerToken0BalanceBefore = token0.balanceOf(owner);

        //     //mint
        //     mint(e, shares, owner, ISilo.CollateralType.Collateral);

        //     //redeem
        //     redeem(e, shares, owner, receiver, ISilo.CollateralType.Collateral);

        //     //values after
        //     uint256 ownerToken0BalanceAfter = token0.balanceOf(owner);

        //     //result is the same
        //     assert cvlApproxSameWithRange(ownerToken0BalanceBefore, ownerToken0BalanceAfter, range);
        // }

        // // * `transitionCollateral()` should not increase users assets
        // rule transitionCollateralShouldNotIncreaseUserAssets(env e){ //@audit-issue increases user assets by 2 wei
        //     configForEightTokensSetupRequirements();
        //     uint256 shares;
        //     address owner;

        //     //values before
        //     uint256 ownerProtectedAssetsBefore;
        //     uint256 ownerCollateralAssetsBefore;
        //     uint256 ownerDebtAssetsBefore;
        //     (ownerProtectedAssetsBefore, ownerCollateralAssetsBefore, ownerDebtAssetsBefore) = getUserAssetsHarness(e, owner);
        
        //     //transition
        //     transitionCollateral(e, shares, owner, ISilo.CollateralType.Collateral);

        //     //values after
        //     uint256 ownerProtectedAssetsAfter;
        //     uint256 ownerCollateralAssetsAfter;
        //     uint256 ownerDebtAssetsAfter;
        //     (ownerProtectedAssetsAfter, ownerCollateralAssetsAfter, ownerDebtAssetsAfter) = getUserAssetsHarness(e, owner);

        //     //otherUsers assets have not changed
        //     assert ownerProtectedAssetsBefore + ownerCollateralAssetsBefore >= ownerProtectedAssetsAfter + ownerCollateralAssetsAfter;
        // }

        // // * transitionCollateral should not decrease user assets by more than 1-2 wei
        // rule transitionCollateralShouldNotDecreaseUserAssetsTooMuch(env e){
        //     configForEightTokensSetupRequirements();
        //     uint256 shares;
        //     address owner;

        //     //values before
        //     uint256 ownerProtectedAssetsBefore;
        //     uint256 ownerCollateralAssetsBefore;
        //     uint256 ownerDebtAssetsBefore;
        //     (ownerProtectedAssetsBefore, ownerCollateralAssetsBefore, ownerDebtAssetsBefore) = getUserAssetsHarness(e, owner);
        
        //     //transition
        //     transitionCollateral(e, shares, owner, ISilo.CollateralType.Collateral);

        //     //values after
        //     uint256 ownerProtectedAssetsAfter;
        //     uint256 ownerCollateralAssetsAfter;
        //     uint256 ownerDebtAssetsAfter;
        //     (ownerProtectedAssetsAfter, ownerCollateralAssetsAfter, ownerDebtAssetsAfter) = getUserAssetsHarness(e, owner);

        //     //owner assets have not changed to much
        //     assert ownerProtectedAssetsBefore + ownerCollateralAssetsBefore - (ownerProtectedAssetsAfter + ownerCollateralAssetsAfter) <= 2;
        // }
    //------------------------- transitionCollateral and user assets -------------------------


    // // transitionCollateral: reverts if owner is insolvant before (if not, rounding in favor of the protocol is wrong) //@audit-issue time out
    // rule transitionCollateralRevertsIfOwnerInsolvantBefore(env e){
    //     configForEightTokensSetupRequirements();
    //     uint256 shares;
    //     address owner;

    //     //values before
    //     address collateralsilo = borrowerCollateralSiloHarness(e, owner);
    //     require(collateralsilo == silo0);
    //     bool ownerSolvent = isSolvent(e, owner);
    //     require(!ownerSolvent);

    //     //transition
    //     transitionCollateral@withrevert(e, shares, owner, ISilo.CollateralType.Collateral);

    //     //call reverted
    //     assert lastReverted;
    // }

//------------------------------- RULES PROBLEMS START ----------------------------------

//------------------------------- RULES OK START ------------------------------------






    // transitionCollateral: same as calling redeem and deposit
    rule transitionCollateralSameAsRedeemAndDeposit(env e){
        configForEightTokensSetupRequirements();
        uint256 share;
        address owner;
        address sender = e.msg.sender;

        //initState
        storage initialStorage = lastStorage;

        //transition
        transitionCollateral(e, share, owner, ISilo.CollateralType.Collateral);

        //values after transition
        //token0 balance
        uint256 siloToken0BalanceAfterTransition = token0.balanceOf(silo0);
        uint256 ownerToken0BalanceAfterTransition = token0.balanceOf(owner);
        uint256 senderToken0BalanceAfterTransition = token0.balanceOf(sender);

        //share balance
        uint256 ownerCollateralSharesAfterTransition = silo0.balanceOf(owner);
        uint256 ownerProtectedSharesAfterTransition = shareProtectedCollateralToken0.balanceOf(owner);


        //withdraw and deposit

        uint256 assets = redeem(e, share, e.msg.sender, owner, ISilo.CollateralType.Collateral) at initialStorage;
        deposit(e, assets, owner, ISilo.CollateralType.Protected); //i: deposit uses allowance

        //values after redeem and deposit
        //token0 balance
        uint256 siloToken0BalanceAfterRedeemAndDeposit = token0.balanceOf(silo0);
        uint256 ownerToken0BalanceAfterRedeemAndDeposit = token0.balanceOf(owner);

        //share balance
        uint256 ownerCollateralSharesAfterRedeemAndDeposit = silo0.balanceOf(owner);
        uint256 ownerProtectedSharesAfterRedeemAndDeposit = shareProtectedCollateralToken0.balanceOf(owner);

        //result is the same
        assert siloToken0BalanceAfterTransition == siloToken0BalanceAfterRedeemAndDeposit;
        assert ownerToken0BalanceAfterTransition == ownerToken0BalanceAfterRedeemAndDeposit;
        assert ownerCollateralSharesAfterTransition == ownerCollateralSharesAfterRedeemAndDeposit;
        assert ownerProtectedSharesAfterTransition == ownerProtectedSharesAfterRedeemAndDeposit;       
    }
    
    // transitionCollateral: prot => coll: Owner: protectedShares decrease by share, collateral shares increase / OtherUser: protectedShares  /collateralShares stay the same
    rule transitionCollateralProtToCollShares(env e){
        configForEightTokensSetupRequirements();
        uint256 shares;
        address owner;
        address otherUser;
        require(owner != otherUser);
        totalSuppliesMoreThanBalances(owner, otherUser);

        //values before
        uint256 ownerCollateralSharesBefore = silo0.balanceOf(owner);
        uint256 ownerProtectedSharesBefore = shareProtectedCollateralToken0.balanceOf(owner);
        uint256 otherUserCollateralSharesBefore = silo0.balanceOf(otherUser);
        uint256 otherUserProtectedSharesBefore = shareProtectedCollateralToken0.balanceOf(otherUser);
        uint256 totalCollateralSharesBefore = silo0.totalSupply();
        uint256 totalProtectedSharesBefore = shareProtectedCollateralToken0.totalSupply();

        //transition
        transitionCollateral(e, shares, owner, ISilo.CollateralType.Protected);

        //values after
        uint256 ownerCollateralSharesAfter = silo0.balanceOf(owner);
        uint256 ownerProtectedSharesAfter = shareProtectedCollateralToken0.balanceOf(owner);
        uint256 otherUserCollateralSharesAfter = silo0.balanceOf(otherUser);
        uint256 otherUserProtectedSharesAfter = shareProtectedCollateralToken0.balanceOf(otherUser);
        uint256 totalCollateralSharesAfter = silo0.totalSupply();
        uint256 totalProtectedSharesAfter = shareProtectedCollateralToken0.totalSupply();
        require(totalCollateralSharesAfter >= totalCollateralSharesBefore);

        //balances of other user are the same
        assert otherUserCollateralSharesBefore == otherUserCollateralSharesAfter;
        assert otherUserProtectedSharesBefore == otherUserProtectedSharesAfter;

        //balances of owner have changed
        assert ownerProtectedSharesAfter == ownerProtectedSharesBefore - shares;
        assert ownerCollateralSharesAfter > ownerCollateralSharesBefore;

        //total shares have changed
        assert totalProtectedSharesAfter == totalProtectedSharesBefore - shares;
        assert totalCollateralSharesAfter > totalCollateralSharesBefore;
    }

    // transitionCollateral: coll => prot: Owner: collateralShares decrease by share, protected shares increase  / OtherUser: collateralShares stay the same
    rule transitionCollateralCollToProtOwnerShares(env e){
        configForEightTokensSetupRequirements();
        uint256 shares;
        address owner;
        address otherUser;
        require(owner != otherUser);
        totalSuppliesMoreThanBalances(owner, otherUser);

        //values before
        uint256 ownerCollateralSharesBefore = silo0.balanceOf(owner);
        uint256 ownerProtectedSharesBefore = shareProtectedCollateralToken0.balanceOf(owner);
        uint256 otherUserCollateralSharesBefore = silo0.balanceOf(otherUser);
        uint256 otherUserProtectedSharesBefore = shareProtectedCollateralToken0.balanceOf(otherUser);
        uint256 totalCollateralSharesBefore = silo0.totalSupply();
        uint256 totalProtectedSharesBefore = shareProtectedCollateralToken0.totalSupply();

        //transition
        transitionCollateral(e, shares, owner, ISilo.CollateralType.Collateral);

        //values after
        uint256 ownerCollateralSharesAfter = silo0.balanceOf(owner);
        uint256 ownerProtectedSharesAfter = shareProtectedCollateralToken0.balanceOf(owner);
        uint256 otherUserCollateralSharesAfter = silo0.balanceOf(otherUser);
        uint256 otherUserProtectedSharesAfter = shareProtectedCollateralToken0.balanceOf(otherUser);
        uint256 totalCollateralSharesAfter = silo0.totalSupply();
        uint256 totalProtectedSharesAfter = shareProtectedCollateralToken0.totalSupply();
        require(totalProtectedSharesAfter >= totalProtectedSharesBefore);

        //balances of other user are the same
        assert otherUserCollateralSharesBefore == otherUserCollateralSharesAfter;
        assert otherUserProtectedSharesBefore == otherUserProtectedSharesAfter;

        //balances of owner have changed
        assert ownerCollateralSharesAfter == ownerCollateralSharesBefore - shares;
        assert ownerProtectedSharesAfter > ownerProtectedSharesBefore;

        //total shares have changed
        assert totalCollateralSharesAfter == totalCollateralSharesBefore - shares;
        assert totalProtectedSharesAfter > totalProtectedSharesBefore;
    }

    // * `transitionCollateral()` for `_transitionFrom` == `CollateralType.Collateral` should revert if not enough liquidity is available
    rule transitionCollateralRevertsIfNotEnoughLiquidity(env e){
        configForEightTokensSetupRequirements();
        uint256 shares;
        address owner;

        //values before
        uint256 liquidityBefore = getLiquidity(e);
        uint256 assets = convertToAssetsHarness(e, shares, ISilo.AssetType.Collateral);
        require(assets > liquidityBefore);

        //transition
        transitionCollateral@withrevert(e, shares, owner, ISilo.CollateralType.Collateral);

        //revert if assets more than liquidity
        assert lastReverted;
    }

    // transitionCollateral: only owner and allowance can call 
    rule transitionCollateralOnlyOwnerAndAllowance(env e){
        configForEightTokensSetupRequirements();
        uint256 shares;
        address owner;
        address caller = e.msg.sender;
        require(owner != caller);
        ISilo.CollateralType collType;
      
        //values before
        uint256 allowanceCaller = collType == ISilo.CollateralType.Collateral ?
                                silo0.balanceOf(owner) : shareProtectedCollateralToken0.allowance(e, owner, caller);
        require(allowanceCaller < shares);

        //transition
        transitionCollateral@withrevert(e, shares, owner, collType);

        //call reverted
        assert lastReverted;
    }

    //transitionCollateral: revert if shares are 0
    rule transitionCollateralRevertIfSharesZero(env e){
        configForEightTokensSetupRequirements();
        uint256 shares = 0;
        address owner;
        ISilo.CollateralType collType;
      
        //transition
        transitionCollateral@withrevert(e, shares, owner, collType);

        //call reverted
        assert lastReverted;
    }

    // transitionCollateral: coll => prot: collateralAssests reduced , protectedAssets increase
    rule transitionCollateralCollProtAssets(env e){
        configForEightTokensSetupRequirements();
        uint256 shares;
        address owner;
                
        //values before
        uint256 protectedAssetsBefore;
        uint256 collateralAssetsBefore;
        (protectedAssetsBefore, collateralAssetsBefore, _) = totalAssetsHarness(e);
       
        //transition
        transitionCollateral(e, shares, owner, ISilo.CollateralType.Collateral);

        //values after
        uint256 protectedAssetsAfter;
        uint256 collateralAssetsAfter;
        (protectedAssetsAfter, collateralAssetsAfter, _) = totalAssetsHarness(e);

        //collateral assets reduced
        assert collateralAssetsAfter < collateralAssetsBefore;
        //protected assets increased
        assert protectedAssetsAfter > protectedAssetsBefore;
    }

    // transitionCollateral: prot => coll: collateralAssests reduced , protectedAssets increase
    rule transitionCollateralProtCollAssets(env e){
        configForEightTokensSetupRequirements();
        uint256 shares;
        address owner;
                
        //values before
        uint256 protectedAssetsBefore;
        uint256 collateralAssetsBefore;
        (protectedAssetsBefore, collateralAssetsBefore, _) = totalAssetsHarness(e);
       
        //transition
        transitionCollateral(e, shares, owner, ISilo.CollateralType.Protected);

        //values after
        uint256 protectedAssetsAfter;
        uint256 collateralAssetsAfter;
        (protectedAssetsAfter, collateralAssetsAfter, _) = totalAssetsHarness(e);

        //collateral assets increased
        assert collateralAssetsAfter > collateralAssetsBefore;
        //protected assets reduced
        assert protectedAssetsAfter < protectedAssetsBefore;
    }

    // transitionCollateral: if owner is solvent before he is solvant after
    rule transitionCollateralOwnerSolventAfter(env e){
        configForEightTokensSetupRequirements();
        uint256 shares;
        address owner;

        //values before
        bool ownerSolventBefore = isSolvent(e, owner);
        require(ownerSolventBefore);

        //transition
        transitionCollateral(e, shares, owner, ISilo.CollateralType.Collateral);

        //owner is solvent after
        assert isSolvent(e, owner);
    }

    // transitionCollateral: debt assets do not change
    rule transitionCollateralDebtAssetsUnchanged(env e){
        configForEightTokensSetupRequirements();
        uint256 shares;
        address owner;
        ISilo.CollateralType colType;
        
        //values before
        uint256 totalDebtAssetsBefore;
        (_, _, totalDebtAssetsBefore) = totalAssetsHarness(e);
       
        //transition
        transitionCollateral(e, shares, owner, colType);

        //values after
        uint256 totalDebtAssetsAfter;
        (_, _, totalDebtAssetsAfter) = totalAssetsHarness(e);
        

        //debt assets have not changed
        assert totalDebtAssetsAfter == totalDebtAssetsBefore;
    }

    // transitionCollateral: debtShares do not change
    rule transitionCollateralDebtSharesUnchanged(env e){
        configForEightTokensSetupRequirements();
        uint256 shares;
        address owner;
        ISilo.CollateralType colType;
        
        //values before
        uint256 totalDebtSharesBefore = shareDebtToken0.totalSupply();
       
        //transition
        transitionCollateral(e, shares, owner, colType);

        //values after
        uint256 totalDebtSharesAfter = shareDebtToken0.totalSupply();
        

        //debt shares have not changed
        assert totalDebtSharesAfter == totalDebtSharesBefore;
    }

    // transitionCollateral: balance of token0 has not changed for anyone
    rule transitionCollateralBalanceOfToken0Unchanged(env e){
        configForEightTokensSetupRequirements();
        uint256 shares;
        address owner;
        address otherUser;
        require(owner != otherUser);

        ISilo.CollateralType colType;

        //values before
        uint256 token0BalanceBefore = token0.balanceOf(owner);
        uint256 token0BalanceOtherUserBefore = token0.balanceOf(otherUser);
        uint256 token0BalanceSiloBefore = token0.balanceOf(silo0);

        //transition
        transitionCollateral(e, shares, owner, colType);

        //values after
        uint256 token0BalanceAfter = token0.balanceOf(owner);
        uint256 token0BalanceOtherUserAfter = token0.balanceOf(otherUser);
        uint256 token0BalanceSiloAfter = token0.balanceOf(silo0);

        //balances have not changed
        assert token0BalanceBefore == token0BalanceAfter;
        assert token0BalanceOtherUserBefore == token0BalanceOtherUserAfter;
        assert token0BalanceSiloBefore == token0BalanceSiloAfter;
    }


//------------------------------- RULES OK END ------------------------------------

//------------------------------- INVARIENTS OK START-------------------------------

//------------------------------- INVARIENTS OK END-------------------------------

//------------------------------- ISSUES OK START-------------------------------

//------------------------------- ISSUES OK END-------------------------------

//-------------------------------OLD RULES START----------------------------------

//-------------------------------OLD RULES END----------------------------------
