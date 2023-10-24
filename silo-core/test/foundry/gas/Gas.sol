// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import {Strings} from "openzeppelin-contracts/utils/Strings.sol";

import {console2} from "forge-std/console2.sol";

import {ISilo} from "silo-core/contracts/interfaces/ISilo.sol";

import {SiloFixture, SiloConfigOverride} from "../_common/fixtures/SiloFixture.sol";
import {MintableToken} from "../_common/MintableToken.sol";
import {SiloLittleHelper} from "../_common/SiloLittleHelper.sol";

/*
forge test -vv --ffi --mt test_gas_ | sort | grep -i '\[GAS\]'
*/
contract Gas is SiloLittleHelper {
    uint256 constant ASSETS = 1e18;
    address constant BORROWER = address(0x1122);
    address constant DEPOSITOR = address(0x9988);

    function _gasTestsInit() internal {
        token0 = new MintableToken();
        token1 = new MintableToken();

        SiloFixture siloFixture = new SiloFixture();
        SiloConfigOverride memory overrides;
        overrides.token0 = address(token0);
        overrides.token1 = address(token1);
        (, silo0, silo1,,) = siloFixture.deploy_local(overrides);

        __init(token0, token1, silo0, silo1);

        uint256 max = 2 ** 128 - 1;

        _mintTokens(token0, max, BORROWER);
        _mintTokens(token1, max, DEPOSITOR);

        _vm.prank(BORROWER);
        token0.approve(address(silo0), max);
        _vm.prank(BORROWER);
        token1.approve(address(silo1), max);

        _vm.prank(DEPOSITOR);
        token0.approve(address(silo0), max);
        _vm.prank(DEPOSITOR);
        token1.approve(address(silo1), max);
    }

    function _action(
        address _sender,
        address _target,
        bytes memory _data,
        string memory _msg,
        uint256 _expectedGas
    ) internal returns (uint256 gas) {
        _vm.startPrank(_sender, _sender);

        uint256 gasStart = gasleft();
        (bool success,) = _target.call(_data);
        uint256 gasEnd = gasleft();
        gas = gasStart - gasEnd;

        _vm.stopPrank();

        if (!success) {
            revert(string(abi.encodePacked("[GAS] ERROR: revert for ", _msg)));
        }

        if (gas != _expectedGas) {
            uint256 diff = _expectedGas > gas ? _expectedGas - gas : gas - _expectedGas;
            string memory diffSign = gas < _expectedGas ? "less" : "more";

            if (diff < 100) {
                console2.log(string(abi.encodePacked("[GAS] ", _msg, ": %s (got bit ", diffSign, " by %s)")), gas, diff);
            } else {
                revert(string(abi.encodePacked(
                    "[GAS] invalid gas for ",
                    _msg,
                    ": expected ",
                    Strings.toString(_expectedGas),
                    " got ",
                    Strings.toString(gas),
                    " it is ",
                    diffSign,
                    " by ",
                    Strings.toString(diff)
                )));
            }
        } else {
            console2.log("[GAS] %s: %s", _msg, gas);
        }
    }
}