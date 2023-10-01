// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "silo-core/contracts/lib/SiloMathLib.sol";

// forge test -vv --mc CalculateUtilizationTest
contract CalculateUtilizationTest is Test {
    /*
    forge test -vv --mt test_calculateUtilization
    */
    function test_calculateUtilization(uint256 _collateralAssets, uint256 _debtAssets) public {
        uint256 dp = 1e18;

        assertEq(SiloMathLib.calculateUtilization(dp, 1e18, 0.9e18), 0.9e18);
        assertEq(SiloMathLib.calculateUtilization(dp, 1e18, 0.1e18), 0.1e18);
        assertEq(SiloMathLib.calculateUtilization(dp, 10e18, 1e18), 0.1e18);
        assertEq(SiloMathLib.calculateUtilization(dp, 100e18, 25e18), 0.25e18);
        assertEq(SiloMathLib.calculateUtilization(dp, 100e18, 49e18), 0.49e18);
        assertEq(SiloMathLib.calculateUtilization(1e4, 100e18, 49e18), 0.49e4);

        assertEq(SiloMathLib.calculateUtilization(1e18, 0, _debtAssets), 0);
        assertEq(SiloMathLib.calculateUtilization(1e18, _collateralAssets, 0), 0);
        assertEq(SiloMathLib.calculateUtilization(0, _collateralAssets, _debtAssets), 0);
    }

    /*
    forge test -vv --mt test_calculateUtilizationWithMax
    */
    function test_calculateUtilizationWithMax(uint256 _dp, uint256 _collateralAssets, uint256 _debtAssets) public {
        vm.assume(_debtAssets < type(uint128).max);
        vm.assume(_dp < type(uint128).max);

        assertTrue(SiloMathLib.calculateUtilization(_dp, _collateralAssets, _debtAssets) <= _dp);
    }
}