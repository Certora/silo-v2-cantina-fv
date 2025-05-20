// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Silo} from "silo-core/contracts/Silo.sol";
import {ISiloFactory} from "silo-core/contracts/interfaces/ISiloFactory.sol";
import {ISiloConfig} from "silo-core/contracts/interfaces/ISiloConfig.sol";
import {SiloSolvencyLib} from "silo-core/contracts/lib/SiloSolvencyLib.sol";
import {IShareToken} from "silo-core/contracts/interfaces/IShareToken.sol";
import {ISilo} from "silo-core/contracts/interfaces/ISilo.sol";
import {Views} from "silo-core/contracts/lib/Views.sol";
import {ShareTokenLib} from "silo-core/contracts//lib/ShareTokenLib.sol";
import {IERC20} from "openzeppelin5/token/ERC20/ERC20.sol";

contract SiloHarnessLiq is Silo {
    constructor(ISiloFactory _siloFactory) Silo(_siloFactory) {}

    uint256[37439836327923360225337895871394760624280537466773280374265222508165906222592] private __gap;
    ERC20Storage public erc20Storage;

    address public assetToken;
    address public debtShareToken;

    address public shareCollateralToken;
    address public shareProtectedToken;

    uint256 public sharesToReturn;

    function repay(uint256 _assets, address _borrower) external override returns(uint256 shares){
        shares = sharesToReturn;
        IShareToken(debtShareToken).burn(_borrower, msg.sender, shares);

        IERC20(assetToken).transferFrom(msg.sender, address(this),_assets);
    }

    function redeem(uint256 _shares, address _receiver, address _owner, ISilo.CollateralType _collateralType) external override returns(uint256 assets) {

        address shareToken = _collateralType == ISilo.CollateralType.Collateral ? shareCollateralToken : shareProtectedToken;

        IShareToken(shareToken).burn(_owner, msg.sender, _shares);

        IERC20(assetToken).transfer(_receiver, assets);

    }

    function getTransferWithChecks() external view returns (bool) {
        IShareToken.ShareTokenStorage storage $ = ShareTokenLib.getShareTokenStorage();
        return $.transferWithChecks;
    }
    


    function getSiloFromStorage() external view returns (ISilo) {
        IShareToken.ShareTokenStorage storage $ = ShareTokenLib.getShareTokenStorage();
        return $.silo;
    }
    
}