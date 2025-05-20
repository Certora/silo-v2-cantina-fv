/////////////////// METHODS START ///////////////////////
methods{
   function _.totalSupply() external envfree; 
   function _.balanceOf(address user) external envfree; 
   function _.allowance(address owner, address spender) external envfree;
   function _.silo() external envfree;
   function silo1.totalAssetsHarness() external returns (uint256, uint256, uint256)envfree;
   function silo0.totalAssetsHarness() external returns (uint256, uint256, uint256)envfree;
   function shareDebtToken0.receiveAllowance(address,address) external returns (uint256) envfree;
   function shareDebtToken1.receiveAllowance(address,address) external returns (uint256) envfree;
   function _.getFeesWithAsset(address _silo) external envfree;


   function _.getCollateralAndDebtTotalsStorage() external => DISPATCHER(true);
}
//add all view functions to methodes and make them envfree

/////////////////// METHODS END ///////////////////////



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
