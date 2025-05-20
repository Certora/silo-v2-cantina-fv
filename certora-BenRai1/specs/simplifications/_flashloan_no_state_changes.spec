methods {

    function _.onFlashLoan(address, address, uint256, uint256, bytes) external 
            => onFlashLoan__noStateChange() expect bytes32;

   

}

function onFlashLoan__noStateChange() returns bytes32 {
   return keccak256("ERC3156FlashBorrower.onFlashLoan");
}