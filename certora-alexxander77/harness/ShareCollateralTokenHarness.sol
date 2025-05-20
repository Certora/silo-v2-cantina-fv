pragma solidity ^0.8.24;

import {ShareCollateralToken} from "silo-core/contracts/utils/ShareCollateralToken.sol";
import {IShareToken} from "silo-core/contracts/interfaces/IShareToken.sol";
import {ShareTokenLib} from "silo-core/contracts/lib/ShareTokenLib.sol";
import {ShareCollateralTokenLib} from "silo-core/contracts/lib/ShareCollateralTokenLib.sol";
import {ISiloConfig} from "silo-core/contracts/interfaces/ISiloConfig.sol";


contract ShareCollateralTokenHarness is ShareCollateralToken {

    uint256[37439836327923360225337895871394760624280537466773280374265222508165906222592] private __gap;

    uint256 public constant MAX_UINT256 = type(uint256).max;
    ERC20Storage public erc20Storage;
    function getStorage() external view returns (IShareToken.ShareTokenStorage memory) {
        return ShareTokenLib.getShareTokenStorage();
    }

    function afterTokenTransfer(address _sender, address _recipient, uint256 _amount) external {
        _afterTokenTransfer(_sender, _recipient, _amount);
    }

    function getSiloAddress() external view returns (address) {
        return address(_getSilo());
    }

    function getSolvency(address _owner) external returns (bool)  {
        return ShareCollateralTokenLib.isSolventAfterCollateralTransfer(_owner);
    }

}