// Define the base storage location for the ShareTokenStorage struct
definition STORAGE_SLOT_SHARE_TOKEN_STORAGE() returns uint256
    = 0x01b0b3f9d6e360167e522fa2b18ba597ad7b2b35841fec7e1ca4dbb0adea1200;
      
// Define the slots for each field in the struct:

// Slot 0: silo (address, 20 bytes)
// Slot 1: siloConfig (address, 20 bytes)
// Slot 2: hookSetup (packed struct with 4 fields)
//    - hookReceiver (address, 20 bytes)
//    - hooksBefore (uint24)
//    - hooksAfter (uint24)
//    - tokenType (uint24)
// Slot 3: transferWithChecks (bool, 1 byte)

definition STORAGE_SLOT_HOOK_SETUP() returns mathint
    = STORAGE_SLOT_SHARE_TOKEN_STORAGE() + 2;

definition STORAGE_SLOT_TRANSFER_WITH_CHECKS() returns mathint
    = 0x1b0b3f9d6e360167e522fa2b18ba597ad7b2b35841fec7e1ca4dbb0adea1203;

//
// Ghost variables to mirror the fields in hookSetup and transferWithChecks:
//
ghost mapping(address => address) ghostHookReceiver;
ghost mapping(address => mathint) ghostHooksBefore; // represents uint24 hooksBefore
ghost mapping(address => mathint) ghostHooksAfter;  // represents uint24 hooksAfter
ghost mapping(address => mathint) ghostTokenType;  // represents uint24 tokenType
ghost mapping(address => bool) ghostTransferWithChecks; // represents bool (0 or 1)
