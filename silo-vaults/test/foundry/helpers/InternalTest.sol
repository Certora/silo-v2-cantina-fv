// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.8.28;

import {IERC4626} from "openzeppelin5/interfaces/IERC4626.sol";

import {BaseTest} from "./BaseTest.sol";
import {MetaMorpho, ConstantsLib} from "../../../contracts/MetaMorpho.sol";

contract InternalTest is BaseTest, MetaMorpho {

    constructor()
        MetaMorpho(OWNER, ConstantsLib.MIN_TIMELOCK, address(loanToken), "MetaMorpho Vault", "MM")
    {

    }

    function setUp() public virtual override {
        _createNewMarkets();

        vm.startPrank(OWNER);
        this.setCurator(CURATOR);
        this.setIsAllocator(ALLOCATOR, true);
        vm.stopPrank();

        emit log_named_address("loanToken", address(loanToken));
        emit log_named_address("collateralToken", address(collateralToken));

        vm.startPrank(SUPPLIER);
        loanToken.approve(address(this), type(uint256).max);
        collateralToken.approve(address(this), type(uint256).max);
        vm.stopPrank();
    }

    function _expectedSupplyAssets(IERC4626 _market, address _user)
        internal
        view
        override(BaseTest, MetaMorpho)
        returns (uint256 assets)
    {
        assets = BaseTest._expectedSupplyAssets(_market, _user);
    }
}