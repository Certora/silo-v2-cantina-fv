methods {
    function SiloConfig.accrueInterestForSilo(address _silo) external => communistInterest(_silo);
    function _.accrueInterestForBothSilos() external => communistInterests() expect void;
    function _.accrueInterestForSilo(address _silo) external => communistInterest(_silo) expect void;
}

persistent ghost address _cachedSiloAddr;

function communistInterest(address _silo) {
    _cachedSiloAddr = _silo;
}
function communistInterests() {
    _cachedSiloAddr = currentContract;
}