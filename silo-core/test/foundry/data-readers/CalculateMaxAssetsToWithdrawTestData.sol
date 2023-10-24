// SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

contract CalculateMaxAssetsToWithdrawTestData {
    uint256 constant BP2DP_NORMALIZATION = 10 ** (18 - 4);

    struct Input {
        uint256 sumOfCollateralsValue;
        uint256 debtValue;
        uint256 ltInDp;
        uint256 borrowerCollateralAssets;
        uint256 borrowerProtectedAssets;
    }

    struct CMATWData {
        string name;
        Input input;
        uint256 maxAssets;
    }

    CMATWData[] allData;

    function getData() external returns (CMATWData[] memory data) {
        _add(0, 0, 0, 0, 0, 0, "when all zeros");
        _add(1, 0, 0, 1, 0, 1, "when no debt");
        _add(1, 0, 0, 0, 1, 1, "when no debt");
        _add(100, 1, 0, 0, 0, 0, "when over LT");
        _add(1e4, 1, 1 * BP2DP_NORMALIZATION, 0, 0, 0, "LT is 0.01% and LTV is 0.01%");

        uint256 ourMax = 9900 - 1;
        _add(1e4, 1, 100 * BP2DP_NORMALIZATION, 0.5e4, 0.5e4, ourMax);
        _add(1e4, 1, 100 * BP2DP_NORMALIZATION, 0.8e4, 0.2e4, ourMax);
        _add(1e4, 1, 100 * BP2DP_NORMALIZATION, 1e4, 0, ourMax);
        _add(1e4, 1, 100 * BP2DP_NORMALIZATION, 0, 1e4, ourMax);
        _add(1e4 - ourMax, 1, 100 * BP2DP_NORMALIZATION, 101, 0, 0, "based on above examples, we expect 0 now");

        ourMax = 2e4 - 202;
        _add(1e4, 1, 100 * BP2DP_NORMALIZATION, 1e4, 1e4, ourMax, "LT 1%, debt 1, so collateral must be 100 (e4)");
        _add(1e4 - ourMax / 2, 1, 100 * BP2DP_NORMALIZATION, 202, 0, 0, "based on prev, we expect 0");

        _add(100, 80, 8000 * BP2DP_NORMALIZATION, 0, 0, 0, "exact LT");
        _add(101, 80, 8000 * BP2DP_NORMALIZATION, 100, 1, 0, "expect 0");

        _add(10, 8, 8888 * BP2DP_NORMALIZATION, 10, 10, 0, "8/(10 - 1) = 100% > LT (!), only zero is acceptable");

        ourMax = 999099909990999099;
        _add(10e18, 8e18, 8888 * BP2DP_NORMALIZATION, 5e18, 5e18, ourMax, "LTV after => 88,88% (1)");
        _add(
            10e18 - ourMax, 8e18, 8888 * BP2DP_NORMALIZATION, 10e18 - ourMax, 0, 0,
            "based on above, we should expect 0"
        );

        ourMax = uint256(999099909990999099) / 5;
        _add(10e18, 8e18, 8888 * BP2DP_NORMALIZATION, 1e18, 1e18, ourMax, "LTV after => 88,88% (2)");
        _add(10e18 - ourMax * 5, 8e18, 8888 * BP2DP_NORMALIZATION, 1e18 - ourMax, 0, 0, "^ LTV after => 88,88% (2)");

        //  0.1e18 / (3e18 - 2882352941176470589));
        ourMax = 2882352941176470588;
        _add(3e18, 0.1e18, 8500 * BP2DP_NORMALIZATION, 2e18, 1e18, ourMax, "LTV after => 85%");
        _add(3e18 - ourMax, 0.1e18, 8500 * BP2DP_NORMALIZATION, 0, 3e18 - ourMax, 0, "^ LTV after => 85%");

        return allData;
    }

    function _add(
        uint256 _sumOfCollateralsValue,
        uint256 _debtValue,
        uint256 _ltInDp,
        uint256 _borrowerCollateralAssets,
        uint256 _borrowerProtectedAssets,
        uint256 _maxAssets
    ) private {
        _add(
            _sumOfCollateralsValue,
            _debtValue,
            _ltInDp,
            _borrowerCollateralAssets,
            _borrowerProtectedAssets,
            _maxAssets,
            ""
        );
    }

    function _add(
        uint256 _sumOfCollateralsValue,
        uint256 _debtValue,
        uint256 _ltInDp,
        uint256 _borrowerCollateralAssets,
        uint256 _borrowerProtectedAssets,
        uint256 _maxAssets,
        string memory _name
    ) private {
        uint256 i = allData.length;
        allData.push();
        allData[i].name = _name;
        allData[i].input.sumOfCollateralsValue = _sumOfCollateralsValue;
        allData[i].input.debtValue = _debtValue;
        allData[i].input.ltInDp = _ltInDp;
        allData[i].input.borrowerCollateralAssets = _borrowerCollateralAssets;
        allData[i].input.borrowerProtectedAssets = _borrowerProtectedAssets;
        allData[i].maxAssets = _maxAssets;
    }
}