// SPDX-License-Identifier: MIT
pragma solidity >=0.5.0;

/// @dev https://docs.diadata.org/documentation/oracle-documentation/access-the-oracle
interface IDIAOracleV2 {
    function getValue(string memory key) external view returns (uint128 latestPrice, uint128 timestampOfLatestPrice);
}
