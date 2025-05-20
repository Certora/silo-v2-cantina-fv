// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ShareDebtToken} from "silo-core/contracts/utils/ShareDebtToken.sol";
import {IShareToken} from "silo-core/contracts/interfaces/IShareToken.sol";
import {ShareTokenLib} from "silo-core/contracts/lib/ShareTokenLib.sol";
contract ShareDebtToken1 is ShareDebtToken {

    uint256[37439836327923360225337895871394760624280537466773280374265222508165906222592] private __gap;
    ERC20Storage public erc20Storage;
    function getTransferWithChecks() external view returns (bool) {
        IShareToken.ShareTokenStorage storage $ = ShareTokenLib.getShareTokenStorage();
        return $.transferWithChecks;
    }
}
