methods {
}

definition STORAGE_SLOT_SILO() returns uint256
    = 0xd7513ffe3a01a9f6606089d1b67011bca35bec018ac0faa914e1c529408f8300;
definition PROTECTED_ASSET_TYPE() returns uint8 = require_uint8(ISilo.AssetType.Protected);
definition COLLATERAL_ASSET_TYPE() returns uint8 = require_uint8(ISilo.AssetType.Collateral);
definition DEBT_ASSET_TYPE() returns uint8 = require_uint8(ISilo.AssetType.Debt);

//
// daoAndDeployerRevenue & interestRateTimestamp (packed in 1 slot)
//

// These two values share a single storage slot
definition STORAGE_SLOT_REVENUE_TIMESTAMP() returns uint256 = STORAGE_SLOT_SILO();

ghost mapping (address => mathint) ghostDaoAndDeployerRevenue{
    init_state axiom forall address i. ghostDaoAndDeployerRevenue[i] == 0;
}
ghost mapping (address => mathint) ghostInterestRateTimestamp{
    init_state axiom forall address i. ghostDaoAndDeployerRevenue[i] == 0;
}

//
// totalAssets (mapping(uint256 => uint256), where uint256 = AssetType enum)
//


definition IS_STORAGE_SLOT_TOTAL_ASSETS(uint256 slot, uint8 assetType) returns bool
    = to_bytes32(slot) == keccak256(assetType,to_bytes32(STORAGE_SLOT_TOTAL_ASSETS()));


definition STORAGE_SLOT_TOTAL_ASSETS() returns uint256 = require_uint256(STORAGE_SLOT_SILO() +1);

persistent ghost mapping (address => mapping(uint8 => mathint)) ghostTotalAssets;