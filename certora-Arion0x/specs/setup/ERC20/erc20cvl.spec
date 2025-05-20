methods {
    // ERC20 standard
    function _.name()                                           external => PER_CALLEE_CONSTANT;
    function _.symbol()                                         external => PER_CALLEE_CONSTANT;
    function _.decimals()                                       external => PER_CALLEE_CONSTANT;
    function _.totalSupply()                                    external => totalSupplyCVL(calledContract) expect uint256;
    function _.balanceOf(address a)                             external => balanceOfCVL(calledContract, a) expect uint256;
    function _._balanceOf(address _token, address _user)        internal => balanceOfCVL(_token,_user) expect uint256;
    function _.allowance(address a, address b)                  external => allowanceCVL(calledContract, a, b) expect uint256;
    function _.approve(address a, uint256 x)                    external with (env e) => approveCVL(calledContract, e.msg.sender, a, x) expect bool;
    function _.transfer(address a, uint256 x)                   external with (env e) => transferCVL(calledContract, e.msg.sender, a, x) expect bool;
    function _._transfer(address from, address to, uint256 x) internal  with (env e) => transferCVL(calledContract,from, to, x) expect bool;
    function _.safeTransfer(address token, address a, uint256 x)external with (env e) => transferCVL(token, e.msg.sender, a, x) expect bool;

    function _.transferFrom(address a, address b, uint256 x)    external with (env e) => transferFromCVL(calledContract, e.msg.sender, a, b, x) expect bool;
    function _.safeTransferFrom(address a, address b, uint256 x) external with (env e) => transferFromCVL(calledContract, e.msg.sender, a, b, x) expect bool;
    // Mint and burn functionality 
    function _.mint(address owner, address spender, uint256 amount) external with (env e) => mintCVL(calledContract, owner, spender, amount) expect bool;
    function _._mint(address owner, uint256 amount) internal with (env e) => mintCVL(calledContract, owner, 0, amount) expect bool;
    function _.burn(address owner, address spender, uint256 amount) external with (env e) => burnCVL(calledContract, owner, spender, amount) expect bool;
    function _._burn(address owner, uint256 amount) internal with (env e) => burnCVL(calledContract, owner, 0, amount) expect bool;

    // balanceOfAndTotalSupply
    function _.balanceOfAndTotalSupply(address account) external => balanceOfAndTotalSupplyCVL(calledContract, account) expect (uint256, uint256);
}

/// CVL simple implementations of IERC20:
/// token => totalSupply
ghost mapping(address => uint256) totalSupplyByToken;
/// token => account => balance
ghost mapping(address => mapping(address => uint256)) balanceByToken;
/// token => owner => spender => allowance
ghost mapping(address => mapping(address => mapping(address => uint256))) allowanceByToken;

function totalSupplyCVL(address token) returns uint256 {
    return totalSupplyByToken[token];
}

function balanceOfCVL(address token, address account) returns uint256 {
    return balanceByToken[token][account];
}

function allowanceCVL(address token, address owner, address spender) returns uint256 {
    return allowanceByToken[token][owner][spender];
}

function balanceOfAndTotalSupplyCVL(address token, address account) returns (uint256, uint256) {
    return (balanceByToken[token][account], totalSupplyByToken[token]);
}

function approveCVL(address token, address approver, address spender, uint256 amount) returns bool {

    allowanceByToken[token][approver][spender] = amount;
    return true;
}

function transferFromCVL(address token, address spender, address from, address to, uint256 amount) returns bool {

    // if (allowanceByToken[token][from][spender] < amount) return false;
    allowanceByToken[token][from][spender] = require_uint256(allowanceByToken[token][from][spender] - amount);
    return transferCVL(token, from, to, amount);
}

function transferCVL(address token, address from, address to, uint256 amount) returns bool {
    if (from == to) return false;

    // if (balanceByToken[token][from] < amount) return false;
    balanceByToken[token][from] = require_uint256(balanceByToken[token][from] - amount);
    balanceByToken[token][to] = require_uint256(balanceByToken[token][to] + amount); // neglect overflows.
    return true;
}

function mintCVL(address token, address owner, address spender, uint256 amount) returns bool {

    // if (owner != spender) {
    //     if (allowanceByToken[token][owner][spender] < amount) return false;
    //     allowanceByToken[token][owner][spender] = assert_uint256(allowanceByToken[token][owner][spender] - amount);
    // }

    totalSupplyByToken[token] = require_uint256(totalSupplyByToken[token] + amount); // Neglect overflows.
    balanceByToken[token][owner] = require_uint256(balanceByToken[token][owner] + amount); // Neglect overflows.
    return true;
}

function burnCVL(address token, address owner, address spender, uint256 amount) returns bool {

    // if (balanceByToken[token][owner] < amount) return false;

    // if (owner != spender) {
    //     if (allowanceByToken[token][owner][spender] < amount) return false;
    //     allowanceByToken[token][owner][spender] = assert_uint256(allowanceByToken[token][owner][spender] - amount);
    // }

    balanceByToken[token][owner] = require_uint256(balanceByToken[token][owner] - amount);
    totalSupplyByToken[token] = require_uint256(totalSupplyByToken[token] - amount);
    return true;
}
