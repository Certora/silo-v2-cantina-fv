persistent ghost uint256 _cachedAsset;
persistent ghost uint256 _cachedAssets;
persistent ghost uint256 _cachedTotalAssets;
persistent ghost uint256 _cachedShare;
persistent ghost uint256 _cachedShares;
persistent ghost uint256 _cachedTotalShares;
persistent ghost uint256 _cachedValue;
persistent ghost uint256 _expectedReturn;
persistent ghost uint256 _passedAssets;
persistent ghost uint256 _passedShares;

persistent ghost mathint _previewType;

persistent ghost address _cachedCollateralShareToken;
persistent ghost address _cachedShareToken;
persistent ghost address _cachedToken;
persistent ghost address _cachedDebtAsset;
persistent ghost address _cachedBorrower;
persistent ghost address _cachedRepayer;
persistent ghost address _cachedDepositor;
persistent ghost address _cachedReceiver;
persistent ghost address _cachedOwner;
persistent ghost address _cachedSpender;
persistent ghost address _cachedTarget;

persistent ghost bool _cachedSameAsset;
persistent ghost bool _returnedSuccess;
persistent ghost bool _actionCalled;

persistent ghost Math.Rounding _cachedRoundingType;
persistent ghost ISilo.CollateralType _cachedCollateralType;
persistent ghost ISilo.AssetType _cachedAssetType;
persistent ghost ISilo.CallType _cachedCallType;

// using these for ISilo.WithdrawArgs / BorrowArgs
persistent ghost uint256 _cachedArgsAssets;
persistent ghost uint256 _cachedArgsShares;
persistent ghost address _cachedArgsReceiver;
persistent ghost address _cachedArgsOwner;
persistent ghost address _cachedArgsSpender;
persistent ghost address _cachedArgsBorrower;
persistent ghost ISilo.CollateralType _cachedArgsCollateralType;
