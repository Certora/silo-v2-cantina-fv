methods{
    function SiloSolvencyLib.calculateLtv(SiloSolvencyLib.LtvData memory _ltvData, address _collateralToken, address _debtAsset) internal returns (uint256, uint256, uint256)=> calculateLtvCLV(_ltvData);
}

function calculateLtvCLV(SiloSolvencyLib.LtvData ltvData) returns (uint256 , uint256 , uint256 ) {
    // exchagerate 1 to 1
    uint256 totalCollateralValue = require_uint256(ltvData.borrowerCollateralAssets + ltvData.borrowerProtectedAssets);
    uint256 totalDebtValue = ltvData.borrowerDebtAssets;
    uint256 ltv = require_uint256(totalDebtValue * 10^18 / totalCollateralValue);
    return (totalCollateralValue, totalDebtValue, ltv);
} 



//------------------------------- RULES TEST START ----------------------------------
    // liquidationPreview(ExecLib) returns 0, 0, error if borrowerDebtAssets or maxDebtToCover == 0
    rule borrowerDebtAssetsOrMaxDebtToCoverZero(env e) {
        SiloSolvencyLib.LtvData ltvData;
        PartialLiquidationLib.LiquidationPreviewParams params;

        // function call
        uint256 receiveCollateralAssets;
        uint256 repayDebtAssets;
        bytes4 customError;
        (receiveCollateralAssets, repayDebtAssets, customError) = liquidationPreviewExecHarness(e, ltvData, params);
        
        assert ltvData.borrowerDebtAssets == 0 || params.maxDebtToCover == 0 => receiveCollateralAssets == 0 && repayDebtAssets == 0 && customError != to_bytes4(0);
    }
    
    // liquidationPreview(ExecLib) sumOfCollateralAsset == 0 => noReceiverCollateral, no error and smaller of maxDebtToCover and  _ltvData.borrowerDebtAssets
    rule sumOfCollateralAssetZero(env e) {
        SiloSolvencyLib.LtvData ltvData;
        PartialLiquidationLib.LiquidationPreviewParams params;
        //prevent earlier return
        require(ltvData.borrowerDebtAssets > 0);
        require(params.maxDebtToCover > 0);
        //require
        require(ltvData.borrowerProtectedAssets + ltvData.borrowerCollateralAssets == 0);

        // function call
        uint256 receiveCollateralAssets;
        uint256 repayDebtAssets;
        bytes4 customError;
        (receiveCollateralAssets, repayDebtAssets, customError) = liquidationPreviewExecHarness(e, ltvData, params);

        uint256 minValue = params.maxDebtToCover < ltvData.borrowerDebtAssets ? params.maxDebtToCover : ltvData.borrowerDebtAssets;
        
        assert receiveCollateralAssets == 0 && repayDebtAssets == minValue && customError == to_bytes4(0);
    }

    // liquidationPreview(ExecLib) if targetLtv >= userLtv => return 0, 0, error
    rule userLTVIsGreaterOrEqualThanCollateralLTV(env e) {
        SiloSolvencyLib.LtvData ltvData;
        PartialLiquidationLib.LiquidationPreviewParams params;
        //prevent earlier return
        require(ltvData.borrowerDebtAssets > 0);
        require(params.maxDebtToCover > 0);
        require(ltvData.borrowerProtectedAssets + ltvData.borrowerCollateralAssets > 0);
        //require
        uint256 userLtv;
        (_,_, userLtv) = calculateLtvCLV(ltvData);
        require(params.collateralLt >= userLtv);

        // function call
        uint256 receiveCollateralAssets;
        uint256 repayDebtAssets;
        bytes4 customError;
        (receiveCollateralAssets, repayDebtAssets, customError) = liquidationPreviewExecHarness(e, ltvData, params);
        
        assert receiveCollateralAssets == 0 && repayDebtAssets == 0 && customError != to_bytes4(0);
    }
    
    // liquidationPreview(ExecLib) if returnValues of liquidationPreview == 0 => return 0,0, error
    rule liquidationPreviewZero(env e) {
        SiloSolvencyLib.LtvData ltvData;
        PartialLiquidationLib.LiquidationPreviewParams params;
        //prevent earlier return
        require(ltvData.borrowerDebtAssets > 0);
        require(params.maxDebtToCover > 0);
        uint256 sumCollateralAssets = require_uint256(ltvData.borrowerProtectedAssets + ltvData.borrowerCollateralAssets);
        require(sumCollateralAssets > 0);
        uint256 collateralAssetsValue;
        uint256 debtAssetsValue;
        uint256 userLtv;
        (collateralAssetsValue, debtAssetsValue, userLtv) = calculateLtvCLV(ltvData);
        require(params.collateralLt < userLtv);

        //values
        uint256 receiveCollateralAssetsCalc;
        uint256 repayDebtAssetsCalc; 
        uint256 ltvAfterCalc;
        (receiveCollateralAssetsCalc, repayDebtAssetsCalc, ltvAfterCalc) = liquidationPreviewHarness(e, userLtv, sumCollateralAssets, collateralAssetsValue, ltvData.borrowerDebtAssets, debtAssetsValue, params);

        // function call
        uint256 receiveCollateralAssets;
        uint256 repayDebtAssets;
        bytes4 customError;
        (receiveCollateralAssets, repayDebtAssets, customError) = liquidationPreviewExecHarness(e, ltvData, params);
        
        assert receiveCollateralAssetsCalc == 0 || repayDebtAssetsCalc == 0 => receiveCollateralAssets == 0 && repayDebtAssets == 0 && customError != to_bytes4(0);
    }
    
    // liquidationPreview(ExecLib) return vales from liquidationPreview
    rule liquidationPreviewValues(env e) {
        SiloSolvencyLib.LtvData ltvData;
        PartialLiquidationLib.LiquidationPreviewParams params;
        //prevent earlier return
        require(ltvData.borrowerDebtAssets > 0);
        require(params.maxDebtToCover > 0);
        uint256 sumCollateralAssets = require_uint256(ltvData.borrowerProtectedAssets + ltvData.borrowerCollateralAssets);
        require(sumCollateralAssets > 0);
        uint256 collateralAssetsValue;
        uint256 debtAssetsValue;
        uint256 userLtv;
        (collateralAssetsValue,debtAssetsValue, userLtv) = calculateLtvCLV(ltvData);
        require(params.collateralLt < userLtv);

        //values
        uint256 receiveCollateralAssetsCalc;
        uint256 repayDebtAssetsCalc; 
        uint256 ltvAfterCalc;
        (receiveCollateralAssetsCalc, repayDebtAssetsCalc, ltvAfterCalc) = liquidationPreviewHarness(e, userLtv, sumCollateralAssets, collateralAssetsValue, ltvData.borrowerDebtAssets, debtAssetsValue, params);
        require(receiveCollateralAssetsCalc != 0 && repayDebtAssetsCalc != 0);

        // function call
        uint256 receiveCollateralAssets;
        uint256 repayDebtAssets;
        bytes4 customError;
        (receiveCollateralAssets, repayDebtAssets, customError) = liquidationPreviewExecHarness(e, ltvData, params);
        
        assert receiveCollateralAssets == receiveCollateralAssetsCalc && repayDebtAssets == repayDebtAssetsCalc && customError == to_bytes4(0);
    }

    // splitReceiveCollateralToLiquidate() protectedCollateral is liquidated first
    rule protectedCollateralIsLiquidatedFirst(env e){
        uint256 collateralToLiquidate;
        uint256 borrowerProtectedAssets;
        //prevent earlier return
        require(collateralToLiquidate > 0);
        //require
        require(collateralToLiquidate < borrowerProtectedAssets);

        uint256 withdrawAssetsFromCollateral;
        uint256 withdrawAssetsFromProtected;
        (withdrawAssetsFromCollateral, withdrawAssetsFromProtected) = splitReceiveCollateralToLiquidateHarness(e, collateralToLiquidate, borrowerProtectedAssets);

        assert withdrawAssetsFromCollateral == 0;
    }

    // splitReceiveCollateralToLiquidate() retunrs 0,0, if no collateral to liquidate
    rule noCollateralToLiquidate(env e){
        uint256 collateralToLiquidate;
        uint256 borrowerProtectedAssets;
        //require
        require(collateralToLiquidate == 0);

        uint256 withdrawAssetsFromCollateral;
        uint256 withdrawAssetsFromProtected;
        (withdrawAssetsFromCollateral, withdrawAssetsFromProtected) = splitReceiveCollateralToLiquidateHarness(e, collateralToLiquidate, borrowerProtectedAssets);

        assert withdrawAssetsFromCollateral == 0 && withdrawAssetsFromProtected == 0;
    }

    // splitReceiveCollateralToLiquidate() sum of returns == collateralToLiquidate
    rule sumOfReturnsEqualsCollateralToLiquidate(env e){
        uint256 collateralToLiquidate;
        uint256 borrowerProtectedAssets;
        //prevent earlier return
        require(collateralToLiquidate > 0);

        uint256 withdrawAssetsFromCollateral;
        uint256 withdrawAssetsFromProtected;
        (withdrawAssetsFromCollateral, withdrawAssetsFromProtected) = splitReceiveCollateralToLiquidateHarness(e, collateralToLiquidate, borrowerProtectedAssets);

        assert withdrawAssetsFromCollateral + withdrawAssetsFromProtected == collateralToLiquidate;
    }


