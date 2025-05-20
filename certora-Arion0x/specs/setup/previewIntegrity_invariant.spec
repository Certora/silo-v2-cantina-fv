// This invariant is required for some of the rules above,
// and should be proved elsewhere
invariant assetsZeroInterestRateTimestampZero(env e)
    silo0.getCollateralAssets(e) > 0 || silo0.getDebtAssets(e) > 0 =>
    silo0.getSiloDataInterestRateTimestamp() > 0 ;