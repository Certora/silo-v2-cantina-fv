methods {

    function _.callMaxLtvOracleBeforeQuote(ISiloConfig.ConfigData memory _config) internal 
            => callMaxLtvOracleBeforeQuote__noStateChange() expect void;

    function _.callSolvencyOracleBeforeQuote(ISiloConfig.ConfigData memory _config) internal 
            => callSolvencyOracleBeforeQuote__noStateChange() expect void;

}

function callMaxLtvOracleBeforeQuote__noStateChange() {
   // no state change but needed to avoid DEVAULT HAVOC
}

function callSolvencyOracleBeforeQuote__noStateChange() {
    // no state change but needed to avoid DEVAULT HAVOC
}