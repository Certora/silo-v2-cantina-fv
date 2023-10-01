// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "silo-core/contracts/lib/SiloMathLib.sol";

// forge test -vv --mc CalculateMaxBorrowValueTest
contract CalculateMaxBorrowValueTest is Test {
    /*
    forge test -vv --mt test_calculateMaxBorrow
    */
    function test_calculateMaxBorrowValue() public {
        uint256 configMaxLtv;
        uint256 sumOfBorrowerCollateralValue;
        uint256 borrowerDebtValue;

        assertEq(
            SiloMathLib.calculateMaxBorrowValue(configMaxLtv, sumOfBorrowerCollateralValue, borrowerDebtValue),
            0, "when all zeros"
        );

        configMaxLtv = 0.5e4;
        sumOfBorrowerCollateralValue = 1e18;
        borrowerDebtValue = 0.5e18;

        assertEq(
            SiloMathLib.calculateMaxBorrowValue(configMaxLtv, sumOfBorrowerCollateralValue, borrowerDebtValue),
            0, "when ltv == limit -> zeros"
        );


        configMaxLtv = 0.5e4;
        sumOfBorrowerCollateralValue = 1e18;
        borrowerDebtValue = 1.5e18;

        assertEq(
            SiloMathLib.calculateMaxBorrowValue(configMaxLtv, sumOfBorrowerCollateralValue, borrowerDebtValue),
            0, "when ltv over limit -> zeros"
        );

        configMaxLtv = 0.5e4;
        sumOfBorrowerCollateralValue = 1e18;
        borrowerDebtValue = 0;

        assertEq(
            SiloMathLib.calculateMaxBorrowValue(configMaxLtv, sumOfBorrowerCollateralValue, borrowerDebtValue),
            0.5e18, "when no debt"
        );

        configMaxLtv = 0.5e4;
        sumOfBorrowerCollateralValue = 1e18;
        borrowerDebtValue = 0.1e18;

        assertEq(
            SiloMathLib.calculateMaxBorrowValue(configMaxLtv, sumOfBorrowerCollateralValue, borrowerDebtValue),
            0.4e18, "when below lTV limit"
        );
    }
}