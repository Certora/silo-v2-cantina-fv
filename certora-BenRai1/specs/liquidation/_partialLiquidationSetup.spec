import "../setup/CompleteSiloSetup.spec";
import "../silo/unresolved.spec";
import "../simplifications/Oracle_quote_one_UNSAFE.spec";
import "../simplifications/SiloMathLib_SAFE.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec"; //accrueInterest does not change state
import "../simplifications/_Oracle_call_before_quote_UNSAFE.spec"; //to avoide DEFAUL HAVOC for oracle calls
// import "../simplifications/SimplifiedGetCompoundInterestRateAndUpdate_SAFE.spec";
// import "../simplifications/_hooks_no_state_change.spec"; //calls to hooks do not change state


//------------------------------- DEFENITION AND METHODS START ---------------------------------- //i: in video 13:42

    methods {
        // ---- `envfree` ----------------------------------------------------------
        function SiloConfig.getConfig(address _silo) external returns (ISiloConfig.ConfigData memory) envfree;

        //------ summaries----------------------------------------------------------
        function _.repay(uint256 assets, address borrower) external => repayCVL(assets, borrower, calledContract) expect (uint256);
        //redeem (silo0 or silo1)
        function _.redeem(uint256 _shares, address _receiver, address _owner, ISilo.CollateralType _collateralType) external => redeemCVL(_shares, _receiver, _owner, _collateralType ,calledContract) expect (uint256);
        function _._callShareTokenForwardTransferNoChecks(address silo, address borrower, address receiver, uint256 withdrawAssets, address _shareToken, ISilo.AssetType _assetType) internal => _callShareTokenForwardTransferNoChecksCVL(borrower, receiver, withdrawAssets, _shareToken, _assetType) expect uint256;
        function _.safeTransferFrom(address _calledContract, address from, address to, uint256 amount) internal => saveTransferFromCVL(from, to, amount, _calledContract) expect bool;
        function _._fetchConfigs(address _siloConfigCached, address _collateralAsset, address _debtAsset, address _borrower) internal => fetchConfigsCVL(_siloConfigCached, _collateralAsset, _debtAsset, _borrower ) expect (ISiloConfig.ConfigData memory, ISiloConfig.ConfigData memory);
        function _.previewRedeem(uint256 shares, ISilo.CollateralType) external => previewRedeemCVL(shares) expect (uint256);
               

        function PartialLiquidationExecLib.getExactLiquidationAmounts(ISiloConfig.ConfigData _collateralConfig, ISiloConfig.ConfigData _debtConfig, address _user, uint256 _maxDebtToCover, uint256 _liquidationFee) external returns (uint256, uint256, uint256, bytes4) => getExactLiquidationAmountsCVL(_collateralConfig, _debtConfig, _user, _maxDebtToCover, _liquidationFee);
    }

    //summary previewRedeem
        function previewRedeemCVL(uint256 shares) returns uint256{
            return shares;
        }


    //summary _fetchConfigs
        function fetchConfigsCVL(address _siloConfigCached, address _collateralAsset, address _debtAsset, address _borrower) returns (ISiloConfig.ConfigData, ISiloConfig.ConfigData){
            //collateralSilo == silo0, debtSilo == silo1
            ISiloConfig.ConfigData collateralConfig = siloConfig.getConfig(silo0);
            ISiloConfig.ConfigData debtConfig = siloConfig.getConfig(silo1);

            return (collateralConfig, debtConfig);
    }

    //summary saveTransfer
        function saveTransferFromCVL(address from, address to, uint256 amount, address _calledContract) returns bool{
            sentTransferredAssets[_calledContract][from] = require_uint256(sentTransferredAssets[_calledContract][from] + amount);
            receivedTransferredAssets[_calledContract][to] = require_uint256(receivedTransferredAssets[_calledContract][to] + amount);
            return true;
        }

        // calledContract => user(sender) => amount
        ghost mapping (address => mapping (address => uint256)) sentTransferredAssets;
        // calledContract => user(receiver) => amount
    ghost mapping (address => mapping (address => uint256)) receivedTransferredAssets;

    //summary getExactLiquidationAmounts
        function getExactLiquidationAmountsCVL(ISiloConfig.ConfigData _collateralConfig, ISiloConfig.ConfigData _debtConfig, address _borrower, uint256 _maxDebtToCover, uint256 _liquidationFee) returns (uint256, uint256, uint256, bytes4){
            //used values
            usedBorrower = _borrower;
            usedMaxDebtToCover = _maxDebtToCover;
            usedLiquidationFee = _liquidationFee;
            usedCollateralToken = _collateralConfig.token;
            usedDebtToken = _debtConfig.token;

            //make output dependent on the input variables
            uint256 withdrawAssetsFromCollateral = 5648;
            uint256 withdrawAssetsFromProtected = 6482;
            uint256 bonus = _maxDebtToCover == 500 ? 100 : 0;
            uint256 repayDebtAssets = require_uint256(_maxDebtToCover + bonus); //to allow for repayDebtAssets to be bigger than maxDebtToCover

            bytes4 customError = _liquidationFee == 12569 ? to_bytes4(1) : to_bytes4(0);

            return (withdrawAssetsFromCollateral, withdrawAssetsFromProtected, repayDebtAssets, customError);
        }

        //used values
        ghost address usedBorrower;
        ghost uint256 usedMaxDebtToCover;
        ghost uint256 usedLiquidationFee;
        ghost address usedCollateralToken;
        ghost address usedDebtToken;



    //summary _callShareTokenForwardTransferNoChecks
        function _callShareTokenForwardTransferNoChecksCVL(address borrower, address receiver, uint256 withdrawAssets, address _shareToken, ISilo.AssetType _assetType) returns uint256 { 
            reducedWithoutChecks[_shareToken][borrower] = require_uint256(reducedWithoutChecks[_shareToken][borrower] + withdrawAssets);
            increasedWithoutChecks[_shareToken][receiver] = require_uint256(increasedWithoutChecks[_shareToken][receiver] + withdrawAssets);

            return withdrawAssets;    
        }

        //shareToken => tokenType => user => amount
        ghost mapping (address => mapping (address => uint256)) reducedWithoutChecks;
    ghost mapping (address => mapping (address => uint256)) increasedWithoutChecks;

    //summary repay
        function repayCVL(uint256 amount, address borrower, address _calledContract) returns uint256{
            repayedAssets[_calledContract][borrower] = require_uint256(repayedAssets[_calledContract][borrower] + amount);
            repayedAssetsToSilo[_calledContract] = require_uint256(repayedAssetsToSilo[_calledContract] + amount);
            return amount;
        }
        ghost mapping (address => uint256) repayedAssetsToSilo;
    ghost mapping (address => mapping (address => uint256)) repayedAssets;  

    //summary redeem
        function redeemCVL(uint256 shares, address receiver, address owner, ISilo.CollateralType _collateralType, address _calledContract) returns uint256{
            bool collateralType = _collateralType == ISilo.CollateralType.Collateral;
            redeemedAssetsFromSilo[_calledContract] = require_uint256(redeemedAssetsFromSilo[_calledContract] + shares);
            redeemedAssets[_calledContract][collateralType][owner] = require_uint256(redeemedAssets[_calledContract][collateralType][owner] + shares);
            receivedRedeemedAssets[_calledContract][collateralType][receiver] = require_uint256(receivedRedeemedAssets[_calledContract][collateralType][receiver] + shares);
            return shares;
        }

        ghost mapping (address => uint256) redeemedAssetsFromSilo;
        //bool: 0 => protected, 1 => collateral(normal )
        ghost mapping (address => mapping( bool => mapping (address => uint256))) redeemedAssets;
    ghost mapping (address => mapping( bool => mapping (address => uint256))) receivedRedeemedAssets;

    
    


  

    definition ignoredMethod(method f) returns bool =
        f.selector == sig:PartialLiquidationHarness.initialize(address, bytes).selector;

