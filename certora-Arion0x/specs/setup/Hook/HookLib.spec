methods{
    function Hook.matchAction(uint256 _action,uint256 _expectedHook) internal returns bool =>CVLMatchAction(_action,_expectedHook);
    function Hook.depositAction(ISilo.CollateralType _type) internal returns uint256 => CVLDepositAction(_type);
    function Hook.withdrawAction(ISilo.CollateralType _type) internal returns uint256 => CVLWithdrawAction(_type);
    function Hook.transitionCollateralAction(ISilo.CollateralType _type) internal returns uint256 => CVLTransitionCollateralAction(_type);
    function Hook.shareTokenTransfer(uint256 tokenType) internal returns uint256 => CVLShareTokenTransfer(tokenType);
}

definition NONE() returns uint256 = 0;
definition DEPOSIT() returns uint256 = 1 << 1;
definition BORROW() returns uint256 = 1 << 2;
definition BORROW_SAME_ASSET() returns uint256 = 1 << 3;
definition REPAY() returns uint256 = 1 << 4;
definition WITHDRAW() returns uint256 = 1 << 5;
definition FLASH_LOAN() returns uint256 = 1 << 6;
definition TRANSITION_COLLATERAL() returns uint256 = 1 << 7;
definition SWITCH_COLLATERAL() returns uint256 = 1 << 8;
definition LIQUIDATION() returns uint256 = 1 << 9;
definition SHARE_TOKEN_TRANSFER() returns uint256 = 1 << 10;
definition COLLATERAL_TOKEN() returns uint256 = 1 << 11;
definition PROTECTED_TOKEN() returns uint256 = 1 << 12;
definition DEBT_TOKEN() returns uint256 = 1 << 13;



/// @notice Checks if the action has a specific hook
/// @param _action The action
/// @param _expectedHook The expected hook
/// @dev The function returns true if the action has the expected hook.
/// As hooks actions can be combined with bitwise OR, the following examples are valid:
/// `matchAction(WITHDRAW | COLLATERAL_TOKEN, WITHDRAW) == true`
/// `matchAction(WITHDRAW | COLLATERAL_TOKEN, COLLATERAL_TOKEN) == true`
/// `matchAction(WITHDRAW | COLLATERAL_TOKEN, WITHDRAW | COLLATERAL_TOKEN) == true`

function CVLMatchAction(uint256 _action,uint256 _expectedHook) returns bool{
    return (_action & _expectedHook) == _expectedHook;
}


/// @notice Returns the action for depositing a specific collateral type
/// @param _type The collateral type
function CVLDepositAction(ISilo.CollateralType _type) returns uint256 {
    return DEPOSIT() | (_type == ISilo.CollateralType.Collateral ? COLLATERAL_TOKEN() : PROTECTED_TOKEN());
}

/// @notice Returns the action for withdrawing a specific collateral type
/// @param _type The collateral type
function CVLWithdrawAction(ISilo.CollateralType _type) returns uint256 {
    return WITHDRAW() | (_type == ISilo.CollateralType.Collateral ? COLLATERAL_TOKEN() : PROTECTED_TOKEN());
}

/// @notice Returns the action for collateral transition
/// @param _type The collateral type
function CVLTransitionCollateralAction(ISilo.CollateralType _type) returns uint256 {
    return TRANSITION_COLLATERAL() | (_type == ISilo.CollateralType.Collateral ? COLLATERAL_TOKEN() : PROTECTED_TOKEN());
}

/// @notice Returns the share token transfer action
/// @param _tokenType The token type (COLLATERAL_TOKEN || PROTECTED_TOKEN || DEBT_TOKEN)
function CVLShareTokenTransfer(uint256 _tokenType) returns uint256 {
    return SHARE_TOKEN_TRANSFER() | _tokenType;
}

