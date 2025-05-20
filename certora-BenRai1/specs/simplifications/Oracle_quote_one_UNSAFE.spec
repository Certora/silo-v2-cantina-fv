methods {
    function _.quote(uint256 _baseAmount, address _baseToken) external
        => price_is_one(_baseAmount, _baseToken, calledContract) expect uint256;
}

persistent ghost mapping(address => mathint) callCountQuote;

function price_is_one(uint256 _baseAmount, address _baseToken, address _calledContract) returns uint256 {
    callCountQuote[_calledContract] = callCountQuote[_calledContract] + 1;
    return _baseAmount;
}
