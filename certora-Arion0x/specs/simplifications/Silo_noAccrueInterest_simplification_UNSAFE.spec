methods {
    function _._accrueInterest()
        internal
         => accrueInterest_noStateChange() expect uint256;

    function _.accrueInterestForAsset(address _interestRateModel, uint256 _daoFee, uint256 _deployerFee)
        internal
         => callAccrueInterestForAsset_noStateChange(_interestRateModel, _daoFee, _deployerFee) expect uint256;
}

function accrueInterest_noStateChange() returns uint256 {
    uint256 anyInterest;

    return anyInterest;
}

function callAccrueInterestForAsset_noStateChange(address _interestRateModel, uint256 _daoFee, uint256 _deployerFee)
    returns uint256
{
    uint256 anyInterest;
    return anyInterest;
}
