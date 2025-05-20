import "../mocks/General.spec";
import "../mocks/ShareTokenMock.spec";

using ShareCollateralTokenHarness as Harness;

methods {
    function ShareTokenLib.decimals() external returns (uint8) =>
        decimalsMock();

    function totalSupply() external returns (uint256) envfree;
    function balanceOf(address) external returns (uint256) envfree;
}

// persistent since we still have methods that havoc & revert
persistent ghost bool balanceHasBeenUpdated;
persistent ghost bool totalSupplyHasBeenUpdated;
persistent ghost bool balanceUpdateFlag;
persistent ghost bool _decimalsCalled;
persistent ghost bool _readAllowance;

ghost mathint sumOfBalances {
    init_state axiom sumOfBalances == 0;
}

function decimalsMock() returns uint8 {
    _decimalsCalled = true;
    return 78; // random number < uint8.max
}


// Hook that flags if someone's balance has changed of the ERC20 token
// Stores the sender of the tokens (should be address(0) if mint() )
hook Sstore currentContract.erc20Storage._balances[KEY address account] uint256 newBalance (uint256 previousBalance) {
    sumOfBalances = sumOfBalances - previousBalance + newBalance;
    if(!balanceUpdateFlag) {
        _cachedOwner = account;
    }
    balanceHasBeenUpdated = true;
    balanceUpdateFlag = true;
}

// Hook that flags if the totalSupply of the ERC20 token has changed
hook Sstore currentContract.erc20Storage._totalSupply uint256 newSupply (uint256 previousSupply) {
    totalSupplyHasBeenUpdated = true;
}

// Hook that flags if something was read from the ERC20 balances mapping
hook Sload uint256 readValue currentContract.erc20Storage._balances[KEY address account] {
    require sumOfBalances >= to_mathint(readValue);
}

invariant sumOfBalancesIsTotalSupply() to_mathint(totalSupply()) == sumOfBalances
    {
        preserved {
            reentrancyProtection = true;
        }
    }

persistent ghost mapping (address => uint256) bals;
function initState() {
    require forall address i. (true) => bals[i] == currentContract.erc20Storage._balances[i];
    havoc sumOfBalances assuming
            forall address i. (true) => sumOfBalances@new == sumOfBalances@old + bals[i];
    mathint sum2 = sumOfBalances;
    requireInvariant sumOfBalancesIsTotalSupply();
}



// Hook that flags if something was read from the ERC20 allowances mapping
hook Sload uint256 readValue currentContract.erc20Storage._allowances[KEY address account][KEY address spender] {

    _readAllowance = true;
}

// Verifies that each of the transfer methods of ERC20 (burn, mint, transfer variations) change someone's balance.
rule erc20TransfersModifyBalance(method f, env e, calldataarg args) filtered {f -> ERC20Transfers(f)} {
    balanceHasBeenUpdated = false;
    reentrancyProtection = true;
    f(e, args);

    assert balanceHasBeenUpdated;
}

// Verifies that methods outside of ERC20 (burn, mint, transfer variations) can't and do not change anyone's balance.
rule nonTransfersDoNotChangeBalance(method f, env e, calldataarg args) filtered {f -> !ERC20Transfers(f)} {
    balanceHasBeenUpdated = false;

    f(e, args);

    assert !balanceHasBeenUpdated;
}

rule mint_correctBalances(env e, address _owner, uint256 _value) {

    uint256 balanceBefore = balanceOf(e, _owner);
    require(balanceBefore <= totalSupply());
    mint(e, _owner, _owner, _value);
    assert balanceBefore + _value == balanceOf(e, _owner);
}

// Checks if mint() and burn() in ShareCollateralToken have the onlySilo() modifier
// Since only mint() and burn() modify the total supply, if the total supply
// has change then the message sender should be a silo
// Verified
rule onlySiloCanMintBurn(method f, env e, calldataarg args) {
    totalSupplyHasBeenUpdated = false;
    reentrancyProtection = true;
    f(e, args);

    assert totalSupplyHasBeenUpdated => e.msg.sender == getSiloAddress(e);
}


