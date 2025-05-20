/* Functions implementing `SiloConfig` for two silos
 *
 * See `summaries/config_for_two_in_cvl.spec` - where this is used.
 * See `meta/config_for_two_equivalence.spec` - where equivalence with `SiloConfig`
 * functions is verified.
 */

// To keep the contract aliases unique, we added the suffix `_CC` (for `CVL Config`)
using SiloConfigHarness as siloConfig_CC;

using Silo0 as silo0_CC;
using Silo1 as silo1_CC;

using ShareDebtToken0 as shareDebtToken0_CC;
using ShareProtectedCollateralToken0 as shareProtectedCollateralToken0_CC;

using ShareDebtToken1 as shareDebtToken1_CC;
using ShareProtectedCollateralToken1 as shareProtectedCollateralToken1_CC;

using Token0 as token0_CC;
using Token1 as token1_CC;

// ---- Implementations --------------------------------------------------------

// @title Implements `SiloConfig.getSilos` in CVL
function CVLGetSilos() returns (address, address) {
    return (silo0_CC, silo1_CC);
}

function CVLGetConfig(address _silo) returns ISiloConfig.ConfigData{
    require _silo == silo0_CC || _silo == silo1_CC;
    ISiloConfig.ConfigData config;
    if(_silo == silo0_CC){
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
    }else{
        require config.daoFee == siloConfig_CC._DAO_FEE;
        require config.deployerFee == siloConfig_CC._DEPLOYER_FEE;
        require config.silo == silo1_CC;
        require config.token == token1_CC;
        require config.protectedShareToken ==shareProtectedCollateralToken1_CC;
        require config.collateralShareToken == silo1_CC;
        require config.debtShareToken == shareDebtToken1_CC;
        require config.solvencyOracle == siloConfig_CC._SOLVENCY_ORACLE1;
        require config.maxLtvOracle == siloConfig_CC._MAX_LTV_ORACLE1;
        require config.interestRateModel == siloConfig_CC._INTEREST_RATE_MODEL1;
        require config.maxLtv == siloConfig_CC._MAX_LTV1;
        require config.lt == siloConfig_CC._LT1;
        require config.liquidationTargetLtv == siloConfig_CC._LIQUIDATION_TARGET_LTV1;
        require config.liquidationFee == siloConfig_CC._LIQUIDATION_FEE1;
        require config.hookReceiver == siloConfig_CC._HOOK_RECEIVER;
        require config.callBeforeQuote == siloConfig_CC._CALL_BEFORE_QUOTE1;
    }
    return config;
}

// @title Implements `SiloConfig.getShareTokens` in CVL
// @notice Assumes each silo is also the collateral share token!
function CVLGtShareTokens(address _silo) returns (address, address, address) {
    require _silo == silo0_CC || _silo == silo1_CC;  // TODO: change to assert?
    if (_silo == siloConfig_CC._SILO0) {
        return (shareProtectedCollateralToken0_CC, silo0_CC, shareDebtToken0_CC);
    } else {
        return (shareProtectedCollateralToken1_CC, silo1_CC, shareDebtToken1_CC);
    }
}

// @title Implements `SiloConfig.getAssetForSilo` in CVL
function CVLGetAssetForSilo(address _silo) returns address {
    require _silo == silo0_CC || _silo == silo1_CC;  // TODO: change to assert?
    if (_silo == siloConfig_CC._SILO0) {
        return token0_CC;
    } else {
        return token1_CC;
    }
}

function CVLGetSilo(address called) returns address {
    if (called == silo1_CC || called == shareDebtToken1_CC || called == shareProtectedCollateralToken1_CC ) 
        return silo1_CC;
    else
        return silo0_CC;
}

// @title Implements `SiloConfig.getFeesWithAsset` in CVL
function CVLGetFeesWithAsset(address _silo) returns (uint256, uint256, uint256, address) {
    require _silo == silo0_CC || _silo == silo1_CC;  // TODO: change to assert?
    if (_silo == siloConfig_CC._SILO0) {
        return (
            siloConfig_CC._DAO_FEE,
            siloConfig_CC._DEPLOYER_FEE,
            siloConfig_CC._FLASHLOAN_FEE0,
            token0_CC
        );
    } else {
        return (
            siloConfig_CC._DAO_FEE,
            siloConfig_CC._DEPLOYER_FEE,
            siloConfig_CC._FLASHLOAN_FEE1,
            token1_CC
        );
    }
}

/// @title Implements `SiloConfig.getCollateralShareTokenAndAsset` in CVL
/// @notice Assumes each silo is also the collateral share token!
function CVLGetCollateralShareTokenAndAsset(
    address _silo,
    ISilo.CollateralType _collateralType
) returns (address, address) {
    require _silo == silo0_CC || _silo == silo1_CC;  // TODO: change to assert?
    if (_silo == siloConfig_CC._SILO0) {
        if (_collateralType == ISilo.CollateralType.Collateral) {
            return (silo0_CC, token0_CC);
        } else {
            return (shareProtectedCollateralToken0_CC, token0_CC);
        }
    } else {
        if (_collateralType == ISilo.CollateralType.Collateral) {
            return (silo1_CC, token1_CC);
        } else {
            return (shareProtectedCollateralToken1_CC, token1_CC);
        }
    }
}

/// @title Implements `SiloConfig.getDebtShareTokenAndAsset` in CVL
function CVLGetDebtShareTokenAndAsset(address _silo) returns (address, address) {
    require _silo == silo0_CC || _silo == silo1_CC;  // TODO: change to assert?
    if (_silo == siloConfig_CC._SILO0) {
        return (shareDebtToken0_CC, token0_CC);
    } else {
        return (shareDebtToken1_CC, token1_CC);
    }
}
