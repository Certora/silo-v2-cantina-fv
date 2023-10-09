// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.18;

import {CommonDeploy} from "../CommonDeploy.sol";
import {SiloOraclesFactoriesContracts} from "../SiloOraclesFactoriesContracts.sol";
import {DIAOraclesConfigsParser as ConfigParser} from "./DIAOraclesConfigsParser.sol";
import {IDIAOracle} from "silo-oracles/contracts/interfaces/IDIAOracle.sol";
import {DIAOracleFactory} from "silo-oracles/contracts/dia/DIAOracleFactory.sol";
import {DIAOracle} from "silo-oracles/contracts/dia/DIAOracle.sol";
import {OraclesDeployments} from "../OraclesDeployments.sol";

/**
FOUNDRY_PROFILE=oracles CONFIG=DIA_Demo_config \
    forge script silo-oracles/deploy/dia-oracle/DIAOracleDeploy.s.sol \
    --ffi --broadcast --rpc-url http://127.0.0.1:8545
 */
contract DIAOracleDeploy is CommonDeploy {
    function run() public returns (DIAOracle oracle) {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);

        string memory configName = vm.envString("CONFIG");

        IDIAOracle.DIADeploymentConfig memory config = ConfigParser.getConfig(
            getChainAlias(),
            configName
        );

        address factory = getDeployedAddress(SiloOraclesFactoriesContracts.DIA_ORACLE_FACTORY);

        oracle = DIAOracleFactory(factory).create(config);

        OraclesDeployments.save(getChainAlias(), configName, address(oracle));

        vm.stopBroadcast();
    }
}