// Checks the appropriate invocation of _spendAllowance() in _burn() with the correct parameters.
// The function only reverts when expected
// Verified
rule burn_revertConditions(env e, address owner, address spender, uint256 value) {
    // requireInvariant balancesUnderTotal(e, owner, spender);
    require e.msg.sender == getSiloAddress(e);

    uint256 balance = balanceOf(owner);
    uint256 allowance = allowance(e, owner, spender);
    _readAllowance = false;

    burn@withrevert(e, owner, spender, value);
    bool _cacheReverted = lastReverted;
    bool _cacheRA = _readAllowance;
    uint256 allowanceAfter = allowance(e, owner, spender);


    bool c1 = (value > allowance);
    bool c2 = (allowance != MAX_UINT256(e));
    assert (owner == spender) => !_cacheRA;
    assert (owner != spender || (owner == 0 && spender == 0)) => (
        (
            (c1 //(value > allowance)
            || (value > balance)
            || (value == 0)
            || (owner == 0)
            || (spender == 0 && c2)) == _cacheReverted
        )
        &&
        (
            c1 || (// allowance <= value
                _cacheReverted || (
                    c2 => allowanceAfter == (allowance - value)
                    // evaluate something based on owner == spender
                )
            )
        )
    );
}

rule afterTokenTransferCalledCorrectly(method f, env e, calldataarg args, address _owner, address _recipient, uint256 _amount)
        filtered { f -> ERC20Transfers(f) } {
    reentrancyProtection = true;
    require getStorage(e).transferWithChecks;

    if (burnSig(f)) {
        burn(e, _owner, _owner, _amount);

        assert _owner == _cachedSender;
        assert 0 == _cachedRecipient;
        assert _amount == _cachedAmount;
    } else if (mintSig(f)) {
        mint(e, _owner, _recipient, _amount);

        assert 0 == _cachedSender;
        assert _owner == _cachedRecipient;
        assert _amount == _cachedAmount;
    } else if (transferFromSig(f)) {
        transferFrom(e, _owner, _recipient, _amount);

        assert _owner == _cachedSender;
        assert _recipient == _cachedRecipient;
        assert _amount == _cachedAmount;
    }  else if (transferSig(f)) {
        transfer(e, _recipient, _amount);

        assert e.msg.sender == _cachedSender;
        assert _recipient == _cachedRecipient;
        assert _amount == _cachedAmount;
    }  else if (transferNoChecksSig(f)) {
        forwardTransferFromNoChecks(e, _owner, _recipient, _amount);

        assert _owner == _cachedSender;
        assert _recipient == _cachedRecipient;
        assert _amount == _cachedAmount;
    } else {
        satisfy true;
    }
}


rule afterTokenTransfer_revertConditions(env e, address _owner, address _spender, uint256 _amount) {
    havoc userSolvency;
    bool checks = getStorage(e).transferWithChecks;
    bool senderIsSolvent = getSolvency(e, _owner);

    afterTokenTransfer@withrevert(e, _owner, _spender, _amount);
    bool _cachedRevert = lastReverted;

    assert (checks && _owner != 0 && _spender != 0 && !senderIsSolvent) == _cachedRevert;
}

rule solvencyCheck(method f, env e, calldataarg args) {
    balanceHasBeenUpdated = false;
    totalSupplyHasBeenUpdated = false;
    reentrancyProtection = true;

    f@withrevert(e, args);
    bool _cachedRevert = lastReverted;

    bool c1 = balanceHasBeenUpdated;
    bool c2 = !totalSupplyHasBeenUpdated;
    bool c3 = !getSolvency(e, _cachedOwner);

    bool t1 = (transferFromSig(f) || transferSig(f));
    bool checks = getStorage(e).transferWithChecks;

    assert (c1 && c1 && c3) =>
        (
            (_cachedRevert == t1)
            ||
            (!_cachedRevert == (!checks && transferNoChecksSig(f) || t1))
        );

}

rule decimals(env e) {
    require e.msg.value == 0; // causes a revert and a dump (think it breaks CVL?)
    uint8 returnedDecimals = decimals@withrevert(e);
    assert (decimalsMock() + require_uint8(3) == returnedDecimals) && _decimalsCalled && !lastReverted;
}

definition burnSig(method f) returns bool = f.selector == sig:Harness.burn(address,address,uint256).selector;
definition mintSig(method f) returns bool = f.selector == sig:Harness.mint(address,address,uint256).selector;
definition transferFromSig(method f) returns bool = f.selector == sig:Harness.transferFrom(address, address, uint256).selector;
definition transferSig(method f) returns bool = f.selector == sig:Harness.transfer(address, uint256).selector;
definition transferNoChecksSig(method f) returns bool = f.selector == sig:Harness.forwardTransferFromNoChecks(address, address, uint256).selector;

definition ERC20Transfers(method f) returns bool = burnSig(f) || mintSig(f) || transferSig(f) || transferFromSig(f) || transferNoChecksSig(f);
