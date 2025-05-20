/* Verifies the protocol allows anyone user access 
 * This setup is for a single silo - `Silo0`
 */

import "../setup/single_silo_tokens_requirements.spec";
import "../setup/summaries/silo0_summaries.spec";
import "../setup/summaries/siloconfig_dispatchers.spec";
import "../setup/summaries/config_for_one_in_cvl.spec";
import "../setup/summaries/safe-approximations.spec";
import "./0base_Silo_single_silo.spec";

methods {
    // ---- `SiloConfig` -------------------------------------------------------
    // `envfree`
    function SiloConfig.accrueInterestForSilo(address) external envfree;
    function SiloConfig.getCollateralShareTokenAndAsset(
        address,
        ISilo.CollateralType
    ) external returns (address, address) envfree;

    // ---- `IInterestRateModel` -----------------------------------------------
    // Since `getCompoundInterestRateAndUpdate` is not *pure*, this is not strictly sound.
    function _.getCompoundInterestRateAndUpdate(
        uint256 _collateralAssets,
        uint256 _debtAssets,
        uint256 _interestRateTimestamp
    ) external =>  CVLGetCompoundInterestRate(
        _collateralAssets,
        _debtAssets,
        _interestRateTimestamp
    ) expect (uint256);
    
    // TODO: Is this sound?
    function _.getCompoundInterestRate(
        address _silo,
        uint256 _blockTimestamp
    ) external => CVLGetCompoundInterestRateForSilo(_silo, _blockTimestamp) expect (uint256);

    // ---- `ISiloOracle` ------------------------------------------------------
    // NOTE: Since `beforeQuote` is not a view function, strictly speaking this is unsound.
    function _.beforeQuote(address) external => NONDET DELETE;
}

// ---- Functions and ghosts START ---------------------------------------------------

    ghost mapping(uint256 => mapping(uint256 => mapping(uint256 => uint256))) interestGhost;

    // @title An arbitrary (pure) function for the interest rate
    function CVLGetCompoundInterestRate(
        uint256 _collateralAssets,
        uint256 _debtAssets,
        uint256 _interestRateTimestamp
    ) returns uint256 {
        return interestGhost[_collateralAssets][_debtAssets][_interestRateTimestamp];
    }


    ghost mapping(address => mapping(uint256 => uint256)) interestGhostSilo;

    // @title An arbitrary (pure) function for the interest rate 
    function CVLGetCompoundInterestRateForSilo(
        address _silo,
        uint256 _blockTimestamp
    ) returns uint256 {
        return interestGhostSilo[_silo][_blockTimestamp];
    }


    // @title Require that the second env has at least as much allowance and balance as first
    function requireSecondEnvAtLeastAsFirst(env e1, env e2) {
        /// At least as much allowance as first `env`
        require (
            token0.allowance(e2, e2.msg.sender, silo0) >=
            token0.allowance(e1, e1.msg.sender, silo0)
        );
        /// At least as much balance as first `env`
        require token0.balanceOf(e2, e2.msg.sender) >= token0.balanceOf(e1, e1.msg.sender);
    }

// ---- Functions and ghosts END ---------------------------------------------------