//------------------------------- DEFENITION AND METHODS END ----------------------------------

//------------------------FUNCTIONS START------------------------



    //inital setup for liquidations (silos different, users different)
    function setupLiquidationRules(env e, address borrower) returns (address, address, ISiloConfig.ConfigData, ISiloConfig.ConfigData) {
        nonSceneAddressRequirements(e.msg.sender);
        nonSceneAddressRequirements(borrower);
        require(borrower != e.msg.sender);

        // collateralSilo == silo0, debtSilo == silo1
        address collateralSilo = siloConfig.borrowerCollateralSilo(e, borrower);
        address debtSilo = siloConfig.getDebtSilo(e, borrower);
        require(collateralSilo == silo0);
        require(debtSilo == silo1);
        ISiloConfig.ConfigData collateralConfig = siloConfig.getConfig(e, collateralSilo);
        ISiloConfig.ConfigData debtConfig = siloConfig.getConfig(e, debtSilo);
        return (collateralSilo, debtSilo, collateralConfig, debtConfig);
    }

    //ensure the borrower has only protected shares, no normal collateral shares
    // function borrowerHasOnlyProtectedShares(env e, address borrower) {
    //     address collateralSilo = siloConfig.borrowerCollateralSilo(e, borrower);
    //     require(collateralSilo.balanceOf(e, borrower) == 0);

    // }

//------------------------FUNCTIONS END------------------------

