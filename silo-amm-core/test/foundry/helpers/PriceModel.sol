// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;
import "../../../contracts/models/AmmPriceModel.sol";

contract PriceModel is AmmPriceModel {
    address immutable _COLLATERAL;

    constructor (address _collateral, AmmPriceModel.AmmPriceConfig memory _config) AmmPriceModel(_config) {
        _COLLATERAL = _collateral;
    }

    function init() external {
        _priceInit(_COLLATERAL);
    }

    function onAddingLiquidity(uint256 _collateralLiquidityBefore, uint256 _collateralLiquidityAfter) external {
        _onAddingLiquidityPriceChange(_COLLATERAL, _collateralLiquidityBefore, _collateralLiquidityAfter);
    }

    function onSwapCalculateK() external view returns (uint256 k) {
        return _onSwapCalculateK(_COLLATERAL, block.timestamp);
    }

    function onSwapPriceChange(uint64 _k) external {
        _onSwapPriceChange(_COLLATERAL, _k);
    }

    function onWithdraw() external {
        _onWithdrawPriceChange(_COLLATERAL);
    }
}