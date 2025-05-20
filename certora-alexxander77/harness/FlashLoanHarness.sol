// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Silo} from "silo-core/contracts/Silo.sol";

import {ISiloFactory} from "silo-core/contracts/interfaces/ISiloFactory.sol";
import {ISiloConfig} from "silo-core/contracts/interfaces/ISiloConfig.sol";
import {IShareToken} from "silo-core/contracts/interfaces/IShareToken.sol";

import {ISilo} from "silo-core/contracts/interfaces/ISilo.sol";

import {Hook} from "silo-core/contracts/lib/Hook.sol";
import {ShareTokenLib} from "silo-core/contracts/lib/ShareTokenLib.sol";
import {SiloStorageLib} from "silo-core/contracts/lib/SiloStorageLib.sol";
import {SiloStdLib} from "silo-core/contracts/lib/SiloStdLib.sol";

import {IERC20} from "openzeppelin5/token/ERC20/ERC20.sol";

import {EmptyFlashBorrower} from "../contract-mocks/EmptyFlashBorrower.sol";


contract FlashLoanHarness is Silo {

    uint256[764520080237424869752330524124367139483859928243420876645759593088794890752] private __gap__;
    IShareToken.ShareTokenStorage shareTokenStorage;
    // uint256[37439836327923360225337895871394760624280537466773280374265222508165906222592] private __gap;
    // ERC20Storage public erc20Storage;

    ISiloConfig public siloConfigHelper;
    address public hookReceiverHelper;
    address public flashLoanReceiverHelper;

    uint256 public constant MAX_UINT256 = type(uint256).max;
    bytes32 public constant _FLASHLOAN_CALLBACK = keccak256("ERC3156FlashBorrower.onFlashLoan");

    constructor(ISiloFactory _siloFactory) Silo(_siloFactory) {}

    function getStorage() external view returns (IShareToken.ShareTokenStorage memory) {
        return ShareTokenLib.getShareTokenStorage();
    }
    function getAddressThis() external view returns (address) {
        return address(this);
    }

    /* ----------------------- helper stuff ----------------------------- */
    // needed cause cvl keccak does something else
    error UnknownEventSignatureIndex(uint256);
    function hashSignature(uint256 signatureIndex) external view returns (bytes32) {
        if (signatureIndex == 0) {
            return keccak256("Deposit(address,address,uint256,uint256)");
        } else if (signatureIndex == 1) {
            return keccak256("DepositProtected(address,address,uint256,uint256)");
        } else if (signatureIndex == 2) {
            return keccak256("Withdraw(address,address,address,uint256,uint256)");
        } else if (signatureIndex == 3) {
            return keccak256("WithdrawProtected(address,address,address,uint256,uint256)");
        } else if (signatureIndex == 4) {
            return keccak256("FlashLoan(uint256)");
        } else {
            revert UnknownEventSignatureIndex(signatureIndex);
        }
    }

    using Hook for uint24;
    using Hook for uint256;
    function matchAction(uint256 _action, uint256 _expectedHook) external returns (bool) {
        return _action.matchAction(_expectedHook);
    }
    function getHooksAfter() external view returns (uint24) {
        IShareToken.ShareTokenStorage storage _shareStorage = ShareTokenLib.getShareTokenStorage();
        return _shareStorage.hookSetup.hooksAfter;
    }
    function getHooksBefore() external view returns (uint24) {
        IShareToken.ShareTokenStorage storage _shareStorage = ShareTokenLib.getShareTokenStorage();
        return _shareStorage.hookSetup.hooksBefore;
    }
    function getStoredHookReceiver() external view returns (address) {
        IShareToken.ShareTokenStorage storage _shareStorage = ShareTokenLib.getShareTokenStorage();
        return _shareStorage.hookSetup.hookReceiver;
    }

    // Assets Helpers
    function getProtectedAssets() external view returns (uint256) {
        ISilo.SiloStorage storage $ = SiloStorageLib.getSiloStorage();
        return $.totalAssets[ISilo.AssetType.Protected];
    }

    function getAssetForSilo() external view returns(address) {
        return ShareTokenLib.siloConfig().getAssetForSilo(address(this));
    }

    function getBalanceOfToken(address token, address user) external returns(uint256) {
        return IERC20(token).balanceOf(user);
    }

    // Flash Loan helpers
    // this includes precision
    // function getFlashFeeHelper(uint256 _amount) external view returns (uint256 flashLoanFee, address _asset, uint256 calculatedFee) {
    //     (,, flashLoanFee, _asset) =  ShareTokenLib.siloConfig().getFeesWithAsset(address(this));
    //     calculatedFee = SiloStdLib.flashFee(ShareTokenLib.getShareTokenStorage().siloConfig, _asset, _amount);
    // }

    function getFlashFeeOpt(ISiloConfig siloConf, uint256 amount) external view returns (uint256 flashLoanFee, address _asset, uint256 calculatedFee) {
        (,, flashLoanFee, _asset) = siloConf.getFeesWithAsset(address(this));
        calculatedFee = SiloStdLib.flashFee(siloConf, _asset, amount);
    }

    // Revenue
    function getDaoAndDeployerRevenue() external view returns(uint192) {
        return SiloStorageLib.getSiloStorage().daoAndDeployerRevenue;

    }

    function getRecordedBalanceFlashReceiver() external view returns(uint256) {
        return EmptyFlashBorrower(flashLoanReceiverHelper).balanceAfterFlashLoan();
    }

    function getRecordedParamsOnFlashLoan() external view returns(uint256, address, address, uint256, uint256) {
        return EmptyFlashBorrower(flashLoanReceiverHelper).getRecordedParams();
    }

    // Needed to avoid vacuity in linked setup
    function _shareTokenInitialize(
        ISilo _silo,
        address _hookReceiver,
        uint24 _tokenType
    )
    internal
    override
    {
        __ERC20Permit_init("SiloShareTokenEIP712Name");

        ShareTokenLib.__ShareToken_init(_silo, _hookReceiver, _tokenType);
    }

}