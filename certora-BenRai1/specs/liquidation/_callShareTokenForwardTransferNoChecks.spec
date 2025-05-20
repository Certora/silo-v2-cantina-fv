import "../setup/CompleteSiloSetup.spec";

//----------------------------SETUP---------------------------------
    methods{
        function _.convertToShares(uint256 _assets, uint256 _totalAssets, uint256 _totalShares, Math.Rounding _rounding, ISilo.AssetType _assetType) internal => convertToSharesCVL(_assets) expect uint256;
        function _.forwardTransferFromNoChecks(address, address,uint256) external => DISPATCHER(true);
    }

    function convertToSharesCVL(uint256 _assets) returns uint256 {
        return require_uint256(_assets - 1); // to be able to test shares
    }

//------------------------------- RULES ----------------------------------

// _callShareTokenForwardTransferNoChecks() returns 0 if shares are 0 and nothing changes
rule returnsZeroIfSharesAreZero(env e) {
    configForEightTokensSetupRequirements();
    address silo;
    address borrower;
    address receiver;
    uint256 withdrawAssets;
    address shareToken;
    ISilo.AssetType assetType;
    require(silo == silo0 || silo == silo1);
    //require
    require(convertToSharesCVL(withdrawAssets) == 0);

    storage initStorage = lastStorage;

    //function call
    uint256 result = _callShareTokenForwardTransferNoChecksHarness(e, silo, borrower, receiver, withdrawAssets, shareToken, assetType);

    storage finalStorage = lastStorage;

    //assert
    assert result == 0;
    assert finalStorage == initStorage;
}

// _callShareTokenForwardTransferNoChecks() returns 0 if  _withdrawAssets == 0 and nothing changes
rule returnsZeroIfWithdrawAssetsAreZero(env e) {
    configForEightTokensSetupRequirements();
    address silo;
    address borrower;
    address receiver;
    uint256 withdrawAssets;
    address shareToken;
    ISilo.AssetType assetType;
    require(silo == silo0 || silo == silo1);
    //require
    require(withdrawAssets == 0);

    storage initStorage = lastStorage;

    //function call
    uint256 result = _callShareTokenForwardTransferNoChecksHarness(e, silo, borrower, receiver, withdrawAssets, shareToken, assetType);

    storage finalStorage = lastStorage;

    //assert
    assert result == 0;
    assert finalStorage == initStorage;
}

// _callShareTokenForwardTransferNoChecks() share balance of borrower is reduced by shares / of receiver is increased by shares
rule shareBalanceOfBorrowerIsReducedBySharesOfReceiverIsIncreasedByShares(env e) {
    configForEightTokensSetupRequirements();
    address silo;
    address borrower;
    address receiver;
    require(borrower != receiver);
    totalSuppliesMoreThanBalances(receiver, borrower);
    uint256 withdrawAssets;
    address shareToken;
    ISilo.AssetType assetType;
    require(silo == silo0 || silo == silo1);
    //require
    require(withdrawAssets > 1);
    require(borrower != receiver);

    //values before
    uint256 borrowerSharesBefore =  shareToken.balanceOf(e,borrower);
    uint256 receiverSharesBefore =  shareToken.balanceOf(e,receiver);


    //function call
    uint256 shares = _callShareTokenForwardTransferNoChecksHarness(e, silo, borrower, receiver, withdrawAssets, shareToken, assetType);

    //values after
    uint256 borrowerSharesAfter =  shareToken.balanceOf(e,borrower);
    uint256 receiverSharesAfter =  shareToken.balanceOf(e,receiver);

    //assert
    assert borrowerSharesAfter == borrowerSharesBefore - shares;
    assert receiverSharesAfter == receiverSharesBefore + shares;
}

// _callShareTokenForwardTransferNoChecks() transferWithChecks before and after is true
rule transferWithChecksAfterIsTrue(env e) {
    configForEightTokensSetupRequirements();
    address silo;
    address borrower;
    address receiver;
    uint256 withdrawAssets;
    address shareToken;
    ISilo.AssetType assetType;
    require(silo == silo0);
    //require
    require(withdrawAssets > 1);


    //function call
    uint256 shares = _callShareTokenForwardTransferNoChecksHarness(e, silo, borrower, receiver, withdrawAssets, shareToken, assetType);

    //values after
    bool transferWithChecksAfter =  shareToken.getTransferWithChecks(e);

    //assert
    assert transferWithChecksAfter;
}



