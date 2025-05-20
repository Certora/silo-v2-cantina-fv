/////////////////// METHODS START ///////////////////////
methods{
   function _.totalSupply() external envfree; 
   function _.balanceOf(address user) external envfree; 
   function _.allowance(address owner, address spender) external envfree;
   function _.silo() external envfree;
   function Silo0.totalAssetsHarness() external returns (uint256, uint256, uint256)envfree;
   function borrowerCollateralSiloHarness(address) external returns (address) envfree;
   function ltvBelowMaxLtvHarness(address) external returns (bool) envfree;
   function shareDebtToken0.receiveAllowance(address,address) external returns (uint256) envfree;
   function repayHarness(address,uint256,uint256,address) external returns (uint256, uint256)  envfree;
   function totalProtectedAssetsHarness() external returns (uint256) envfree;
   function maxFlashLoan(address) external returns (uint256) envfree;
   function flashFeeHarness(address token, uint256 amount) external returns (uint256) envfree;
   function _.getFeesWithAsset(address _silo) external envfree;
   function hookCallActivatedHarness(uint256 action, bool before) external returns (bool) envfree;
   function hookReceiverHarness(address silo) external returns (address) envfree;
   function getTokenAndAssetsDataHarness(ISilo.AssetType) external returns (address, uint256) envfree; 
   function sumHarness(uint256 a, uint256 b) external returns (uint256) envfree;


   function _.getCollateralAndDebtTotalsStorage() external => DISPATCHER(true);
}
//add all view functions to methodes and make them envfree

/////////////////// METHODS END ///////////////////////

///////////////// DEFINITIONS START /////////////////////
   definition HARNESS_METHODS(method f) returns bool = 
      f.selector == sig:hooksBeforeHarness().selector ||
      f.selector == sig:hooksAfterHarness().selector ||
      f.selector == sig:sumHarness(uint256, uint256).selector ||
      f.selector == sig:userLTVHarness(uint256,uint256).selector ||
      f.selector == sig:isSolventHarness(address,ISilo.AccrueInterestInMemory).selector ||
      f.selector == sig:assetsBorrowerForLTVHarness(ISiloConfig.ConfigData,ISiloConfig.ConfigData,address,ISilo.OracleType,ISilo.AccrueInterestInMemory).selector ||
      f.selector == sig:getSiloStorageHarness().selector ||
      f.selector == sig:getTokenAndAssetsDataHarness(ISilo.AssetType).selector ||
      f.selector == sig:hookReceiverHarness(address).selector ||
      f.selector == sig:hookCallActivatedHarness(uint256,bool).selector ||
      f.selector == sig:flashFeeHarness(address,uint256).selector ||
      f.selector == sig:totalProtectedAssetsHarness().selector ||
      f.selector == sig:repayHarness(address,uint256,uint256,address).selector ||
      f.selector == sig:getSiloDataInterestRateTimestamp().selector ||
      f.selector == sig:getSiloDataDaoAndDeployerRevenue().selector ||
      f.selector == sig:getFlashloanFee0().selector ||
      f.selector == sig:reentrancyGuardEntered().selector ||
      f.selector == sig:getDaoFee().selector ||
      f.selector == sig:getDeployerFee().selector ||
      f.selector == sig:getLTV(address).selector ||
      f.selector == sig:getAssetsDataForLtvCalculations(address).selector ||
      f.selector == sig:getTransferWithChecks().selector ||
      f.selector == sig:getSiloFromStorage().selector ||
      f.selector == sig:totalAssetsHarness().selector ||
      f.selector == sig:borrowerCollateralSiloHarness(address).selector ||
      f.selector == sig:ltvBelowMaxLtvHarness(address).selector ||
      f.selector == sig:getUserAssetsHarness(address).selector ||
      f.selector == sig:convertToAssetsHarness(uint256, ISilo.AssetType).selector;









// definition HARNESS_VIEW_METHODS(method f) returns bool 
//    = HARNESS_METHODS(f) || f.isView;"
  //  f.selector == sig:evcCompatibleAsset().selector
  //  || f.selector == sig:isKnownNonOwnerAccountHarness(address).selector"
//creat a definiton which holds all view
//use definitions for cluster of functions
///////////////// DEFINITIONS END /////////////////////

////////////////// FUNCTIONS START //////////////////////

/// @title `approxSameWithRange` implementation in CVL
/// @notice This will never revert!
function cvlApproxSameWithRange(mathint x, mathint y, uint256 range) returns bool {
    return x > y ? x - y <= range : y-x <= range;
}

////////////////// FUNCTIONS END //////////////////////

///////////////// GHOSTS & HOOKS START //////////////////

///////////////// GHOSTS & HOOKS END //////////////////

///////////////// INITIAL PROPERTIES START /////////////

///////////////// INITIAL PROPERTIES END /////////////
