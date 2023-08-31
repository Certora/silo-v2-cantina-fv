// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.7.6;
pragma abicoder v2;

import {IUniswapV3Pool} from  "uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";

import {IUniswapV3Oracle} from "../interfaces/IUniswapV3Oracle.sol";

/// @notice to keep config contract size low (this is the one that will be deployed each time)
/// factory contract take over verification. You should not deploy or use config that was not created by factory.
contract UniswapV3OracleConfig {
    /// @dev UniV3 pool address that is used for TWAP price
    IUniswapV3Pool internal immutable _POOL; // solhint-disable-line var-name-mixedcase

    /// @dev Asset in which oracle denominates its price
    address internal immutable _QUOTE_TOKEN; // solhint-disable-line var-name-mixedcase

    /// @dev TWAP period in seconds
    uint32 internal immutable _PERIOD_FOR_AVG_PRICE; // solhint-disable-line var-name-mixedcase

    /// @dev how many observations we need for provided periodForAvgPrice and blockTime
    uint16 internal immutable _REQUIRED_CARDINALITY; // solhint-disable-line var-name-mixedcase

    /// @dev It is assumed that this contract will be deployed once per blockchain so blockTime can safely use
    /// immutable variable even thought it is used as implementation contract for a proxy.
    /// It is number with 1 decimal eg blockTime=5 => 0.5 sec
    /// It is better to set it bit lower than higher that avg block time
    /// eg. if ETH block time is 13~13.5s, you can set it to 12s
    uint8 internal immutable _BLOCK_TIME; // solhint-disable-line var-name-mixedcase

    constructor(
        IUniswapV3Oracle.UniswapV3OracleInitConfig memory _config,
        uint16 _requiredCardinality
    ) {
        _REQUIRED_CARDINALITY = _requiredCardinality;
        _POOL = _config.pool;
        _QUOTE_TOKEN = _config.quoteToken;
        _PERIOD_FOR_AVG_PRICE = _config.periodForAvgPrice;
        _BLOCK_TIME = _config.blockTime;
    }

    function getOracleSetup() external view virtual returns (IUniswapV3Oracle.UniswapV3OracleSetup memory setup) {
        setup.pool = _POOL;
        setup.quoteToken = _QUOTE_TOKEN;
        setup.periodForAvgPrice = _PERIOD_FOR_AVG_PRICE;
        setup.requiredCardinality = _REQUIRED_CARDINALITY;
    }
}