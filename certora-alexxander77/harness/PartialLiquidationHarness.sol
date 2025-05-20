// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IERC20} from "openzeppelin5/interfaces/IERC20.sol";
import {Math} from "openzeppelin5/utils/math/Math.sol";
import {Rounding} from "silo-core/contracts/lib/Rounding.sol";
import "../../silo-core/contracts/utils/hook-receivers/liquidation/PartialLiquidation.sol";
import {ISilo} from "silo-core/contracts/interfaces/ISilo.sol";
import {ISiloConfig} from "silo-core/contracts/interfaces/ISiloConfig.sol";
import {Actions} from "silo-core/contracts/lib/Actions.sol";
import {ShareTokenLib} from "silo-core/contracts/lib/ShareTokenLib.sol";
import {IERC3156FlashBorrower} from "silo-core/contracts/interfaces/IERC3156FlashBorrower.sol";
import {SiloStdLib} from "silo-core/contracts/lib/SiloStdLib.sol";
import {Silo} from "silo-core/contracts/Silo.sol";

contract PartialLiquidationHarness is PartialLiquidation {
    constructor() {}

    uint256[37439836327923360225337895871394760624280537466773280374265222508165906222592] private __gap;
    uint256 public constant MAX_UINT256 = type(uint256).max;

    function getStorage() external view returns (IShareToken.ShareTokenStorage memory) {
        return ShareTokenLib.getShareTokenStorage();

    }
    function getERCBalance(address token, address addr) external view returns (uint256) {
        return IERC20(token).balanceOf(addr);
    }

    function getERCAllowance(address token, address owner, address spender) external view returns(uint256) {
        return IERC20(token).allowance(owner, spender);
    }

    function getConfigsForSolvencyHarness(ISiloConfig _siloConfig, address _borrower) external returns (address, address, address, address) {
       (ISiloConfig.ConfigData memory collateralConfig,
        ISiloConfig.ConfigData memory debtConfig) = _siloConfig.getConfigsForSolvency(_borrower);
        return(debtConfig.silo, debtConfig.token, collateralConfig.silo, collateralConfig.token);
    }
    function getConfigCustom(ISiloConfig _siloConfigCached, address _collateralAsset, address _debtAsset, address _borrower) 
        external returns (ISiloConfig.ConfigData memory, ISiloConfig.ConfigData memory) 
    {
        return _fetchConfigs(_siloConfigCached, _collateralAsset, _debtAsset, _borrower);
    }

    function flashLoan(IERC3156FlashBorrower _receiver, address _token, uint256 _amount, bytes calldata _data) 
        external returns (bool) 
    {
        return Actions.flashLoan(_receiver, _token, _amount, _data);
    }

    function emptyConfigDatas() external view returns (ISiloConfig.ConfigData memory a, ISiloConfig.ConfigData memory b) {
        return (a,b);
    }
}