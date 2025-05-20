// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ISilo} from "silo-core/contracts/interfaces/ISilo.sol";
import {IShareToken} from "silo-core/contracts/interfaces/IShareToken.sol";
import {ISiloConfig} from "silo-core/contracts/interfaces/ISiloConfig.sol";
import {Hook} from "silo-core/contracts/lib/Hook.sol";
import {IHookReceiver} from "silo-core/contracts/interfaces/IHookReceiver.sol";
import {SiloHookReceiver} from "silo-core/contracts/utils/hook-receivers/_common/SiloHookReceiver.sol";

/// @notice Silo share token hook receiver for the gauge.
/// It notifies the gauge (if configured) about any balance update in the Silo share token.
contract EmptyHookReceiver is SiloHookReceiver {
    using Hook for uint256;
    using Hook for bytes;

    uint24 public constant HOOKS_BEFORE_NOT_CONFIGURED = 0;
    
    /// ACTIONS
        /// @dev The hooks are stored as a bitmap and can be combined with bitwise OR
        uint256 public constant NONE = 0;
        uint256 public constant DEPOSIT = 2 ** 1;
        uint256 public constant DEPOSIT_COLLATERAL = DEPOSIT | COLLATERAL_TOKEN;
        uint256 public constant DEPOSIT_PROTECTED = DEPOSIT | PROTECTED_TOKEN;
        uint256 public constant BORROW = 2 ** 2;
        uint256 public constant BORROW_SAME_ASSET = 2 ** 3;
        uint256 public constant REPAY = 2 ** 4;
        uint256 public constant WITHDRAW = 2 ** 5;
        uint256 public constant WITHDRAW_COLLATERAL = WITHDRAW | COLLATERAL_TOKEN;
        uint256 public constant WITHDRAW_PROTECTED = WITHDRAW | PROTECTED_TOKEN;
        uint256 public constant FLASH_LOAN = 2 ** 6;
        uint256 public constant TRANSITION_COLLATERAL = 2 ** 7;
        uint256 public constant TRANSITION_COLLATERAL_COLLATERAL = TRANSITION_COLLATERAL | COLLATERAL_TOKEN;
        uint256 public constant TRANSITION_COLLATERAL_PROTECTED = TRANSITION_COLLATERAL | PROTECTED_TOKEN;
        uint256 public constant SWITCH_COLLATERAL = 2 ** 8;
        uint256 public constant LIQUIDATION = 2 ** 9;
        uint256 public constant SHARE_TOKEN_TRANSFER = 2 ** 10;
        uint256 public constant SHARE_TOKEN_TRANSFER_COLLATERAL = SHARE_TOKEN_TRANSFER | COLLATERAL_TOKEN;
        uint256 public constant SHARE_TOKEN_TRANSFER_PROTECTED = SHARE_TOKEN_TRANSFER | PROTECTED_TOKEN;
        uint256 public constant SHARE_TOKEN_TRANSFER_DEBT = SHARE_TOKEN_TRANSFER | DEBT_TOKEN;
        uint256 public constant COLLATERAL_TOKEN = 2 ** 11;
        uint256 public constant PROTECTED_TOKEN = 2 ** 12;
    uint256 public constant DEBT_TOKEN = 2 ** 13;

    //COUNTERS  which indicate if an action was called
        uint256 public NONE_COUNTER_BEFORE;
        uint256 public NONE_COUNTER_AFTER;
        uint256 public DEPOSIT_COLLATERAL_COUNTER_BEFORE;
        uint256 public DEPOSIT_COLLATERAL_COUNTER_AFTER;
        uint256 public DEPOSIT_PROTECTED_COUNTER_BEFORE;
        uint256 public DEPOSIT_PROTECTED_COUNTER_AFTER;
        uint256 public BORROW_COUNTER_BEFORE;
        uint256 public BORROW_COUNTER_AFTER;
        uint256 public BORROW_SAME_ASSET_COUNTER_BEFORE;
        uint256 public BORROW_SAME_ASSET_COUNTER_AFTER;
        uint256 public REPAY_COUNTER_BEFORE;
        uint256 public REPAY_COUNTER_AFTER;
        uint256 public WITHDRAW_COLLATERAL_COUNTER_BEFORE;
        uint256 public WITHDRAW_COLLATERAL_COUNTER_AFTER;
        uint256 public WITHDRAW_PROTECTED_COUNTER_BEFORE;
        uint256 public WITHDRAW_PROTECTED_COUNTER_AFTER;
        uint256 public FLASH_LOAN_COUNTER_BEFORE;
        uint256 public FLASH_LOAN_COUNTER_AFTER;
        uint256 public TRANSITION_COLLATERAL_COLLATERAL_COUNTER_BEFORE;
        uint256 public TRANSITION_COLLATERAL_COLLATERAL_COUNTER_AFTER;
        uint256 public TRANSITION_COLLATERAL_PROTECTED_COUNTER_BEFORE;
        uint256 public TRANSITION_COLLATERAL_PROTECTED_COUNTER_AFTER;
        uint256 public SWITCH_COLLATERAL_COUNTER_BEFORE;
        uint256 public SWITCH_COLLATERAL_COUNTER_AFTER;
        uint256 public LIQUIDATION_COUNTER_BEFORE;
        uint256 public LIQUIDATION_COUNTER_AFTER;
        uint256 public TRANSFER_COLLATERAL_COUNTER_BEFORE;
        uint256 public TRANSFER_COLLATERAL_COUNTER_AFTER;
        uint256 public TRANSFER_PROTECTED_COUNTER_BEFORE;
        uint256 public TRANSFER_PROTECTED_COUNTER_AFTER;
        uint256 public TRANSFER_DEBT_COUNTER_BEFORE;
    uint256 public TRANSFER_DEBT_COUNTER_AFTER;



    ISiloConfig public siloConfig;

    /// @inheritdoc IHookReceiver
    function initialize(ISiloConfig _siloConfig, bytes calldata _data) external {
        siloConfig = _siloConfig;
    }

    /// @inheritdoc IHookReceiver
    function beforeAction(address _silo, uint256 action, bytes memory ) external {
       if(action == DEPOSIT_COLLATERAL){
            DEPOSIT_COLLATERAL_COUNTER_BEFORE++;
        } else if(action == DEPOSIT_PROTECTED){
            DEPOSIT_PROTECTED_COUNTER_BEFORE++;
        } else if(action == BORROW){
            BORROW_COUNTER_BEFORE++;
        } else if(action == BORROW_SAME_ASSET){
            BORROW_SAME_ASSET_COUNTER_BEFORE++;
        } else if(action == REPAY){
            REPAY_COUNTER_BEFORE++;
        } else if(action == WITHDRAW_COLLATERAL){
            WITHDRAW_COLLATERAL_COUNTER_BEFORE++;
        } else if(action == WITHDRAW_PROTECTED){
            WITHDRAW_PROTECTED_COUNTER_BEFORE++;
        } else if(action == FLASH_LOAN){
            FLASH_LOAN_COUNTER_BEFORE++;
        } else if(action == TRANSITION_COLLATERAL_COLLATERAL){
            TRANSITION_COLLATERAL_COLLATERAL_COUNTER_BEFORE++;
        } else if(action == TRANSITION_COLLATERAL_PROTECTED){
            TRANSITION_COLLATERAL_PROTECTED_COUNTER_BEFORE++;
        } else if(action == SWITCH_COLLATERAL){
            SWITCH_COLLATERAL_COUNTER_BEFORE++;
        } else if(action == LIQUIDATION){
            LIQUIDATION_COUNTER_BEFORE++;
        } else if(action == SHARE_TOKEN_TRANSFER_COLLATERAL){
            TRANSFER_COLLATERAL_COUNTER_BEFORE++;
        } else if(action == SHARE_TOKEN_TRANSFER_PROTECTED){
            TRANSFER_PROTECTED_COUNTER_BEFORE++;
        } else if(action == SHARE_TOKEN_TRANSFER_DEBT){
            TRANSFER_DEBT_COUNTER_BEFORE++;
        } else{
            NONE_COUNTER_BEFORE++;
       }
    }

    /// @inheritdoc IHookReceiver
    function afterAction(address _silo, uint256 action, bytes memory ) external {
        if(action == DEPOSIT_COLLATERAL){
            DEPOSIT_COLLATERAL_COUNTER_AFTER++;
        } else if(action == DEPOSIT_PROTECTED){
            DEPOSIT_PROTECTED_COUNTER_AFTER++;
        } else if(action == BORROW){
            BORROW_COUNTER_AFTER++;
        } else if(action == BORROW_SAME_ASSET){
            BORROW_SAME_ASSET_COUNTER_AFTER++;
        } else if(action == REPAY){
            REPAY_COUNTER_AFTER++;
        } else if(action == WITHDRAW_COLLATERAL){
            WITHDRAW_COLLATERAL_COUNTER_AFTER++;
        } else if(action == WITHDRAW_PROTECTED){
            WITHDRAW_PROTECTED_COUNTER_AFTER++;
        } else if(action == FLASH_LOAN){
            FLASH_LOAN_COUNTER_AFTER++;
        } else if(action == TRANSITION_COLLATERAL_COLLATERAL){
            TRANSITION_COLLATERAL_COLLATERAL_COUNTER_AFTER++;
        } else if(action == TRANSITION_COLLATERAL_PROTECTED){
            TRANSITION_COLLATERAL_PROTECTED_COUNTER_AFTER++;
        } else if(action == SWITCH_COLLATERAL){
            SWITCH_COLLATERAL_COUNTER_AFTER++;
        } else if(action == LIQUIDATION){
            LIQUIDATION_COUNTER_AFTER++;
        } else if(action == SHARE_TOKEN_TRANSFER_COLLATERAL){
            TRANSFER_COLLATERAL_COUNTER_AFTER++;
        } else if(action == SHARE_TOKEN_TRANSFER_PROTECTED){
            TRANSFER_PROTECTED_COUNTER_AFTER++;
        } else if(action == SHARE_TOKEN_TRANSFER_DEBT){
            TRANSFER_DEBT_COUNTER_AFTER++;
        } else{
            NONE_COUNTER_AFTER++;
        }
    }
    
    // TODO: is this correct implementation?
    function hookReceiverConfig(address _silo) external view returns (
        uint24 hooksBefore,
        uint24 hooksAfter
    ) {
        return _hookReceiverConfig(_silo);
    }

    function sumOfCountersBefore() external view returns (uint256) {
        return  NONE_COUNTER_BEFORE + 
                DEPOSIT_COLLATERAL_COUNTER_BEFORE + 
                DEPOSIT_PROTECTED_COUNTER_BEFORE + 
                BORROW_COUNTER_BEFORE + 
                BORROW_SAME_ASSET_COUNTER_BEFORE + 
                REPAY_COUNTER_BEFORE + 
                WITHDRAW_COLLATERAL_COUNTER_BEFORE + 
                WITHDRAW_PROTECTED_COUNTER_BEFORE + 
                FLASH_LOAN_COUNTER_BEFORE +
                TRANSITION_COLLATERAL_COLLATERAL_COUNTER_BEFORE +
                TRANSITION_COLLATERAL_PROTECTED_COUNTER_BEFORE +
                SWITCH_COLLATERAL_COUNTER_BEFORE +
                LIQUIDATION_COUNTER_BEFORE +
                TRANSFER_COLLATERAL_COUNTER_BEFORE +
                TRANSFER_PROTECTED_COUNTER_BEFORE +
                TRANSFER_DEBT_COUNTER_BEFORE;
    }

    function sumOfCountersAfter() external view returns (uint256) {
        return  NONE_COUNTER_AFTER + 
                DEPOSIT_COLLATERAL_COUNTER_AFTER + 
                DEPOSIT_PROTECTED_COUNTER_AFTER + 
                BORROW_COUNTER_AFTER + 
                BORROW_SAME_ASSET_COUNTER_AFTER + 
                REPAY_COUNTER_AFTER + 
                WITHDRAW_COLLATERAL_COUNTER_AFTER + 
                WITHDRAW_PROTECTED_COUNTER_AFTER + 
                FLASH_LOAN_COUNTER_AFTER +
                TRANSITION_COLLATERAL_COLLATERAL_COUNTER_AFTER +
                TRANSITION_COLLATERAL_PROTECTED_COUNTER_AFTER +
                SWITCH_COLLATERAL_COUNTER_AFTER +
                LIQUIDATION_COUNTER_AFTER +
                TRANSFER_COLLATERAL_COUNTER_AFTER +
                TRANSFER_PROTECTED_COUNTER_AFTER +
                TRANSFER_DEBT_COUNTER_AFTER;
    }
}