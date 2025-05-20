methods {

    function _.synchronizeHooks(uint24,uint24) external 
            => synchronizeHooks__noStateChange() expect void;
    function _.hookReceiverConfig(address) external 
            => hookReceiverConfig__noStateChange() expect (uint24, uint24); 
    function _.reentrancyGuardEntered() external 
            => reentrancyGuardEntered__noStateChange() expect bool;

   

}

function synchronizeHooks__noStateChange() {
   // no state change but needed to avoid DEVAULT HAVOC
}

function hookReceiverConfig__noStateChange() returns (uint24, uint24) {
   // no state change but needed to avoid DEVAULT HAVOC
   return (0, 0);
}

function reentrancyGuardEntered__noStateChange() returns bool {
   // no state change but needed to avoid DEVAULT HAVOC
   bool anyBool;
   return anyBool;
}