//------------------------------- RULES TEST START ----------------------------------
    
    rule onlySpecificFunctionsCanChangeTotalSupplyProtected(env e, method f, calldataarg args) filtered{f-> !f.isView} {
        uint256 totalSupplyBefore = silo0.totalSupply();

        f(e, args);

        uint256 totalSupplyAfter = silo0.totalSupply();

        assert(totalSupplyBefore != totalSupplyAfter => 
                f.selector == sig:burn(address,address,uint256).selector || 
                f.selector == sig:withdraw(uint256,address,address).selector ||
                f.selector == sig:redeem(uint256,address,address).selector ||
                f.selector == sig:deposit(uint256,address).selector ||
                f.selector == sig:mint(uint256,address).selector ||
                f.selector == sig:mint(address,address,uint256).selector ||
                f.selector == sig:redeem(uint256,address,address,ISilo.CollateralType).selector || 
                f.selector == sig:deposit(uint256,address,ISilo.CollateralType).selector ||
                f.selector == sig:mint(uint256,address,ISilo.CollateralType).selector ||
                f.selector == sig:transitionCollateral(uint256,address,ISilo.CollateralType).selector ||
                f.selector == sig:withdraw(uint256,address,address,ISilo.CollateralType).selector || 
                f.selector == sig:callOnBehalfOfSilo(address,uint256,ISilo.CallType,bytes).selector 
        );
    }




    //with the same share amount, the result of all mints is the same
    rule mintResultIsTheSameBalances(env e) {
        configForEightTokensSetupRequirements();
        uint256 shares;
        address receiver;
        address sender = e.msg.sender;

        //ensuer not interest is accrued
        require require_uint64(e.block.timestamp) == silo0.getSiloDataInterestRateTimestamp(e);

        //balances before
        uint256 assetsSenderToken0Before = token0.balanceOf(sender);
        uint256 assetsSiloToken0Before = token0.balanceOf(silo0);

        //totalSupply before mint
        uint256 totalSupplyCollateralBeforeMint = silo0.totalSupply();
        uint256 totalSupplyProtectedCollateralBeforeMint = shareProtectedCollateralToken0.totalSupply();

        //total assets silo before
        uint256 totalProtectedAssetsBefore;
        uint256 totalCollateralAssetsBefore;
        uint256 totalDebtAssetsBefore;
        (totalProtectedAssetsBefore, totalCollateralAssetsBefore, totalDebtAssetsBefore) = totalAssetsHarness(e);


        //ensure same share and assets
        require totalSupplyCollateralBeforeMint == totalSupplyProtectedCollateralBeforeMint;
        require totalCollateralAssetsBefore == totalProtectedAssetsBefore;

        //inital storage
        storage initState = lastStorage;

        //mint
        mint(e, shares, receiver);

        //balances after mint
        uint256 assetsSenderToken0AfterMint = token0.balanceOf(sender);
        uint256 assetsSiloToken0AfterMint = token0.balanceOf(silo0);

        
        

        //mint collateral at initial storage
        mint(e, shares, receiver, ISilo.CollateralType.Collateral) at initState;

        //balances after mint collateral
        uint256 assetsSenderToken0AfterMintCollateral = token0.balanceOf(sender);
        uint256 assetsSiloToken0AfterMintCollateral = token0.balanceOf(silo0);

        //mint protected collateral at initial storage
        mint(e, shares, receiver, ISilo.CollateralType.Protected) at initState;

        //balances after mint protected collateral
        uint256 assetsSenderToken0AfterMintProtectedCollateral = token0.balanceOf(sender);
        uint256 assetsSiloToken0AfterMintProtectedCollateral = token0.balanceOf(silo0);

        //assert that the final balances are the same
        assert assetsSenderToken0AfterMint == assetsSenderToken0AfterMintCollateral && assetsSenderToken0AfterMint == assetsSenderToken0AfterMintProtectedCollateral;
        assert assetsSiloToken0AfterMint == assetsSiloToken0AfterMintCollateral && assetsSiloToken0AfterMint == assetsSiloToken0AfterMintProtectedCollateral;
    }
  

    //when a user mints x and burns x he gets back the same value
    rule redeemRecoversMint(env e){
        configForEightTokensSetupRequirements();
        uint256 shares;
        address sender = e.msg.sender;
        
        //balance before
        uint256 assetsSenderToken0Before = token0.balanceOf(sender);
        uint256 sharesSenderBefore = silo0.balanceOf(sender);

        mint(e, shares, sender);

        //balance after mint
        uint256 assetsSenderToken0AfterMint = token0.balanceOf(sender);

        redeem(e, shares, sender, sender);

        //balance after burn
        uint256 assetsSenderToken0AfterRedeem = token0.balanceOf(sender);
        uint256 sharesSenderAfterRedeem = silo0.balanceOf(sender);

        //assert that the final balances equals the starting balance
        //@audit-issue how to make it equal but not exactly the same? 
        // Also, we had more assets after burn, this should be an issue: https://prover.certora.com/output/8418/d43cc3c0c83a457eaad21f5b8d0ebacf/?anonymousKey=22676493230c29d653a5272a7407faa8f649c4fb
        assert assetsSenderToken0Before == assetsSenderToken0AfterRedeem; 
        //assert that no shares are left to redeem
        assert sharesSenderBefore == sharesSenderAfterRedeem;
    }

    //When a user deposits x and withdraws max he gets back the same amount
    rule withdrawRecoversDeposit(env e){
        configForEightTokensSetupRequirements();
        uint256 assets;
        address sender = e.msg.sender;

        //ensure no interst is accrued
        require require_uint64(e.block.timestamp) == silo0.getSiloDataInterestRateTimestamp(e);
        
        //balance before
        uint256 assetsSenderToken0Before = token0.balanceOf(sender);
        uint256 sharesSenderBefore = silo0.balanceOf(sender);

        deposit(e, assets, sender);

        //balance after deposit
        uint256 assetsSenderToken0AfterDeposit = token0.balanceOf(sender);

        withdraw(e, assets, sender, sender);

        //balance after withdraw
        uint256 assetsSenderToken0AfterWithdraw = token0.balanceOf(sender);
        uint256 sharesSenderAfterWithdraw = silo0.balanceOf(sender);

        // final balances equals the starting balance
        assert assetsSenderToken0Before == assetsSenderToken0AfterWithdraw;
        // no shares are left to redeem
        assert sharesSenderBefore == sharesSenderAfterWithdraw;
    } 

    //protected collateral can always be withdrawn
    rule protectedCanAlwaysBeWithdrawn(env e, method f, calldataarg arg) filtered{f-> !f.isView}{
        configForEightTokensSetupRequirements();
        uint256 assets;
        address sender = e.msg.sender;

        //deposit protected collateral
        deposit(e, assets, sender, ISilo.CollateralType.Protected);

        //shares sender after deposit
        uint256 protectedCollateralSharesSenderAfterDeposit = shareProtectedCollateralToken0.balanceOf(sender);

        f(e, arg);

        //shares sender after function call
        uint256 protectedCollateralSharesSenderAfterFunctionCall = shareProtectedCollateralToken0.balanceOf(sender);
        require(protectedCollateralSharesSenderAfterFunctionCall == protectedCollateralSharesSenderAfterDeposit);

        //withdraw protected collateral
        withdraw@withrevert(e, assets, sender, sender, ISilo.CollateralType.Protected);

        assert !lastReverted;
    }

    






        // mint protected collateral
            // no one has allowance
            // invariants: protected Assets >= ProtectedAsset shares
            //invariant: silo holds at least the amount of assets that are protected
        // do something
        // withdraw protected collateral => should not fail

    //when a user deposits x and withdraws x he is left with 0 shares


    // minting the amount of shares rereived by depositiong cost the same amount of assets and vice versa (use return values of deposit and mint)
    // the right amount of assets are transfered when minting
    // the right amount of shares are transfered when depositing
    // the right amount of assets are transfered when redeeming
    // the right amount of shares are transfered when withdrawing




    

    
        
    

    //callOnBehalfOfSilo can only be called by hookReceiver



//------------------------------- RULES TEST END ----------------------------------

//------------------------------- RULES PROBLEMS START ----------------------------------

//------------------------------- RULES PROBLEMS START ----------------------------------

