// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import {IERC20Metadata} from "openzeppelin-contracts/token/ERC20/extensions/IERC20Metadata.sol";

/// @notice please read carefully unchecked comments, there are some requirements tht must be met in order to not
/// over/under flow
library OracleNormalization {
    error Overflow();

    /// @param _priceDecimals decimals of "base price" eg. 8. In case final price is calculated from two prices:
    /// eg. base price and eth price, `_priceDecimals` is always decimals of first/base price.
    /// @param _ethPriceDecimals decimals of ETH price eg. 18. If set to 0, that means there is no second/ETH price
    /// @return divider
    /// @return multiplier max value for first price 10^36 and for ETH price 10^(36+36)
    /// but this is assuming unreal decimals. TODO certora?
    function normalizationNumbers( // solhint-disable-line code-complexity, function-max-lines
        IERC20Metadata _baseToken,
        IERC20Metadata _quoteToken,
        uint256 _priceDecimals,
        uint256 _ethPriceDecimals
    )
        internal
        view
        returns (uint256 divider, uint256 multiplier)
    {
        uint256 quoteDecimals = _quoteToken.decimals();

        // this is arbitrary check, 36 is high enough
        // anything above 36 might cause precision errors in price and it will make no sense to have it
        // we can always create separate version of lib if we need
        uint256 arbitraryMaxDecimals = 36;

        if (quoteDecimals > arbitraryMaxDecimals) revert Overflow();

        uint256 baseDecimals = _baseToken.decimals();
        bool useMultiplier = false;

        // below check prevents underflow on subtraction
        if (quoteDecimals > baseDecimals + _priceDecimals) {
            // safe because of above `quoteDecimals > baseDecimals + _priceDecimals`
            unchecked { multiplier = quoteDecimals - (baseDecimals + _priceDecimals); }
            useMultiplier = true;
        } else {
            // make no sense to support that weird base tokens
            if (baseDecimals > arbitraryMaxDecimals) revert Overflow();

            // safe because of above `quoteDecimals > baseDecimals + _priceDecimals`
            unchecked { divider = baseDecimals + _priceDecimals - quoteDecimals; }
        }

        if (_ethPriceDecimals == 0) {
            return (useMultiplier ? 0 : 10 ** divider, useMultiplier ? 10 ** multiplier : 0);
        }

        if (_ethPriceDecimals > arbitraryMaxDecimals) revert Overflow();

        if (useMultiplier) {
            // safe because we working on small decimals numbers < arbitraryMaxDecimals
            unchecked { multiplier += _ethPriceDecimals; }
        } else {
            if (_ethPriceDecimals > divider) {
                // safe to unchecked because of `_ethPriceDecimals > divider`
                unchecked { multiplier = _ethPriceDecimals - divider; }
                divider = 0;
                useMultiplier = true;
            } else {
                // safe to unchecked because of `_ethPriceDecimals > divider`
                unchecked { divider = divider - _ethPriceDecimals; }
            }
        }

        return (useMultiplier ? 0 : 10 ** divider, useMultiplier ? 10 ** multiplier : 0);
    }

    /// @notice if you call normalizePrice directly you can create overflow
    /// @param _baseAmount amount of base token (can not be higher than uint128!)
    /// @param _assetPrice price returned by oracle (can not be higher than uint128!)
    /// @param _normalizationDivider constant that allows to translate output price to expected decimals
    /// @param _normalizationMultiplier constant that allows to translate output price to expected decimals
    /// @return assetPrice uint256 18 decimals price
    function normalizePrice(
        uint256 _baseAmount,
        uint256 _assetPrice,
        uint256 _normalizationDivider,
        uint256 _normalizationMultiplier
    )
        internal
        pure
        returns (uint256 assetPrice)
    {
        if (_normalizationMultiplier == 0) {
            // `_baseAmount * _assetPrice` is safe because we multiply uint128 * uint128
            // - _baseAmount is checked in `_quote`
            // - _assetPrice is uint128
            // div is safe
            unchecked { return _baseAmount * _assetPrice / _normalizationDivider; }
        }

        uint256 mul;
        // this is save, check explanation above
        unchecked { mul = _baseAmount * _assetPrice; }

        return mul * _normalizationMultiplier;
    }

    /// @notice if you call normalizePrice directly you can create overflow
    /// @param _baseAmount amount of base token (can not be higher than uint128!)
    /// @param _assetPrice price returned by oracle (can not be higher than uint128!)
    /// @param _ethPriceInUsd price of ETH is USD returned by oracle (can not be higher than uint128!)
    /// @param _normalizationDivider constant that allows to translate output price to expected decimals
    /// @param _normalizationMultiplier constant that allows to translate output price to expected decimals
    /// @return assetPrice uint256 18 decimals price
    function normalizePriceEth(
        uint256 _baseAmount,
        uint256 _assetPrice,
        uint256 _ethPriceInUsd,
        uint256 _normalizationDivider,
        uint256 _normalizationMultiplier
    )
        internal
        pure
        returns (uint256 assetPrice)
    {
        if (_normalizationMultiplier == 0) {
            // `_baseAmount * _assetPrice` is safe because we multiply uint128 * uint128
            // - _baseAmount is checked in `_quote`, that checks covers `*1e8`, so we sure it is up to uint128
            // - _assetPrice is uint128
            // however if you call normalizePrice directly (because it is public) you can create overflow
            // div is safe
            unchecked {
                return _baseAmount * _assetPrice / _normalizationDivider / _ethPriceInUsd;
            }
        }

        uint256 mul;
        // this is save, check explanation above
        unchecked { mul = _baseAmount * _assetPrice; }

        mul = mul * _normalizationMultiplier;

        // div is safe
        unchecked { return mul / _ethPriceInUsd; }
    }
}