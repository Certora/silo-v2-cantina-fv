// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import {ISiloOracle} from "silo-core/contracts/interfaces/ISiloOracle.sol";

contract DummyOracle is ISiloOracle {
    uint256 internal price;
    address public quoteToken;

    bool _expectBeforeQuote;

    constructor(uint256 _price, address _quoteToken) {
        price = _price;
        quoteToken = _quoteToken;
    }

    function beforeQuote(address _baseToken) external view {
        if (_baseToken == quoteToken) revert("beforeQuote(): wrong base token");
        if (!_expectBeforeQuote) revert("beforeQuote() was not expected, but was called anyway");
    }

    function setExpectBeforeQuote(bool _expect) external {
        _expectBeforeQuote = _expect;
    }

    function quote(uint256 _baseAmount, address _baseToken) external view returns (uint256 quoteAmount) {
        if (_baseToken == quoteToken) revert("wrong base token");

        quoteAmount = _baseAmount * price / 1e18;
    }
}