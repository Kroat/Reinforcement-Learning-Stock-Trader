# Reinforcement Learning Stock Trader
## What:
This Reinforcement Learning Stock Trader uses Q-Learning, along with some basic price modeling with the Black-Scholes-Model to trade equities found on Yahoo Finance. 

## Simple Quick Guide
To use:

1. Make sure all necessary libraries are installed: Numpy, Pandas, Scipy
1. Copy RL-Trader.py to a project directory
2. cd into the project directory
3. Pass the following commmand: ```RL-Trader.py [EQUITY] [START DATE - DAY/MONTH/YEAR]```

For example: ```RL-Trader.py F 1/1/2000```

This runs the RL script against Ford's historical data and shows trades the logic would make, the resulting Q-Table at the end, as well as the profit.

## What this code does well (so far)

I have found that this script works especially well against times of economic contraction. It works less well against FANG securities and volatility indicies. This may be adjusted by changing attributes in the ```state_logic``` function.

## Reinforcement Learning Logic

Unlike other Reinforcement Learning scripts, it is better to keep the greedy factor (Epsilon) low (around .05-.1) as it increases the amount of analytical decisions the script makes. Because markets have a stochastic factor, it did not make sense to have the script choose a random 'buy' or 'sell' call, but instead use logic an analyist might use (this is under ```state_logic```), only maximizing when there is enough data in the Q-Table (analagous to traders using trading strategies that have worked before).
