import "General.spec";
import "SiloMathLibMock.spec";

methods {
    function SiloStdLib.getTotalAssetsAndTotalSharesWithInterest(
        ISiloConfig.ConfigData memory _configData,
        ISilo.AssetType _assetType
    ) internal returns (uint256, uint256) =>
        getTotalAssetsAndTotalSharesWithInterestMock(_configData, _assetType);
}

function getTotalAssetsAndTotalSharesWithInterestMock(
    ISiloConfig.ConfigData _configData,
    ISilo.AssetType _assetType
) returns (uint256, uint256) {
    env e;
    uint256 totalAssets = _passedAssets;
    uint256 totalShares = _passedShares;

    _cachedAssetType = _assetType;
    _cachedAsset = totalAssets;
    _cachedShares = totalShares;
    if (_previewType == 0) {
        _expectedReturn = sharesToAssetsMock(_passedShares, totalAssets, totalShares, ROUNDING_mint(e), _assetType);
    } else if (_previewType == 1) {
        _expectedReturn = assetsToSharesMock(_passedAssets, totalAssets, totalShares, ROUNDING_deposit(e), _assetType);
    } else if (_previewType == 2) {
        _expectedReturn = sharesToAssetsMock(_passedShares, totalAssets, totalShares, ROUNDING_redeem(e), _assetType);
    } else if (_previewType == 3) {
        _expectedReturn = assetsToSharesMock(_passedAssets, totalAssets, totalShares, ROUNDING_withdraw(e), _assetType);
    }
    return (totalAssets, totalShares);
}