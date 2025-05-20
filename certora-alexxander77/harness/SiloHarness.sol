// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Silo} from "silo-core/contracts/Silo.sol";

import {ISiloFactory} from "silo-core/contracts/interfaces/ISiloFactory.sol";
import {ISiloConfig} from "silo-core/contracts/interfaces/ISiloConfig.sol";
import {IShareToken} from "silo-core/contracts/interfaces/IShareToken.sol";
import {IHookReceiver} from "silo-core/contracts/interfaces/IHookReceiver.sol";
import {ISilo} from "silo-core/contracts/interfaces/ISilo.sol";
import {IERC3156FlashBorrower} from "silo-core/contracts/interfaces/IERC3156FlashBorrower.sol";

import {SiloSolvencyLib} from "silo-core/contracts/lib/SiloSolvencyLib.sol";
import {Hook} from "silo-core/contracts/lib/Hook.sol";
import {Views} from "silo-core/contracts/lib/Views.sol";
import {ShareTokenLib} from "silo-core/contracts/lib/ShareTokenLib.sol";
import {SiloLendingLib} from "silo-core/contracts/lib/SiloLendingLib.sol";
import {SiloStorageLib} from "silo-core/contracts/lib/SiloStorageLib.sol";
import {Rounding} from "silo-core/contracts//lib/Rounding.sol";
import {Actions} from "silo-core/contracts//lib/Actions.sol";
import {SiloStdLib} from "silo-core/contracts/lib/SiloStdLib.sol";
import {ShareCollateralTokenLib} from "silo-core/contracts/lib/ShareCollateralTokenLib.sol";

import {Math} from "openzeppelin5/utils/math/Math.sol";
import {IERC20} from "openzeppelin5/token/ERC20/ERC20.sol";


