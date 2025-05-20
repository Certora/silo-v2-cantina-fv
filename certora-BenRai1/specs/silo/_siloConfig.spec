import "../setup/CompleteSiloSetup.spec";

//------------------------------------ SETUP START --------------------------------------

    methods {
        // function _.accrueInterestForConfig(address, uint256, uint256) external => accrueInterestForSiloCVL(calledContract) expect void;
    }

    function accrueInterestForSiloCVL(address silo) {
        accrueInterestCalled[silo] = accrueInterestCalled[silo] + 1;
    }


    ghost mapping (address => mathint) accrueInterestCalled;

    function debtSiloAndCollateralSiloAreDifferent(env e, address borrower) {
        address debtSilo = siloConfig.getDebtSilo(e, borrower);
        address collateralSilo = siloConfig.borrowerCollateralSilo[borrower];
        require debtSilo != collateralSilo || debtSilo == 0 && collateralSilo == 0;
        require debtSilo == silo0 || collateralSilo == silo1 || debtSilo == 0;
        require collateralSilo == silo0 || collateralSilo == silo1 || collateralSilo == 0;
    }

//------------------------------------ SETUP END --------------------------------------

//------------------------------- RULES TEST START ----------------------------------



    // // setThisSiloAsCollateralSilo() can only be called by silo //@audit-issue fails
    // rule setThisSiloAsCollateralSiloOnlyBySilo(env e) {
    //     configForEightTokensSetupRequirements();
    //     address borrower;

    //     //function call
    //     siloConfig.setThisSiloAsCollateralSilo@withrevert(e, borrower);

    //     //assert
    //     assert e.msg.sender != silo0 || e.msg.sender != silo0 => lastReverted;
    // }




    // getConfigsForBorrow() reverts if input silo is not silo0 or silo1
    rule getConfigsForBorrowRevertsIfSiloNotSilo0OrSilo1(env e) {
        configForEightTokensSetupRequirements();
        address debtSilo;

        //function call
        siloConfig.getConfigsForBorrow@withrevert(e, debtSilo);

        //assert
        assert debtSilo != silo0 && debtSilo != silo1 => lastReverted;
    }

    // * `getConfigsForBorrow()` collateralConfig.silo is always equal to other silo than _debtSilo
    rule getConfigsForBorrowCollateralSiloIsNotDebtSilo(env e) {
        configForEightTokensSetupRequirements();
        address debtSilo;

        //function call
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (collateralConfig, debtConfig) = siloConfig.getConfigsForBorrow(e,debtSilo);


        //assert
        assert collateralConfig.silo != debtSilo;
        assert debtSilo == silo0 => collateralConfig.silo == silo1;
        assert debtSilo == silo1 => collateralConfig.silo == silo0;
    }

    // * `getConfigsForBorrow()` debtConfig.silo is always equal _debtSilo
    rule getConfigsForBorrowDebtSiloIsDebtSilo(env e) {
        configForEightTokensSetupRequirements();
        address debtSilo;

        //function call
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (collateralConfig, debtConfig) = siloConfig.getConfigsForBorrow(e,debtSilo);

        //assert
        assert debtConfig.silo == debtSilo;
    }

    // * `getConfigsForSolvency()` collateralConfig.silo is equal `borrowerCollateralSilo[borrower]` if there is debt
    rule getConfigsForSolvencyCollateralSiloIsBorrowerCollateralSilo(env e) { 
        configForEightTokensSetupRequirements();
        address borrower;
        debtSiloAndCollateralSiloAreDifferent(e, borrower);

        //function call
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (collateralConfig, debtConfig) = siloConfig.getConfigsForSolvency(e,borrower);

        //assert
        assert siloConfig.getDebtSilo(e, borrower) != 0 => siloConfig.borrowerCollateralSilo[borrower] == collateralConfig.silo;
    }

    // * `getConfigsForSolvency()` debtConfig.silo is always the silo that debt share token balance is not equal 0 or zero address otherwise
    rule getConfigsForSolvencyDebtSiloIsDebtSilo(env e) {
        configForEightTokensSetupRequirements();
        address borrower;
        debtSiloAndCollateralSiloAreDifferent(e, borrower);

        //function call
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (collateralConfig, debtConfig) = siloConfig.getConfigsForSolvency(e,borrower);

        //assert
        assert debtConfig.silo == 0 => shareDebtToken0.balanceOf(borrower) == 0 && shareDebtToken1.balanceOf(borrower) == 0;
        assert debtConfig.silo != 0 => debtConfig.debtShareToken.balanceOf(e, borrower) != 0 && collateralConfig.debtShareToken.balanceOf(e, borrower) == 0;
    }

    // * `getConfigsForSolvency()` if no debt, both configs (collateralConfig, debtConfig) are zero
    rule getConfigsForSolvencyIfNoDebtBothConfigsAreZero(env e) {
        configForEightTokensSetupRequirements();
        address borrower;

        //function call
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (collateralConfig, debtConfig) = siloConfig.getConfigsForSolvency(e,borrower);

        //assert
        assert shareDebtToken0.balanceOf(borrower) == 0 && shareDebtToken1.balanceOf(borrower) == 0 => collateralConfig.silo == 0 && debtConfig.silo == 0;
    }

    // * `getConfigsForWithdraw()` collateralConfig.silo is equal `borrowerCollateralSilo[depositOwner]` if there is debt
    rule getConfigsForWithdrawCollateralSiloIsBorrowerCollateralSilo(env e) { 
        configForEightTokensSetupRequirements();
        address silo;
        address depositOwner;

        //function call
        ISiloConfig.DepositConfig depositConfig;
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (depositConfig, collateralConfig, debtConfig) = siloConfig.getConfigsForWithdraw(e, silo, depositOwner);

        //assert
        assert shareDebtToken0.balanceOf(depositOwner) != 0 || shareDebtToken1.balanceOf(depositOwner) != 0 && 
            !(shareDebtToken0.balanceOf(depositOwner) != 0 && shareDebtToken1.balanceOf(depositOwner) != 0) =>  siloConfig.borrowerCollateralSilo[depositOwner] == collateralConfig.silo;
    }

    // * `getConfigsForWithdraw()` debtConfig.silo is always the silo that debt share token balance is not equal 0 or zero address otherwise
    rule getConfigsForWithdrawDebtSiloIsDebtSilo(env e) {
        configForEightTokensSetupRequirements();
        address silo;
        address depositOwner;
        debtSiloAndCollateralSiloAreDifferent(e, depositOwner);

        //function call
        ISiloConfig.DepositConfig depositConfig;
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (depositConfig, collateralConfig, debtConfig) = siloConfig.getConfigsForWithdraw(e, silo, depositOwner);

        //assert
        assert debtConfig.silo == 0 => shareDebtToken0.balanceOf(depositOwner) == 0 && shareDebtToken1.balanceOf(depositOwner) == 0;
        assert debtConfig.silo != 0 => debtConfig.debtShareToken.balanceOf(e, depositOwner) != 0 && collateralConfig.debtShareToken.balanceOf(e, depositOwner) == 0;
    }

    // * `getConfigsForWithdraw()` depositConfig.silo is always _silo
    rule getConfigsForWithdrawDepositSiloIsSilo(env e) {
        configForEightTokensSetupRequirements();
        address silo;
        address depositOwner;

        //function call
        ISiloConfig.DepositConfig depositConfig;
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (depositConfig, collateralConfig, debtConfig) = siloConfig.getConfigsForWithdraw(e, silo, depositOwner);

        //assert
        assert depositConfig.silo == silo;
    }

    // * `getConfigsForWithdraw()` if debtConfig.silo is not zero then collateralConfig.silo is not zero
    rule getConfigsForWithdrawIfDebtSiloNotZeroThenCollateralSiloNotZero(env e) {
        configForEightTokensSetupRequirements();
        address silo;
        address depositOwner;

        //function call
        ISiloConfig.DepositConfig depositConfig;
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (depositConfig, collateralConfig, debtConfig) = siloConfig.getConfigsForWithdraw(e, silo, depositOwner);

        //assert
        assert debtConfig.silo != 0 => collateralConfig.silo != 0;
    }

    // * `getConfigsForWithdraw()` if no debt, both configs (collateralConfig, debtConfig) are zero
    rule getConfigsForWithdrawIfNoDebtBothConfigsAreZero(env e) {
        configForEightTokensSetupRequirements();
        address silo;
        address depositOwner;

        //function call
        ISiloConfig.DepositConfig depositConfig;
        ISiloConfig.ConfigData collateralConfig;
        ISiloConfig.ConfigData debtConfig;
        (depositConfig, collateralConfig, debtConfig) = siloConfig.getConfigsForWithdraw(e, silo, depositOwner);

        //assert
        assert shareDebtToken0.balanceOf(depositOwner) == 0 && shareDebtToken1.balanceOf(depositOwner) == 0 => collateralConfig.silo == 0 && debtConfig.silo == 0;
    }

    // getConfigsForWithdraw() reverts if input silo is not silo0 or silo1
    rule getConfigsForWithdrawRevertsIfSiloNotSilo0OrSilo1(env e) {
        configForEightTokensSetupRequirements();
        address silo;
        address depositOwner;

        //function call
        siloConfig.getConfigsForWithdraw@withrevert(e, silo, depositOwner);

        //assert
        assert silo != silo0 && silo != silo1 => lastReverted;
    }

    // setThisSiloAsCollateralSilo() borrowerCollateralSilo[_borrower] is set to msg.sender
    rule setThisSiloAsCollateralSiloCollateralSiloIsMsgSender(env e) {
        configForEightTokensSetupRequirements();
        address borrower;

        //function call
        siloConfig.setThisSiloAsCollateralSilo(e, borrower);

        //assert
        assert siloConfig.borrowerCollateralSilo[borrower] == e.msg.sender;
    }

    // setOtherSiloAsCollateralSilo() can only be called by silo
    rule setOtherSiloAsCollateralSiloOnlyBySilo(env e) {
        configForEightTokensSetupRequirements();
        address borrower;

        //function call
        siloConfig.setOtherSiloAsCollateralSilo@withrevert(e, borrower);

        //assert
        assert e.msg.sender != silo0 && e.msg.sender != silo1 => lastReverted;
    }

    // setOtherSiloAsCollateralSilo() the silo which deos not call is set to borrowerCollateralSilo[_borrower]
    rule setOtherSiloAsCollateralSiloCollateralSiloIsNotMsgSender(env e) {
        configForEightTokensSetupRequirements();
        address borrower;

        //function call
        siloConfig.setOtherSiloAsCollateralSilo(e, borrower);

        //assert
        assert e.msg.sender == silo0 => siloConfig.borrowerCollateralSilo[borrower] == silo1;
        assert e.msg.sender == silo1 => siloConfig.borrowerCollateralSilo[borrower] == silo0;
    }

    // onDebtTransfer() can only be called by _DEBT_SHARE_TOKEN0 or msg.sender == _DEBT_SHARE_TOKEN1
    rule onDebtTransferOnlyByDebtShareToken0OrDebtShareToken1(env e) {
        configForEightTokensSetupRequirements();
        address sender;
        address recipient;

        //function call
        siloConfig.onDebtTransfer@withrevert(e, sender, recipient);
        bool reverted = lastReverted;

        //assert
        assert e.msg.sender != shareDebtToken0 && e.msg.sender != shareDebtToken1 => reverted;
    }

    // onDebtTransfer() reverts if recipient has debt in silo not connected to the calling debt token
    rule onDebtTransferRevertsIfRecipientHasDebtInOtherSilo(env e) {
        configForEightTokensSetupRequirements();
        address sender;
        address recipient;

        //function call
        siloConfig.onDebtTransfer@withrevert(e, sender, recipient);
        bool reverted = lastReverted;

        //assert
        assert e.msg.sender == shareDebtToken0 && shareDebtToken1.balanceOf(recipient) != 0 => reverted;
        assert e.msg.sender == shareDebtToken1 && shareDebtToken0.balanceOf(recipient) != 0 => reverted;
    }

    // onDebtTransfer() borrowerCollateralSilo[recipient] == 0 it becomes borrowerCollateralSilo[sender]
    rule onDebtTransferCollateralSiloIsSender(env e) {
        configForEightTokensSetupRequirements();
        address sender;
        address recipient;

        //values before
        address senderCollateralSiloBefore = siloConfig.borrowerCollateralSilo[sender];
        address recipientCollateralSiloBefore = siloConfig.borrowerCollateralSilo[recipient];

        //function call
        siloConfig.onDebtTransfer(e, sender, recipient);

        //values after
        address senderCollateralSiloAfter = siloConfig.borrowerCollateralSilo[sender];
        address recipientCollateralSiloAfter = siloConfig.borrowerCollateralSilo[recipient];


        //assert
        assert recipientCollateralSiloBefore == 0 => recipientCollateralSiloAfter == senderCollateralSiloBefore;
        assert senderCollateralSiloBefore ==  senderCollateralSiloAfter;
    }

    // hasDebtInOtherSilo() reverts if input silo is not silo0 or silo1
    rule hasDebtInOtherSiloRevertsIfSiloNotSilo0OrSilo1(env e) {
        configForEightTokensSetupRequirements();
        address thisSilo;
        address borrower;

        //function call
        siloConfig.hasDebtInOtherSilo@withrevert(e, thisSilo, borrower);

        //assert
        assert thisSilo != silo0 && thisSilo != silo1 => lastReverted;
    }

    // hasDebtInOtherSilo() returns true if use has debt in other silo
    rule hasDebtInOtherSiloReturnsTrueIfUserHasDebtInOtherSilo(env e) {
        configForEightTokensSetupRequirements();
        address thisSilo;
        address borrower;

        //function call
        bool hasDebtInOtherSilo = siloConfig.hasDebtInOtherSilo(e, thisSilo, borrower);

        //assert
        assert thisSilo == silo0 && shareDebtToken1.balanceOf(borrower) != 0 => hasDebtInOtherSilo;
        assert thisSilo == silo1 && shareDebtToken0.balanceOf(borrower) != 0 => hasDebtInOtherSilo;
    }

    // hasDebtInOtherSilo() returns false if use has no debt in other silo
    rule hasDebtInOtherSiloReturnsFalseIfUserHasNoDebtInOtherSilo(env e) {
        configForEightTokensSetupRequirements();
        address thisSilo;
        address borrower;

        //function call
        bool hasDebtInOtherSilo = siloConfig.hasDebtInOtherSilo(e, thisSilo, borrower);

        //assert
        assert thisSilo == silo0 && shareDebtToken1.balanceOf(borrower) == 0 => !hasDebtInOtherSilo;
        assert thisSilo == silo1 && shareDebtToken0.balanceOf(borrower) == 0 => !hasDebtInOtherSilo;
    }

    // accrueInterestForSilo() reverts if input silo is not silo0 or silo1
    rule accrueInterestForSiloRevertsIfSiloNotSilo0OrSilo1(env e) {
        configForEightTokensSetupRequirements();
        address silo;

        //function call
        siloConfig.accrueInterestForSilo@withrevert(e, silo);

        //assert
        assert silo != silo0 && silo != silo1 => lastReverted;
    }

    // getSilos() returns silo0 first
    rule getSilosReturnsSilo0First(env e) {
        configForEightTokensSetupRequirements();

        //function call
        address firstSilo;
        address secondSilo;
        (firstSilo, secondSilo) = siloConfig.getSilos(e);

        //assert
        assert firstSilo == silo0 && secondSilo == silo1;
    }

    // getShareTokens() returns the right tokens depending on the silo
    rule getShareTokensReturnsRightTokensDependingOnSilo(env e) {
        configForEightTokensSetupRequirements();
        address silo;

        //function call
        address protectedShareToken;
        address collateralShareToken;
        address debtShareToken;
        (protectedShareToken, collateralShareToken, debtShareToken) = siloConfig.getShareTokens(e, silo);

        //assert
        assert silo == silo0 => 
                    protectedShareToken == shareProtectedCollateralToken0 &&
                    collateralShareToken == silo0 &&
                    debtShareToken == shareDebtToken0;
        assert silo == silo1 => 
                    protectedShareToken == shareProtectedCollateralToken1 &&
                    collateralShareToken == silo1 &&
                    debtShareToken == shareDebtToken1;
    }

    // getShareTokens() reverts if input silo is not silo0 or silo1
    rule getShareTokensRevertsIfSiloNotSilo0OrSilo1(env e) {
        configForEightTokensSetupRequirements();
        address silo;

        //function call
        siloConfig.getShareTokens@withrevert(e, silo);

        //assert
        assert silo != silo0 && silo != silo1 => lastReverted;
    }

    // getAssetForSilo() retruns the right asset depending on the silo
    rule getAssetForSiloReturnsRightAssetDependingOnSilo(env e) {
        configForEightTokensSetupRequirements();
        address silo;

        //function call
        address asset = siloConfig.getAssetForSilo(e, silo);

        //assert
        assert silo == silo0 => asset == token0;
        assert silo == silo1 => asset == token1;
    }

    // getAssetForSilo() reverts if input silo is not silo0 or silo1
    rule getAssetForSiloRevertsIfSiloNotSilo0OrSilo1(env e) {
        configForEightTokensSetupRequirements();
        address silo;

        //function call
        siloConfig.getAssetForSilo@withrevert(e, silo);

        //assert
        assert silo != silo0 && silo != silo1 => lastReverted;
    }

    // getCollateralShareTokenAndAsset() returns the right tokens depending on the silo
    rule getCollateralShareTokenAndAssetReturnsRightTokensDependingOnSilo(env e) {
        configForEightTokensSetupRequirements();
        address silo;
        ISilo.CollateralType collateralType;

        //function call
        address shareToken;
        address asset;
        (shareToken, asset) = siloConfig.getCollateralShareTokenAndAsset(e, silo, collateralType);

        //assert
        assert silo == silo0 && collateralType == ISilo.CollateralType.Protected => shareToken == shareProtectedCollateralToken0 && asset == token0;
        assert silo == silo0 && collateralType == ISilo.CollateralType.Collateral => shareToken == silo0 && asset == token0;
        assert silo == silo1 && collateralType == ISilo.CollateralType.Protected => shareToken == shareProtectedCollateralToken1 && asset == token1;
        assert silo == silo1 && collateralType == ISilo.CollateralType.Collateral => shareToken == silo1 && asset == token1;
    }

    // getCollateralShareTokenAndAsset() reverts if input silo is not silo0 or silo1
    rule getCollateralShareTokenAndAssetRevertsIfSiloNotSilo0OrSilo1(env e) {
        configForEightTokensSetupRequirements();
        address silo;
        ISilo.CollateralType collateralType;

        //function call
        siloConfig.getCollateralShareTokenAndAsset@withrevert(e, silo, collateralType);

        //assert
        assert silo != silo0 && silo != silo1 => lastReverted;
    }

    // getConfig() returns the right values depending on the silo
    rule getConfigReturnsRightTokensDependingOnSilo(env e) {
        configForEightTokensSetupRequirements();
        address silo;

        //target values
        uint256 daoFee0;
        uint256 deployerFee0;
        uint256 flashloanFee0; 
        address asset0;
        (daoFee0, deployerFee0, flashloanFee0, asset0) = siloConfig.getFeesWithAsset(e, silo0);

        uint256 daoFee1;
        uint256 deployerFee1;
        uint256 flashloanFee1;
        address asset1;
        (daoFee1, deployerFee1, flashloanFee1, asset1) = siloConfig.getFeesWithAsset(e, silo1);

        ISiloConfig.DepositConfig depositConfig0;
        (depositConfig0, _, _) = siloConfig.getConfigsForWithdraw(e, silo0, e.msg.sender);
        
        ISiloConfig.DepositConfig depositConfig1;
        (depositConfig1, _, _) = siloConfig.getConfigsForWithdraw(e, silo1, e.msg.sender);


        //function call
        ISiloConfig.ConfigData config = siloConfig.getConfig(e, silo);

        //assert
        assert silo == silo0 => 
                    config.daoFee == daoFee0 &&
                    config.deployerFee == deployerFee0 &&
                    config.silo == silo0 &&
                    config.token == token0 &&
                    config.protectedShareToken == shareProtectedCollateralToken0 &&
                    config.collateralShareToken == silo0 &&
                    config.debtShareToken == shareDebtToken0 &&
                    config.interestRateModel == depositConfig0.interestRateModel &&
                    config.flashloanFee == flashloanFee0;
                    
        assert silo == silo1 => 
                    config.daoFee == daoFee1 &&
                    config.deployerFee == deployerFee1 &&
                    config.silo == silo1 &&
                    config.token == token1 &&
                    config.protectedShareToken == shareProtectedCollateralToken1 &&
                    config.collateralShareToken == silo1 &&
                    config.debtShareToken == shareDebtToken1 &&
                    config.interestRateModel == depositConfig1.interestRateModel &&
                    config.flashloanFee == flashloanFee1;
    }

    // getConfig() reverts if input silo is not silo0 or silo1
    rule getConfigRevertsIfSiloNotSilo0OrSilo1(env e) {
        configForEightTokensSetupRequirements();
        address silo;

        //function call
        siloConfig.getConfig@withrevert(e, silo);

        //assert
        assert silo != silo0 && silo != silo1 => lastReverted;
    }

    // getDebtSilo() reverts if borrower has debtTokens in both silos
    rule getDebtSiloRevertsIfBorrowerHasDebtTokensInBothSilos(env e) {
        configForEightTokensSetupRequirements();
        address borrower;

        //function call
        siloConfig.getDebtSilo@withrevert(e, borrower);
        bool reverted = lastReverted;

        //assert
        assert shareDebtToken0.balanceOf(borrower) != 0 && shareDebtToken1.balanceOf(borrower) != 0 => reverted;
    }

    // getDebtSilo() returns 0 if borrower has no debtTokens
    rule getDebtSiloReturns0IfBorrowerHasNoDebtTokens(env e) {
        configForEightTokensSetupRequirements();
        address borrower;

        //function call
        address debtSilo = siloConfig.getDebtSilo(e, borrower);

        //assert
        assert shareDebtToken0.balanceOf(borrower) == 0 && shareDebtToken1.balanceOf(borrower) == 0 => debtSilo == 0;
    }

    // getDebtSilo() returns the silo if borrower has debtTokens for one silo
    rule getDebtSiloReturnsSiloIfBorrowerHasDebtTokensForOneSilo(env e) {
        configForEightTokensSetupRequirements();
        address borrower;

        //function call
        address debtSilo = siloConfig.getDebtSilo(e, borrower);

        //assert
        assert shareDebtToken0.balanceOf(borrower) != 0 && shareDebtToken1.balanceOf(borrower) == 0 => debtSilo == silo0;
        assert shareDebtToken0.balanceOf(borrower) == 0 && shareDebtToken1.balanceOf(borrower) != 0 => debtSilo == silo1;
    }

    // getFeesWithAsset() returns the right values based on the silo
    rule getFeesWithAssetReturnsRightValuesBasedOnSilo(env e) {
        configForEightTokensSetupRequirements();
        address silo;

        //target values
        ISiloConfig.ConfigData configSilo0 = siloConfig.getConfig(e, silo0);
        ISiloConfig.ConfigData configSilo1 = siloConfig.getConfig(e, silo1);

        //function call
        uint256 daoFee;
        uint256 deployerFee;
        uint256 flashloanFee; 
        address asset;
        (daoFee, deployerFee, flashloanFee, asset) = siloConfig.getFeesWithAsset(e, silo);

        //assert
        assert silo == silo0 => 
                    daoFee == configSilo0.daoFee &&
                    deployerFee == configSilo0.deployerFee &&
                    flashloanFee == configSilo0.flashloanFee &&
                    asset == token0;
        assert silo == silo1 => 
                    daoFee == configSilo1.daoFee &&
                    deployerFee == configSilo1.deployerFee &&
                    flashloanFee == configSilo1.flashloanFee &&
                    asset == token1;
    }

    // getFeesWithAsset() reverts if input silo is not silo0 or silo1
    rule getFeesWithAssetRevertsIfSiloNotSilo0OrSilo1(env e) {
        configForEightTokensSetupRequirements();
        address silo;

        //function call
        siloConfig.getFeesWithAsset@withrevert(e, silo);

        //assert
        assert silo != silo0 && silo != silo1 => lastReverted;
    }

    // getDebtShareTokenAndAsset() returns the right values based on the silo
    rule getDebtShareTokenAndAssetReturnsRightValuesBasedOnSilo(env e) {
        configForEightTokensSetupRequirements();
        address silo;

        //function call
        address debtShareToken;
        address asset;
        (debtShareToken, asset) = siloConfig.getDebtShareTokenAndAsset(e, silo);

        //assert
        assert silo == silo0 => 
                    debtShareToken == shareDebtToken0 &&
                    asset == token0;
        assert silo == silo1 => 
                    debtShareToken == shareDebtToken1 &&
                    asset == token1;
    }

    // getDebtShareTokenAndAsset() reverts if input silo is not silo0 or silo1
    rule getDebtShareTokenAndAssetRevertsIfSiloNotSilo0OrSilo1(env e) {
        configForEightTokensSetupRequirements();
        address silo;

        //function call
        siloConfig.getDebtShareTokenAndAsset@withrevert(e, silo);

        //assert
        assert silo != silo0 && silo != silo1 => lastReverted;
    }


