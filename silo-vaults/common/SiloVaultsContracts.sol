// SPDX-License-Identifier: BUSL-1.1
pragma solidity >=0.7.6 <0.9.0;

import {Deployments} from "silo-foundry-utils/lib/Deployments.sol";

library SiloVaultsContracts {
    string public constant META_MORPHO_FACTORY = "MetaMorphoFactory.sol";
    string public constant PUBLIC_ALLOCATOR = "PublicAllocator.sol";
}

library SiloVaultsDeployments {
    string public constant DEPLOYMENTS_DIR = "silo-vaults";

    function get(string memory _contract, string memory _network) internal returns(address) {
        return Deployments.getAddress(DEPLOYMENTS_DIR, _network, _contract);
    }
}