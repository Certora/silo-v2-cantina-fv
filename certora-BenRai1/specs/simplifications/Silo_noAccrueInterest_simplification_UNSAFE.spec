methods {
    function _._accrueInterest() internal => accrueInterest_noStateChange()  expect uint256;
    // function Silo1._accrueInterest() internal returns (uint256) => accrueInterest_noStateChange();

    function _._accrueInterestForAsset(address _interestRateModel, uint256 _daoFee, uint256 _deployerFee)
        internal
        => accrueInterestForAsset_noStateChange(_interestRateModel, _daoFee, _deployerFee)  expect uint256;
        // returns (uint256) => accrueInterestForAsset_noStateChange(_interestRateModel, _daoFee, _deployerFee);
    function _.getDebtAmountsWithInterest(uint256 debtWithoutInterest, uint256 interestRate) external => getDebtAmountsWithInterest__noStateChange(debtWithoutInterest) expect uint256;

    function _.getCompoundInterestRate(address, uint256) external => getCompoundInterestRate_noStateChange() expect uint256;
    function _.getCompoundInterestRateAndUpdate(uint256, uint256, uint256) external => getCompoundInterestRateAndUpdate_noStateChange() expect uint256;
}

function accrueInterest_noStateChange() returns uint256 {
    return 0;
}

function accrueInterestForAsset_noStateChange(address _interestRateModel, uint256 _daoFee, uint256 _deployerFee)
    returns uint256
{
    return 0;
}

function getCompoundInterestRate_noStateChange() returns uint256  {
    return 0;
}

function getCompoundInterestRateAndUpdate_noStateChange() returns uint256 {
    return 0;
}

function getDebtAmountsWithInterest__noStateChange(uint256 _debtWithoutInterest) returns uint256 {
    return _debtWithoutInterest;
}