// function fetchConfigsSummary() returns (ISiloConfig.ConfigData, ISiloConfig.ConfigData){
    //     ISiloConfig.ConfigData collateralConfig = siloConfig.getConfig(silo0);
    //     ISiloConfig.ConfigData debtConfig = siloConfig.getConfig(silo1);
    //     return (collateralConfig, debtConfig);
    // }

    // //setup: collateral silo is silo0, debt silo is silo1, user has no protected collateral, only normal collateral
    // function setupFewerPaths(env e, address borrower) returns (address, address){
    //     //collateral silo is silo0
    //     address collateralSilo = siloConfig.borrowerCollateralSilo(e, borrower);
    //     require(collateralSilo == silo0);
    //     //only normal collateral
    //     address protectedShateToken = siloConfig.getConfig(e, collateralSilo).protectedShareToken;
    //     require(protectedShateToken.balanceOf(e, borrower) == 0);
    //     //debt silo is silo1
    //     address debtSilo = siloConfig.getDebtSilo(e, borrower);
    //     require(debtSilo == silo1);

    //     //oracles not set => no quote
    //     address silo0MaxLTVOracle = siloConfig.getConfig(e, silo0).maxLtvOracle;
    //     require(silo0MaxLTVOracle == 0);
    //     address silo0SolvencyOracle = siloConfig.getConfig(e, silo0).solvencyOracle;
    //     require(silo0SolvencyOracle == 0);
    //     address silo1MaxLTVOracle = siloConfig.getConfig(e, silo1).maxLtvOracle;
    //     require(silo1MaxLTVOracle == 0);
    //     address silo1SolvencyOracle = siloConfig.getConfig(e, silo1).solvencyOracle;
    //     require(silo1SolvencyOracle == 0);

    //     //callBeforeQuote = false => no calls
    //     bool silo0CallBeforeQuote = siloConfig.getConfig(e, silo0).callBeforeQuote;
    //     require(!silo0CallBeforeQuote);
    //     bool silo1CallBeforeQuote = siloConfig.getConfig(e, silo1).callBeforeQuote;
    //     require(!silo1CallBeforeQuote);

    //     totalSuppliesMoreThanBalance(borrower);

    //     //assets and shares are 1 to 1 for silo0
    //     address protectedShareTokenSilo0 = siloConfig.getConfig(e, silo0).protectedShareToken;
    //     address debtShareTokenSilo0 = siloConfig.getConfig(e, silo0).debtShareToken;
    //     uint256 protectedShareTokenSilo0TotalSupply = protectedShareTokenSilo0.totalSupply(e);
    //     uint256 collateralShareTokenSilo0TotalSupply = silo0.totalSupply(e);
    //     uint256 debtShareTokenSilo0TotalSupply = debtShareTokenSilo0.totalSupply(e);
    //     uint256 protectedAssetsSilo0;
    //     uint256 collateralAssetsSilo0;
    //     uint256 debtAssetsSilo0;
    //     (_, _, protectedAssetsSilo0, collateralAssetsSilo0, debtAssetsSilo0) = silo0.getSiloStorage(e);
    //     require protectedShareTokenSilo0TotalSupply == protectedAssetsSilo0;
    //     require collateralShareTokenSilo0TotalSupply == collateralAssetsSilo0;
    //     require debtShareTokenSilo0TotalSupply == debtAssetsSilo0;

    //     //assets and shares are 1 to 1 for silo1
    //     address protectedShareTokenSilo1 = siloConfig.getConfig(e, silo1).protectedShareToken;
    //     address debtShareTokenSilo1 = siloConfig.getConfig(e, silo1).debtShareToken;
    //     uint256 protectedShareTokenSilo1TotalSupply = protectedShareTokenSilo1.totalSupply(e);
    //     uint256 collateralShareTokenSilo1TotalSupply = silo1.totalSupply(e);
    //     uint256 debtShareTokenSilo1TotalSupply = debtShareTokenSilo1.totalSupply(e);
    //     uint256 protectedAssetsSilo1;
    //     uint256 collateralAssetsSilo1;
    //     uint256 debtAssetsSilo1;
    //     (_, _, protectedAssetsSilo1, collateralAssetsSilo1, debtAssetsSilo1) = silo1.getSiloStorage(e);
    //     require protectedShareTokenSilo1TotalSupply == protectedAssetsSilo1;
    //     require collateralShareTokenSilo1TotalSupply == collateralAssetsSilo1;
    //     require debtShareTokenSilo1TotalSupply == debtAssetsSilo1;

    //     //hooksBefore == 0 and hooksAfter == 0 => hooks are not called
    //     uint256 hooksBeforeSilo0 = silo0.hooksBeforeHarness(e);
    //     require hooksBeforeSilo0 == 0;
    //     uint256 hooksAfterSilo0 = silo0.hooksAfterHarness(e);
    //     require hooksAfterSilo0 == 0;
    //     uint256 hooksBeforeSilo1 = silo1.hooksBeforeHarness(e);
    //     require hooksBeforeSilo1 == 0;
    //     uint256 hooksAfterSilo1 = silo1.hooksAfterHarness(e);
    //     require hooksAfterSilo1 == 0;

    //     return (collateralSilo, debtSilo);
    // }
