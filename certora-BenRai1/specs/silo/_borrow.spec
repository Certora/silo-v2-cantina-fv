/* Rules concerning borrow  */

import "../setup/CompleteSiloSetup.spec";
import "./0base_Silo.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";
import "../simplifications/_Oracle_call_before_quote_UNSAFE.spec";

//------------------------------- RULES TEST START ----------------------------------

    // // borrow should be the same as borrowShares with shares = shares minted by borrow 
    // rule borrowIsTheSameAsBorrowShares(env e){ 
    //     configForEightTokensSetupRequirements();
    //     uint256 assets;
    //     address receiver;
    //     address borrower;
    //     nonSceneAddressRequirements(borrower);

    //     storage init = lastStorage;

    //     uint256 shares = borrow(e, assets, receiver, borrower);

    //     storage storageAfterBorrow = lastStorage;

    //     borrowShares(e, shares, receiver, borrower) at init;

    //     storage storageAfterBorrowShares = lastStorage;

    //     assert storageAfterBorrow == storageAfterBorrowShares;
    // }


    



    // * `borrow()` user borrows maxAssets returned by maxBorrow, borrow should not revert because of solvency check





//------------------------------- RULES TEST END ----------------------------------

//------------------------------- RULES PROBLEMS START ----------------------------------

    // borrow reverts if _assets to borrow > liquidity of the silo (SiloMathLib.liquidity) 
    rule borrowRevertsIfAssetsToBorrowGreaterThanLiquidity(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address borrower;
        nonSceneAddressRequirements(borrower);

        uint256 liquidity = getLiquidity(e);

        borrow@withrevert(e, assets, receiver, borrower);

        assert assets > liquidity => lastReverted;
    }

    // // after borrow, borrower ltv is below MaxLtv (isBelowMaxLtv) //@audit-issue vacouse rule => strange, check closer
    // rule borrowerLtvIsbelwoMaxLtvAfterBorrow(env e){
    //     configForEightTokensSetupRequirements();
    //     uint256 assets;
    //     address receiver;
    //     address borrower;
    //     nonSceneAddressRequirements(borrower);

    //     silo0.borrow(e, assets, receiver, borrower);

    //     assert ltvBelowMaxLtvHarness(borrower);
    // }

//------------------------------- RULES PROBLEMS START ----------------------------------

