// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import "forge-std/Test.sol";

import "../../../contracts/interestRateModel/InterestRateModelV2.sol";
import "../_common/InterestRateModelConfigs.sol";
import "../../../contracts/interestRateModel/InterestRateModelV2ConfigFactory.sol";


// forge test -vv --mt InterestRateModelV2Test
contract InterestRateModelV2Test is Test, InterestRateModelConfigs {
    uint256 constant TODAY = 1682885514;
    InterestRateModelV2 immutable INTEREST_RATE_MODEL;

    uint256 constant DP = 10 ** 18;
    uint256 constant BASIS_POINTS = 10000;

    constructor() {
        INTEREST_RATE_MODEL = new InterestRateModelV2();
    }

    function test_IRM_DP() public {
        assertEq(INTEREST_RATE_MODEL.DP(), DP);
    }

    function test_IRM_RCOMP_MAX() public {
        assertEq(INTEREST_RATE_MODEL.RCOMP_MAX(), 2 ** 16 * DP);
    }

    function test_IRM_X_MAX() public {
        assertEq(INTEREST_RATE_MODEL.X_MAX(), 11090370147631773313);
    }

    function test_IRM_ASSET_DATA_OVERFLOW_LIMIT() public {
        assertEq(INTEREST_RATE_MODEL.ASSET_DATA_OVERFLOW_LIMIT(), 2 ** 196);
    }

    function test_IRM_calculateCompoundInterestRate_InvalidTimestamps() public {
        IInterestRateModel.ConfigWithState memory c;
        vm.expectRevert(IInterestRateModel.InvalidTimestamps.selector);
        INTEREST_RATE_MODEL.calculateCompoundInterestRate(c, 0, 0, 1, 0);
    }

    function test_IRM_calculateCurrentInterestRate_InvalidTimestamps() public {
        IInterestRateModel.ConfigWithState memory c;
        vm.expectRevert(IInterestRateModel.InvalidTimestamps.selector);
        INTEREST_RATE_MODEL.calculateCurrentInterestRate(c, 0, 0, 1, 0);
    }
    
    // forge test -vv --mt test_IRM_calculateCurrentInterestRate_CAP
    function test_IRM_calculateCurrentInterestRate_CAP() public {
        uint256 rcur = INTEREST_RATE_MODEL.calculateCurrentInterestRate(
            _configWithState(),
            100e18, // _totalDeposits,
            99e18, // _totalBorrowAmount,
            TODAY, // _interestRateTimestamp,
            TODAY + 60 days // after 59 days we got capped
        );

        assertEq(rcur, 10**20, "expect to return CAP");
    }

    function test_IRM_calculateCurrentInterestRate_revertsWhenTimestampInvalid() public {
        IInterestRateModel.ConfigWithState memory emptyConfig;

        // currentTime should always be larger than last, so this should revert
        uint256 lastTransactionTime = 1;
        uint256 currentTime = 0;

        vm.expectRevert(IInterestRateModel.InvalidTimestamps.selector);
        INTEREST_RATE_MODEL.calculateCurrentInterestRate(emptyConfig, 0, 0, lastTransactionTime, currentTime);
    }

    // forge test -vv --mt test_IRM_calculateCompoundInterestRateWithOverflowDetection_CAP
    function test_IRM_calculateCompoundInterestRateWithOverflowDetection_CAP(uint256 _t) public {
        vm.assume(_t < 5 * 365 days);

        uint256 cap = 3170979198376 * (1 + _t);

        (uint256 rcur,,,) = INTEREST_RATE_MODEL.calculateCompoundInterestRateWithOverflowDetection(
            _configWithState(),
            100e18, // _totalDeposits,
            99e18, // _totalBorrowAmount,
            TODAY, // _interestRateTimestamp,
            TODAY + 1 + _t // +1 so we always have some time pass
        );

        assertGt(rcur, 0, "expect to get some %");
        assertLe(rcur, cap, "expect to have CAP");
    }

    // forge test -vv --mt test_IRM_calculateCompoundInterestRateWithOverflowDetection_ZERO
    function test_IRM_calculateCompoundInterestRateWithOverflowDetection_ZERO() public {
        (uint256 rcur,,,) = INTEREST_RATE_MODEL.calculateCompoundInterestRateWithOverflowDetection(
            _configWithState(),
            100e18, // _totalDeposits,
            99e18, // _totalBorrowAmount,
            TODAY, // _interestRateTimestamp,
            TODAY
        );

        assertEq(rcur, 0, "expect to get 0 for time 0");
    }
}