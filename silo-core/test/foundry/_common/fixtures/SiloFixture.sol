// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import {console2} from "forge-std/console2.sol";

import {StdCheats} from "forge-std/StdCheats.sol";
import {AddrLib} from "silo-foundry-utils/lib/AddrLib.sol";

import {VeSiloContracts} from "ve-silo/common/VeSiloContracts.sol";

import {MainnetDeploy} from "silo-core/deploy/MainnetDeploy.s.sol";
import {SiloDeploy_ETH_USDC_1} from "silo-core/deploy/silo/SiloDeploy_ETH_USDC_1.s.sol";

import {ISiloConfig} from "silo-core/contracts/interfaces/ISiloConfig.sol";
import {ISilo} from "silo-core/contracts/interfaces/ISilo.sol";

import {TokenMock} from "../../_mocks/TokenMock.sol";

contract SiloDeploy_ETH_USDC_1_Local is SiloDeploy_ETH_USDC_1 {
    address token0;
    address token1;

    constructor(address _token0, address _token1) {
        token0 = _token0;
        token1 = _token1;

        // we se here just placeholder, it will be override in `beforeCreateSilo`
        setAddress(31337, "LOCAL", address(0));
    }

    function beforeCreateSilo(ISiloConfig.InitData memory _config) internal view override {
        _config.token0 = token0;
        _config.token1 = token1;
    }
}

contract SiloFixture is StdCheats {
    struct Override {
        address token0;
        address token1;
    }

    uint256 internal constant _FORKING_BLOCK_NUMBER = 17336000;

    function deploy_ETH_USDC()
        external
        returns (ISiloConfig siloConfig, ISilo silo0, ISilo silo1, address weth, address usdc)
    {
        return _deploy(new SiloDeploy_ETH_USDC_1());
    }

    function deploy_local(Override memory _override)
        external
        returns (ISiloConfig siloConfig, ISilo silo0, ISilo silo1, address weth, address usdc)
    {
        // Mock addresses that we need for the `SiloFactoryDeploy` script
        AddrLib.setAddress(VeSiloContracts.TIMELOCK_CONTROLLER, makeAddr("Timelock"));
        AddrLib.setAddress(VeSiloContracts.FEE_DISTRIBUTOR, makeAddr("FeeDistributor"));
        console2.log("[SiloFixture] _deploy: setAddress done.");

        return _deploy(new SiloDeploy_ETH_USDC_1_Local(_override.token0, _override.token1));
    }

    function _deploy(SiloDeploy_ETH_USDC_1 _siloDeploy1)
        internal
        returns (ISiloConfig siloConfig, ISilo silo0, ISilo silo1, address token0, address token1)
    {
        MainnetDeploy mainnetDeploy = new MainnetDeploy();
        mainnetDeploy.disableDeploymentsSync();
        mainnetDeploy.run();
        console2.log("[SiloFixture] _deploy: mainnetDeploy.run() done.");

        siloConfig = _siloDeploy1.run();
        console2.log("[SiloFixture] _deploy: _siloDeploy1.run() done.");

        (address silo,) = siloConfig.getSilos();
        (ISiloConfig.ConfigData memory siloConfig0, ISiloConfig.ConfigData memory siloConfig1) = siloConfig.getConfigs(silo);
        silo0 = ISilo(siloConfig0.silo);
        silo1 = ISilo(siloConfig1.silo);

        token0 = siloConfig0.token;
        token1 = siloConfig1.token;
    }
}