//------------------------------- RULES OK START ------------------------------------



    // borrow increses total supply of debtShare by increase of debt shares of borrower
    rule borrowIncreasesDebtShare(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address borrower;
        nonSceneAddressRequirements(borrower);

        uint256 totalSupplyDebtSharesBefore = shareDebtToken0.totalSupply();
        uint256 balanceDebtSharesBorrowerBefore = shareDebtToken0.balanceOf(borrower);

        silo0.borrow(e, assets, receiver, borrower);

        uint256 totalSupplyDebtSharesAfter = shareDebtToken0.totalSupply();
        uint256 balanceDebtSharesBorrowerAfter = shareDebtToken0.balanceOf(borrower);
        require(balanceDebtSharesBorrowerAfter >= balanceDebtSharesBorrowerBefore);
        require(totalSupplyDebtSharesAfter >= totalSupplyDebtSharesBefore);

        assert totalSupplyDebtSharesAfter == totalSupplyDebtSharesBefore + balanceDebtSharesBorrowerAfter - balanceDebtSharesBorrowerBefore;
    }

    // borrow results in > 0 debtShare for the borrower
    rule borrowResultsInPositiveDebtShare(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address borrower;
        nonSceneAddressRequirements(borrower);

        uint256 balanceDebtSharesBorrowerBefore = shareDebtToken0.balanceOf(borrower);

        uint256 shares = silo0.borrow(e, assets, receiver, borrower);

        //prevent overflow
        require shares + balanceDebtSharesBorrowerBefore <= max_uint256;

        uint256 balanceDebtSharesBorrowerAfter = shareDebtToken0.balanceOf(borrower);

        assert balanceDebtSharesBorrowerAfter > 0;
    }

    // borrow does not change debtShares of other user or receiver if they are not the borrower
    rule borrowDoesNotChangeDebtSharesOfOtherUsers(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address borrower;
        address otherUser;
        require otherUser != borrower;
        require receiver != borrower;

        uint256 balanceDebtSharesReceiverBefore = shareDebtToken0.balanceOf(receiver);
        uint256 balanceDebtSharesOtherUserBefore = shareDebtToken0.balanceOf(otherUser);

        silo0.borrow(e, assets, receiver, borrower);

        uint256 balanceDebtSharesReceiverAfter = shareDebtToken0.balanceOf(receiver);
        uint256 balanceDebtSharesOtherUserAfter = shareDebtToken0.balanceOf(otherUser);

        assert balanceDebtSharesReceiverAfter == balanceDebtSharesReceiverBefore;
        assert balanceDebtSharesOtherUserAfter == balanceDebtSharesOtherUserBefore;
    }

    // borrow does not change balanceToken0 of other user or borrower if they are not the receiver or silo0
    rule borrowDoesNotChangeToken0BalanceOfOtherUsers(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address borrower;
        address otherUser;
        require otherUser != receiver && otherUser != silo0;
        require borrower != receiver && borrower != silo0;

        uint256 balanceToken0OtherUserBefore = token0.balanceOf(otherUser);
        uint256 balanceToken0BorrowerBefore = token0.balanceOf(borrower);

        silo0.borrow(e, assets, receiver, borrower);

        uint256 balanceToken0OtherUserAfter = token0.balanceOf(otherUser);
        uint256 balanceToken0BorrowerAfter = token0.balanceOf(borrower);

        assert balanceToken0OtherUserAfter == balanceToken0OtherUserBefore;
        assert balanceToken0BorrowerAfter == balanceToken0BorrowerBefore;
    }

    // borrow does not change collateralAssets or protectedCollateral assets if no interes is accrued
    rule borrowDoesNotChangeCollateralAssetOrProtectedAsset(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address borrower;

        uint256 collateralAssetsBefore;
        uint256 protectedCollateralAssetsBefore;
        uint256 debtAssetsBefore;
        (protectedCollateralAssetsBefore, collateralAssetsBefore, debtAssetsBefore) = silo0.totalAssetsHarness(e);

        //ensure no interest is accrued
        require require_uint64(e.block.timestamp) == silo0.getSiloDataInterestRateTimestamp(e);

        silo0.borrow(e, assets, receiver, borrower);

        uint256 collateralAssetsAfter;
        uint256 protectedCollateralAssetsAfter;
        uint256 debtAssetsAfter;
        (protectedCollateralAssetsAfter, collateralAssetsAfter, debtAssetsAfter) = silo0.totalAssetsHarness(e);

        assert collateralAssetsAfter == collateralAssetsBefore;
        assert protectedCollateralAssetsAfter == protectedCollateralAssetsBefore;
    }

    // borrow reverts if borrower has debtshares in silo1
    rule borrowRevertsIfBorrowerHasDebtSharesInSilo1(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address borrower;
        nonSceneAddressRequirements(borrower);

        uint256 balanceDebtSharesSilo1BorrowerBefore = shareDebtToken1.balanceOf(borrower);

        borrow@withrevert(e, assets, receiver, borrower);

        assert balanceDebtSharesSilo1BorrowerBefore > 0 => lastReverted;
    }

    // borrow sets silo1 as borrowerCollateralSilo
    rule borrowSetsSilo1AsBorrowerCollateralSilo(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address borrower;

        borrow(e, assets, receiver, borrower);

        assert borrowerCollateralSiloHarness(borrower) == silo1;
    }

    // `borrow()` should decrease Silo balance by exactly `_assets`
    rule borrowDecreasesSiloBalanceExactlyByAssets(env e) {
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        nonSceneAddressRequirements(receiver);
        address borrower;

        uint256 balanceToken0Before = token0.balanceOf(silo0);
        require balanceToken0Before >= assets;

        silo0.borrow(e, assets, receiver, borrower);

        uint256 balanceToken0After = token0.balanceOf(silo0);

        assert balanceToken0After == balanceToken0Before - assets;
    }

    //`borrow()` should increase balance of the receiver by assets
    rule borrowIncreasesReceiverBalanceExactlyByAssets(env e) {
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address borrower;
        nonSceneAddressRequirements(receiver);
        totalSuppliesMoreThanBalances(receiver, silo0);

        uint256 balanceReceiverBefore = token0.balanceOf(receiver);

        silo0.borrow(e, assets, receiver, borrower);

        uint256 balanceReceiverAfter = token0.balanceOf(receiver);

        assert balanceReceiverAfter == balanceReceiverBefore + assets;
    }

    // borrow does not change collateral and protected shares
    rule borrowDoesNotChangeCollateralAndProtectedShares(env e) {
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address borrower;
        nonSceneAddressRequirements(receiver);

        uint256 totalSupplyCollateralSharesBefore = silo0.totalSupply();
        uint256 totalSupplyProtectedSharesBefore = shareProtectedCollateralToken0.totalSupply();

        silo0.borrow(e, assets, receiver, borrower);

        uint256 totalSupplyCollateralSharesAfter = silo0.totalSupply();
        uint256 totalSupplyProtectedSharesAfter = shareProtectedCollateralToken0.totalSupply();

        assert totalSupplyCollateralSharesAfter == totalSupplyCollateralSharesBefore;
        assert totalSupplyProtectedSharesAfter == totalSupplyProtectedSharesBefore;
    
    }

    // borrow increases debt assets by _assets if no interest is accrued
    rule borrowIncreasesDebtAssets(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address borrower;

        uint256 debtAssetsBefore;
        (_, _, debtAssetsBefore) = silo0.totalAssetsHarness(e);

        //ensure no interest is accrued
        require require_uint64(e.block.timestamp) == silo0.getSiloDataInterestRateTimestamp(e);

        silo0.borrow(e, assets, receiver, borrower);

        uint256 debtAssetsAfter;
        (_, _, debtAssetsAfter) = silo0.totalAssetsHarness(e);

        assert debtAssetsAfter == debtAssetsBefore + assets;
    }

//------------------------------- RULES OK END ------------------------------------

//------------------------------- INVARIENTS OK START-------------------------------

//------------------------------- INVARIENTS OK END-------------------------------

//------------------------------- ISSUES OK START-------------------------------

//------------------------------- ISSUES OK END-------------------------------
