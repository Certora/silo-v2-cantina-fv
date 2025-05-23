import "silo0_summaries.spec";
import "../two_silos_methods.spec";

/* Summaries for two silos setup */

methods {
    // ---- `envfree` ----------------------------------------------------------
    function Silo1.config() external returns (address) envfree;
    function Silo1.getTotalAssetsStorage(ISilo.AssetType) external returns(uint256) envfree;
}
