import "./_partialLiquidationSetup.spec";

function noReverts(env e){
    uint256 maxDebtToCover;
    address borrower;
    require siloConfig(e) != 0;
    require maxDebtToCover != 0;
    setupLiquidationRules(e, borrower);

    address collateralSilo = siloConfig.borrowerCollateralSilo(e, borrower);
    address debtSilo = siloConfig.getDebtSilo(e, borrower);
    ISiloConfig.ConfigData collateralConfig = siloConfig.getConfig(e, collateralSilo);

    require(collateralConfig.liquidationFee != 12569); //summary returns custom error
    require(maxDebtToCover != 500);
}



//------------------------------- RULES  ----------------------------------

    // liquidationCall() revert if customError != 0
    rule revertIfCustomErrorIsNotZero(env e){
        configForEightTokensSetupRequirements();
        address collateralAsset;
        address debtAsset;
        address borrower;
        uint256 maxDebtToCover;
        bool receiveSToken;

        //setup
        address collateralSilo;
        address debtSilo;
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (collateralSilo, debtSilo, collateralConfig, debtConfig) = setupLiquidationRules(e, borrower);
        uint256 withdrawAssetsFromCollateral;
        uint256 withdrawAssetsFromProtected;
        uint256 repayDebtAssets;
        bytes4 customError;
        (withdrawAssetsFromCollateral, withdrawAssetsFromProtected, repayDebtAssets, customError) = 
        getExactLiquidationAmountsCVL(collateralConfig, debtConfig, borrower, maxDebtToCover, collateralConfig.liquidationFee); 

        //require customError != 0
        require(collateralConfig.liquidationFee == 12569); //summary returns custom error
        

        //function call
        liquidationCall@withrevert(e, collateralAsset, debtAsset, borrower, maxDebtToCover, receiveSToken);

        //call reverted
        assert lastReverted;        
    }

    // liquidationCall() revert if repayDebtAssets > maxDebtToCover
    rule revertIfRepayDebtAssetsGreaterThanMaxDebtToCover(env e){
        configForEightTokensSetupRequirements();
        address collateralAsset;
        address debtAsset;
        address borrower;
        uint256 maxDebtToCover;
        bool receiveSToken;

        //require
        require(maxDebtToCover == 500); //force repayDebtAssets > maxDebtToCover

        //function call
        liquidationCall@withrevert(e, collateralAsset, debtAsset, borrower, maxDebtToCover, receiveSToken);

        //call reverted
        assert lastReverted;        
    }

    // liquidationCall() borrower debtShare reduced by repayDebtAssets
    rule borrowerDebtSharesDecrease(env e){
        configForEightTokensSetupRequirements();
        address collateralAsset;
        address debtAsset;
        address borrower;
        uint256 maxDebtToCover;
        bool receiveSToken;

        //setup
        address collateralSilo;
        address debtSilo;
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (collateralSilo, debtSilo, collateralConfig, debtConfig) = setupLiquidationRules(e, borrower);
        uint256 withdrawAssetsFromCollateral;
        uint256 withdrawAssetsFromProtected;
        uint256 repayDebtAssets;
        bytes4 customError;
        (withdrawAssetsFromCollateral, withdrawAssetsFromProtected, repayDebtAssets, customError) = 
        getExactLiquidationAmountsCVL(collateralConfig, debtConfig, borrower, maxDebtToCover, collateralConfig.liquidationFee); 


        //values before
        uint256 transferedDebtSharesBorrowerBefore = repayedAssets[debtSilo][borrower];

        //function call
        liquidationCall(e, collateralAsset, debtAsset, borrower, maxDebtToCover, receiveSToken);

        //values after
        uint256 transferedDebtSharesBorrowerAfter = repayedAssets[debtSilo][borrower];

        //asserts
        assert transferedDebtSharesBorrowerAfter == transferedDebtSharesBorrowerBefore + repayDebtAssets;   
    }

    // liquidationCall() borrower collateralShares (protected/normal) reduced by withdrawAssetsFromCollateral and withdrawAssetsFromProtected
    rule borrowerCollateralShareDecrease(env e){
        configForEightTokensSetupRequirements();
        address collateralAsset;
        address debtAsset;
        address borrower;
        uint256 maxDebtToCover;
        bool receiveSToken;

        //setup
        address collateralSilo;
        address debtSilo;
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (collateralSilo, debtSilo, collateralConfig, debtConfig) = setupLiquidationRules(e, borrower);
        uint256 withdrawAssetsFromCollateral;
        uint256 withdrawAssetsFromProtected;
        uint256 repayDebtAssets;
        bytes4 customError;
        (withdrawAssetsFromCollateral, withdrawAssetsFromProtected, repayDebtAssets, customError) = 
        getExactLiquidationAmountsCVL(collateralConfig, debtConfig, borrower, maxDebtToCover, collateralConfig.liquidationFee); 

        //values before
        uint256 reducedWithoutChecksProtectedBorrowerBefore = reducedWithoutChecks[collateralConfig.protectedShareToken][borrower];
        uint256 reducedWithoutChecksCollateralBorrowerBefore = reducedWithoutChecks[collateralSilo][borrower];

        //function call
        liquidationCall(e, collateralAsset, debtAsset, borrower, maxDebtToCover, receiveSToken);

        //values after
        uint256 reducedWithoutChecksProtectedBorrowerAfter = reducedWithoutChecks[collateralConfig.protectedShareToken][borrower];
        uint256 reducedWithoutChecksCollateralBorrowerAfter = reducedWithoutChecks[collateralSilo][borrower];

        //asserts
        assert reducedWithoutChecksProtectedBorrowerAfter == reducedWithoutChecksProtectedBorrowerBefore + withdrawAssetsFromProtected;
        assert reducedWithoutChecksCollateralBorrowerAfter == reducedWithoutChecksCollateralBorrowerBefore + withdrawAssetsFromCollateral;  
    }

    // liquidationCall() no balances for other user are changed
    rule balanceOfOtherUserDoesNotChange(env e){
        configForEightTokensSetupRequirements();
        address collateralAsset;
        address debtAsset;
        address borrower;
        uint256 maxDebtToCover;
        bool receiveSToken;
        address otherUser;
        nonSceneAddressRequirements(otherUser);
        require(otherUser != currentContract);
        threeUsersNotEqual(e.msg.sender, borrower, otherUser);

        //setup
        address collateralSilo;
        address debtSilo;
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (collateralSilo, debtSilo, collateralConfig, debtConfig) = setupLiquidationRules(e, borrower);
        uint256 withdrawAssetsFromCollateral;
        uint256 withdrawAssetsFromProtected;
        uint256 repayDebtAssets;
        bytes4 customError;
        (withdrawAssetsFromCollateral, withdrawAssetsFromProtected, repayDebtAssets, customError) = 
        getExactLiquidationAmountsCVL(collateralConfig, debtConfig, borrower, maxDebtToCover, collateralConfig.liquidationFee); 

        //values before
        uint256 token0sentTransferredAssetsBefore = sentTransferredAssets[token0][otherUser];
        uint256 token1sentTransferredAssetsBefore = sentTransferredAssets[token1][otherUser];
        uint256 token0sentReceivedTransferredAssetsBefore = receivedTransferredAssets[token0][otherUser];
        uint256 token1sentReceivedTransferredAssetsBefore = receivedTransferredAssets[token1][otherUser];
        uint256 reducedWithoutChecksProtectedOtherUserBefore = reducedWithoutChecks[collateralConfig.protectedShareToken][otherUser];
        uint256 reducedWithoutChecksCollateralOtherUserBefore = reducedWithoutChecks[collateralSilo][otherUser];
        uint256 increasedWithoutChecksProtectedOtherUserBefore = increasedWithoutChecks[collateralConfig.protectedShareToken][otherUser];
        uint256 increasedWithoutChecksCollateralOtherUserBefore = increasedWithoutChecks[collateralSilo][otherUser];
        uint256 repayedAssetsOtherUserBefore = repayedAssets[debtSilo][otherUser];
        uint256 redeemedAssetsProtectedOtherUserBefore = redeemedAssets[collateralSilo][false][otherUser];
        uint256 redeemedAssetsCollateralOtherUserBefore = redeemedAssets[collateralSilo][true][otherUser];
        uint256 receivedRedeemedAssetsProtectedOtherUserBefore = receivedRedeemedAssets[collateralSilo][false][otherUser];
        uint256 receivedRedeemedAssetsCollateralOtherUserBefore = receivedRedeemedAssets[collateralSilo][true][otherUser];

        //function call
        liquidationCall(e, collateralAsset, debtAsset, borrower, maxDebtToCover, receiveSToken);    

        //values after
        uint256 token0sentTransferredAssetsAfter = sentTransferredAssets[token0][otherUser];
        uint256 token1sentTransferredAssetsAfter = sentTransferredAssets[token1][otherUser];
        uint256 token0sentReceivedTransferredAssetsAfter = receivedTransferredAssets[token0][otherUser];
        uint256 token1sentReceivedTransferredAssetsAfter = receivedTransferredAssets[token1][otherUser];
        uint256 reducedWithoutChecksProtectedOtherUserAfter = reducedWithoutChecks[collateralConfig.protectedShareToken][otherUser];
        uint256 reducedWithoutChecksCollateralOtherUserAfter = reducedWithoutChecks[collateralSilo][otherUser];
        uint256 increasedWithoutChecksProtectedOtherUserAfter = increasedWithoutChecks[collateralConfig.protectedShareToken][otherUser];
        uint256 increasedWithoutChecksCollateralOtherUserAfter = increasedWithoutChecks[collateralSilo][otherUser];
        uint256 repayedAssetsOtherUserAfter = repayedAssets[debtSilo][otherUser];
        uint256 redeemedAssetsProtectedOtherUserAfter = redeemedAssets[collateralSilo][false][otherUser];
        uint256 redeemedAssetsCollateralOtherUserAfter = redeemedAssets[collateralSilo][true][otherUser];
        uint256 receivedRedeemedAssetsProtectedOtherUserAfter = receivedRedeemedAssets[collateralSilo][false][otherUser];
        uint256 receivedRedeemedAssetsCollateralOtherUserAfter = receivedRedeemedAssets[collateralSilo][true][otherUser];

        //asserts
        assert token0sentTransferredAssetsAfter == token0sentTransferredAssetsBefore;
        assert token1sentTransferredAssetsAfter == token1sentTransferredAssetsBefore;
        assert token0sentReceivedTransferredAssetsAfter == token0sentReceivedTransferredAssetsBefore;
        assert token1sentReceivedTransferredAssetsAfter == token1sentReceivedTransferredAssetsBefore;
        assert reducedWithoutChecksProtectedOtherUserAfter == reducedWithoutChecksProtectedOtherUserBefore;
        assert reducedWithoutChecksCollateralOtherUserAfter == reducedWithoutChecksCollateralOtherUserBefore;
        assert increasedWithoutChecksProtectedOtherUserAfter == increasedWithoutChecksProtectedOtherUserBefore;
        assert increasedWithoutChecksCollateralOtherUserAfter == increasedWithoutChecksCollateralOtherUserBefore;
        assert repayedAssetsOtherUserAfter == repayedAssetsOtherUserBefore;
        assert redeemedAssetsProtectedOtherUserAfter == redeemedAssetsProtectedOtherUserBefore;
        assert redeemedAssetsCollateralOtherUserAfter == redeemedAssetsCollateralOtherUserBefore;
        assert receivedRedeemedAssetsProtectedOtherUserAfter == receivedRedeemedAssetsProtectedOtherUserBefore;
        assert receivedRedeemedAssetsCollateralOtherUserAfter == receivedRedeemedAssetsCollateralOtherUserBefore;
    }

    // liquidationCall() msg.sender: underlyingTokenBalanceSender is reduced by repayDebtAssets
    rule debtAssetBalanceOfMsgSenderDecreasesByRepayDebtAssets(env e){
        configForEightTokensSetupRequirements();
        address collateralAsset;
        address debtAsset;
        address borrower;
        uint256 maxDebtToCover;
        bool receiveSToken;

        //setup
        address collateralSilo;
        address debtSilo;
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (collateralSilo, debtSilo, collateralConfig, debtConfig) = setupLiquidationRules(e, borrower);
        uint256 withdrawAssetsFromCollateral;
        uint256 withdrawAssetsFromProtected;
        uint256 repayDebtAssets;
        bytes4 customError;
        (withdrawAssetsFromCollateral, withdrawAssetsFromProtected, repayDebtAssets, customError) = 
        getExactLiquidationAmountsCVL(collateralConfig, debtConfig, borrower, maxDebtToCover, collateralConfig.liquidationFee); 

        //values before
        uint256 sentTransferredAssetsSenderBefore = sentTransferredAssets[debtConfig.token][e.msg.sender];
        uint256 receivedTransferredAssetsHookBefore = receivedTransferredAssets[debtConfig.token][currentContract]; 

        //function call
        liquidationCall(e, collateralAsset, debtAsset, borrower, maxDebtToCover, receiveSToken);

        //values after
        uint256 sentTransferredAssetsSenderAfter = sentTransferredAssets[debtConfig.token][e.msg.sender];
        uint256 receivedTransferredAssetsHookAfter = receivedTransferredAssets[debtConfig.token][currentContract];

        //asserts
        assert sentTransferredAssetsSenderAfter == sentTransferredAssetsSenderBefore + repayDebtAssets;
        assert receivedTransferredAssetsHookAfter == receivedTransferredAssetsHookBefore + repayDebtAssets;
    }

    // liquidationCall() _receiveSToken == true: msg.sender collateralShares (protected/normal) increased by withdrawAssetsFromCollateral and withdrawAssetsFromProtected and balance collateralAssetSender does not change
    rule collateralSharesIncreaseByWithdrawAssets(env e){
        configForEightTokensSetupRequirements();
        address collateralAsset;
        address debtAsset;
        address borrower;
        uint256 maxDebtToCover;
        bool receiveSToken;

        //setup
        require receiveSToken;
        require e.msg.sender != currentContract;
        address collateralSilo;
        address debtSilo;
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (collateralSilo, debtSilo, collateralConfig, debtConfig) = setupLiquidationRules(e, borrower);
        uint256 withdrawAssetsFromCollateral;
        uint256 withdrawAssetsFromProtected;
        uint256 repayDebtAssets;
        bytes4 customError;
        (withdrawAssetsFromCollateral, withdrawAssetsFromProtected, repayDebtAssets, customError) = 
        getExactLiquidationAmountsCVL(collateralConfig, debtConfig, borrower, maxDebtToCover, collateralConfig.liquidationFee); 

        //values before
        uint256 increasedWithoutChecksProtectedSenderBefore = increasedWithoutChecks[collateralConfig.protectedShareToken][e.msg.sender];
        uint256 increasedWithoutChecksCollateralSenderBefore = increasedWithoutChecks[collateralSilo][e.msg.sender];
        uint256 receivedRedeemedAssetsProtectedSenderBefore = receivedRedeemedAssets[collateralSilo][false][e.msg.sender];
        uint256 receivedRedeemedAssetsCollateralSenderBefore = receivedRedeemedAssets[collateralSilo][true][e.msg.sender];

        //function call
        liquidationCall(e, collateralAsset, debtAsset, borrower, maxDebtToCover, receiveSToken);

        //values after
        uint256 increasedWithoutChecksProtectedSenderAfter = increasedWithoutChecks[collateralConfig.protectedShareToken][e.msg.sender];
        uint256 increasedWithoutChecksCollateralSenderAfter = increasedWithoutChecks[collateralSilo][e.msg.sender];
        uint256 receivedRedeemedAssetsProtectedSenderAfter = receivedRedeemedAssets[collateralSilo][false][e.msg.sender];
        uint256 receivedRedeemedAssetsCollateralSenderAfter = receivedRedeemedAssets[collateralSilo][true][e.msg.sender];

        //asserts
        assert increasedWithoutChecksProtectedSenderAfter == increasedWithoutChecksProtectedSenderBefore + withdrawAssetsFromProtected;
        assert increasedWithoutChecksCollateralSenderAfter == increasedWithoutChecksCollateralSenderBefore + withdrawAssetsFromCollateral;
        assert receivedRedeemedAssetsProtectedSenderAfter == receivedRedeemedAssetsProtectedSenderBefore;
        assert receivedRedeemedAssetsCollateralSenderAfter == receivedRedeemedAssetsCollateralSenderBefore;
    }

    // liquidationCall() _receiveSToken == false: balance collateralAssetSender increased by withdrawAssetsFromCollateral and withdrawAssetsFromProtected and collateralShare of msg.sender do not change
    rule collateralSharesDoNotChange(env e){
        configForEightTokensSetupRequirements();
        address collateralAsset;
        address debtAsset;
        address borrower;
        uint256 maxDebtToCover;
        bool receiveSToken;

        //setup
        require !receiveSToken;
        require e.msg.sender != currentContract;
        address collateralSilo;
        address debtSilo;
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (collateralSilo, debtSilo, collateralConfig, debtConfig) = setupLiquidationRules(e, borrower);
        uint256 withdrawAssetsFromCollateral;
        uint256 withdrawAssetsFromProtected;
        uint256 repayDebtAssets;
        bytes4 customError;
        (withdrawAssetsFromCollateral, withdrawAssetsFromProtected, repayDebtAssets, customError) = 
        getExactLiquidationAmountsCVL(collateralConfig, debtConfig, borrower, maxDebtToCover, collateralConfig.liquidationFee); 

        //values before
        uint256 increasedWithoutChecksProtectedSenderBefore = increasedWithoutChecks[collateralConfig.protectedShareToken][e.msg.sender];
        uint256 increasedWithoutChecksCollateralSenderBefore = increasedWithoutChecks[collateralSilo][e.msg.sender];
        uint256 receivedRedeemedAssetsProtectedSenderBefore = receivedRedeemedAssets[collateralSilo][false][e.msg.sender];
        uint256 receivedRedeemedAssetsCollateralSenderBefore = receivedRedeemedAssets[collateralSilo][true][e.msg.sender];

        //function call
        liquidationCall(e, collateralAsset, debtAsset, borrower, maxDebtToCover, receiveSToken);

        //values after
        uint256 increasedWithoutChecksProtectedSenderAfter = increasedWithoutChecks[collateralConfig.protectedShareToken][e.msg.sender];
        uint256 increasedWithoutChecksCollateralSenderAfter = increasedWithoutChecks[collateralSilo][e.msg.sender];
        uint256 receivedRedeemedAssetsProtectedSenderAfter = receivedRedeemedAssets[collateralSilo][false][e.msg.sender];
        uint256 receivedRedeemedAssetsCollateralSenderAfter = receivedRedeemedAssets[collateralSilo][true][e.msg.sender];

        //asserts
        assert increasedWithoutChecksProtectedSenderAfter == increasedWithoutChecksProtectedSenderBefore;
        assert increasedWithoutChecksCollateralSenderAfter == increasedWithoutChecksCollateralSenderBefore;
        assert receivedRedeemedAssetsProtectedSenderAfter == receivedRedeemedAssetsProtectedSenderBefore + withdrawAssetsFromProtected;
        assert receivedRedeemedAssetsCollateralSenderAfter == receivedRedeemedAssetsCollateralSenderBefore + withdrawAssetsFromCollateral;
    }

    // liquidationCall() msg.sender never pays more than _maxDebtToConvert
    rule msgSenderNeverPaysMoreThanMaxDebtToCover(env e){
        configForEightTokensSetupRequirements();
        address collateralAsset;
        address debtAsset;
        address borrower;
        uint256 maxDebtToCover;
        bool receiveSToken;

        //setup
        address collateralSilo;
        address debtSilo;
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (collateralSilo, debtSilo, collateralConfig, debtConfig) = setupLiquidationRules(e, borrower);
        uint256 withdrawAssetsFromCollateral;
        uint256 withdrawAssetsFromProtected;
        uint256 repayDebtAssets;
        bytes4 customError;
        (withdrawAssetsFromCollateral, withdrawAssetsFromProtected, repayDebtAssets, customError) = 
        getExactLiquidationAmountsCVL(collateralConfig, debtConfig, borrower, maxDebtToCover, collateralConfig.liquidationFee); 

        //values before
        uint256 sentTransferredAssetsSenderBefore = sentTransferredAssets[debtConfig.token][e.msg.sender];

        //function call
        liquidationCall(e, collateralAsset, debtAsset, borrower, maxDebtToCover, receiveSToken);

        //values after
        uint256 sentTransferredAssetsSenderAfter = sentTransferredAssets[debtConfig.token][e.msg.sender];
        

        //asserts
        assert sentTransferredAssetsSenderAfter - sentTransferredAssetsSenderBefore <= maxDebtToCover;
    }

    // liquidationCall() balanceUnderlingToken increases by repayDebtAssets
    rule debtTokenBalanceOfSiloIncreasesByRepayDebtAssets(env e){
        configForEightTokensSetupRequirements();
        address collateralAsset;
        address debtAsset;
        address borrower;
        uint256 maxDebtToCover;
        bool receiveSToken;

        //setup
        address collateralSilo;
        address debtSilo;
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (collateralSilo, debtSilo, collateralConfig, debtConfig) = setupLiquidationRules(e, borrower);
        uint256 withdrawAssetsFromCollateral;
        uint256 withdrawAssetsFromProtected;
        uint256 repayDebtAssets;
        bytes4 customError;
        (withdrawAssetsFromCollateral, withdrawAssetsFromProtected, repayDebtAssets, customError) = 
        getExactLiquidationAmountsCVL(collateralConfig, debtConfig, borrower, maxDebtToCover, collateralConfig.liquidationFee); 
            

        //values before
        uint256 repayedAssetsToSiloDebtSilo = repayedAssetsToSilo[debtSilo];

        //function call
        liquidationCall(e, collateralAsset, debtAsset, borrower, maxDebtToCover, receiveSToken);

        //values after
        uint256 repayedAssetsToSiloDebtSiloAfter = repayedAssetsToSilo[debtSilo];

        //asserts
        assert repayedAssetsToSiloDebtSiloAfter == repayedAssetsToSiloDebtSilo + repayDebtAssets;
    }


    // liquidationCall()  _receiveSToken == true: balance underlingToken does not change
    rule underlyingTokenBalanceOfCollateralSiloDoesNotChange(env e){
        configForEightTokensSetupRequirements();
        address collateralAsset;
        address debtAsset;
        address borrower;
        uint256 maxDebtToCover;
        bool receiveSToken;

        //setup
        require(receiveSToken);
        address collateralSilo;
        address debtSilo;
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (collateralSilo, debtSilo, collateralConfig, debtConfig) = setupLiquidationRules(e, borrower);
        uint256 withdrawAssetsFromCollateral;
        uint256 withdrawAssetsFromProtected;
        uint256 repayDebtAssets;
        bytes4 customError;
        (withdrawAssetsFromCollateral, withdrawAssetsFromProtected, repayDebtAssets, customError) = 
        getExactLiquidationAmountsCVL(collateralConfig, debtConfig, borrower, maxDebtToCover, collateralConfig.liquidationFee); 

        //values before
        uint256 redeemedAssetsFromSiloCollateralSiloBefore = redeemedAssetsFromSilo[collateralSilo];

        //function call
        liquidationCall(e, collateralAsset, debtAsset, borrower, maxDebtToCover, receiveSToken);

        //values after
        uint256 redeemedAssetsFromSiloCollateralSiloAfter = redeemedAssetsFromSilo[collateralSilo];

        //asserts
        assert redeemedAssetsFromSiloCollateralSiloAfter == redeemedAssetsFromSiloCollateralSiloBefore;
    }

    // liquidationCall() _receiveSToken == false: balance of underlingToken is reduced by withdrawAssetsFromCollateral and withdrawAssetsFromProtected
    rule underlyingTokenBalanceOfCollateralSiloDecreasesByWithdrawAssets(env e){
        configForEightTokensSetupRequirements();
        address collateralAsset;
        address debtAsset;
        address borrower;
        uint256 maxDebtToCover;
        bool receiveSToken;

        //setup
        require !receiveSToken;
        address collateralSilo;
        address debtSilo;
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (collateralSilo, debtSilo, collateralConfig, debtConfig) = setupLiquidationRules(e, borrower);
        uint256 withdrawAssetsFromCollateral;
        uint256 withdrawAssetsFromProtected;
        uint256 repayDebtAssets;
        bytes4 customError;
        (withdrawAssetsFromCollateral, withdrawAssetsFromProtected, repayDebtAssets, customError) = 
        getExactLiquidationAmountsCVL(collateralConfig, debtConfig, borrower, maxDebtToCover, collateralConfig.liquidationFee); 

        //values before
        uint256 redeemedAssetsFromSiloCollateralSiloBefore = redeemedAssetsFromSilo[collateralSilo];

        //function call
        liquidationCall(e, collateralAsset, debtAsset, borrower, maxDebtToCover, receiveSToken);

        //values after
        uint256 redeemedAssetsFromSiloCollateralSiloAfter = redeemedAssetsFromSilo[collateralSilo];

        //asserts
        assert redeemedAssetsFromSiloCollateralSiloAfter == redeemedAssetsFromSiloCollateralSiloBefore + withdrawAssetsFromCollateral + withdrawAssetsFromProtected;
    }

    // liquidationCall() only values in the right silo change (debtSilo and collaterealSilo are not the same)
    rule onlyValuesInRightSiloChange(env e){
        configForEightTokensSetupRequirements();
        address collateralAsset;
        address debtAsset;
        address borrower;
        uint256 maxDebtToCover;
        bool receiveSToken;

        //setup
        address collateralSilo;
        address debtSilo;
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (collateralSilo, debtSilo, collateralConfig, debtConfig) = setupLiquidationRules(e, borrower);
        uint256 withdrawAssetsFromCollateral;
        uint256 withdrawAssetsFromProtected;
        uint256 repayDebtAssets;
        bytes4 customError;
        (withdrawAssetsFromCollateral, withdrawAssetsFromProtected, repayDebtAssets, customError) = 
        getExactLiquidationAmountsCVL(collateralConfig, debtConfig, borrower, maxDebtToCover, collateralConfig.liquidationFee); 
        address anyUser;
        nonSceneAddressRequirements(anyUser);

        //values before
        //_callShareTokenForwardTransferNoChecks
        uint256 reducedWithoutChecksAnyUserDebtSiloProtectedBefore = reducedWithoutChecks[debtConfig.protectedShareToken][anyUser];
        uint256 reducedWithoutChecksAnyUserDebtSiloCollateralBefore = reducedWithoutChecks[debtSilo][anyUser];
        //repay
        uint256 repayedAssetsToSiloCollateralSiloBefore = repayedAssetsToSilo[collateralSilo];
        //redeem
        uint256 redeemedAssetsFromSiloDebtSiloBefore = redeemedAssetsFromSilo[debtSilo];

        //function call
        liquidationCall(e, collateralAsset, debtAsset, borrower, maxDebtToCover, receiveSToken);

        //values after
        //_callShareTokenForwardTransferNoChecks
        uint256 reducedWithoutChecksAnyUserDebtSiloProtectedAfter = reducedWithoutChecks[debtConfig.protectedShareToken][anyUser];
        uint256 reducedWithoutChecksAnyUserDebtSiloCollateralAfter = reducedWithoutChecks[debtSilo][anyUser];
        //repay
        uint256 repayedAssetsToSiloCollateralSiloAfter = repayedAssetsToSilo[collateralSilo];
        //redeem
        uint256 redeemedAssetsFromSiloDebtSiloAfter = redeemedAssetsFromSilo[debtSilo];

        //asserts
        assert reducedWithoutChecksAnyUserDebtSiloProtectedAfter == reducedWithoutChecksAnyUserDebtSiloProtectedBefore;
        assert reducedWithoutChecksAnyUserDebtSiloCollateralAfter == reducedWithoutChecksAnyUserDebtSiloCollateralBefore;
        assert repayedAssetsToSiloCollateralSiloAfter == repayedAssetsToSiloCollateralSiloBefore;
        assert redeemedAssetsFromSiloDebtSiloAfter == redeemedAssetsFromSiloDebtSiloBefore;
    }

    // hookReceiver never owns collateralShares ( require hookReceiver not to be msg.sender)
    rule hookReceiverNeverOwnsCollateralShares(env e){
        configForEightTokensSetupRequirements();
        address collateralAsset;
        address debtAsset;
        address borrower;
        uint256 maxDebtToCover;
        bool receiveSToken;

        //setup
        require(currentContract != e.msg.sender);
        require(currentContract != borrower);
        address collateralSilo;
        address debtSilo;
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (collateralSilo, debtSilo, collateralConfig, debtConfig) = setupLiquidationRules(e, borrower);
        uint256 withdrawAssetsFromCollateral;
        uint256 withdrawAssetsFromProtected;
        uint256 repayDebtAssets;
        bytes4 customError;
        (withdrawAssetsFromCollateral, withdrawAssetsFromProtected, repayDebtAssets, customError) = 
        getExactLiquidationAmountsCVL(collateralConfig, debtConfig, borrower, maxDebtToCover, collateralConfig.liquidationFee); 

        //values before
        //_callShareTokenForwardTransferNoChecks
        uint256 increasedWithoutChecksCurrentContractProtectedBefore = increasedWithoutChecks[collateralConfig.protectedShareToken][currentContract];
        uint256 increasedWithoutChecksCurrentContractCollateralBefore = increasedWithoutChecks[collateralSilo][currentContract];
        //redeem
        uint256 redeemedAssetsProtectedcurrentContract = redeemedAssets[collateralSilo][false][currentContract];
        uint256 redeemedAssetsCollateralcurrentContract = redeemedAssets[collateralSilo][true][currentContract];

        //function call
        liquidationCall(e, collateralAsset, debtAsset, borrower, maxDebtToCover, receiveSToken);

        //values after
        //_callShareTokenForwardTransferNoChecks
        uint256 increasedWithoutChecksCurrentContractProtectedAfter = increasedWithoutChecks[collateralConfig.protectedShareToken][currentContract];
        uint256 increasedWithoutChecksCurrentContractCollateralAfter = increasedWithoutChecks[collateralSilo][currentContract];
        //redeem
        uint256 redeemedAssetsProtectedCurrentContractAfter = redeemedAssets[collateralSilo][false][currentContract];
        uint256 redeemedAssetsCollateralCurrentContractAfter = redeemedAssets[collateralSilo][true][currentContract];

        //calculations
        mathint receivedProtectedShares = increasedWithoutChecksCurrentContractProtectedAfter - increasedWithoutChecksCurrentContractProtectedBefore;  
        mathint receivedCollateralShares = increasedWithoutChecksCurrentContractCollateralAfter - increasedWithoutChecksCurrentContractCollateralBefore;
        mathint redeemedProtectedShares = redeemedAssetsProtectedCurrentContractAfter - redeemedAssetsProtectedcurrentContract;
        mathint redeemedCollateralShares = redeemedAssetsCollateralCurrentContractAfter - redeemedAssetsCollateralcurrentContract;
        

        //asserts
        assert receivedProtectedShares == redeemedProtectedShares;
        assert receivedCollateralShares == redeemedCollateralShares; 
    }


    //liquidationCall returns the right values
    rule liquidationCallReturnsRightValues(env e){
        configForEightTokensSetupRequirements();
        address collateralAsset;
        address debtAsset;
        address borrower;
        uint256 maxDebtToCover;
        bool receiveSToken;

        //setup
        address collateralSilo;
        address debtSilo;
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (collateralSilo, debtSilo, collateralConfig, debtConfig) = setupLiquidationRules(e, borrower);
        uint256 withdrawAssetsFromCollateral;
        uint256 withdrawAssetsFromProtected;
        uint256 repayDebtAssets;
        bytes4 customError;
        (withdrawAssetsFromCollateral, withdrawAssetsFromProtected, repayDebtAssets, customError) = 
        getExactLiquidationAmountsCVL(collateralConfig, debtConfig, borrower, maxDebtToCover, collateralConfig.liquidationFee); 

        //function call
        uint256 withdrawCollateralResult;
        uint256 repayDebtAssetsResult;
        (withdrawCollateralResult, repayDebtAssetsResult) = 
        liquidationCall(e, collateralAsset, debtAsset, borrower, maxDebtToCover, receiveSToken);

        //asserts
        assert withdrawCollateralResult == withdrawAssetsFromCollateral + withdrawAssetsFromProtected;
        assert repayDebtAssetsResult == repayDebtAssets;
    }

    


