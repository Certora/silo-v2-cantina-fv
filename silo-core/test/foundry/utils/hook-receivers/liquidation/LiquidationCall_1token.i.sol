// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.20;

import {Test} from "forge-std/Test.sol";

import {IERC20} from "openzeppelin5/token/ERC20/IERC20.sol";

import {ISiloConfig} from "silo-core/contracts/interfaces/ISiloConfig.sol";
import {ISilo} from "silo-core/contracts/interfaces/ISilo.sol";
import {IPartialLiquidation} from "silo-core/contracts/interfaces/IPartialLiquidation.sol";
import {IShareToken} from "silo-core/contracts/interfaces/IShareToken.sol";
import {IInterestRateModel} from "silo-core/contracts/interfaces/IInterestRateModel.sol";
import {SiloLensLib} from "silo-core/contracts/lib/SiloLensLib.sol";
import {Hook} from "silo-core/contracts/lib/Hook.sol";
import {AssetTypes} from "silo-core/contracts/lib/AssetTypes.sol";

import {SiloLittleHelper} from "../../../_common/SiloLittleHelper.sol";
import {MintableToken} from "../../../_common/MintableToken.sol";


/*
    forge test -vv --ffi --mc LiquidationCall1TokenTest
*/
contract LiquidationCall1TokenTest is SiloLittleHelper, Test {
    using SiloLensLib for ISilo;

    address constant BORROWER = address(0x123);
    uint256 constant COLLATERAL = 10e18;
    uint256 constant DEBT = 7.5e18;
    bool constant SAME_TOKEN = true;

    ISiloConfig siloConfig;

    event LiquidationCall(address indexed liquidator, bool receiveSToken);
    error SenderNotSolventAfterTransfer();

    function setUp() public {
        siloConfig = _setUpLocalFixture();

        vm.prank(BORROWER);
        token0.mint(BORROWER, COLLATERAL);

        vm.prank(BORROWER);
        token0.approve(address(silo0), COLLATERAL);

        vm.prank(BORROWER);
        silo0.leverageSameAsset(
            COLLATERAL,
            DEBT,
            BORROWER,
            ISilo.CollateralType.Collateral
        );

        assertEq(token0.balanceOf(address(this)), 0, "liquidation should have no collateral");
        assertEq(token0.balanceOf(address(silo0)), COLLATERAL - DEBT, "silo0 has only 2.5 debt token (10 - 7.5)");

        ISiloConfig.ConfigData memory silo0Config = siloConfig.getConfig(address(silo0));

        assertEq(silo0Config.liquidationFee, 0.05e18, "liquidationFee1");
    }

    /*
    forge test -vv --ffi --mt test_liquidationCall_UnexpectedDebtToken
    */
    function test_liquidationCall_UnexpectedDebtToken_1token() public {
        uint256 debtToCover = 1;
        bool receiveSToken;

        vm.expectRevert(IPartialLiquidation.UnexpectedDebtToken.selector);
        partialLiquidation.liquidationCall(address(token0), address(token1), BORROWER, debtToCover, receiveSToken);
    }

    /*
    forge test -vv --ffi --mt test_liquidationCall_NoDebtToCover_whenUserSolvent
    */
    function test_liquidationCall_NoDebtToCover_whenUserSolvent_1token() public {
        uint256 debtToCover = 1e18;
        bool receiveSToken;

        vm.expectRevert(IPartialLiquidation.NoDebtToCover.selector);

        partialLiquidation.liquidationCall(address(token0), address(token0), BORROWER, debtToCover, receiveSToken);

        _assertLiquidationModuleDoNotHaveTokens();
    }

    /*
    forge test -vv --ffi --mt test_liquidationCall_revert_noDebt
    */
    function test_liquidationCall_revert_noDebt_1token() public {
        address userWithoutDebt = address(1);
        uint256 debtToCover = 1e18;
        bool receiveSToken;

        ISiloConfig.ConfigData memory debt;

        (, debt) = siloConfig.getConfigs(userWithoutDebt);

        assertTrue(debt.silo == address(0), "we need user without debt for this test");

        vm.expectRevert(IPartialLiquidation.UserIsSolvent.selector);

        partialLiquidation.liquidationCall(
            address(token0), address(token0), userWithoutDebt, debtToCover, receiveSToken
        );

        _assertLiquidationModuleDoNotHaveTokens();
    }

    /*
    forge test -vv --ffi --mt test_liquidationCall_self
    */
    function test_liquidationCall_self_1token() public {
        uint256 debtToCover = 1e18;
        bool receiveSToken;

        token0.mint(BORROWER, debtToCover);
        vm.prank(BORROWER);
        token0.approve(address(partialLiquidation), debtToCover);

        vm.expectEmit(true, true, true, true);
        emit LiquidationCall(BORROWER, receiveSToken);

        vm.prank(BORROWER);

        partialLiquidation.liquidationCall(address(token0), address(token0), BORROWER, debtToCover, receiveSToken);

        _assertLiquidationModuleDoNotHaveTokens();
    }

    /*
    forge test -vv --ffi --mt test_liquidationCall_partial
    */
    function test_liquidationCall_partial_1token() public {
        uint256 debtToCover = 1e5; // tiny partial liquidation at begin

        ISiloConfig.ConfigData memory debtConfig = siloConfig.getConfig(address(silo0));

        (, uint64 interestRateTimestamp0) = silo0.siloData();
        (, uint64 interestRateTimestamp1) = silo1.siloData();
        assertEq(interestRateTimestamp0, 1, "interestRateTimestamp0 is 1 because we deposited and borrow same asset");
        assertEq(block.timestamp, 1, "block.timestamp");

        assertEq(
            interestRateTimestamp1,
            0,
            "interestRateTimestamp1 is 0 because because on borrow same asset we accrue interest only for one silo"
        );

        (
            uint256 collateralToLiquidate, uint256 debtToRepay, bool sTokenRequired
        ) = partialLiquidation.maxLiquidation(BORROWER);

        assertTrue(!sTokenRequired, "sTokenRequired not required when solvent");
        assertEq(collateralToLiquidate, 0, "no collateralToLiquidate yet");
        assertEq(debtToRepay, 0, "no debtToRepay yet");

        emit log_named_decimal_uint("[test] LTV", silo0.getLtv(BORROWER), 16);

        // move forward with time so we can have interests
        uint256 timeForward = 57 days;
        vm.warp(block.timestamp + timeForward);

        (collateralToLiquidate, debtToRepay, sTokenRequired) = partialLiquidation.maxLiquidation(BORROWER);
        assertTrue(sTokenRequired, "sTokenRequired required, because we have collateral only from borrower");
        assertGt(collateralToLiquidate, 0, "expect collateralToLiquidate");
        assertGt(debtToRepay, debtToCover, "expect debtToRepay");
        emit log_named_decimal_uint("[test] max debtToRepay", debtToRepay, 18);
        emit log_named_decimal_uint("[test] debtToCover", debtToCover, 18);

        vm.expectCall(address(silo0), abi.encodeWithSelector(ISilo.accrueInterestForConfig.selector));
        vm.expectCall(
            address(debtConfig.interestRateModel),
            abi.encodeWithSelector(IInterestRateModel.getCompoundInterestRateAndUpdate.selector)
        );

        emit log_named_decimal_uint("[test] LTV after interest", silo0.getLtv(BORROWER), 16);
        assertEq(silo0.getLtv(BORROWER), 89_4686387330403830, "LTV after interest");
        assertLt(silo0.getLtv(BORROWER), 0.90e18, "expect LTV to be below dust level");
        assertFalse(silo0.isSolvent(BORROWER), "expect BORROWER to be insolvent");

        token0.mint(address(this), debtToCover);
        token0.approve(address(partialLiquidation), debtToCover);

        // uint256 collateralWithFee = debtToCover + 0.05e5; // too deep

        { // too deep
            // repay debt liquidator -> hook
            vm.expectCall(
                address(token0),
                abi.encodeWithSelector(IERC20.transferFrom.selector, address(this), address(partialLiquidation), debtToCover)
            );

            // repay debt hook -> silo
            vm.expectCall(
                address(token0),
                abi.encodeWithSelector(IERC20.transferFrom.selector, address(partialLiquidation), address(silo0), debtToCover)
            );

            // collateral with fee from silo to liquidator
            vm.expectCall(
                address(token0),
                abi.encodeWithSelector(IERC20.transfer.selector, address(this), debtToCover + 0.05e5 - 1)
            );

            (
                uint256 withdrawAssetsFromCollateral, uint256 repayDebtAssets
            ) = partialLiquidation.liquidationCall(
                address(token0), address(token0), BORROWER, debtToCover, false /* receiveSToken */
            );

            emit log_named_decimal_uint("[test] withdrawAssetsFromCollateral", withdrawAssetsFromCollateral, 18);
            emit log_named_decimal_uint("[test] repayDebtAssets", repayDebtAssets, 18);
        }

        { // too deep
            emit log_named_decimal_uint("[test] LTV after small liquidation", silo0.getLtv(BORROWER), 16);
            assertEq(silo0.getLtv(BORROWER), 89_4686387330403375, "LTV after small liquidation");
            assertGt(silo0.getLtv(BORROWER), 0, "expect user to be still insolvent after small partial liquidation");
            assertTrue(!silo0.isSolvent(BORROWER), "expect BORROWER to be insolvent after small partial liquidation");

            uint256 roundingError = 1; // because of liquidation toShares conversion

            assertEq(
                token0.balanceOf(address(this)),
                debtToCover + 0.05e5 - roundingError,
                "liquidator should get collateral + 5% fee"
            );

            assertEq(
                token0.balanceOf(address(silo0)),
                COLLATERAL - DEBT - (debtToCover + 0.05e5) + debtToCover + roundingError,
                "collateral should be transfer to liquidator AND debt token should be repayed"
            );

            assertEq(
                silo0.getCollateralAssets(),
                COLLATERAL - 0.05e5 + 3_298470185392175403 + roundingError,
                "total collateral - liquidation fee + interest"
            );

            assertEq(
                silo0.getDebtAssets(),
                DEBT + 3_298470185392175403 + 1_099490061797425134,
                "debt token + interest + daoFee"
            );
        }

        { // too deep
            (, uint64 interestRateTimestamp0After) = silo0.siloData();
            (, uint64 interestRateTimestamp1After) = silo1.siloData();

            assertEq(interestRateTimestamp0 + timeForward, interestRateTimestamp0After, "interestRateTimestamp #0");
            assertGt(interestRateTimestamp1After, 0, "interestRateTimestamp #1 (because of withdraw)");

            (collateralToLiquidate, debtToRepay, sTokenRequired) = partialLiquidation.maxLiquidation(BORROWER);
            assertTrue(sTokenRequired, "sTokenRequired required, because tiny liquidation 1e5 did not change anything");
            assertGt(collateralToLiquidate, 0, "expect collateralToLiquidate after partial liquidation");
            assertGt(debtToRepay, 0, "expect partial debtToRepay after partial liquidation");

            assertLt(
                debtToRepay,
                DEBT + 3_298470185392175403 + 1_099490061797425134,
                "expect partial debtToRepay to be less than full"
            );

            token0.mint(address(this), debtToRepay);
            token0.approve(address(partialLiquidation), debtToRepay);

            // repay debt liquidator -> hook
            vm.expectCall(
                address(token0),
                abi.encodeWithSelector(IERC20.transferFrom.selector, address(this), address(partialLiquidation), 8_765593674025871302)
            );

            // repay debt hook -> silo
            vm.expectCall(
                address(token0),
                abi.encodeWithSelector(IERC20.transferFrom.selector, address(partialLiquidation), address(silo0), 8_765593674025871302)
            );

            // collateral with fee from silo to liquidator
            vm.expectCall(
                address(token0),
                abi.encodeWithSelector(IERC20.transfer.selector, address(this), 9_203873357727164866)
            );

            (
                uint256 withdrawAssetsFromCollateral, uint256 repayDebtAssets
            ) = partialLiquidation.liquidationCall(
                address(token0), address(token0), BORROWER, 2 ** 128, false /* receiveSToken */
            );

            emit log_named_decimal_uint("[test] withdrawAssetsFromCollateral2", withdrawAssetsFromCollateral, 18);
            emit log_named_decimal_uint("[test] repayDebtAssets2", repayDebtAssets, 18);

            emit log_named_decimal_uint("[test] LTV after max liquidation", silo0.getLtv(BORROWER), 16);
            assertGt(silo0.getLtv(BORROWER), 0, "expect some LTV after partial liquidation");
            assertTrue(silo0.isSolvent(BORROWER), "expect BORROWER to be solvent");
        }

        _assertLiquidationModuleDoNotHaveTokens();
    }

    /*
    forge test -vv --ffi --mt test_liquidationCall_DebtToCoverTooSmall_1token
    */
    function test_liquidationCall_DebtToCoverTooSmall_1token() public {
        // move forward with time so we can have interests
        uint256 timeForward = 75 days;
        vm.warp(block.timestamp + timeForward);
        assertLt(silo0.getLtv(BORROWER), 1e18, "expect insolvency, but not bad debt");
        assertGt(silo0.getLtv(BORROWER), 0.98e18, "expect hi LTV so we force full liquidation");

        (
            uint256 collateralToLiquidate, uint256 debtToRepay, bool sTokenRequired
        ) = partialLiquidation.maxLiquidation(BORROWER);

        // -1 for rounding policy
        // +2 for underestimation
        assertEq(silo0.getLiquidity() - 1, collateralToLiquidate - debtToRepay + 2, "without bad debt there is some liquidity");
        assertTrue(sTokenRequired, "sTokenRequired required, because 'some liquidity' is not enough");
        emit log_named_decimal_uint("collateralToLiquidate", collateralToLiquidate, 18);
        emit log_named_decimal_uint("debtToRepay", debtToRepay, 18);
        assertEq(debtToRepay, silo0.getDebtAssets(), "debtToRepay is max debt when we forcing full liquidation");

        uint256 debtToCover = debtToRepay - 1; // -1 to check if tx reverts with DebtToCoverTooSmall
        bool receiveSToken;

        vm.expectRevert(IPartialLiquidation.DebtToCoverTooSmall.selector);
        partialLiquidation.liquidationCall(address(token0), address(token0), BORROWER, debtToCover, receiveSToken);

        _assertLiquidationModuleDoNotHaveTokens();
    }

    /*
    forge test -vv --ffi --mt test_liquidationCall_badDebt_partial_1token_noDepositors
    */
    function test_liquidationCall_badDebt_partial_1token_noDepositors() public {
        uint256 debtToCover = 100e18;
        bool receiveSToken;

        ISiloConfig.ConfigData memory debtConfig = siloConfig.getConfig(address(silo1));

        (, uint64 interestRateTimestamp0) = silo0.siloData();
        (, uint64 interestRateTimestamp1) = silo1.siloData();

        // move forward with time so we can have interests

        uint256 timeForward = 120 days;
        vm.warp(block.timestamp + timeForward);
        // expected debt should grow from 7.5 => ~55
        emit log_named_decimal_uint("user ltv", silo0.getLtv(BORROWER), 16);
        assertGt(silo0.getLtv(BORROWER), 1e18, "expect bad debt");

        uint256 collateralToLiquidate;
        uint256 debtToRepay;

        { // too deep
            bool sTokenRequired;
            (collateralToLiquidate, debtToRepay, sTokenRequired) = partialLiquidation.maxLiquidation(BORROWER);
            assertTrue(sTokenRequired, "sTokenRequired required, because no depositors");
        }

        assertEq(silo0.getLiquidity(), 0, "with bad debt and no depositors, no liquidity");
        emit log_named_decimal_uint("collateralToLiquidate", collateralToLiquidate, 18);
        emit log_named_decimal_uint("debtToRepay", debtToRepay, 18);
        assertEq(debtToRepay, silo0.getDebtAssets(), "debtToRepay is max debt");
        assertEq(
            collateralToLiquidate / 100,
            silo0.getCollateralAssets() / 100,
            "we should get all collateral (precision 100)"
        );

        uint256 interest = 48_313643495964160590;
        assertEq(debtToRepay - DEBT, interest, "interests on debt");

        vm.expectCall(address(silo0), abi.encodeWithSelector(ISilo.accrueInterestForConfig.selector));
        vm.expectCall(
            address(debtConfig.interestRateModel),
            abi.encodeWithSelector(IInterestRateModel.getCompoundInterestRateAndUpdate.selector)
        );

        // same token liquidation, so `collateralConfig.interestRateModel` is the same as for debt
        // vm.expectCall(
        //    address(collateralConfig.interestRateModel),
        //     abi.encodeWithSelector(IInterestRateModel.getCompoundInterestRateAndUpdate.selector)
        // );

        assertEq(token0.balanceOf(address(this)), 0, "liquidator has no tokens");

        token0.mint(address(this), debtToCover);
        token0.approve(address(partialLiquidation), debtToCover);

        assertEq(silo0.convertToAssets(1), 4, "rounding error atm");

        partialLiquidation.liquidationCall(address(token0), address(token0), BORROWER, debtToCover, receiveSToken);

        assertTrue(silo0.isSolvent(BORROWER), "user is solvent after liquidation");
        assertTrue(silo1.isSolvent(BORROWER), "user is solvent after liquidation");

        assertEq(debtConfig.daoFee, 0.15e18, "just checking on daoFee");
        assertEq(debtConfig.deployerFee, 0.10e18, "just checking on deployerFee");

        { // too deep
            uint256 dust = 4;
            // newest liquidation process is based on sToken transfer and recalculating shares from assets,
            // this leads to less assets in result, rounding error for this test is 5
            uint256 roundingError = 5;

            { // too deep
                uint256 daoAndDeployerFees = interest * (0.15e18 + 0.10e18) / 1e18; // dao fee + deployer fee

                assertEq(
                    token0.balanceOf(address(silo0)),
                    daoAndDeployerFees + dust + roundingError,
                    "all silo collateral should be transfer to liquidator, fees left"
                );
            }

            assertEq(
                token0.balanceOf(address(this)),
                debtToCover - debtToRepay + collateralToLiquidate - roundingError + 2, /* +2 for underestimate */
                "liquidator should get all borrower collateral, no fee because of bad debt"
            );

            silo0.withdrawFees();

            assertEq(token0.balanceOf(address(silo0)), dust + roundingError, "no balance after withdraw fees (except dust!)");
            assertEq(IShareToken(debtConfig.debtShareToken).totalSupply(), 0, "expected debtShareToken burned");
            assertEq(IShareToken(debtConfig.collateralShareToken).totalSupply(), 0, "expected collateralShareToken burned");
            assertEq(silo0.total(AssetTypes.COLLATERAL), dust + roundingError, "storage AssetType.Collateral");
            assertEq(silo0.getDebtAssets(), 0, "total debt == 0");
            assertEq(silo0.getCollateralAssets(), dust + roundingError, "total collateral == 4+5, dust!");
            assertEq(silo0.getLiquidity(), dust + roundingError, "getLiquidity == 4+5, dust!");
        }

        { // too deep
            (, uint64 interestRateTimestamp0After) = silo0.siloData();
            (, uint64 interestRateTimestamp1After) = silo1.siloData();

            assertEq(interestRateTimestamp0 + timeForward, interestRateTimestamp0After, "interestRateTimestamp #0");

            // we executing accrue on other silo?
            // on new liquidation, sToken is transfer to liquidation module and module has no debt
            // so on withdraw, when we getting configs, we not getting configs for borrower but for module
            // so debt and collateral configs are by default different and we call accrue
            assertLt(interestRateTimestamp1, interestRateTimestamp1After, "interestRateTimestamp #1");
        }

        _assertLiquidationModuleDoNotHaveTokens();
    }

    /*
    forge test -vv --ffi --mt test_liquidationCall_badDebt_partial_1token_withDepositors
    */
    function test_liquidationCall_badDebt_partial_1token_withDepositors() public {
        _deposit(1e18, makeAddr("depositor"));

        uint256 debtToCover = 100e18;
        bool receiveSToken;

        ISiloConfig.ConfigData memory debtConfig = siloConfig.getConfig(address(silo0));

        (, uint64 interestRateTimestamp0) = silo0.siloData();
        (, uint64 interestRateTimestamp1) = silo1.siloData();

        // move forward with time so we can have interests

        uint256 timeForward = 150 days;
        vm.warp(block.timestamp + timeForward);
        // expected debt should grow from 7.5 => ~73
        emit log_named_decimal_uint("user ltv", silo0.getLtv(BORROWER), 16);
        assertGt(silo0.getLtv(BORROWER), 1e18, "expect bad debt");

        uint256 collateralToLiquidate;
        uint256 debtToRepay;

        { // too deep
            bool sTokenRequired;
            (collateralToLiquidate, debtToRepay, sTokenRequired) = partialLiquidation.maxLiquidation(BORROWER);
            assertEq(silo0.getLiquidity(), 0, "bad debt too big to have liquidity");
            assertTrue(sTokenRequired, "sTokenRequired required");
        }

        { // too deep
            address depositor = makeAddr("depositor");
            vm.prank(depositor);
            vm.expectRevert();
            silo0.redeem(1, depositor, depositor);
        }

        emit log_named_decimal_uint("collateralToLiquidate", collateralToLiquidate, 18);
        emit log_named_decimal_uint("debtToRepay", debtToRepay, 18);

        assertEq(debtToRepay, silo0.getDebtAssets(), "debtToRepay is max debt");
        assertEq(
            collateralToLiquidate + 2, // +2 to compensate underestimation
            (silo0.getCollateralAssets() - (1e18 + 4_491873366236992444)),
            "we should get all collateral (except depositor deposit + fees), (precision 100)"
        );

        uint256 interest = 65_880809371475889105;
        assertEq(debtToRepay - DEBT, interest, "interests on debt");

        vm.expectCall(address(silo0), abi.encodeWithSelector(ISilo.accrueInterestForConfig.selector));
        vm.expectCall(
            address(debtConfig.interestRateModel),
            abi.encodeWithSelector(IInterestRateModel.getCompoundInterestRateAndUpdate.selector)
        );

        // same token liquidation, so `collateralConfig.interestRateModel` is the same as for debt
        // vm.expectCall(
        //    address(collateralConfig.interestRateModel),
        //    abi.encodeWithSelector(IInterestRateModel.getCompoundInterestRateAndUpdate.selector)
        // );

        assertEq(token0.balanceOf(address(this)), 0, "liquidator has no tokens");

        token0.mint(address(this), debtToCover);
        token0.approve(address(partialLiquidation), debtToCover);

        partialLiquidation.liquidationCall(address(token0), address(token0), BORROWER, debtToCover, receiveSToken);

        assertTrue(silo0.isSolvent(BORROWER), "user is solvent after liquidation");
        assertTrue(silo0.isSolvent(BORROWER), "user is solvent after liquidation");

        assertEq(debtConfig.daoFee, 0.15e18, "just checking on daoFee");
        assertEq(debtConfig.deployerFee, 0.10e18, "just checking on deployerFee");

        { // too deep
            uint256 daoAndDeployerFees = interest * (0.15e18 + 0.10e18) / 1e18; // dao fee + deployer fee
            uint256 deposit = 1e18 + 4_491873366236992444;
            // newest liquidation process is based on sToken transfer and recalculating shares from assets,
            // this leads to less assets in result, rounding error for this test is 5
            // uint256 roundingError = 5; too deep

            assertEq(
                token0.balanceOf(address(this)),
                debtToCover - debtToRepay + collateralToLiquidate - 5 + 2 /* - roundingError + underestimate */,
                "liquidator should get all borrower collateral, no fee because of bad debt"
            );

            assertEq(
                token0.balanceOf(address(silo0)),
                daoAndDeployerFees + deposit + 5 /* roundingError */,
                "all silo collateral should be transfer to liquidator, fees left and deposit"
            );

            silo0.withdrawFees();

            assertEq(token0.balanceOf(address(silo0)), deposit + 5 /* roundingError */, "no additional balance after withdraw fees");
            assertEq(silo0.getDebtAssets(), 0, "total debt == 0");
            assertEq(silo0.getCollateralAssets(), deposit + 5 /* roundingError */, "total collateral == additional deposit");
            assertEq(silo0.getLiquidity(), deposit + 5 /* roundingError */, "getLiquidity == deposit");
        }

        { // too deep
            (, uint64 interestRateTimestamp0After) = silo0.siloData();
            (, uint64 interestRateTimestamp1After) = silo1.siloData();

            assertEq(interestRateTimestamp0 + timeForward, interestRateTimestamp0After, "interestRateTimestamp #0");
            assertLt(interestRateTimestamp1, interestRateTimestamp1After, "interestRateTimestamp #1");
        }

        { // to deep
            address depositor = makeAddr("depositor");
            vm.prank(depositor);
            silo0.redeem(1e18, depositor, depositor);
            assertEq(token0.balanceOf(depositor), 1e18 + 4_491873366236992444 - 5, "depositor can withdraw, left deposit");
            assertEq(token0.balanceOf(address(silo0)), 5 + 5 /* roundingError */, "silo should be empty (just dust left)");
        }

        _assertLiquidationModuleDoNotHaveTokens();
    }

    /*
    forge test -vv --ffi --mt test_liquidationCall_badDebt_full_withToken
    */
    function test_liquidationCall_badDebt_full_withToken_1token() public {
        bool receiveSToken;
        address liquidator = makeAddr("liquidator");
        uint256 dust = 2 + 3; // +3 rounding error

        // repay
        vm.expectCall(
            address(token0),
            abi.encodeWithSelector(IERC20.transferFrom.selector, address(partialLiquidation), address(silo0), 30_372197335919815515)
        );

        // redeem collateral
        vm.expectCall(
            address(token0),
            abi.encodeWithSelector(IERC20.transfer.selector, liquidator, 27_154148001939861632)
        );

        _liquidationCall_badDebt_full(receiveSToken);

        assertEq(silo0.getCollateralAssets(), dust, "total collateral (dust)");

        uint256 interest = 30_372197335919815515 - 7.5e18;
        uint256 daoAndDeployerFees = interest * (0.15e18 + 0.10e18) / 1e18; // dao fee + deployer fee

        assertEq(
            token0.balanceOf(address(silo0)),
            daoAndDeployerFees + dust,
            "silo collateral should be transfer to liquidator, fees left"
        );

        _assertLiquidationModuleDoNotHaveTokens();
    }

    /*
    forge test -vv --ffi --mt test_liquidationCall_badDebt_full_withSToken
    */
    function test_liquidationCall_badDebt_full_withSToken_1token() public {
        bool receiveSToken = true;
        address liquidator = makeAddr("liquidator");

        ISiloConfig.ConfigData memory collateralConfig = siloConfig.getConfig(address(silo0));

        // IERC20(debtConfig.token).safeTransferFrom(msg.sender, address(this), repayDebtAssets);
        vm.expectCall(
            address(token0),
            abi.encodeWithSelector(
                IERC20.transferFrom.selector, liquidator, address(partialLiquidation), 30372197335919815515
            )
        );

        // ISilo(debtConfig.silo).repay(repayDebtAssets, _borrower);
        vm.expectCall(
            address(token0),
            abi.encodeWithSelector(
                IERC20.transferFrom.selector, address(partialLiquidation), address(silo0), 30372197335919815515
            )
        );

        // shares -> liquidator (because of receive sToken)
        vm.expectCall(
            collateralConfig.collateralShareToken,
            abi.encodeWithSelector(
                IShareToken.forwardTransferFromNoChecks.selector, BORROWER, liquidator, COLLATERAL - 1
            )
        );

        _liquidationCall_badDebt_full(receiveSToken);

        assertEq(
            IShareToken(collateralConfig.collateralShareToken).balanceOf(liquidator),
            COLLATERAL - 1,
            "liquidator should have s-collateral, because of sToken"
        );

        assertEq(
            IShareToken(collateralConfig.collateralShareToken).balanceOf(BORROWER),
            1,
            "BORROWER should have NO s-collateral"
        );

        _assertLiquidationModuleDoNotHaveTokens();
    }

    function _liquidationCall_badDebt_full(bool _receiveSToken) internal {
        uint256 debtToCover = 100e18;
        address liquidator = makeAddr("liquidator");

        // move forward with time so we can have interests

        uint256 timeForward = 100 days;
        vm.warp(block.timestamp + timeForward);

        assertGt(silo0.getLtv(BORROWER), 1e18, "[_liquidationCall_badDebt_full] expect bad debt");

        uint256 maxRepay = silo0.maxRepay(BORROWER);
        uint256 interest = 30_372197335919815515 - 7.5e18;
        uint256 daoAndDeployerFees = interest * (0.15e18 + 0.10e18) / 1e18; // dao fee + deployer fee

        (
            uint256 collateralToLiquidate, uint256 debtToRepay, bool sTokenRequired
        ) = partialLiquidation.maxLiquidation(BORROWER);

        emit log_named_decimal_uint("[test] getDebtAssets", silo0.getDebtAssets(), 18);
        assertTrue(sTokenRequired, "sTokenRequired required, because we have only borrower collateral here");

        assertEq(
            collateralToLiquidate + 4, // +2 dust +2 underestimation
            silo0.getCollateralAssets(),
            "expect full collateralToLiquidate on bad debt"
        );

        assertEq(debtToRepay, maxRepay, "debtToRepay == maxRepay");
        assertEq(debtToRepay, silo0.getDebtAssets(), "debtToRepay == all debt");

        token0.mint(liquidator, debtToCover);
        vm.prank(liquidator);
        token0.approve(address(partialLiquidation), debtToCover);

        emit log_named_decimal_uint("[test] debtToCover", debtToCover, 18);

        vm.prank(liquidator);
        partialLiquidation.liquidationCall(address(token0), address(token0), BORROWER, debtToCover, _receiveSToken);

        maxRepay = silo0.maxRepay(BORROWER);
        assertEq(maxRepay, 0, "there will be NO leftover for same token");

        if (_receiveSToken) {
            assertEq(
                token0.balanceOf(address(silo0)),
                COLLATERAL - DEBT + debtToRepay,
                "[_receiveSToken] all collateral available after repay"
            );
        } else {
            assertEq(
                token0.balanceOf(address(silo0)) - 5, // dust(2) + rounding error(3)
                daoAndDeployerFees,
                "[!_receiveSToken] silo has just fees"
            );

            assertEq(silo0.getCollateralAssets(), 5, "only dust (2) + rounding error (3) left from collateral");
        }

        assertEq(silo0.getDebtAssets(), 0, "debt is repay");

        if (!_receiveSToken) {
            assertEq(
                token0.balanceOf(liquidator),
                // -3 for rounding error, +2 to balace out underestimation
                100e18 - debtToRepay + collateralToLiquidate - 3 + 2,
                "liquidator should get all collateral because of full liquidation"
            );
        }

        _assertLiquidationModuleDoNotHaveTokens();
    }

    function _assertLiquidationModuleDoNotHaveTokens() private view {
        address module = address(partialLiquidation);

        assertEq(token0.balanceOf(module), 0);
        assertEq(token1.balanceOf(module), 0);

        ISiloConfig.ConfigData memory silo0Config = siloConfig.getConfig(address(silo0));
        ISiloConfig.ConfigData memory silo1Config = siloConfig.getConfig(address(silo1));

        assertEq(IShareToken(silo0Config.collateralShareToken).balanceOf(module), 0);
        assertEq(IShareToken(silo0Config.protectedShareToken).balanceOf(module), 0);
        assertEq(IShareToken(silo0Config.debtShareToken).balanceOf(module), 0);

        assertEq(IShareToken(silo1Config.collateralShareToken).balanceOf(module), 0);
        assertEq(IShareToken(silo1Config.protectedShareToken).balanceOf(module), 0);
        assertEq(IShareToken(silo1Config.debtShareToken).balanceOf(module), 0);
    }
}