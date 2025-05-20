/* Rules concerning deposit and mint  */

import "../setup/CompleteSiloSetup.spec";
import "./0base_Silo.spec";
import "../simplifications/Silo_noAccrueInterest_simplification_UNSAFE.spec";
import "../simplifications/_Oracle_call_before_quote_UNSAFE.spec";

//@audit-issue !ISSUE! allowance and not receiveAllowance is used when minting for an other user
// only user or _receiveAllowance can borrow() for user 
rule onlyUserOrReceiverAllowanceCanBorrow(env e){
    configForEightTokensSetupRequirements();
    uint256 assets;
    address receiver;
    address borrower;
    address caller = e.msg.sender;

    uint256 receiveAllowancCaller = shareDebtToken0.receiveAllowance(borrower, caller);

    uint256 mintedShares = borrow(e, assets, receiver, borrower);

    assert caller == borrower ||  receiveAllowancCaller >= mintedShares;
}