//------------------------------- RULES TEST END ----------------------------------

//------------------------------- RULES PROBLEMS START ----------------------------------


//------------------------------- RULES PROBLEMS START ----------------------------------

//------------------------------- RULES OK START ------------------------------------

   
     // revert if siloConfig is not set
    rule revertIfSiloConfigIsNotSet(env e){
        address collateralAsset;
        address debtAsset;
        address borrower;
        uint256 maxDebtToCover;
        bool receiveSToken;

        //require siloConfig is not set
        require siloConfig(e) == 0;

        //function call
        liquidationCall@withrevert(e, collateralAsset, debtAsset, borrower, maxDebtToCover, receiveSToken);
        
        //call reverted
        assert lastReverted;        
    }

    // 	liquidationCall() reverts if _maxDebtToConvert == 0
    rule revertIfMaxDebtToConvertIsZero(env e){
        configForEightTokensSetupRequirements();
        address collateralAsset;
        address debtAsset;
        address borrower;
        uint256 maxDebtToCover;
        bool receiveSToken;
        require maxDebtToCover == 0;

        //function call
        liquidationCall@withrevert(e, collateralAsset, debtAsset, borrower, maxDebtToCover, receiveSToken);
        
        //call reverted
        assert lastReverted;        
    }

    
    //hookReceiverConfig() always returns (0,0)
    rule hookReceiverConfigAlwaysReturnsZero(env e, address _address){
        uint24 hooksBefore;
        uint24 hooksAfter;
        (hooksBefore, hooksAfter) = hookReceiverConfig(e, _address);
        assert hooksBefore == 0;
        assert hooksAfter == 0;
    }

    //calling beforeAction and afterAction should never revert
    rule beforeAfterActionNeverReverts(env e, address _address, uint256 number, bytes data){
        require(e.msg.value == 0);
        
        beforeAction@withrevert(e, _address, number, data);
        assert(!lastReverted, "beforeAction reverted");
        
        afterAction@withrevert(e, _address, number, data);
        assert(!lastReverted, "afterAction reverted");
    }

    //calling beforeAction and afterAction does not change any state
    rule beforeAfterActionDoesNotChangeState(env e, address _address, uint256 number, bytes data){
        storage initial = lastStorage;
        beforeAction@withrevert(e, _address, number, data);
        afterAction@withrevert(e, _address, number, data);
        storage final = lastStorage;
        assert initial == final;
    }

//------------------------------- RULES OK END ------------------------------------

//------------------------------- INVARIENTS OK START-------------------------------

//------------------------------- INVARIENTS OK END-------------------------------

//------------------------------- ISSUES OK START-------------------------------

//------------------------------- ISSUES OK END-------------------------------


//-------------------------------OLD RULES START----------------------------------


    rule doesntAlwaysRevert(method f, env e)
        filtered { f -> !ignoredMethod(f) }
    {
        SafeAssumptionsEnv_withInvariants(e);
        calldataarg args;
        f(e, args);
        satisfy true;
    }

    // rule maxLiquidationNeverReverts(env e, address user)
    // {
    //     address colSiloBefore = siloConfig(e).borrowerCollateralSilo(e, user);
    //     require colSiloBefore == silo0 || colSiloBefore == silo1 || colSiloBefore == 0;
    //     SafeAssumptions_withInvariants(e, user);
    //     uint256 collateralToLiquidate; uint256 debtToRepay; bool sTokenRequired;
    //     collateralToLiquidate, debtToRepay, sTokenRequired = maxLiquidation@withrevert(e, user);
    //     assert !lastReverted;
    // }

//-------------------------------OLD RULES END----------------------------------