//------------------------------- RULES OK START ------------------------------------


    

    //mint moves underlying asset to silo
    rule mintMovesUnderlyingAssetToSilo(env e) {
        configForEightTokensSetupRequirements();
        nonSceneAddressRequirements(e.msg.sender);
        uint256 shares;
        address receiver;
        address sender = e.msg.sender;
        //prevent overflow balances
        totalSuppliesMoreThanBalances(sender, silo0);

        //assets before
        uint256 assetsSenderToken0Before = token0.balanceOf(sender);
        uint256 assetsSiloToken0Before = token0.balanceOf(silo0);

        mint(e, shares, receiver);

        //assets after
        uint256 assetsSenderToken0After = token0.balanceOf(sender);
        uint256 assetsSiloToken0After = token0.balanceOf(silo0);

        //diffs of balances of token0 for sender and silo
        mathint diffSender = assetsSenderToken0Before - assetsSenderToken0After;
        mathint diffSilo = assetsSiloToken0After - assetsSiloToken0Before;

        //difs are the oposite
        assert diffSender == diffSilo;
    }
    
    // deposit moves underlying asset to silo
    rule depositMovesUnderlyingAssetToSilo(env e) {
        configForEightTokensSetupRequirements();
        nonSceneAddressRequirements(e.msg.sender);
        uint256 assets;
        address receiver;
        address sender = e.msg.sender;
        //prevent overflow balances
        totalSuppliesMoreThanBalances(sender, silo0);
        //assets before
        uint256 assetsSenderToken0Before = token0.balanceOf(sender);
        uint256 assetsSiloToken0Before = token0.balanceOf(silo0);

        deposit(e, assets, receiver);

        //assets after
        uint256 assetsSenderToken0After = token0.balanceOf(sender);
        uint256 assetsSiloToken0After = token0.balanceOf(silo0);

        //balances of token0 for sender decreased by assets
        assert(assetsSenderToken0After == assetsSenderToken0Before - assets);
        //balances of token0 for silo increased by assets
        assert(assetsSiloToken0After == assetsSiloToken0Before + assets);
    }

    // with the same asset amount, the result of all deposites is the same
    rule depositResultIsTheSameBalances(env e) {
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        address sender = e.msg.sender;

        //balances before
        uint256 assetsSenderToken0Before = token0.balanceOf(sender);
        uint256 assetsSiloToken0Before = token0.balanceOf(silo0);

        //inital storage
        storage initState = lastStorage;

        //deposit
        deposit(e, assets, receiver);

        //balances after deposit
        uint256 assetsSenderToken0AfterDeposit = token0.balanceOf(sender);
        uint256 assetsSiloToken0AfterDeposit = token0.balanceOf(silo0);

        //deposit collateral at initial storage
        deposit(e, assets, receiver, ISilo.CollateralType.Collateral) at initState;

        //balances after deposit collateral
        uint256 assetsSenderToken0AfterDepositCollateral = token0.balanceOf(sender);
        uint256 assetsSiloToken0AfterDepositCollateral = token0.balanceOf(silo0);

        //deposit protected collateral at initial storage
        deposit(e, assets, receiver, ISilo.CollateralType.Protected) at initState;

        //balances after deposit protected collateral
        uint256 assetsSenderToken0AfterDepositProtectedCollateral = token0.balanceOf(sender);
        uint256 assetsSiloToken0AfterDepositProtectedCollateral = token0.balanceOf(silo0);

        //assert that the final balances are the same
        assert assetsSenderToken0AfterDeposit == assetsSenderToken0AfterDepositCollateral && assetsSenderToken0AfterDeposit == assetsSenderToken0AfterDepositProtectedCollateral;
        assert assetsSiloToken0AfterDeposit == assetsSiloToken0AfterDepositCollateral && assetsSiloToken0AfterDeposit == assetsSiloToken0AfterDepositProtectedCollateral;
    }

    // deposit only increases collateral
    rule depositOnlyIncreasesCollateralAssets(env e) {
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        //prevent overflow in receiver balances
        totalSuppliesMoreThanBalance(receiver);
        //receiver shares before
        uint256 protectedCollateralSharesReceiverBefore = shareProtectedCollateralToken0.balanceOf(receiver);
        uint256 collateralSharesReceiverBefore = silo0.balanceOf(receiver);
        uint256 debtSharesReceiverBefore = shareDebtToken0.balanceOf(e, receiver);
        //total supply before
        uint256 protectedCollateralTotalSupplyBefore = shareProtectedCollateralToken0.totalSupply();
        uint256 collateralTotalSupplyBefore = silo0.totalSupply();
        uint256 debtTotalSupplyBefore = shareDebtToken0.totalSupply();
       
        //total assets silo before
        uint256 totalProtectedAssetsBefore;
        uint256 totalCollateralAssetsBefore;
        uint256 totalDebtAssetsBefore;
        (totalProtectedAssetsBefore, totalCollateralAssetsBefore, totalDebtAssetsBefore) = totalAssetsHarness(e);

        //ensure no interst is accrued
        require require_uint64(e.block.timestamp) == silo0.getSiloDataInterestRateTimestamp(e);

        deposit(e, assets, receiver);

        //receiver shares after
        uint256 protectedCollateralSharesReceiverAfter = shareProtectedCollateralToken0.balanceOf(receiver);
        uint256 collateralSharesReceiverAfter = silo0.balanceOf(receiver);
        uint256 debtSharesReceiverAfter = shareDebtToken0.balanceOf(e, receiver);
        
        //total supply after
        uint256 protectedCollateralTotalSupplyAfter = shareProtectedCollateralToken0.totalSupply();
        uint256 collateralTotalSupplyAfter = silo0.totalSupply();
        uint256 debtTotalSupplyAfter = shareDebtToken0.totalSupply();
       
        //total assets silo after
        uint256 totalProtectedAssetsAfter;
        uint256 totalCollateralAssetsAfter;
        uint256 totalDebtAssetsAfter;
        (totalProtectedAssetsAfter, totalCollateralAssetsAfter, totalDebtAssetsAfter) = totalAssetsHarness(e);

        //prevent overflow
        require(protectedCollateralTotalSupplyAfter >= protectedCollateralTotalSupplyBefore);
        require(collateralTotalSupplyAfter >= collateralTotalSupplyBefore);
        require(debtTotalSupplyAfter >= debtTotalSupplyBefore);
        require(totalCollateralAssetsAfter >= totalCollateralAssetsBefore);


        //change in collateral shares
        mathint changeCollateralShares = collateralTotalSupplyAfter - collateralTotalSupplyBefore;

        //total supply collateral increased
        assert(collateralTotalSupplyAfter > collateralTotalSupplyBefore);
        //total supply protected collateral unchanged
        assert(protectedCollateralTotalSupplyAfter == protectedCollateralTotalSupplyBefore);
        //total supply debt unchanged
        assert(debtTotalSupplyAfter == debtTotalSupplyBefore);
        //balance of receiver collateral increases by change in shares
        assert(collateralSharesReceiverAfter == collateralSharesReceiverBefore + changeCollateralShares);
        //balance of receiver protected collateral unchanged
        assert(protectedCollateralSharesReceiverAfter == protectedCollateralSharesReceiverBefore);
        //balance of receiver debt unchanged
        assert(debtSharesReceiverAfter == debtSharesReceiverBefore);
        //total collateral assets increased by assets
        assert(totalCollateralAssetsAfter == totalCollateralAssetsBefore + assets);
        //total protected assets unchanged
        assert(totalProtectedAssetsAfter == totalProtectedAssetsBefore);
        //total debt assets unchanged
        assert(totalDebtAssetsAfter == totalDebtAssetsBefore);
    }

    // deposit of collateral only increases collateral 
    rule depositOfCollateralAssetsOnlyIncreasesCollateralAssets(env e) {
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        //prevent overflow in receiver balances
        totalSuppliesMoreThanBalance(receiver);
        //receiver shares before
        uint256 protectedCollateralSharesReceiverBefore = shareProtectedCollateralToken0.balanceOf(receiver);
        uint256 collateralSharesReceiverBefore = silo0.balanceOf(receiver);
        uint256 debtSharesReceiverBefore = shareDebtToken0.balanceOf(e, receiver);
        //total supply before
        uint256 protectedCollateralTotalSupplyBefore = shareProtectedCollateralToken0.totalSupply();
        uint256 collateralTotalSupplyBefore = silo0.totalSupply();
        uint256 debtTotalSupplyBefore = shareDebtToken0.totalSupply();
       
        //total assets silo before
        uint256 totalProtectedAssetsBefore;
        uint256 totalCollateralAssetsBefore;
        uint256 totalDebtAssetsBefore;
        (totalProtectedAssetsBefore, totalCollateralAssetsBefore, totalDebtAssetsBefore) = totalAssetsHarness(e);

        //ensure no interst is accrued
        require require_uint64(e.block.timestamp) == silo0.getSiloDataInterestRateTimestamp(e);

        silo0.deposit(e, assets, receiver, ISilo.CollateralType.Collateral);

        //receiver shares after
        uint256 protectedCollateralSharesReceiverAfter = shareProtectedCollateralToken0.balanceOf(receiver);
        uint256 collateralSharesReceiverAfter = silo0.balanceOf(receiver);
        uint256 debtSharesReceiverAfter = shareDebtToken0.balanceOf(e, receiver);
        
        //total supply after
        uint256 protectedCollateralTotalSupplyAfter = shareProtectedCollateralToken0.totalSupply();
        uint256 collateralTotalSupplyAfter = silo0.totalSupply();
        uint256 debtTotalSupplyAfter = shareDebtToken0.totalSupply();
       
        //total assets silo after
        uint256 totalProtectedAssetsAfter;
        uint256 totalCollateralAssetsAfter;
        uint256 totalDebtAssetsAfter;
        (totalProtectedAssetsAfter, totalCollateralAssetsAfter, totalDebtAssetsAfter) = totalAssetsHarness(e);

        //prevent overflow
        require(protectedCollateralTotalSupplyAfter >= protectedCollateralTotalSupplyBefore);
        require(collateralTotalSupplyAfter >= collateralTotalSupplyBefore);
        require(debtTotalSupplyAfter >= debtTotalSupplyBefore);
        require(totalCollateralAssetsAfter >= totalCollateralAssetsBefore);


        //change in collateral shares
        mathint changeCollateralShares = collateralTotalSupplyAfter - collateralTotalSupplyBefore;

        //total supply collateral increased
        assert(collateralTotalSupplyAfter > collateralTotalSupplyBefore);
        //total supply protected collateral unchanged
        assert(protectedCollateralTotalSupplyAfter == protectedCollateralTotalSupplyBefore);
        //total supply debt unchanged
        assert(debtTotalSupplyAfter == debtTotalSupplyBefore);
        //balance of receiver collateral increases by change in shares
        assert(collateralSharesReceiverAfter == collateralSharesReceiverBefore + changeCollateralShares);
        //balance of receiver protected collateral unchanged
        assert(protectedCollateralSharesReceiverAfter == protectedCollateralSharesReceiverBefore);
        //balance of receiver debt unchanged
        assert(debtSharesReceiverAfter == debtSharesReceiverBefore);
        //total collateral assets increased by assets
        assert(totalCollateralAssetsAfter == totalCollateralAssetsBefore + assets);
        //total protected assets unchanged
        assert(totalProtectedAssetsAfter == totalProtectedAssetsBefore);
        //total debt assets unchanged
        assert(totalDebtAssetsAfter == totalDebtAssetsBefore);
    }

    // mint of collateral shares only increases collateral shares
    rule mintOfCollateralSharesOnlyIncreasesCollateralShares(env e) {
        configForEightTokensSetupRequirements();
        uint256 shares;
        address receiver;
        //prevent overflow in receiver balances
        totalSuppliesMoreThanBalance(receiver);

        //receiver shares before
        uint256 protectedCollateralSharesReceiverBefore = shareProtectedCollateralToken0.balanceOf(receiver);
        uint256 collateralSharesReceiverBefore = silo0.balanceOf(receiver);
        uint256 debtSharesReceiverBefore = shareDebtToken0.balanceOf(e, receiver);
        
        //total supply before
        uint256 protectedCollateralTotalSupplyBefore = shareProtectedCollateralToken0.totalSupply();
        uint256 collateralTotalSupplyBefore = silo0.totalSupply();
        uint256 debtTotalSupplyBefore = shareDebtToken0.totalSupply();
       
        //total assets silo before
        uint256 totalProtectedAssetsBefore;
        uint256 totalCollateralAssetsBefore;
        uint256 totalDebtAssetsBefore;
        (totalProtectedAssetsBefore, totalCollateralAssetsBefore, totalDebtAssetsBefore) = totalAssetsHarness(e);

        //ensure no interst is accrued
        require require_uint64(e.block.timestamp) == silo0.getSiloDataInterestRateTimestamp(e);

        mint(e, shares, receiver, ISilo.CollateralType.Collateral);

        //receiver shares after
        uint256 protectedCollateralSharesReceiverAfter = shareProtectedCollateralToken0.balanceOf(receiver);
        uint256 collateralSharesReceiverAfter = silo0.balanceOf(receiver);
        uint256 debtSharesReceiverAfter = shareDebtToken0.balanceOf(e, receiver);
        
        //total supply after
        uint256 protectedCollateralTotalSupplyAfter = shareProtectedCollateralToken0.totalSupply();
        uint256 collateralTotalSupplyAfter = silo0.totalSupply();
        uint256 debtTotalSupplyAfter = shareDebtToken0.totalSupply();
       
        //total assets silo after
        uint256 totalProtectedAssetsAfter;
        uint256 totalCollateralAssetsAfter;
        uint256 totalDebtAssetsAfter;
        (totalProtectedAssetsAfter, totalCollateralAssetsAfter, totalDebtAssetsAfter) = totalAssetsHarness(e);

        //prevent overflow
        require(protectedCollateralTotalSupplyAfter >= protectedCollateralTotalSupplyBefore);
        require(collateralTotalSupplyAfter >= collateralTotalSupplyBefore);
        require(debtTotalSupplyAfter >= debtTotalSupplyBefore);
        require(totalCollateralAssetsAfter >= totalCollateralAssetsBefore);

        //change in collateral assets
        mathint changeCollateralAssets = totalCollateralAssetsAfter - totalCollateralAssetsBefore;

        //total supply collateral increased by shares
        assert(collateralTotalSupplyAfter == collateralTotalSupplyBefore + shares);
        //total supply protected collateral unchanged
        assert(protectedCollateralTotalSupplyAfter == protectedCollateralTotalSupplyBefore);
        //total supply debt unchanged
        assert(debtTotalSupplyAfter == debtTotalSupplyBefore);
        //balance of receiver collateral increases by change in shares
        assert(collateralSharesReceiverAfter == collateralSharesReceiverBefore + shares);    
        //balance of receiver protected collateral unchanged
        assert(protectedCollateralSharesReceiverAfter == protectedCollateralSharesReceiverBefore);
        //balance of receiver debt unchanged
        assert(debtSharesReceiverAfter == debtSharesReceiverBefore);
        //total collateral assets increased
        assert(totalCollateralAssetsAfter > totalCollateralAssetsBefore);
        //total protected assets unchanged
        assert(totalProtectedAssetsAfter == totalProtectedAssetsBefore);
        //total debt assets unchanged
        assert(totalDebtAssetsAfter == totalDebtAssetsBefore);
    }

    // mint only increases collateral shares
    rule mintOnlyIncreasesCollateralShares(env e) {
        configForEightTokensSetupRequirements();
        uint256 shares;
        address receiver;
        //prevent overflow in receiver balances
        totalSuppliesMoreThanBalance(receiver);

        //receiver shares before
        uint256 protectedCollateralSharesReceiverBefore = shareProtectedCollateralToken0.balanceOf(receiver);
        uint256 collateralSharesReceiverBefore = silo0.balanceOf(receiver);
        uint256 debtSharesReceiverBefore = shareDebtToken0.balanceOf(e, receiver);
        
        //total supply before
        uint256 protectedCollateralTotalSupplyBefore = shareProtectedCollateralToken0.totalSupply();
        uint256 collateralTotalSupplyBefore = silo0.totalSupply();
        uint256 debtTotalSupplyBefore = shareDebtToken0.totalSupply();
       
        //total assets silo before
        uint256 totalProtectedAssetsBefore;
        uint256 totalCollateralAssetsBefore;
        uint256 totalDebtAssetsBefore;
        (totalProtectedAssetsBefore, totalCollateralAssetsBefore, totalDebtAssetsBefore) = totalAssetsHarness(e);

        //ensure no interst is accrued
        require require_uint64(e.block.timestamp) == silo0.getSiloDataInterestRateTimestamp(e);

        mint(e, shares, receiver);

        //receiver shares after
        uint256 protectedCollateralSharesReceiverAfter = shareProtectedCollateralToken0.balanceOf(receiver);
        uint256 collateralSharesReceiverAfter = silo0.balanceOf(receiver);
        uint256 debtSharesReceiverAfter = shareDebtToken0.balanceOf(e, receiver);
        
        //total supply after
        uint256 protectedCollateralTotalSupplyAfter = shareProtectedCollateralToken0.totalSupply();
        uint256 collateralTotalSupplyAfter = silo0.totalSupply();
        uint256 debtTotalSupplyAfter = shareDebtToken0.totalSupply();
       
        //total assets silo after
        uint256 totalProtectedAssetsAfter;
        uint256 totalCollateralAssetsAfter;
        uint256 totalDebtAssetsAfter;
        (totalProtectedAssetsAfter, totalCollateralAssetsAfter, totalDebtAssetsAfter) = totalAssetsHarness(e);

        //prevent overflow
        require(protectedCollateralTotalSupplyAfter >= protectedCollateralTotalSupplyBefore);
        require(collateralTotalSupplyAfter >= collateralTotalSupplyBefore);
        require(debtTotalSupplyAfter >= debtTotalSupplyBefore);
        require(totalCollateralAssetsAfter >= totalCollateralAssetsBefore);

        //change in collateral assets
        mathint changeCollateralAssets = totalCollateralAssetsAfter - totalCollateralAssetsBefore;

        //total supply collateral increased by shares
        assert(collateralTotalSupplyAfter == collateralTotalSupplyBefore + shares);
        //total supply protected collateral unchanged
        assert(protectedCollateralTotalSupplyAfter == protectedCollateralTotalSupplyBefore);
        //total supply debt unchanged
        assert(debtTotalSupplyAfter == debtTotalSupplyBefore);
        //balance of receiver collateral increases by change in shares
        assert(collateralSharesReceiverAfter == collateralSharesReceiverBefore + shares);    
        //balance of receiver protected collateral unchanged
        assert(protectedCollateralSharesReceiverAfter == protectedCollateralSharesReceiverBefore);
        //balance of receiver debt unchanged
        assert(debtSharesReceiverAfter == debtSharesReceiverBefore);
        //total collateral assets increased
        assert(totalCollateralAssetsAfter > totalCollateralAssetsBefore);
        //total protected assets unchanged
        assert(totalProtectedAssetsAfter == totalProtectedAssetsBefore);
        //total debt assets unchanged
        assert(totalDebtAssetsAfter == totalDebtAssetsBefore);
    }

    // mint of protected shares only increases protected shares
    rule mintOfProtectedSharesOnlyIncreasesProtectedShares(env e) {
        configForEightTokensSetupRequirements();
        uint256 shares;
        address receiver;
        //prevent overflow in receiver balances
        totalSuppliesMoreThanBalance(receiver);
        //receiver shares before
        uint256 protectedCollateralSharesReceiverBefore = shareProtectedCollateralToken0.balanceOf(receiver);
        uint256 collateralSharesReceiverBefore = silo0.balanceOf(receiver);
        uint256 debtSharesReceiverBefore = shareDebtToken0.balanceOf(e, receiver);
        //total supply before
        uint256 protectedCollateralTotalSupplyBefore = shareProtectedCollateralToken0.totalSupply();
        uint256 collateralTotalSupplyBefore = silo0.totalSupply();
        uint256 debtTotalSupplyBefore = shareDebtToken0.totalSupply();
       
        //total assets silo before
        uint256 totalProtectedAssetsBefore;
        uint256 totalCollateralAssetsBefore;
        uint256 totalDebtAssetsBefore;
        (totalProtectedAssetsBefore, totalCollateralAssetsBefore, totalDebtAssetsBefore) = totalAssetsHarness(e);

        //ensure no interst is accrued
        require require_uint64(e.block.timestamp) == silo0.getSiloDataInterestRateTimestamp(e);

        mint(e, shares, receiver, ISilo.CollateralType.Protected);

        //receiver shares after
        uint256 protectedCollateralSharesReceiverAfter = shareProtectedCollateralToken0.balanceOf(receiver);
        uint256 collateralSharesReceiverAfter = silo0.balanceOf(receiver);
        uint256 debtSharesReceiverAfter = shareDebtToken0.balanceOf(e, receiver);
        
        //total supply after
        uint256 protectedCollateralTotalSupplyAfter = shareProtectedCollateralToken0.totalSupply();
        uint256 collateralTotalSupplyAfter = silo0.totalSupply();
        uint256 debtTotalSupplyAfter = shareDebtToken0.totalSupply();
       
        //total assets silo after
        uint256 totalProtectedAssetsAfter;
        uint256 totalCollateralAssetsAfter;
        uint256 totalDebtAssetsAfter;
        (totalProtectedAssetsAfter, totalCollateralAssetsAfter, totalDebtAssetsAfter) = totalAssetsHarness(e);


        //prevent overflow
        require(protectedCollateralTotalSupplyAfter >= protectedCollateralTotalSupplyBefore);
        require(collateralTotalSupplyAfter >= collateralTotalSupplyBefore);
        require(debtTotalSupplyAfter >= debtTotalSupplyBefore);
        require(totalProtectedAssetsAfter >= totalProtectedAssetsBefore);

        //change in protected collateral assets
        mathint changeProtectedCollateralAssets = totalProtectedAssetsAfter - totalProtectedAssetsBefore;

        //total supply protectedCollateral increased by shares
        assert(protectedCollateralTotalSupplyAfter == protectedCollateralTotalSupplyBefore + shares);
        //total supply collateral unchanged
        assert(collateralTotalSupplyAfter == collateralTotalSupplyBefore);
        //total supply debt unchanged
        assert(debtTotalSupplyAfter == debtTotalSupplyBefore);
        //balance of receiver protected collateral increases by change in shares
        assert(protectedCollateralSharesReceiverAfter == protectedCollateralSharesReceiverBefore + shares);
        //balance of receiver collateral unchanged
        assert(collateralSharesReceiverAfter == collateralSharesReceiverBefore);
        //balance of receiver debt unchanged
        assert(debtSharesReceiverAfter == debtSharesReceiverBefore);
        //total protected assets increased
        assert(totalProtectedAssetsAfter > totalProtectedAssetsBefore);
        //total collateral assets unchanged
        assert(totalCollateralAssetsAfter == totalCollateralAssetsBefore);
        //total debt assets unchanged
        assert(totalDebtAssetsAfter == totalDebtAssetsBefore);
    }
    
    // deposit of protected collateral only increases protected collateral
    rule depositOfProtectedAssetOnlyIncreasesProtectedAsset(env e) {
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        totalSuppliesMoreThanBalance(receiver);
        //receiver shares before
        uint256 protectedCollateralSharesReceiverBefore = shareProtectedCollateralToken0.balanceOf(receiver);
        uint256 collateralSharesReceiverBefore = silo0.balanceOf(receiver);
        uint256 debtSharesReceiverBefore = shareDebtToken0.balanceOf(e, receiver);
        //total supply before
        uint256 protectedCollateralTotalSupplyBefore = shareProtectedCollateralToken0.totalSupply();
        uint256 collateralTotalSupplyBefore = silo0.totalSupply();
        uint256 debtTotalSupplyBefore = shareDebtToken0.totalSupply();

        //ensure no interst is accrued
        require require_uint64(e.block.timestamp) == silo0.getSiloDataInterestRateTimestamp(e);
       
        //total assets silo before
        uint256 totalProtectedAssetsBefore;
        uint256 totalCollateralAssetsBefore;
        uint256 totalDebtAssetsBefore;
        (totalProtectedAssetsBefore, totalCollateralAssetsBefore, totalDebtAssetsBefore) = totalAssetsHarness(e);

        silo0.deposit(e, assets, receiver, ISilo.CollateralType.Protected);

        //receiver shares after
        uint256 protectedCollateralSharesReceiverAfter = shareProtectedCollateralToken0.balanceOf(receiver);
        uint256 collateralSharesReceiverAfter = silo0.balanceOf(receiver);
        uint256 debtSharesReceiverAfter = shareDebtToken0.balanceOf(e, receiver);
        
        //total supply after
        uint256 protectedCollateralTotalSupplyAfter = shareProtectedCollateralToken0.totalSupply();
        uint256 collateralTotalSupplyAfter = silo0.totalSupply();
        uint256 debtTotalSupplyAfter = shareDebtToken0.totalSupply();
       
        //total assets silo after
        uint256 totalProtectedAssetsAfter;
        uint256 totalCollateralAssetsAfter;
        uint256 totalDebtAssetsAfter;
        (totalProtectedAssetsAfter, totalCollateralAssetsAfter, totalDebtAssetsAfter) = totalAssetsHarness(e);

        //prevent overflow
        require(protectedCollateralTotalSupplyAfter >= protectedCollateralTotalSupplyBefore);
        require(collateralTotalSupplyAfter >= collateralTotalSupplyBefore);
        require(debtTotalSupplyAfter >= debtTotalSupplyBefore);
        require(totalProtectedAssetsAfter >= totalProtectedAssetsBefore);

        //change in protected collateral shares
        mathint changeProtectedCollateralShares = protectedCollateralTotalSupplyAfter - protectedCollateralTotalSupplyBefore;

        //total supply protectedCollateral increased
        assert(protectedCollateralTotalSupplyAfter > protectedCollateralTotalSupplyBefore);
        //total supply collateral unchanged
        assert(collateralTotalSupplyAfter == collateralTotalSupplyBefore);
        //total supply debt unchanged
        assert(debtTotalSupplyAfter == debtTotalSupplyBefore);
        //balance of receiver protected collateral increases by change in shares
        assert(protectedCollateralSharesReceiverAfter == protectedCollateralSharesReceiverBefore + changeProtectedCollateralShares);
        //balance of receiver collateral unchanged
        assert(collateralSharesReceiverAfter == collateralSharesReceiverBefore);
        //balance of receiver debt unchanged
        assert(debtSharesReceiverAfter == debtSharesReceiverBefore);
        //total protected assets increased by assets
        assert(totalProtectedAssetsAfter == totalProtectedAssetsBefore + assets);
        //total collateral assets unchanged
        assert(totalCollateralAssetsAfter == totalCollateralAssetsBefore);
        //total debt assets unchanged
        assert(totalDebtAssetsAfter == totalDebtAssetsBefore);
    }
    
    // deposit and deposit collateral result is the same
    rule depositAndDepositCollateralResultIsTheSame(env e) {
        configForEightTokensSetupRequirements();
        uint256 assets;
        address receiver;
        //inital storage
        storage initState = lastStorage;

        //deposit
        deposit(e, assets, receiver);

        //final storage deposit
        storage finalStateDeposit = lastStorage;

        //deposit collateral at initial storage
        deposit(e, assets, receiver, ISilo.CollateralType.Collateral) at initState;

        //final storage deposit collateral
        storage finalStateDepositCollateral = lastStorage;

        //assert that the final storage is the same
        assert finalStateDeposit == finalStateDepositCollateral;
    }
    
    // mint and mint collateral result is the same
    rule mintAndMintCollateralResultIsTheSame(env e) {
        configForEightTokensSetupRequirements();
        uint256 shares;
        address receiver;
        
        //inital storage
        storage initState = lastStorage;

        //mint
        mint(e, shares, receiver);
        
        //final storage mint
        storage finalStateMint = lastStorage;

        //mint collateral at initial storage
        mint(e, shares, receiver, ISilo.CollateralType.Collateral) at initState;

        //final storage mint collateral
        storage finalStateMintCollateral = lastStorage;

        //assert that the final storage is the same
        assert finalStateMint == finalStateMintCollateral;
    }

    //only specific functions can change the ballance of a user
    rule onlySpecificFunctionsCanChangeBalanceOfUser(env e, method f, calldataarg args) filtered{f-> !f.isView} {
        address user;
        uint256 balanceBefore = silo0.balanceOf(user);

        f(e, args);

        uint256 balanceAfter = silo0.balanceOf(user);

        assert(balanceBefore != balanceAfter =>
                f.selector == sig:burn(address,address,uint256).selector || 
                f.selector == sig:withdraw(uint256,address,address).selector ||
                f.selector == sig:redeem(uint256,address,address).selector ||
                f.selector == sig:deposit(uint256,address).selector ||
                f.selector == sig:mint(uint256,address).selector ||
                f.selector == sig:mint(address,address,uint256).selector ||
                f.selector == sig:redeem(uint256,address,address,ISilo.CollateralType).selector || 
                f.selector == sig:deposit(uint256,address,ISilo.CollateralType).selector ||
                f.selector == sig:mint(uint256,address,ISilo.CollateralType).selector ||
                f.selector == sig:transitionCollateral(uint256,address,ISilo.CollateralType).selector ||
                f.selector == sig:withdraw(uint256,address,address,ISilo.CollateralType).selector || 
                f.selector == sig:transfer(address,uint256).selector || 
                f.selector == sig:transferFrom(address,address,uint256).selector || 
                f.selector == sig:forwardTransferFromNoChecks(address,address,uint256).selector || 
                f.selector == sig:callOnBehalfOfSilo(address,uint256,ISilo.CallType,bytes).selector
        );
    }
    //balacenOfAndTotalSupply returns the right values
    rule balanceOfAndTotalSupplyWorks(env e) {
        address user;
        uint256 balance = silo0.balanceOf(user);
        uint256 totalSupply = silo0.totalSupply();

        uint256 balanceResult;
        uint256 totalSupplyResult;
        (balanceResult, totalSupplyResult) = silo0.balanceOfAndTotalSupply(e,user);

        assert balance == balanceResult && totalSupply == totalSupplyResult;
    }

    //only Silo can call mint and burn
    rule onlySiloCanCallMintAndBurn(env e, method f, calldataarg args) filtered{f->
        f.selector == sig:mint(address,address,uint256).selector || 
        f.selector == sig:burn(address,address,uint256).selector} {
        
        f(e, args);

        assert e.msg.sender == getSiloFromStorage(e);
    }

    //only specific functions can change the total supply
    rule onlySpecificFunctionsCanChangeTotalSupplyCollateral(env e, method f, calldataarg args) filtered{f-> !f.isView} {
        uint256 totalSupplyBefore = silo0.totalSupply();

        f(e, args);

        uint256 totalSupplyAfter = silo0.totalSupply();

        assert(totalSupplyBefore != totalSupplyAfter => 
                f.selector == sig:burn(address,address,uint256).selector || 
                f.selector == sig:withdraw(uint256,address,address).selector ||
                f.selector == sig:redeem(uint256,address,address).selector ||
                f.selector == sig:deposit(uint256,address).selector ||
                f.selector == sig:mint(uint256,address).selector ||
                f.selector == sig:mint(address,address,uint256).selector ||
                f.selector == sig:redeem(uint256,address,address,ISilo.CollateralType).selector || 
                f.selector == sig:deposit(uint256,address,ISilo.CollateralType).selector ||
                f.selector == sig:mint(uint256,address,ISilo.CollateralType).selector ||
                f.selector == sig:transitionCollateral(uint256,address,ISilo.CollateralType).selector ||
                f.selector == sig:withdraw(uint256,address,address,ISilo.CollateralType).selector || 
                f.selector == sig:callOnBehalfOfSilo(address,uint256,ISilo.CallType,bytes).selector 
        );
    }

