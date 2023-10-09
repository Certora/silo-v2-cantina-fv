// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import {Test} from "forge-std/Test.sol";

import {ERC20} from "openzeppelin-contracts/token/ERC20/ERC20.sol";

import {ISiloConfig} from "silo-core/contracts/interfaces/ISiloConfig.sol";
import {ISilo} from "silo-core/contracts/interfaces/ISilo.sol";
import {IShareToken} from "silo-core/contracts/interfaces/IShareToken.sol";


contract SiloInvariants is Test {
    ISiloConfig immutable siloConfig;

    ISilo immutable silo0;
    ISilo immutable silo1;

    ERC20 immutable token0;
    ERC20 immutable token1;

    constructor(ISiloConfig _siloConfig, ISilo _silo0, ISilo _silo1, ERC20 _token0, ERC20 _token1) {
        siloConfig = _siloConfig;
        silo0 = _silo0;
        silo1 = _silo1;
        token0 = _token0;
        token1 = _token1;
    }

    function siloInvariant_userIsSolvent(address _user) external {
        assertTrue(silo0.isSolvent(_user), "_user solvent silo0");
        assertTrue(silo1.isSolvent(_user), "_user solvent silo1");
    }

    function siloInvariant_balanceOfSiloMustBeEqToAssets() external {
        assertEq(
            token0.balanceOf(address(silo0)), // this is only true if we do not transfer tokens directly
            silo0.getCollateralAssets() + silo0.getProtectedAssets(),
            "balanceOf"
        );
    }

    function siloInvariant_whenNoInterestSharesEqAssets() external {
        (ISiloConfig.ConfigData memory collateral, ISiloConfig.ConfigData memory debt) = siloConfig.getConfigs(address(silo0));

        assertEq(
            silo0.getCollateralAssets(),
            IShareToken(collateral.collateralShareToken).totalSupply(),
            "silo0: collateral shares == assets"
        );

        assertEq(
            silo0.getProtectedAssets(),
            IShareToken(collateral.protectedShareToken).totalSupply(),
            "silo0: protected shares == assets"
        );

        assertEq(
            silo0.getDebtAssets(),
            IShareToken(collateral.debtShareToken).totalSupply(),
            "silo0: debt shares == assets"
        );

        assertEq(
            silo1.getCollateralAssets(),
            IShareToken(debt.collateralShareToken).totalSupply(),
            "silo1: collateral shares == assets"
        );

        assertEq(
            silo1.getProtectedAssets(),
            IShareToken(debt.protectedShareToken).totalSupply(),
            "silo1: protected shares == assets"
        );

        assertEq(
            silo1.getDebtAssets(),
            IShareToken(debt.debtShareToken).totalSupply(),
            "silo1: debt shares == assets"
        );
    }
}