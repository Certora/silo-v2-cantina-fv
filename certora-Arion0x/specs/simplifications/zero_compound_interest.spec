methods{
    // ---- `IInterestRateModel` -----------------------------------------------
    function _.getCompoundInterestRate(
        address _silo,
        uint256 _blockTimestamp
    ) external => ALWAYS(0);
    
    function _.getCompoundInterestRateAndUpdate(
        uint256 _collateralAssets,
        uint256 _debtAssets,
        uint256 _interestRateTimestamp
    ) external => ALWAYS(0);
}