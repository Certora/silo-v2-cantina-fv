/* Rules concerning repay and repayShares  */

import "../setup/CompleteSiloSetup.spec";
import "./0base_Silo.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";
import "../simplifications/_Oracle_call_before_quote_UNSAFE.spec";
import "../simplifications/Oracle_quote_one_UNSAFE.spec";

//------------------------------- RULES TEST START ----------------------------------
    



    






//------------------------------- RULES TEST END ----------------------------------

//------------------------------- RULES PROBLEMS START ----------------------------------


    // // repay() any user that can repay the debt should be able to repay the debt //@audit-issue if (!success) revert for second call
    // rule repayAnyUserCanRepay (env e1, env e2) {
    //     configForEightTokensSetupRequirements();
    //     uint256 assets;
    //     address borrower;
    //     address msgSender1 = e1.msg.sender;
    //     address msgSender2 = e2.msg.sender;
    //     threeUsersNotEqual(borrower, msgSender1, msgSender2);
    //     nonSceneAddressRequirements(msgSender1);
    //     nonSceneAddressRequirements(msgSender2);
    //     totalSuppliesMoreThanBalance(borrower);

    //     //balances before
    //     uint256 borrowerDebtShareTokensBefore = shareDebtToken0.balanceOf(borrower);
    //     uint256 msgSender1BalanceBefore = token0.balanceOf(msgSender1);
    //     uint256 msgSender2BalanceBefore = token0.balanceOf(msgSender2);
    //     require(msgSender1BalanceBefore == msgSender2BalanceBefore);

    //     //prevent revert because of sending ETH
    //     require(e1.msg.value == e2.msg.value);

    //     //init state
    //     storage init = lastStorage;

    //     //repay1
    //     repay(e1, assets, borrower);

    //     //balance after repay1
    //     uint256 borrowerDebtShareTokensAfterRepay1 = shareDebtToken0.balanceOf(borrower);

    //     //repay2
    //     repay@withrevert(e2, assets, borrower) at init;

    //     bool secondReverted = lastReverted;

    //     //balance after repay2
    //     uint256 borrowerDebtShareTokensAfterRepay2 = shareDebtToken0.balanceOf(borrower);

    //     satisfy !secondReverted;
    //     assert borrowerDebtShareTokensAfterRepay1 == borrowerDebtShareTokensAfterRepay2;
    // }

    // // repay() can not repay more assets than borrowed (check balances of token0)
    // rule repayMoreAssetsThanBorrowed (env e) {
    //     configForEightTokensSetupRequirements();
    //     uint256 assets;
    //     address borrower;
    //     address msgSender = e.msg.sender;
    //     nonSceneAddressRequirements(msgSender);
    //     totalSuppliesMoreThanBalance(borrower);

    //     //balance before
    //     uint256 msgSenderToken0BalanceBefore = token0.balanceOf(msgSender);
    //     uint256 borrowerDebtSharesBefore = shareDebtToken0.balanceOf(borrower);

    //     uint256 repayedAssets;
    //     uint256 repayedShares;
    //     (repayedAssets, repayedShares) = repayHarness(e, shareDebtToken0, 0, borrowerDebtSharesBefore, borrower);
    //     //i: example with 1 bitcoin deposited 
    //     require(repayedShares > 10**8);	

    //     //repay
    //     uint256 shares = repay(e, assets, borrower);

    //     //balance after
    //     uint256 msgSenderToken0BalanceAfter = token0.balanceOf(msgSender);

    //     //repay not more assets than borrowed
    //     assert(msgSenderToken0BalanceAfter >= msgSenderToken0BalanceBefore - repayedAssets || 
    //         cvlApproxSameWithRange(msgSenderToken0BalanceAfter, msgSenderToken0BalanceBefore - repayedAssets, 2000000000));
    // }

    // // repay() should not be able to repay more than maxRepay //@audit-issue when you have half of the shares, you can overpay if assets is set to high
    // rule repayMoreThanMaxRepay (env e) {
    //     configForEightTokensSetupRequirements();
    //     uint256 assets;
    //     address borrower;
    //     address msgSender = e.msg.sender;
    //     totalSuppliesMoreThanBalance(msgSender);
    //     totalSuppliesMoreThanBalance(borrower);

    //     //balanaces before
    //     uint256 msgSenderBalanceBefore = token0.balanceOf(msgSender);

    //     //maxRepay
    //     uint256 maxRepayAssets = maxRepay(e, borrower);

    //     //repay
    //     repay(e, assets, borrower);

    //     //balances after
    //     uint256 msgSenderBalanceAfter = token0.balanceOf(msgSender);

    //     //repay not more than maxRepay
    //     assert(msgSenderBalanceAfter >= msgSenderBalanceBefore - maxRepayAssets || 
    //         cvlApproxSameWithRange(msgSenderBalanceAfter, msgSenderBalanceBefore - maxRepayAssets, 2));
    // }

    // // repay() repaying all shares with repay() and repayShares() should be the same //@audit might be off my one
    // rule repayAndRepaySharesIsTheSame (env e) {
    //     configForEightTokensSetupRequirements();
    //     uint256 assets;
    //     address borrower;
    //     address msgSender = e.msg.sender;
    //     totalSuppliesMoreThanBalance(msgSender);
    //     totalSuppliesMoreThanBalance(borrower);

    //     //balances before
    //     uint256 msgSenderBalanceBefore = token0.balanceOf(msgSender);
    //     uint256 borrowerDebtShareTokensBefore = shareDebtToken0.balanceOf(borrower);

    //     //init state
    //     storage init = lastStorage;

    //     //repay
    //     uint256 shares = repay(e, assets, borrower) at init;
    //     require(shares == borrowerDebtShareTokensBefore);

    //     //balances after repay
    //     uint256 msgSenderBalanceAfterRepay = token0.balanceOf(msgSender);

    //     //repayShares all shares
    //     repayShares(e, borrowerDebtShareTokensBefore, borrower) at init;

    //     //balances after repayShares
    //     uint256 msgSenderBalanceAfterRepayShares = token0.balanceOf(msgSender);

    //     //repay and repayShares the same
    //     assert cvlApproxSameWithRange(msgSenderBalanceAfterRepay, msgSenderBalanceAfterRepayShares, 2); //@audit test differetn ranges to see how high we can go
    // }


    
    // // repay() user that can repay, calling `repay()` with `maxRepay()` result should never revert 
    // rule repayMaxRepayNeverRevert (env e) {
    //     configForEightTokensSetupRequirements();
    //     uint256 assets;
    //     address borrower;
    //     address msgSender = e.msg.sender;
    //     totalSuppliesMoreThanBalance(borrower);

    //     //maxRepay
    //     uint256 maxRepayAssets = maxRepay(e, borrower);
    //     uint256 msgSenderBalanceBefore = token0.balanceOf(msgSender);
    //     require(msgSenderBalanceBefore >= maxRepayAssets);

    //     //prevent revert because of sending ETH
    //     require(e.msg.value == 0);

    //     //init state
    //     storage init = lastStorage;

    //     //call repay to ensure the storage does not result in reverts (e.g _crossReentrancy = true)
    //     repay(e, assets, borrower) at init;

    //     //repay
    //     repay@withrevert(e, maxRepayAssets, borrower) at init;

    //     //did not revert
    //     assert !lastReverted;
    // }


