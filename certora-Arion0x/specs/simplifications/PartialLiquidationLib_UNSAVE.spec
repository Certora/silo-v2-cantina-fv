methods {
    function PartialLiquidationLib.liquidationPreview(uint256 _ltvBefore,uint256 _sumOfCollateralAssets,
        uint256 _sumOfCollateralValue,
        uint256 _borrowerDebtAssets,
        uint256 _borrowerDebtValue,
        PartialLiquidationLib.LiquidationPreviewParams memory _params) 
        internal returns (uint256,uint256,uint256) => liquidationPreviewCVL(_ltvBefore,_sumOfCollateralAssets,_sumOfCollateralValue,_borrowerDebtAssets,_borrowerDebtValue,_params);
}

function liquidationPreviewCVL(uint256 _ltvBefore,uint256 _sumOfCollateralAssets,
        uint256 _sumOfCollateralValue,
        uint256 _borrowerDebtAssets,
        uint256 _borrowerDebtValue,
        PartialLiquidationLib.LiquidationPreviewParams _params)
        returns (uint256,uint256,uint256)
    {
        uint256 ANYCollateralToLiquidate;
        uint256 ANYDebtToRepay;
        uint256 ANYLtvAfter;
        return (ANYCollateralToLiquidate,ANYDebtToRepay,ANYLtvAfter);
    }