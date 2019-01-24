# Import libraries for trading strategy
from scipy import stats
import numpy as np
from math import *

# Function that contains our investment logic. Edit this to change how the RL brain acts
# This is a simple boilerplate trading strategy that should be modified to yield better returns
# ** If you are changing the trading strategy, keep 0 for Sell and 1 for Buy ** 
def state_logic(pointer, data):
    # BSM for if the option's exercise price appreciates by 5%
    price_increase = calculate_BSM(data['EQUITY'][pointer],
                                   data['EQUITY'][pointer] * 1.05, # 5% appreciation
                                   data['RF'][pointer] / 100,
                                   data['SIGMA'][pointer] / 100, 30.42 # Roughly one month timeframe
                                   / 365.0)
    # BSM for if the option's exercise price holds its value
    stable_price = calculate_BSM(data['EQUITY'][pointer], data['EQUITY'
                                 ][pointer], data['RF'][pointer] / 100,
                                 data['SIGMA'][pointer] / 100, 30.42
                                 / 365.0)
    # Tinker with this 
    returns = log(stable_price / price_increase)
    # Tinker with the return threshold as well
    if returns <= 2:
        return 0  # Sell
    if returns > 2:
        return 1  # Buy

# Black-Scholes Model function needed for our current state logic
def calculate_BSM(
    Equity,
    Strike_Price,
    RF_Rate,
    MKT_Vol,
    TimeFrame,
    ):
    d1 = (np.log(Equity / Strike_Price) + (RF_Rate + 0.5 * MKT_Vol
          ** 2) * TimeFrame) / (float(MKT_Vol) * np.sqrt(TimeFrame))
    d2 = (np.log(Equity / Strike_Price) + (RF_Rate - 0.5 * MKT_Vol
          ** 2) * TimeFrame) / (float(MKT_Vol) * np.sqrt(TimeFrame))
    value = Equity * stats.norm.cdf(d1, 0.0, 1.0) - Strike_Price \
        * np.exp(-RF_Rate * TimeFrame) * stats.norm.cdf(d2, 0.0, 1.0)
    return value
