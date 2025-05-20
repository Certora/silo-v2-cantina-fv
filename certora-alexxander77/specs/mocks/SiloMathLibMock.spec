import "General.spec";

methods {
    function SiloMathLib.convertToShares(
        uint256 _assets,
        uint256 _totalAssets,
        uint256 _totalShares,
        Math.Rounding _rounding,
        ISilo.AssetType _assetType
    ) internal returns (uint256) =>
        assetsToSharesMock(_assets, _totalAssets, _totalShares, _rounding, _assetType);

    function SiloMathLib.convertToAssets(
        uint256 _shares,
        uint256 _totalAssets,
        uint256 _totalShares,
        Math.Rounding _rounding,
        ISilo.AssetType _assetType
    ) internal returns (uint256) =>
        sharesToAssetsMock(_shares, _totalAssets, _totalShares, _rounding, _assetType);
}

function assetsToSharesMock(
    uint256 _assets,
    uint256 _totalAssets,
    uint256 _totalShares,
    Math.Rounding _rounding,
    ISilo.AssetType _assetType
) returns uint256 {
    _cachedAssets = _assets;
    _cachedTotalAssets = _totalAssets;
    _cachedTotalShares = _totalShares;
    _cachedAssetType = _assetType;

    _cachedRoundingType = _rounding;
    return require_uint256(_assets + _totalAssets + _totalShares);
}

function sharesToAssetsMock(
    uint256 _shares,
    uint256 _totalAssets,
    uint256 _totalShares,
    Math.Rounding _rounding,
    ISilo.AssetType _assetType
) returns uint256 {
    _cachedShares = _shares;
    _cachedTotalAssets = _totalAssets;
    _cachedTotalShares = _totalShares;
    _cachedAssetType = _assetType;

    _cachedRoundingType = _rounding;
    return require_uint256(_shares + _totalAssets + _totalShares);
}

