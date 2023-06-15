// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.19;

import "./external/interfaces/ISiloOracle.sol";
import "./interfaces/IAmmPriceModel.sol";


/// @dev annotations like (A) or (Ci) is reference to the internal document that describes model in mathematical way.
contract AmmPriceModel is IAmmPriceModel {
    /// @dev floating point 1.0
    /// @notice this has noting to do with tokens decimals, this is just precision
    uint256 constant public ONE = 1e18;

    uint256 constant public DECIMALS = 1e18;

    /// @dev positive number, scope: [0, 1.0], where 1.0 is treated as 1e18
    uint256 public immutable K_MIN; // solhint-disable-line var-name-mixedcase

    /// @dev positive number, scope: [0, 1.0], where 1.0 is treated as 1e18
    uint256 public immutable K_MAX; // solhint-disable-line var-name-mixedcase

    /// @dev positive number, scope: [0, 1.0], where 1.0 is treated as 1e18
    uint256 public immutable DELTA_K; // solhint-disable-line var-name-mixedcase

    /// @dev If a swap has occurred, we may assume that the current price is fair and slow down decreasing
    /// the value `k` for time Tslow, and then come back to the basic rate of decrease, if nothing happens
    /// time in seconds
    uint256 public immutable T_SLOW; // solhint-disable-line var-name-mixedcase

    /// @dev coefficient K decreases with a rate Vfast, which it is a constant.
    uint256 public immutable V_FAST; // solhint-disable-line var-name-mixedcase

    /// @dev the deceleration factor for the rate of decrease of variable k in the case of a swap, [0, 1.0]
    uint256 public immutable Q; // solhint-disable-line var-name-mixedcase

    /// @dev collateral token address => state
    mapping (address => AmmPriceState) internal _priceState;

    constructor(AmmPriceConfig memory _config) {
        ammConfigVerification(_config);

        K_MIN = _config.kMin;
        K_MAX = _config.kMax;
        DELTA_K = _config.deltaK;
        T_SLOW = _config.tSlow;
        V_FAST = _config.vFast;
        Q = _config.q;
    }

    function getAmmConfig() external view returns (AmmPriceConfig memory ammConfig) {
        ammConfig.kMin = uint64(K_MIN);
        ammConfig.kMax = uint64(K_MAX);
        ammConfig.deltaK = uint64(DELTA_K);
        ammConfig.tSlow = uint32(T_SLOW);
        ammConfig.vFast = uint64(V_FAST);
        ammConfig.q = uint64(Q);
    }

    function getPriceState(address _collateral) external view returns (AmmPriceState memory) {
        return _priceState[_collateral];
    }

    /// @param _collateralAmount how much collateral you want to buy, amount with 18 decimals
    /// @param _collateralTwapPrice collateral price in ??? there are few cases...
    function collateralPrice(address _collateral, uint256 _collateralAmount, uint256 _collateralTwapPrice)
        public
        view
        returns (uint256 debtAmount)
    {
        uint256 value = _priceState[_collateral].k * _collateralTwapPrice * _collateralAmount;

        unchecked {
            // div is safe
            // div(DECIMALS) because twap price is in decimals
            // div(ONE) because of k
            return value / DECIMALS / uint256(ONE);
        }
    }

    function ammConfigVerification(AmmPriceConfig memory _config) public pure {
        // week is arbitrary value, we assume 1 week for waiting for price to go to minimum is abstract enough
        uint256 week = 7 days;

        if (!(_config.tSlow <= week)) revert INVALID_T_SLOW();
        if (!(_config.kMax != 0 && _config.kMax <= ONE)) revert INVALID_K_MAX();
        if (!(_config.kMin <= _config.kMax)) revert INVALID_K_MIN();
        if (!(_config.q <= ONE)) revert INVALID_Q();
        if (!(_config.vFast <= ONE)) revert INVALID_V_FAST();
        if (!(_config.deltaK <= _config.tSlow)) revert INVALID_DELTA_K();
    }

    /// @dev The initial action is adding liquidity. This method should be call on first `addLiquidity`
    function _priceInit(address _collateral) internal {
        if (_priceState[_collateral].init) {
            return;
        }

        _priceState[_collateral].k = uint64(K_MAX);
        _priceState[_collateral].lastActionTimestamp = uint64(block.timestamp);
        _priceState[_collateral].liquidityAdded = true;
        _priceState[_collateral].swap = false;
        _priceState[_collateral].init = true;
    }

    /// @dev Add liquidity should not change the price. But the following situation may occur.
    /// The collateral amount in the pool is very small, so the swap is not profitable even at a very low AMM price.
    /// At the same time, the AMM price continues to decrease due to a decrease in variable, and becomes inadequate.
    /// If liquidity is added at this moment, then part of the collateral will be swaped at a low price.
    /// To prevent this, we reset the values of `k` and `t`, if the previous action was either swap or withdraw, i.e.,
    /// if the previous action reduced the volume of the AMM.
    function _priceChangeOnAddingLiquidity(address _collateral) internal {
        if (_priceState[_collateral].liquidityAdded) {
            return;
        }

        _priceState[_collateral].k = uint64(K_MAX);
        _priceState[_collateral].liquidityAdded = true;
        _priceState[_collateral].swap = false;
        _priceState[_collateral].lastActionTimestamp = uint64(block.timestamp);
    }

    function _onSwapPriceChange(address _collateral) internal {
        uint256 k;

        unchecked {
            // unchecked: timestamp is at least lastActionTimestamp so we do not underflow
            uint256 time = block.timestamp - _priceState[_collateral].lastActionTimestamp;

            if (_priceState[_collateral].swap) {
                if (time > T_SLOW) {
                    // unchecked: all this values are max 64bits, so we can not produce value that is more than 128b
                    // and it is OK to got negative number on `(time - DELTA_K)`
                    time = (time - DELTA_K) * V_FAST;
                } else {
                    // unchecked: all this values are max 64bits (<1e18), so we can not produce value that will
                    // over or under flow
                    // unchecked: we need to div(ONE) because of Q, division is safe
                    time = time * Q * V_FAST / ONE;
                }
            } else {
                // unchecked: all this values are max 64bits (<1e18), so we can not produce value that will
                // over or under flow
                time = time * V_FAST;
            }

            // unchecked: all this values are max 64bits (<1e18), so we can not produce value that will
            // over or under flow
            k = _priceState[_collateral].k - time;
        }

        _priceState[_collateral].k = uint64(k > K_MIN ? k : K_MIN);
        _priceState[_collateral].swap = true;
        _priceState[_collateral].liquidityAdded = false;
        _priceState[_collateral].lastActionTimestamp = uint64(block.timestamp);
    }

    /// @dev If a withdraw has occurred, the AMM price is not needed, therefore, the only change to be made is updating
    /// parameter AL. This means that on the next step we will know that the previous action reduced the volume of the
    /// AMM.
    function _priceChangeOnWithdraw(address _collateral) internal {
        _priceState[_collateral].liquidityAdded = false;
    }
}