contract SiloHarness is Silo {

    uint256[37439836327923360225337895871394760624280537466773280374265222508165906222592] private __gap;
    ERC20Storage public erc20Storage;

    ISiloConfig public siloConfigHelper;
    address public hookReceiverHelper;

    uint256 public constant MAX_UINT256 = type(uint256).max;
    bytes32 public constant _FLASHLOAN_CALLBACK = keccak256("ERC3156FlashBorrower.onFlashLoan");

    bytes public hashBlobStorage0;
    bytes public hashBlobStorage1;

    ISiloConfig.ConfigData collateralConfig;
    ISiloConfig.ConfigData debtConfig;

    constructor(ISiloFactory _siloFactory) Silo(_siloFactory) {}

    function getStorage() external view returns (IShareToken.ShareTokenStorage memory) {
        return ShareTokenLib.getShareTokenStorage();
    }
    function getAddressThis() external view returns (address) {
        return address(this);
    }
    function setHash0(bytes memory input) external {
        hashBlobStorage0 = input;
    }
    function setHash1(bytes memory input) external {
        hashBlobStorage1 = input;
    }

    function getHash0() external returns (bytes memory) {
        return hashBlobStorage0;
    }
    function getHash1() external returns (bytes memory) {
        return hashBlobStorage1;
    }

    function setCollateralConfig(ISiloConfig.ConfigData memory input) external {
        collateralConfig = input;
    }
    function setDebtConfig(ISiloConfig.ConfigData memory input) external {
        debtConfig = input;
    }
    function getCollateralConfig() external returns (ISiloConfig.ConfigData memory) {
        return collateralConfig;
    }
    function getDebtConfig() external returns (ISiloConfig.ConfigData memory) {
        return debtConfig;
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

    /* ----------------------- internal functionality ----------------------------- */
    function convertToAssetsHarness(uint256 _shares, AssetType _assetType) external view virtual returns (uint256) {
        return _convertToAssets(_shares, _assetType);
    }
    function convertToSharesHarness(uint256 _assets, AssetType _assetType) external view virtual returns (uint256) {
        return _convertToShares(_assets, _assetType);
    }

    // deposit stuff
    function previewMintHarness(uint256 _shares, CollateralType _collateralType) external view virtual returns (uint256) {
        return _previewMint(_shares, _collateralType);
    }
    function previewDepositHarness(uint256 _assets, CollateralType _collateralType) external view virtual returns (uint256) {
        return _previewDeposit(_assets, _collateralType);
    }
    function depositHarness(uint256 _assets, uint256 _shares, address _receiver, ISilo.CollateralType _collateralType)
    external virtual returns (uint256, uint256) {
        return _deposit(_assets, _shares, _receiver, _collateralType);
    }

    // withdraw stuff
    function previewRedeemHarness(uint256 _shares, CollateralType _collateralType) external view virtual returns (uint256) {
        return _previewRedeem(_shares, _collateralType);
    }
    function previewWithdrawHarness(uint256 _assets, CollateralType _collateralType) external view virtual returns (uint256) {
        return _previewWithdraw(_assets, _collateralType);
    }
    function withdrawHarness(uint256 _assets, uint256 _shares, address _receiver, address _owner, address _spender, ISilo.CollateralType _collateralType)
    external virtual returns (uint256, uint256) {
        return _withdraw(_assets, _shares, _receiver, _owner, _spender, _collateralType);
    }

    // internal getters
    function totalAssetsHarness() external view virtual returns (uint256) {
        return _totalAssets();
    }
    function maxWithdrawHarness(address _owner, ISilo.CollateralType _collateralType) external view virtual returns (uint256 assets, uint256 shares) {
        return _maxWithdraw(_owner, _collateralType);
    }
    function getAccrueInterestHarness() external virtual returns (uint256) {
        return _accrueInterest();
    }
    function getAccrueInterestForAssetHarness(address _interestRateModel, uint256 _daoFee, uint256 _deployerFee) external virtual returns (uint256) {
        return _accrueInterestForAsset(_interestRateModel, _daoFee, _deployerFee);
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
        } else if (signatureIndex == 5) {
            return keccak256("HooksUpdated(uint24,uint24)");
        } else {
            revert UnknownEventSignatureIndex(signatureIndex);
        }
    }
    function hashAddress(bytes32 topic, address original) external pure returns (bool)  {
        return topic == bytes32(abi.encode(original));
    }
    function getBalanceOf(address _owner) external view returns (uint256) {
        return balanceOf(_owner);
    }
    Math.Rounding public constant ROUNDING_mint = Rounding.DEPOSIT_TO_ASSETS; // (Math.Rounding.Ceil); // mint
    Math.Rounding public constant ROUNDING_deposit = Rounding.DEPOSIT_TO_SHARES; // (Math.Rounding.Floor); //deposit
    Math.Rounding public constant ROUNDING_redeem = Rounding.WITHDRAW_TO_ASSETS; // (Math.Rounding.Floor); // redeem
    Math.Rounding public constant ROUNDING_withdraw = Rounding.WITHDRAW_TO_SHARES; // (Math.Rounding.Ceil); // withdraw
    Math.Rounding public constant ROUNDING_BORROW_TO_SHARES = Rounding.BORROW_TO_SHARES; // (Math.Rounding.Ceil); // withdraw
    Math.Rounding public constant ROUNDING_DEPOSIT_TO_SHARES = Rounding.DEPOSIT_TO_SHARES; // (Math.Rounding.Ceil); // withdraw
    Math.Rounding public constant ROUNDING_BORROW_TO_ASSETS = Rounding.BORROW_TO_ASSETS; // (Math.Rounding.Ceil); // withdraw
    Math.Rounding public constant ROUNDING_DEPOSIT_TO_ASSETS = Rounding.DEPOSIT_TO_ASSETS; // (Math.Rounding.Ceil); // withdraw

    function expectedAssetType(CollateralType _collateralType) external view returns (AssetType) {
        return AssetType(uint256(_collateralType));
    }

    // actions
    function getDepositAction(ISilo.CollateralType _type) external pure returns (uint256) {
        return Hook.depositAction(_type);
    }
    function getWithdrawAction(ISilo.CollateralType _type) external pure returns (uint256) {
        return Hook.withdrawAction(_type);
    }
    function getTransitionCollateralActionAction(ISilo.CollateralType _type) external pure returns (uint256) {
        return Hook.transitionCollateralAction(_type);
    }

    using Hook for uint24;
    using Hook for uint256;
    function matchAction(uint256 _action, uint256 _expectedHook) external returns (bool) {
        return _action.matchAction(_expectedHook);
    }

    function encodeWithdrawDataBefore(uint256 assets, uint256 shares, address receiver, address owner, address spender) external returns (bytes memory) {
        return abi.encodePacked(assets, shares, receiver, owner, spender);
    }
    function encodeWithdrawDataAfter(uint256 assets, uint256 shares, address receiver, address owner, address spender, uint256 _assets, uint256 _shares) external returns (bytes memory) {
        return abi.encodePacked(assets, shares, receiver, owner, spender, _assets, _shares);
    }

    function encodeBorrowDataBefore(ISilo.BorrowArgs calldata args, address sender) external returns (bytes memory) {
        return abi.encodePacked(args.assets,args.shares,args.receiver,args.borrower,sender);
    }
    function encodeBorrowDataAfter(ISilo.BorrowArgs calldata args, address sender, uint256 assets, uint256 shares) external returns (bytes memory) {
        return abi.encodePacked(args.assets,args.shares,args.receiver,args.borrower,sender,assets,shares);
    }

    function encodeTransitionCollateralBefore(uint256 shares, address owner) external returns (bytes memory) {
        return abi.encodePacked(shares, owner);
    }
    function encodeTransitionCollateralAfter(uint256 assets, address owner, uint256 shares) external returns (bytes memory) {
        return abi.encodePacked(assets, owner, shares);
    }

    function encodeDepositDataBefore(uint256 _assets, uint256 _shares, address _receiver) external returns (bytes memory) {
        return abi.encodePacked(_assets, _shares, _receiver);
    }
    function encodeDepositDataAfter(uint256 _assets, uint256 _shares, address _receiver, uint256 _exactAssets, uint256 _exactShare) external returns (bytes memory) {
        return abi.encodePacked(_assets, _shares, _receiver, _exactAssets, _exactShare);
    }

    function encodeRepayDataBefore(uint256 _assets, uint256 _shares, address _borrower, address _repayer) external returns (bytes memory) {
        return abi.encodePacked(_assets, _shares, _borrower, _repayer);
    }
    function encodeRepayDataAfter(uint256 _assets, uint256 _shares, address _borrower, address _repayer, uint256 _exactAssets, uint256 _exactShare) external returns (bytes memory) {
        return abi.encodePacked(_assets, _shares, _borrower, _repayer, _exactAssets, _exactShare);
    }

    function encodeSwitchCollateralDataBefore(address sender) external returns (bytes memory) {
        return abi.encodePacked(sender);
    }
    function encodeSwitchCollateralDataAfter(address sender) external returns (bytes memory) {
        return abi.encodePacked(sender);
    }

    function getHooksAfter() external view returns (uint24) {
        IShareToken.ShareTokenStorage storage _shareStorage = ShareTokenLib.getShareTokenStorage();
        return _shareStorage.hookSetup.hooksAfter;
    }
    function getHooksBefore() external view returns (uint24) {
        IShareToken.ShareTokenStorage storage _shareStorage = ShareTokenLib.getShareTokenStorage();
        return _shareStorage.hookSetup.hooksBefore;
    }
    function getStoredTokenType() external view returns (uint24) {
        IShareToken.ShareTokenStorage storage _shareStorage = ShareTokenLib.getShareTokenStorage();
        return _shareStorage.hookSetup.tokenType;
    }
    function getStoredHookReceiver() external view returns (address) {
        IShareToken.ShareTokenStorage storage _shareStorage = ShareTokenLib.getShareTokenStorage();
        return _shareStorage.hookSetup.hookReceiver;
    }

    function getInitializeStateResult() external view returns(ISilo, ISiloConfig, address, uint24, bool) {
        IShareToken.ShareTokenStorage storage _shareStorage = ShareTokenLib.getShareTokenStorage();
        return(_shareStorage.silo, _shareStorage.siloConfig, _shareStorage.hookSetup.hookReceiver, _shareStorage.hookSetup.tokenType, _shareStorage.transferWithChecks);
    }

    function getFullHookSetup(ISiloConfig.ConfigData memory cfg) external returns (uint24,uint24,uint24,uint24,uint24,uint24) {
        return (IShareToken(cfg.collateralShareToken).hookSetup().hooksBefore,
                IShareToken(cfg.collateralShareToken).hookSetup().hooksAfter,
                IShareToken(cfg.protectedShareToken).hookSetup().hooksBefore,
                IShareToken(cfg.protectedShareToken).hookSetup().hooksAfter,
                IShareToken(cfg.debtShareToken).hookSetup().hooksBefore,
                IShareToken(cfg.debtShareToken).hookSetup().hooksAfter);
    }
    function getHooksForToken(address token) external view returns(uint24, uint24) {
        return (0,0);
    }

    // Assets Helpers
    function getProtectedAssets() external view returns (uint256) {
        ISilo.SiloStorage storage $ = SiloStorageLib.getSiloStorage();
        return $.totalAssets[ISilo.AssetType.Protected];
    }
    function getTypeAssets(ISilo.AssetType assetType) external view returns (uint256) {
        ISilo.SiloStorage storage $ = SiloStorageLib.getSiloStorage();
        return $.totalAssets[assetType];
    }

    function debtAssetsWithInterest() internal view returns (uint256 totalDebtAssets) {
        ISiloConfig.ConfigData memory thisSiloConfig = ShareTokenLib.getConfig();

        totalDebtAssets = SiloStdLib.getTotalDebtAssetsWithInterest(
            thisSiloConfig.silo, thisSiloConfig.interestRateModel
        );
    }

    function getAssetForSilo() external view returns(address) {
        return ShareTokenLib.siloConfig().getAssetForSilo(address(this));
    }

    function getBalanceOfToken(address token, address user) external returns(uint256) {
        return IERC20(token).balanceOf(user);
    }

    // Flash Loan helpers
    // this includes precision
    function getFlashFeeHelper(uint256 _amount) external view returns (uint256 flashLoanFee, address asset, uint256 calculatedFee) {
        (,, flashLoanFee, asset) =  ShareTokenLib.siloConfig().getFeesWithAsset(address(this));
        calculatedFee = SiloStdLib.flashFee(ShareTokenLib.getShareTokenStorage().siloConfig, asset, _amount);
    }
    // Revenue
    function getDaoAndDeployerRevenue() external view returns(uint192) {
        return SiloStorageLib.getSiloStorage().daoAndDeployerRevenue;
    }
    // interest
    function getInterestRateTimestamp() external view returns(uint64) {
        return SiloStorageLib.getSiloStorage().interestRateTimestamp;
    }


    // Needed to avoid vacuity in linked setupinit
    function _shareTokenInitialize(
        ISilo _silo,
        address _hookReceiver,
        uint24 _tokenType
    )
    internal
    override
    {
//        __ERC20Permit_init("SiloShareTokenEIP712Name");

        ShareTokenLib.__ShareToken_init(_silo, _hookReceiver, _tokenType);
    }


    // ---------------- ACTIONS
    function depositActions(
        uint256 _assets,
        uint256 _shares,
        address _receiver,
        ISilo.CollateralType _collateralType
    ) external returns (uint256, uint256) {
        return Actions.deposit(_assets, _shares, _receiver, _collateralType);
    }
    function withdrawActions(ISilo.WithdrawArgs calldata _args) external returns (uint256, uint256) {
        return Actions.withdraw(_args);
    }
    function borrowActions(ISilo.BorrowArgs calldata _args) external returns (uint256, uint256) {
        return Actions.borrow(_args);
    }
    function borrowSameAssetActions(ISilo.BorrowArgs calldata _args) external returns (uint256, uint256) {
        return Actions.borrowSameAsset(_args);
    }
    function repayActions(
        uint256 _assets,
        uint256 _shares,
        address _borrower,
        address _repayer
    ) external returns (uint256, uint256) {
        return Actions.repay(_assets, _shares, _borrower, _repayer);
    }
    function transitionCollateralActions(ISilo.TransitionCollateralArgs memory _args) external returns (uint256, uint256) {
        return Actions.transitionCollateral(_args);
    }

    function getDebt(address _silo) external view returns (uint256) {
        return ISilo(_silo).getDebtAssets();
    }

    function getERCBalance(address token, address addr) external view returns (uint256) {
        return IERC20(token).balanceOf(addr);
    }
    function getCollateralShareToken(ISilo.CollateralType _collateralType) external view returns (address, address) {
        return ShareTokenLib.getShareTokenStorage().siloConfig.getCollateralShareTokenAndAsset(address(this), _collateralType);
    }
    function getDebtShareToken() external view returns (address, address) {
        return ShareTokenLib.getShareTokenStorage().siloConfig.getDebtShareTokenAndAsset(address(this));
    }
    function getWithdrawConfigs(address owner) external view returns (
        ISiloConfig.DepositConfig memory depositConfig,
        ISiloConfig.ConfigData memory collateralConfig,
        ISiloConfig.ConfigData memory debtConfig
    ) {
        return ShareTokenLib.getShareTokenStorage().siloConfig.getConfigsForWithdraw(address(this), owner);
    }
    function getBorrowConfigs() external view returns (
        ISiloConfig.ConfigData memory collateralConfig,
        ISiloConfig.ConfigData memory debtConfig
    ) {
        return ShareTokenLib.getShareTokenStorage().siloConfig.getConfigsForBorrow(address(this));
    }
    function getBaseConfig() external view returns (ISiloConfig.ConfigData memory) {
        return ShareTokenLib.getShareTokenStorage().siloConfig.getConfig(address(this));
    }
    function getSolvencyConfigs() external returns (ISiloConfig.ConfigData memory, ISiloConfig.ConfigData memory) {
        return ShareTokenLib.getShareTokenStorage().siloConfig.getConfigsForSolvency(msg.sender);
    }
    function getSiloConfig() external returns (ISiloConfig) {
        return ShareTokenLib.getShareTokenStorage().siloConfig;
    }

    function switchCollateral() external {
        Actions.switchCollateralToThisSilo();
    }
    function withdrawFee(ISilo _silo) external returns (uint256, uint256) {
        return Actions.withdrawFees(_silo);
    }
    function updateHooksAction() external returns (uint24, uint24) {
        return Actions.updateHooks();
    }

    function getFeesAndFeeReceivers(ISilo _silo) external view returns (address, address, uint256, uint256, address) {
        return SiloStdLib.getFeesAndFeeReceiversWithAsset(_silo);
    }

    function solvencyCheck(
        ISiloConfig.ConfigData memory a,
        ISiloConfig.ConfigData memory b,
        address c,
        ISilo.AccrueInterestInMemory d)
    external view returns (bool) {
        return SiloSolvencyLib.isSolvent(a, b, c, d);
    }

    function isInitializing() external returns (bool) {
        return _isInitializing();
    }
}