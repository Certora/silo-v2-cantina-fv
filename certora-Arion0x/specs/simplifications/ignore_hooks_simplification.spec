methods{
    function _._hookCallBeforeWithdraw(ISilo.WithdrawArgs calldata) internal => NONDET;
    function _._hookCallAfterWithdraw(ISilo.WithdrawArgs calldata,uint256,uint256) internal => NONDET;
    function _._hookCallBeforeBorrow(ISilo.BorrowArgs memory,uint256) internal => NONDET;
    function _._hookCallAfterBorrow(ISilo.BorrowArgs memory,uint256,uint256,uint256) internal => NONDET;
    function _._hookCallBeforeTransitionCollateral(ISilo.TransitionCollateralArgs memory) internal => NONDET;
    function _._hookCallAfterTransitionCollateral(ISilo.TransitionCollateralArgs memory,uint256,uint256) internal => NONDET;
    function _._hookCallBeforeDeposit(ISilo.CollateralType,uint256,uint256,address) internal => NONDET;
    function _._hookCallAfterDeposit(ISilo.CollateralType,uint256,uint256,address,uint256,uint256) internal => NONDET;
}