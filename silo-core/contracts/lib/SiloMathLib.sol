// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.19;

import {MathUpgradeable} from "openzeppelin-contracts-upgradeable/utils/math/MathUpgradeable.sol";

library SiloMathLib {
    using MathUpgradeable for uint256;

    uint256 internal constant _PRECISION_DECIMALS = 1e18;
    uint256 internal constant _BASIS_POINTS = 1e4;

    /// @dev this is constant version of openzeppelin-contracts/contracts/token/ERC20/extensions/ERC4626._decimalsOffset
    uint256 internal constant _DECIMALS_OFFSET_POW = 10 ** 2; // TODO when 128 change to 0?

    /// @notice Returns available liquidity to be borrowed
    /// @dev Accrued interest is entirely added to `debtAssets` but only part of it is added to `collateralAssets`. The
    ///      difference is DAO's and deployer's cut. That means DAO's and deployer's cut is not considered a borrowable
    ///      liquidity.
    function liquidity(uint256 _collateralAssets, uint256 _debtAssets) internal pure returns (uint256 liquidAssets) {
        unchecked {
            // we checked the underflow
            liquidAssets = _debtAssets > _collateralAssets ? 0 : _collateralAssets - _debtAssets;
        }
    }

    function getCollateralAmountsWithInterest(
        uint256 _collateralAssets,
        uint256 _debtAssets,
        uint256 _rcompInDp,
        uint256 _daoFeeInBp,
        uint256 _deployerFeeInBp
    )
        internal
        pure
        returns (
            uint256 collateralAssetsWithInterest,
            uint256 debtAssetsWithInterest,
            uint256 daoAndDeployerFees,
            uint256 accruedInterest
        )
    {
        (debtAssetsWithInterest, accruedInterest) = getDebtAmountsWithInterest(_debtAssets, _rcompInDp);
        uint256 collateralInterest;

        unchecked {
            // If we overflow on multiplication it should not revert tx, we will get lower fees
            daoAndDeployerFees = accruedInterest * (_daoFeeInBp + _deployerFeeInBp) / _BASIS_POINTS;
            // we will not underflow because daoAndDeployerFees is chunk of accruedInterest
            collateralInterest = accruedInterest - daoAndDeployerFees;
        }

        collateralAssetsWithInterest = _collateralAssets + collateralInterest;
    }

    function getDebtAmountsWithInterest(uint256 _debtAssets, uint256 _rcompInDp)
        internal
        pure
        returns (uint256 debtAssetsWithInterest, uint256 accruedInterest)
    {
        if (_debtAssets == 0 || _rcompInDp == 0) {
            return (_debtAssets, 0);
        }

        unchecked {
        // If we overflow on multiplication it should not revert tx, we will get lower fees
            accruedInterest = _debtAssets * _rcompInDp / _PRECISION_DECIMALS;
        }

        debtAssetsWithInterest = _debtAssets + accruedInterest;
    }

    /// @notice Calculates fraction between borrowed and deposited amount of tokens denominated in percentage
    /// @dev It assumes `_dp` = 100%.
    /// @param _dp decimal points used by model
    /// @param _collateralAssets current total deposits for assets
    /// @param _debtAssets current total borrows for assets
    /// @return utilization value, capped to 100%
    /// Limiting utilisation ratio by 100% max will allows us to perform better interest rate computations
    /// and should not affect any other part of protocol.
    function calculateUtilization(uint256 _dp, uint256 _collateralAssets, uint256 _debtAssets)
        internal
        pure
        returns (uint256 utilization)
    {
        if (_collateralAssets == 0 || _debtAssets == 0) return 0;

        utilization = _debtAssets * _dp;
        // _collateralAssets is not 0 based on above check, so it is safe to uncheck this division
        unchecked {
            utilization /= _collateralAssets;
        }

        // cap at 100%
        if (utilization > _dp) utilization = _dp;
    }

    function convertToAssetsAndToShares(
        uint256 _assets,
        uint256 _shares,
        uint256 _totalAssets,
        uint256 _totalShares,
        MathUpgradeable.Rounding _roundingToAssets,
        MathUpgradeable.Rounding _roundingToShares
    ) internal pure returns (uint256 assets, uint256 shares) {
        if (_assets == 0) {
            shares = _shares;
            assets = convertToAssets(_shares, _totalAssets, _totalShares, _roundingToAssets);
        } else {
            shares = convertToShares(_assets, _totalAssets, _totalShares, _roundingToShares);
            assets = _assets;
        }
    }

    /// @dev this is exact copy of openzeppelin-contracts/contracts/token/ERC20/extensions/ERC4626._convertToShares
    function convertToShares(
        uint256 _assets,
        uint256 _totalAssets,
        uint256 _totalShares,
        MathUpgradeable.Rounding _rounding
    ) internal pure returns (uint256) {
        return _assets.mulDiv(_totalShares + _DECIMALS_OFFSET_POW, _totalAssets + 1, _rounding);
    }

    /// @dev this is exact copy of openzeppelin-contracts/contracts/token/ERC20/extensions/ERC4626._convertToAssets
    function convertToAssets(
        uint256 _shares,
        uint256 _totalAssets,
        uint256 _totalShares,
        MathUpgradeable.Rounding _rounding
    ) internal pure returns (uint256 assets) {
        assets = _shares.mulDiv(_totalAssets + 1, _totalShares + _DECIMALS_OFFSET_POW, _rounding);
    }
}