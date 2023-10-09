## Silo Core
Silo is the main component of the protocol. It implements lending logic, manages and isolates risk, acts as a vault for assets, and performs liquidations. Each Silo is composed of the two asset for which it was created and is immutable after being created. Creation of the Silo is permission less and can be done via [Silo Factory](https://github.com/silo-finance/silo-contracts-v2/blob/develop/silo-core/contracts/SiloFactory.sol).

|<img src="./docs/_images/silo_v2_core_architecture.jpeg" alt="Silo V2 core architecture" title="Silo V2 core architecture">|
|:--:| 
| Silo V2 core architecture |

### Silo shares tokens
For each asset in a Silo, there are two [ERC-20](https://github.com/silo-finance/silo-contracts-v2/blob/develop/silo-core/contracts/utils/ShareToken.sol) tokens deployed and one [ERC20R](https://github.com/silo-finance/silo-contracts-v2/blob/develop/silo-core/contracts/utils/ShareDebtToken.sol):
- [Share collateral token](https://github.com/silo-finance/silo-contracts-v2/blob/develop/silo-core/contracts/utils/ShareCollateralToken.sol) (ERC-20). This token represent a user deposited assets that can be borrowed.
- [Share protected collateral token](https://github.com/silo-finance/silo-contracts-v2/blob/develop/silo-core/contracts/utils/ShareCollateralToken.sol)(ERC-20). This token represent a user deposited assets that can't be borrowed.
- [Share debt token](https://github.com/silo-finance/silo-contracts-v2/blob/develop/silo-core/contracts/utils/ShareDebtToken.sol)(ERC20R). This tokens will be minted to represent a debt.

When the user deposits into a Silo they can decide where their deposit can be borrowed by other users to earn interest. Protected deposits are also called "collateral only" and other users cannot borrow them.

Silo uses the mint and burn functions to operate these underlying tokens. Meanwhile, the transfer is still available and can be used by any third-party application (MetaMask, DEX, etc...). Underlying tokens support hooks and can notify about transfer operation third party smart contract. This simple hook provides enough information to reverse engineer exact action that is happening in the core protocol. See [HookReceiver](https://github.com/silo-finance/silo-contracts-v2/blob/develop/silo-core/contracts/utils/HookReceiver.sol) which notifies the [gauge](https://github.com/silo-finance/silo-contracts-v2/blob/develop/ve-silo/contracts/gauges/ethereum/SiloLiquidityGauge.vy#L396) whenever the balance is updated.

### Price oracle
The role of an oracle is to provide Silo with the correct price of an asset. Each oracle to work with Silo should implement [ISiloOracle](https://github.com/silo-finance/silo-contracts-v2/blob/develop/silo-core/contracts/interfaces/ISiloOracle.sol) interface. Price Oracle for each token is optional. Both tokens may have one or just one or none.

Each token may use up to two oracles: [solvency](https://github.com/silo-finance/silo-contracts-v2/blob/7f82b14ee8da33dfdccde99e0fe8c48a0a126aad/silo-core/contracts/interfaces/ISiloConfig.sol#L45) oracle and [maxLtv](https://github.com/silo-finance/silo-contracts-v2/blob/7f82b14ee8da33dfdccde99e0fe8c48a0a126aad/silo-core/contracts/interfaces/ISiloConfig.sol#L46) oracle. Solvency oracle is used to calculate if user is [solvent](https://github.com/silo-finance/silo-contracts-v2/blob/7f82b14ee8da33dfdccde99e0fe8c48a0a126aad/silo-core/contracts/lib/SiloSolvencyLib.sol#L39). MaxLtv oracle is used to decided if user can borrow assets he wants to borrow. MaxLtv is always below liquidation threshold which is a value used for solvency math.

Each token can use solvency and maxLtv oracles, just solvency oracle, just maxLtv oracle or none. If both oracles are setup, each is used for its designed purpose. If only solvency oracle is setup, maxLtv calculations will fallback to using solvency oracle. If only maxLtv oracle is setup, maxLtv calculation will use it but solvency calculations will default prices to "1". If no oracle is setup, all prices are assumed to be "1". In practice, if token0 has no oracle setup, it means token1 has oracle that is returning the price of token1 in token0.
- [Chainlink V3 oracle](https://github.com/silo-finance/silo-contracts-v2/tree/develop/silo-oracles/contracts/chainlinkV3) is an oracle module that is responsible for pulling the correct prices of a given asset from [Chainlink Price Feeds](https://docs.chain.link/data-feeds/price-feeds/addresses?network=ethereum&page=1).
- [Uniswap V3 oracle](https://github.com/silo-finance/silo-contracts-v2/tree/develop/silo-oracles/contracts/uniswapV3) is an oracle module that is responsible for pulling the correct prices of a given asset from [UniswapV3 pools](https://info.uniswap.org/#/pools). It performs security checks and returns TWAP prices when requested.
- [DIA oracle](https://github.com/silo-finance/silo-contracts-v2/tree/develop/silo-oracles/contracts/dia) is an oracle module that is responsible for pulling the correct prices of a given asset from [DIA Price Feeds](https://www.diadata.org/app/source/defi/).

### Interest rate model
The interest rate model is a mathematical algorithm used by the protocol to automatically set the borrowing interest rate (also known as the borrowing APY) and is created for each Silo asset with its configuration. [Silo Interest model V2](https://github.com/silo-finance/silo-contracts-v2/blob/develop/silo-core/contracts/interestRateModel/InterestRateModelV2.sol) is a dynamic interest rate model. In control-theoretic parlance, we designed a [PI controller](https://en.wikipedia.org/wiki/Proportional%E2%80%93integral%E2%80%93derivative_controller#PI_controller) with a deadband in the proportional term and some other modifications. With the current model we achieve following goals:
- Optimal operation where the system reach a stable equilibrium state at an optimal utilization level $Uopt$, i.e., to keep the utilization in a neighborhood of $Uopt$ while holding the interest rate relatively constant.
- Utilization stays below a critical level $Ucrit$ even in volatile market conditions as a safety measure to ensure liquidity.
- Attractive interest rate for borrowers. The interest rate quickly react when utilization drops too low (below a certain level $Ulow$).
- Guaranteed returns on deposits even if the utilization is low, Silo interest rate model will keep small but non-zero interest rate.

|<img src="./docs/_images/silo_v2_interest_rate_model.jpeg" alt="Silo interest rate model visualization" title="Silo interest rate model visualization">|
|:--:| 
| Silo interest rate model visualization |

### Silo ERC-4626
Each Silo is standardized yield-bearing vault as it implements [ERC-4626 interface](https://github.com/silo-finance/silo-contracts-v2/blob/develop/silo-core/contracts/utils/SiloERC4626.sol). For more information see [ERC-4626 tokenized vault standard](https://ethereum.org/en/developers/docs/standards/tokens/erc-4626/).

### Silo EIP-3156
Silo provides standard interfaces and processes for single-asset flash loans([IERC3156FlashBorrower](https://github.com/silo-finance/silo-contracts-v2/blob/develop/silo-core/contracts/interfaces/IERC3156FlashBorrower.sol), [IERC3156FlashLender](https://github.com/silo-finance/silo-contracts-v2/blob/develop/silo-core/contracts/interfaces/IERC3156FlashLender.sol)). For more information see [EIP-3156](https://eips.ethereum.org/EIPS/eip-3156)