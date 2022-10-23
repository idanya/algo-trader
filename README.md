# algo-trader 
Trading strategies builder, backtester and realtime trader.

## Intro
algo-trader is an implementation of an algorithmic trading strategy executer and backtester.
Capable of backtesting strategies locally and trade them in realtime via your broker API.

algo-trader is written in Python, and it's current stack compose of:
1. MongoDB as a backend data store for backtesting strategies
2. [tulipy](https://github.com/jesse-ai/tulipy) - Python bindings for [Tulip Indicators](https://tulipindicators.org/). Used to provide technical indicators calculations.
3. ib_client (Optional) - Python library to communicate with Interactive Brokers gateway. Only needed if you plan on doing real trading via IB.  

## Architecture

![System design](./design/diagram.png)

### Sources
A [Source](src/pipeline/source.py) is an implementation of a Candle Iterator. This is the starting point of the pipeline and the "source" for the incoming candles processed.
 
### Processors
[Processor](src/pipeline/processor.py) is the basic processing unit in the pipeline. Processors can be constructed in any order while Candles are flowing from the source, forward through all processors. 
Each processor is responsible on sending the candles it processes to the next processor (unless it has a reason not to).

The `process()` function gets with each candle also an object called [`SharedContext`](src/pipeline/shared_context.py). 
The context is basically an instance of an in-memory KV store to share context and information between processors. 

Another way to share data between processors is to make use of the `attachments` field on the Candle itself. 
This field is intended for metadata on the candle, like calculations and state relevant for that candle point in time. Candle attachments are persistent throughout the pipeline.

#### Reprocessing
Reprocessing is a feature that enables a processor to re-send an already processed candle to the next processor. 
Reprocessing is useful for processors that does some logic outside the main flow of the pipeline. for example, upon events, external triggers, market/trade providers events/issues etc...
Example for reprocessing can be found in the [AssetCorrelationProcessor](src/pipeline/processors/assets_correlation.py)

### Events
An [Event](src/entities/event.py) as it name suggests, defines an event that was occurred in the system. 
It follows the same flow as the Candles, passing between processors. Each processor is responsible on propagating the event to the next processor (if needed).

Because a pipelines are data driven and not time driven, events can be used as checkpoints to indicated something happened in the datastream. 
For example, running the same pipeline from a DB source and from a Realtime market data source can have different effect if processor were to relay on time.

_It is crucial to have the same behaviour when fast-running from DB and realtime for backtesting to be useful._

### Strategies
Strategies are executed per candle by the [StrategyProcessor](src/pipeline/processors/strategy.py).
A strategy is responsible on executing the trading logic and dispatching Signals ([StrategySignal](src/entities/strategy_signal.py)). 
On the event a strategy is raising a trading signal, the StrategyProcessor will catch and pass it to the [SignalsExecutor](src/trade/signals_executor.py) for execution.  

### Terminators
A [Terminator](src/pipeline/terminator.py) is an optional final piece of the pipeline. It's executed at the very end of a pipeline when the Source iterator has been fully consumed.
Terminators are useful for unit testing, back testing, and environment cleanups. 


## Running locally
algo-trader is using MongoDB for data storage. In order to run Mongo locally use `docker-compose`.
```shell
docker-compose -f docker-compose.yml up -d
```

## Running tests
* Unit: `./scripts/test-unit.sh`
* Integration (needs IB gateway running): `./scripts/test-integration.sh`
* All: `./scripts/test-all.sh`

