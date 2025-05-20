import "./siloStorage.spec";
import "./shareTokenStorage.spec";
//
// 🔍 Hooks for Storage Reads (SLOAD)
//
hook ALL_SLOAD(uint256 slot) uint256 val {
    if (slot == STORAGE_SLOT_REVENUE_TIMESTAMP()) {
        require(require_uint192(ghostDaoAndDeployerRevenue[executingContract]) == require_uint192(val));
        require(require_uint64(ghostInterestRateTimestamp[executingContract]) == require_uint64(val >> 192));
    } 
    else if (IS_STORAGE_SLOT_TOTAL_ASSETS(slot,PROTECTED_ASSET_TYPE())) {
            require(ghostTotalAssets[executingContract][PROTECTED_ASSET_TYPE()] == val);
    }else if(IS_STORAGE_SLOT_TOTAL_ASSETS(slot,COLLATERAL_ASSET_TYPE())) {
            require(ghostTotalAssets[executingContract][COLLATERAL_ASSET_TYPE()] == val);
    }else if(IS_STORAGE_SLOT_TOTAL_ASSETS(slot,DEBT_ASSET_TYPE())) {
            require(ghostTotalAssets[executingContract][DEBT_ASSET_TYPE()] == val);
    }
    //shareToken storage
    if (slot == STORAGE_SLOT_HOOK_SETUP()) {
        // For hookSetup, unpack the values:
        // - The lower 160 bits are the hookReceiver (address).
        // - The next 24 bits (bits 160..183) are hooksBefore.
        // - The next 24 bits (bits 183..206) are hooksAfter.
        // - The next 24 bits (bits 206..229) are tokenType.
        require(require_uint160(val) == require_uint160(ghostHookReceiver[executingContract]));
        require(require_uint24(val >> 160) == ghostHooksBefore[executingContract]);
        require(require_uint24(val >> 184) == ghostHooksAfter[executingContract]);
        require(require_uint24(val >> 208) == ghostTokenType[executingContract]);
    }
    if (slot == STORAGE_SLOT_TRANSFER_WITH_CHECKS()) {
        // For transferWithChecks, check the boolean value (0 or 1):
        // The boolean value is stored in the first byte of the storage slot
        uint8 transferWithChecksByte = require_uint8(val);
        
        // Check if the value matches the stored transferWithChecks state
        if (transferWithChecksByte == 0) {
            require(ghostTransferWithChecks[executingContract] == false);
        } else {
            require(ghostTransferWithChecks[executingContract] == true);
        }
    }
}

//
// ✍️ Hooks for Storage Writes (SSTORE)
//
hook ALL_SSTORE(uint256 slot, uint256 val) {
    if (slot == STORAGE_SLOT_REVENUE_TIMESTAMP()) {
        ghostDaoAndDeployerRevenue[executingContract] = require_uint192(val);
        ghostInterestRateTimestamp[executingContract] = require_uint64(val >> 192);
    } 
    else if (IS_STORAGE_SLOT_TOTAL_ASSETS(slot,PROTECTED_ASSET_TYPE())) {
            ghostTotalAssets[executingContract][PROTECTED_ASSET_TYPE()] = val;
    }
    else if(IS_STORAGE_SLOT_TOTAL_ASSETS(slot,COLLATERAL_ASSET_TYPE())) {
            ghostTotalAssets[executingContract][COLLATERAL_ASSET_TYPE()] = val;
    }else if(IS_STORAGE_SLOT_TOTAL_ASSETS(slot,DEBT_ASSET_TYPE())) {
            ghostTotalAssets[executingContract][DEBT_ASSET_TYPE()] = val;
    }
    //share token 
    if (slot == STORAGE_SLOT_HOOK_SETUP()) {
        // Update ghostHookReceiver with the lower 160 bits:
        ghostHookReceiver[executingContract] = require_address(to_bytes32(val & ((2 ^ 160) - 1)));
        // Update ghostHooksBefore with the next 24 bits:
        ghostHooksBefore[executingContract] = require_uint24(val >> 160);
        // Update ghostHooksAfter with the next 24 bits:
        ghostHooksAfter[executingContract] = require_uint24(val >> 184);
        // Update ghostTokenType with the next 24 bits:
        ghostTokenType[executingContract] = require_uint24(val >> 208);
    }
    if (slot == STORAGE_SLOT_TRANSFER_WITH_CHECKS()) {
        // For transferWithChecks, check the boolean value (0 or 1):
        // The boolean value is stored in the first byte of the storage slot
        uint8 transferWithChecksByte = require_uint8(val);
        
        // Check if the value matches the stored transferWithChecks state
        if (transferWithChecksByte == 0) {
            ghostTransferWithChecks[executingContract] = false;
        } else {
            ghostTransferWithChecks[executingContract] = true;
        }
    }
}