//------------------------------- RULES OK END ------------------------------------

//------------------------------- INVARIENTS OK START-------------------------------

//------------------------------- INVARIENTS OK END-------------------------------

//------------------------------- ISSUES OK START-------------------------------

//------------------------------- ISSUES OK END-------------------------------

//-------------------------------OLD RULES START----------------------------------



    // ---- Rules ------------------------------------------------------------------

    /// @title For testing the setup
    rule sanityWithSetup_borrow() {
        calldataarg args;
        env e; 
        configForEightTokensSetupRequirements();
        nonSceneAddressRequirements(e.msg.sender);
        silosTimestampSetupRequirements(e);
        silo0.borrow(e, args);
        satisfy true;
    }

    /// @title If a user may deposit some amount, any other user also may
    /// @property user-access
    rule RA_anyone_may_deposit(env e1, env e2, address recipient, uint256 amount) {
        /// Assuming same context (time and value).
        require e1.block.timestamp == e2.block.timestamp;
        require e1.msg.value == e2.msg.value;

        // Block time-stamp >= interest rate time-stamp
        silosTimestampSetupRequirements(e1);
        silosTimestampSetupRequirements(e2);

        // Conditions necessary that `e2` will not revert if `e1` did not
        requireSecondEnvAtLeastAsFirst(e1, e2);

        storage initState = lastStorage;
        deposit(e1, amount, recipient);
        deposit@withrevert(e2, amount, recipient) at initState;

        assert e2.msg.sender != 0 => !lastReverted;
    }

    /// @title If one user can repay some borrower's debt, any other user also can
    /// @property user-access
    rule RA_anyone_may_repay(env e1, env e2, uint256 amount, address borrower) {
        /// Assuming same context (time and value).
        require e1.block.timestamp == e2.block.timestamp;
        require e1.msg.value == e2.msg.value;

        // Block time-stamp >= interest rate time-stamp
        silosTimestampSetupRequirements(e1);
        silosTimestampSetupRequirements(e2);

        // Conditions necessary that `e2` will not revert if `e1` did not
        requireSecondEnvAtLeastAsFirst(e1, e2);

        storage initState = lastStorage;
        repay(e1, amount, borrower);
        repay@withrevert(e2, amount, borrower) at initState;

        assert e2.msg.sender != 0 => !lastReverted;
    }


    /// @title The deposit recipient is not discriminated
    /// @property user-access
    rule RA_deposit_recipient_is_not_restricted(address user1, address user2, uint256 amount) {
        env e;

        storage initState = lastStorage;
        deposit(e, amount, user1);
        deposit@withrevert(e, amount, user2) at initState;

        assert user2 !=0 => !lastReverted;
    }

    /// @title The repay action of a borrower is not discriminated (by shares)
    /// @property user-access
    // rule RA_repay_borrower_is_not_restricted_by_shares(
    //     address borrower1,
    //     address borrower2,
    //     uint256 amount
    // ) {
    //     env e;
    //     require borrower2 != 0;

    //     // Get the borrowers debts
    //     uint256 debt1 = shareDebtToken0.balanceOf(e, borrower1);
    //     uint256 debt2 = shareDebtToken0.balanceOf(e, borrower2);
    //     require debt2 >= debt1;

    //     storage initState = lastStorage;
    //     repay(e, amount, borrower1);
    //     repay@withrevert(e, amount, borrower2) at initState;


    //     // The repaid amount is less than the borrower's debt, hence the operation must succeed.
    //     assert !lastReverted;
    // }
//-------------------------------OLD RULES END----------------------------------





