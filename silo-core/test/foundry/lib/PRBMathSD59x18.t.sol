// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import "../_common/Assertions.sol";

import "openzeppelin-contracts/utils/Strings.sol";

import "silo-core/contracts/lib/PRBMathSD59x18.sol";

import "../data/PRBMathSD59x18_exp2_data.sol";
import "../data/PRBMathSD59x18_exp_data.sol";

contract PRBMathSD59x18Test is Assertions, PRBMathSD59x18_exp2_data, PRBMathSD59x18_exp_data {
    using Strings for uint256;

    function setUp() public {}

    function test_PRBMathCommon_exp() public {
        (int256[] memory inputs, int256[] memory expected) = expData();

        unchecked {
            for (uint256 i; i < inputs.length; i++) {
                assertRelativeCloseTo(
                    PRBMathSD59x18.exp(inputs[i]),
                    expected[i],
                    22, // 22e-18%
                    string(abi.encodePacked("#exp FAILED@", i.toString()))
                );
            }
        }
    }

    function test_PRBMathCommon_exp2_withIntegers() public {
        (int256[] memory inputs, int256[] memory expected) = exp2IntegersData();

        unchecked {
            for (uint256 i; i < inputs.length; i++) {
                assertEq(
                    PRBMathSD59x18.exp2(inputs[i]),
                    expected[i],
                    string(abi.encodePacked("#exp2 FAILED@", i.toString()))
                );
            }
        }
    }

    function test_PRBMathCommon_exp2_withFloating() public {
        (int256[] memory inputs, int256[] memory expected) = exp2FloatingData();

        unchecked {
            for (uint256 i; i < inputs.length; i++) {
                assertCloseTo(
                    PRBMathSD59x18.exp2(inputs[i]),
                    expected[i],
                    1000,
                    string(abi.encodePacked("#exp2 with 'floating' numbers FAILED@", i.toString()))
                );
            }
        }
    }
}