///
methods {
    // Summarizations:
    function SiloStdLib.getTotalAssetsAndTotalSharesWithInterest(ISiloConfig.ConfigData memory _configData
    ,ISilo.AssetType _assetType)internal returns (uint256,uint256)
     => getTotalAssetsAndTotalSharesCVL(_configData,_assetType);

    function SiloStdLib.getTotalCollateralAssetsWithInterest(address _silo,address _interestRateModel
    ,uint256 _daoFee,uint256 _deployerFee) internal returns (uint256)
    => getTotalCollateralCVL(_silo,_interestRateModel,_daoFee,_deployerFee);

    function SiloStdLib.getTotalDebtAssetsWithInterest(address _silo,address _interestRateModel)
    internal returns (uint256) => getTotalDebtCVL(_silo,_interestRateModel);

    function SiloStdLib.getFeesAndFeeReceiversWithAsset(address _silo) internal 
    returns (address,address,uint256,uint256,address) => getFeesAndFeeReceiverWithAssetCVL(_silo);
}

/*
Summary for getAssetsDataForLtvCalculations()
Doesn't include timestamp dependence - assumes last timestamp is the current timestamp, so
that the total assets values already include the interest.
*/

function getTotalAssetsAndTotalSharesCVL(ISiloConfig.ConfigData _configData,ISilo.AssetType _assetType)
 returns (uint256,uint256){
    uint256 totalAssets;
    uint256 totalShares;
    if (_assetType == ISilo.AssetType.Protected){
        totalAssets = require_uint256(ghostTotalAssets[_configData.silo][PROTECTED_ASSET_TYPE()]);
        totalShares = totalSupplyCVL(_configData.protectedShareToken);
    }else if (_assetType == ISilo.AssetType.Collateral){
        totalAssets = getTotalCollateralCVL( _configData.silo,_configData.interestRateModel,
        _configData.daoFee,_configData.deployerFee);
        totalShares = totalSupplyCVL(_configData.collateralShareToken);
    }else{
        totalAssets = getTotalDebtCVL(_configData.silo,_configData.interestRateModel);
        totalShares = totalSupplyCVL(_configData.debtShareToken);
    }
    return (totalAssets,totalShares);
}

function getTotalCollateralCVL(address _silo,address _interestRateModel,uint256 _daoFee,uint256 _deployerFee)
returns uint256{
    uint256 totalCollateralAssets;
    uint256 collateralAssets;
    uint256 debtAssets;
    collateralAssets = require_uint256(ghostTotalAssets[_silo][COLLATERAL_ASSET_TYPE()]);
    debtAssets = require_uint256(ghostTotalAssets[_silo][DEBT_ASSET_TYPE()]);
    totalCollateralAssets,_,_,_ = getCollateralAmountsWithInterestCVL(collateralAssets,debtAssets,0,_daoFee,_deployerFee); 
    return totalCollateralAssets;
}

function getTotalDebtCVL(address _silo,address _interestRateModel) returns uint256 {
    uint256 totalDebtAssets;
    totalDebtAssets,_ = getDebtAmountsWithInterestCVL(require_uint256(ghostTotalAssets[_silo][DEBT_ASSET_TYPE()]),0);
    return totalDebtAssets;
}

persistent ghost address daoFeeReceiverGhost;
persistent ghost address deployerFeeReceiverGhost;

function getFeesAndFeeReceiverWithAssetCVL(address _silo) returns (address,address,uint256,uint256,address){
    uint256 daoFee;
    uint256 deployerFee;
    address asset;

    daoFee,deployerFee,_,asset = CVLGetFeesWithAsset(_silo);
    nonSceneAddressRequirements(daoFeeReceiverGhost);
    nonSceneAddressRequirements(deployerFeeReceiverGhost);

    require daoFeeReceiverGhost!= deployerFeeReceiverGhost;
    return (daoFeeReceiverGhost,deployerFeeReceiverGhost,daoFee,deployerFee,asset);
}

//CVLGetFeesWithAsset/