//------------------------------- RULES PROBLEMS START ----------------------------------

//------------------------------- RULES OK START ------------------------------------



    // repay() maxRepay() should never return more than `totalAssets[AssetType.Debt]`
    rule repayMaxRepayNeverMoreThanDebt (env e) {
        configForEightTokensSetupRequirements();
        address borrower;
        totalSuppliesMoreThanBalance(borrower);

        //maxRepay
        uint256 maxRepayAssets = maxRepay(e, borrower);
        uint256 debtAssets;
        (_, _, _, _, debtAssets) = getSiloStorage();

        //maxRepay never more than debt
        assert(maxRepayAssets <= debtAssets);
    }

    // repay()  any other user than borrower can repay
    rule repayOtherUserCanRepay (env e) {
        configForEightTokensSetupRequirements();
        uint256 assets;
        address borrower;
        address msgSender = e.msg.sender;
        require(msgSender != borrower);

        uint256 repayedAssets;
        uint256 repayedShares;
        (repayedAssets, repayedShares) = repayHarness(shareDebtToken0, assets, 0, borrower);

        //balances before
        uint256 msgSenderBalanceBefore = token0.balanceOf(msgSender);
        require(msgSenderBalanceBefore >= repayedAssets);
        //prevent revert because of sending ETH
        require(e.msg.value == 0);

        //repay
        repay@withrevert(e, assets, borrower);

        //did not revert
        satisfy !lastReverted;
    }
   
    // repay() return value of `previewRepay()` should be always equal to `repay()`
    rule repayPreviewRepay (env e) {
        configForEightTokensSetupRequirements();
        uint256 assets;
        address borrower;
        address msgSender = e.msg.sender;
        totalSuppliesMoreThanBalance(borrower);

        //previewRepay
        uint256 previewRepayShares = previewRepay(e, assets);
        uint256 borrowerDebtShareTokensBefore = shareDebtToken0.balanceOf(borrower);
        require(borrowerDebtShareTokensBefore >= previewRepayShares);

        //repay
        uint256 repayShares = repay(e, assets, borrower);

        //previewRepay == repay
        assert(previewRepayShares == repayShares);
    }

    // repay() msg.sender and other user shareDebtToken0 token stay the same, borrower shareDebtToken0 token decreases by result
    rule repayshareDebtToken0Balances (env e) {
        configForEightTokensSetupRequirements();
        uint256 assets;
        address borrower;
        address msgSender = e.msg.sender;
        address otherUser;
        threeUsersNotEqual(borrower, msgSender, otherUser);
        totalSuppliesMoreThanBalance(borrower);

        //balances before
        uint256 msgSenderBalanceBefore = shareDebtToken0.balanceOf(msgSender);
        uint256 otherUserBalanceBefore = shareDebtToken0.balanceOf(otherUser);
        uint256 borrowerBalanceBefore = shareDebtToken0.balanceOf(borrower);
        uint256 totalSupplyBefore = shareDebtToken0.totalSupply();

        //repay
        uint256 shares = repay(e, assets, borrower);

        //balances after
        uint256 msgSenderBalanceAfter = shareDebtToken0.balanceOf(msgSender);
        uint256 otherUserBalanceAfter = shareDebtToken0.balanceOf(otherUser);
        uint256 borrowerBalanceAfter = shareDebtToken0.balanceOf(borrower);
        uint256 totalSupplyAfter = shareDebtToken0.totalSupply();

        //balances the same
        assert(msgSenderBalanceBefore == msgSenderBalanceAfter);
        assert(otherUserBalanceBefore == otherUserBalanceAfter);
        //borrower balance decreases by shares
        assert(borrowerBalanceAfter == borrowerBalanceBefore - shares);
        //totalSupply decreases by shares
        assert(totalSupplyAfter == totalSupplyBefore - shares);
    }
    
    // repay() if user repay all debt, no extra debt should be created
    rule repayAllDebtNoExtraDebt (env e) {
        configForEightTokensSetupRequirements();
        uint256 assets;
        address borrower;
        totalSuppliesMoreThanBalance(borrower);

        //balances before
        uint256 borrowerDebtShareTokensBefore = shareDebtToken0.balanceOf(borrower);

        uint256 repayedAssets;
        uint256 repayedShares;
        (repayedAssets, repayedShares) = repayHarness(e, shareDebtToken0, 0, borrowerDebtShareTokensBefore, borrower);
        require(assets == repayedAssets+10);

        //repay
        repay(e, assets, borrower);

        //balances after
        uint256 borrowerDebtShareTokensAfter = shareDebtToken0.balanceOf(borrower);

        //no extra debt
        assert(borrowerDebtShareTokensAfter == 0);
    }

    // repay() should decrease the debt (for a single block)
    rule repayDecreaseDebt (env e) {
        configForEightTokensSetupRequirements();
        uint256 assets;
        address borrower;
        totalSuppliesMoreThanBalance(borrower);

        //debt before
        uint256 debtAssetsBefore;
        (_, _, _, _, debtAssetsBefore) = getSiloStorage();
        uint256 borrowerDebtShareTokensBefore = shareDebtToken0.balanceOf(borrower);

        //repay
        repay(e, assets, borrower);

        //debt after
        uint256 debtAssetsAfter;
        (_, _, _, _, debtAssetsAfter) = getSiloStorage();
        uint256 borrowerDebtShareTokensAfter = shareDebtToken0.balanceOf(borrower);

        //debt decreases
        assert(debtAssetsAfter < debtAssetsBefore );
        assert(borrowerDebtShareTokensAfter < borrowerDebtShareTokensBefore);
    }

    // repay() can not repay more shares than the borrower has
    rule repayMoreSharesThanBorrowerHas (env e) {
        configForEightTokensSetupRequirements();
        uint256 assets;
        address borrower;
        totalSuppliesMoreThanBalance(borrower);

        //debt shares owner before
        uint256 sharesBefore = shareDebtToken0.balanceOf(borrower);

        //repay
        uint256 shares = repay(e, assets, borrower);

        //repay more shares than borrower has
        assert(sharesBefore >= shares);
    }

    // // repay() collateralAssets and protectedAssets stay the same, debtAssets decrease by assets
    rule repayAssets (env e) {
        configForEightTokensSetupRequirements();
        uint256 assets;
        address borrower;
        totalSuppliesMoreThanBalance(borrower);

        //assets before
        uint256 protectedAssetsBefore;
        uint256 collateralAssetsBefore;
        uint256 debtAssetsBefore;
        (_, _, protectedAssetsBefore, collateralAssetsBefore, debtAssetsBefore) = getSiloStorage();

        uint256 repayedAssets;
        uint256 repayedShares;
        (repayedAssets, repayedShares) = repayHarness(e, shareDebtToken0, assets, 0, borrower);


        //repay
        uint256 shares = repay(e, assets, borrower);

        //assets after
        uint256 protectedAssetsAfter;
        uint256 collateralAssetsAfter;
        uint256 debtAssetsAfter;
        (_, _, protectedAssetsAfter, collateralAssetsAfter, debtAssetsAfter) = getSiloStorage();

        //assets are the same
        assert(protectedAssetsBefore == protectedAssetsAfter);
        assert(collateralAssetsBefore == collateralAssetsAfter);
        //debtAssets decrease by assets
        assert(debtAssetsAfter == debtAssetsBefore - repayedAssets);
    }

    // repay() increases siloBalance of token0 by assets, decreases the same ammount for msg.sender, other balances stay the same
    rule repayBalancesToken0 (env e) {
        configForEightTokensSetupRequirements();
        uint256 assets;
        address borrower;
        address msgSender = e.msg.sender;
        nonSceneAddressRequirements(borrower);
        address otherUser;
        threeUsersNotEqual(borrower, msgSender, otherUser);
        totalSuppliesMoreThanBalances(silo0, msgSender);

        uint256 repayedAssets;
        uint256 repayedShares;
        (repayedAssets, repayedShares) = repayHarness(e, shareDebtToken0, assets, 0, borrower);

        //balances before
        uint256 borrowerBalanceBefore = token0.balanceOf(borrower);
        uint256 msgSenderBalanceBefore = token0.balanceOf(msgSender);
        uint256 otherUserBalanceBefore = token0.balanceOf(otherUser);
        uint256 siloBalanceBefore = token0.balanceOf(silo0);

        //repay
        repay(e, assets, borrower);

        //balances after
        uint256 borrowerBalanceAfter = token0.balanceOf(borrower);
        uint256 msgSenderBalanceAfter = token0.balanceOf(msgSender);
        uint256 otherUserBalanceAfter = token0.balanceOf(otherUser);
        uint256 siloBalanceAfter = token0.balanceOf(silo0);

        //balances the same
        assert(borrowerBalanceBefore == borrowerBalanceAfter);
        assert(otherUserBalanceBefore == otherUserBalanceAfter);
        //siloBalance increases by assets
        assert(siloBalanceAfter == siloBalanceBefore + repayedAssets);
        //msgSender balance decreases
        assert(msgSenderBalanceAfter == msgSenderBalanceBefore - repayedAssets);
        assert(repayedAssets <= assets);
        assert(repayedAssets > 0);
    }

//------------------------------- RULES OK END ------------------------------------

//------------------------------- INVARIENTS OK START-------------------------------

//------------------------------- INVARIENTS OK END-------------------------------

//------------------------------- ISSUES OK START-------------------------------

//------------------------------- ISSUES OK END-------------------------------
