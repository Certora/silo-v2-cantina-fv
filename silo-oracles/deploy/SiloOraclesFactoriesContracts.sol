// SPDX-License-Identifier: MIT
pragma solidity >=0.7.6 <0.9.0;

import {Deployments} from "silo-foundry-utils/lib/Deployments.sol";

library SiloOraclesFactoriesContracts {
    string public constant UNISWAP_V3_ORACLE_FACTORY = "UniswapV3OracleFactory.sol";
    string public constant CHAINLINK_V3_ORACLE_FACTORY = "ChainlinkV3OracleFactory.sol";
    string public constant DIA_ORACLE_FACTORY = "DIAOracleFactory.sol";
}

library SiloOraclesFactoriesDeployments {
    string public constant DEPLOYMENTS_DIR = "silo-oracles";

    function get(string memory _contract, string memory _network) internal returns(address) {
        return Deployments.getAddress(DEPLOYMENTS_DIR, _network, _contract);
    }
}