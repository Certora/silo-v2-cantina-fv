//
// SiloConfig.borrowerCollateralSilo mapping
//

persistent ghost mapping (address => address) ghostBorrowerCollateralSilo {
    init_state axiom forall address i. ghostBorrowerCollateralSilo[i] == 0;
    // axiom forall address i. ghostBorrowerCollateralSilo[i] == silo0 || ghostBorrowerCollateralSilo[i] == silo1;
}
//currentContract should be SiloConfigHarness
hook Sload address val currentContract.borrowerCollateralSilo[KEY address i] {
    require(ghostBorrowerCollateralSilo[i] == val);
} 

hook Sstore currentContract.borrowerCollateralSilo[KEY address i] address val {
    ghostBorrowerCollateralSilo[i] = val;
}
