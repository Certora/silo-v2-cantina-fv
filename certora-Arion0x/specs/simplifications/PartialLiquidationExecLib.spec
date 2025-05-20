methods {
    function PartialLiquidationExecLib.getExactLiquidationAmounts(ISiloConfig.ConfigData _collateralConfig,
        ISiloConfig.ConfigData _debtConfig,
        address _user,
        uint256 _maxDebtToCover,
        uint256 _liquidationFee) external returns (uint256,uint256,uint256,bytes4) 
        => CVLGetExactLiquidationAmounts(_collateralConfig,_debtConfig,_user,_maxDebtToCover,_liquidationFee);

    function PartialLiquidationLib.splitReceiveCollateralToLiquidate(uint256 _collateralToLiquidate, uint256 _borrowerProtectedAssets) 
        internal returns (uint256,uint256) => splitReceiveCollateralToLiquidateCVL(_collateralToLiquidate, _borrowerProtectedAssets);
    function PartialLiquidationExecLib.liquidationPreview(SiloSolvencyLib.LtvData memory _ltvData,PartialLiquidationLib.LiquidationPreviewParams memory _params)
    internal returns(uint256,uint256,bytes4) => CVLLiquidationPreview(_ltvData,_params);
}

function CVLGetExactLiquidationAmounts(ISiloConfig.ConfigData _collateralConfig,ISiloConfig.ConfigData _debtConfig,
        address _user,
        uint256 _maxDebtToCover,
        uint256 _liquidationFee) returns (uint256,uint256,uint256,bytes4){
        SiloSolvencyLib.LtvData ltvData;
        ltvData = calculateAssetsDataCVL(_collateralConfig.silo, _debtConfig.silo, _user, 0);

        PartialLiquidationLib.LiquidationPreviewParams _params;
        require _params.collateralLt == _collateralConfig.lt;
        require _params.collateralConfigAsset == _collateralConfig.token;
        require _params.debtConfigAsset == _debtConfig.token;
        require _params.maxDebtToCover == _maxDebtToCover;
        require _params.liquidationTargetLtv == _collateralConfig.liquidationTargetLtv;
        require _params.liquidationFee == _liquidationFee;

        uint256 borrowerCollateralToLiquidate;
        uint256 repayDebtAssets;
        bytes4 customError;

        borrowerCollateralToLiquidate, repayDebtAssets, customError
        = CVLLiquidationPreview(ltvData,_params);

        uint256 withdrawAssetsFromCollateral;
        uint256 withdrawAssetsFromProtected;
        withdrawAssetsFromCollateral, withdrawAssetsFromProtected
        = splitReceiveCollateralToLiquidateCVL(borrowerCollateralToLiquidate,ltvData.borrowerProtectedAssets);
        return (withdrawAssetsFromCollateral,withdrawAssetsFromProtected,repayDebtAssets,customError); 

    }

persistent ghost bytes4 customErrorGhost{
    init_state axiom customErrorGhost == to_bytes4(0);
}
function CVLLiquidationPreview(SiloSolvencyLib.LtvData _ltvData,PartialLiquidationLib.LiquidationPreviewParams _params) returns (uint256,uint256,bytes4){
        uint256 sumOfCollateralAssets = require_uint256(_ltvData.borrowerCollateralAssets + _ltvData.borrowerProtectedAssets);
        bytes4 error;
        require (_ltvData.borrowerDebtAssets != 0 && _params.maxDebtToCover != 0);
        require sumOfCollateralAssets > 0;
        uint256 sumOfBorrowerCollateralValue; uint256 totalBorrowerDebtValue; uint256 ltvBefore;
        sumOfBorrowerCollateralValue,totalBorrowerDebtValue,ltvBefore = calculateLtvCVL(_ltvData, _params.collateralConfigAsset, _params.debtConfigAsset);
        require _params.collateralLt < ltvBefore;
        uint256 receiveCollateralAssets;
        uint256 repayDebtAssets;
        uint256 ltvAfter;

        (receiveCollateralAssets, repayDebtAssets, ltvAfter) = liquidationPreviewHarness(
            ltvBefore,
            sumOfCollateralAssets,
            sumOfBorrowerCollateralValue,
            _ltvData.borrowerDebtAssets,
            totalBorrowerDebtValue,
            _params
        );
        require (receiveCollateralAssets != 0 && repayDebtAssets != 0);
        require customErrorGhost == error;
        return (receiveCollateralAssets,repayDebtAssets,error);
}


function splitReceiveCollateralToLiquidateCVL(uint256 _collateralToLiquidate,uint256 _borrowerProtectedAssets)
        returns (uint256,uint256)
    {
        if (_collateralToLiquidate == 0){
            return (0,0);
        }
        if(_collateralToLiquidate > _borrowerProtectedAssets){
            
            return (require_uint256(_collateralToLiquidate - _borrowerProtectedAssets), _borrowerProtectedAssets);
        }else{
            return (0,_collateralToLiquidate);
        }
    }