/* Functions implementing `SiloConfig` for single silo setup
 *
 * See `summaries/config_for_one_in_cvl.spec` - where this is used.
 * See `meta/config_for_one_equivalence.spec` - where equivalence with `SiloConfig`
 * functions is verified.
 */

// To keep the contract aliases unique, we added the suffix `_CC` (for `CVL Config`)
using SiloConfigHarness as siloConfig_CC;

using Silo0 as silo0_CC;

using ShareDebtToken0 as shareDebtToken0_CC;
using ShareProtectedCollateralToken0 as shareProtectedCollateralToken0_CC;

using Token0 as token0_CC;

// ---- Implementations --------------------------------------------------------

/// @title Implements `SiloConfig.getSilos` in CVL
function CVLGetSilos() returns (address, address) {
    return (silo0_CC, siloConfig_CC._SILO1);
}

function CVLGetConfig(address _silo) returns ISiloConfig.ConfigData{
    require _silo == silo0_CC;
    ISiloConfig.ConfigData config;
    require config.daoFee == siloConfig_CC._DAO_FEE;
    require config.deployerFee == siloConfig_CC._DEPLOYER_FEE;
    require config.silo == silo0_CC;
    require config.token == token0_CC;
    require config.protectedShareToken ==shareProtectedCollateralToken0_CC;
    require config.collateralShareToken == silo0_CC;
    require config.debtShareToken == shareDebtToken0_CC;
    require config.solvencyOracle == siloConfig_CC._SOLVENCY_ORACLE0;
    require config.maxLtvOracle == siloConfig_CC._MAX_LTV_ORACLE0;
    require config.interestRateModel == siloConfig_CC._INTEREST_RATE_MODEL0;
    require config.maxLtv == siloConfig_CC._MAX_LTV0;
    require config.lt == siloConfig_CC._LT0;
    require config.liquidationTargetLtv == siloConfig_CC._LIQUIDATION_TARGET_LTV0;
    require config.liquidationFee == siloConfig_CC._LIQUIDATION_FEE0;
    require config.hookReceiver == siloConfig_CC._HOOK_RECEIVER;
    require config.callBeforeQuote == siloConfig_CC._CALL_BEFORE_QUOTE0;
    return config;
}

/// @title Implements `SiloConfig.getShareTokens` in CVL
/// @notice Assumes the silo is also the collateral share token!
function CVLGtShareTokens(address _silo) returns (address, address, address) {
    require _silo == silo0_CC;  // TODO: change to assert?
    return (shareProtectedCollateralToken0_CC, silo0_CC, shareDebtToken0_CC);
}



/// @title Implements `SiloConfig.getAssetForSilo` in CVL
function CVLGetAssetForSilo(address _silo) returns address {
    require _silo == silo0_CC;  // TODO: change to assert?
    return token0_CC;
}


/// @title Implements `SiloConfig.getFeesWithAsset` in CVL
function CVLGetFeesWithAsset(address _silo) returns (uint256, uint256, uint256, address) {
    require _silo == silo0_CC;  // TODO: change to assert?
    return (
        siloConfig_CC._DAO_FEE,
        siloConfig_CC._DEPLOYER_FEE,
        siloConfig_CC._FLASHLOAN_FEE0,
        token0_CC
    );
}

/// @title Implements `SiloConfig.getCollateralShareTokenAndAsset` in CVL
/// @notice Assumes each silo is also the collateral share token!
function CVLGetCollateralShareTokenAndAsset(
    address _silo,
    ISilo.CollateralType _collateralType
) returns (address, address) {
    require _silo == silo0_CC;  // TODO: change to assert?
    if (_collateralType == ISilo.CollateralType.Collateral) {
        return (silo0_CC, token0_CC);
    } else {
        return (shareProtectedCollateralToken0_CC, token0_CC);
    }
}


/// @title Implements `SiloConfig.getDebtShareTokenAndAsset` in CVL
function CVLGetDebtShareTokenAndAsset(address _silo) returns (address, address) {
    require _silo == silo0_CC;  // TODO: change to assert?
    return (shareDebtToken0_CC, token0_CC);
}
