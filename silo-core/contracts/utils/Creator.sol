// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.21;

contract Creator {
    address private immutable _creator;

    error OnlyCreator();

    constructor() {
        _creator = msg.sender;
    }

    modifier onlyCreator() {
        if (msg.sender != _creator) revert OnlyCreator();
        _;
    }
}