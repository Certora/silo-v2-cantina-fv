import "./SiloMathLib_SAFE.spec";
methods {
    function SiloMathLib.getCollateralAmountsWithInterest(
        uint256 _collateralAssets,
        uint256 _debtAssets,
        uint256 _rcomp,
        uint256 _daoFee,
        uint256 _deployerFee
    ) internal returns (uint256,uint256,uint256,uint256) => getCollateralAmountsWithInterestCVL(_collateralAssets,_debtAssets,_rcomp,_daoFee,_deployerFee);
}

function getCollateralAmountsWithInterestCVL(uint256 collateralAssets,uint256 debtAssets,uint256 rcomp,uint256 daoFee,uint256 deployerFee) returns (uint256,uint256,uint256,uint256){
    uint256 collateralAssetsWithInterest;
    uint256 debtAssetsWithInterest;
    uint256 daoAndDeployerRevenue;
    uint256 accruedInterest;
    
    debtAssetsWithInterest,accruedInterest = getDebtAmountsWithInterestCVL(debtAssets,rcomp);

    collateralAssetsWithInterest = require_uint256(collateralAssets + accruedInterest); // ignore dao and depolyer fee

    return (collateralAssetsWithInterest,debtAssetsWithInterest,daoAndDeployerRevenue,accruedInterest);
}
