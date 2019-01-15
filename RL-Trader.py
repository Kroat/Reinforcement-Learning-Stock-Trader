# Reinforcement Learning Equity Trader
# By Matija Krolo || github.com/Kroat
# To use:
# 1.) Ensure all necessary libraries are installed on your machine (Numpy, Scipy, Pandas)
# 2.) Place RL-Trader.py in a project directory
# 3.) cd into the project directory
# 4.) Pass the command:
#       RL-Trader.py [EQUITY] [START DATE - DAY/MONTH/YEAR]
#
# ex: RL-Trader.py F 1/1/2000

# ** Please note that this RL script only trades one equity at a time!

# Edit these values to change how the RL brain learns
EPSILON = .1
ALPHA = .1
GAMMA = .1

# Import Libraries
import numpy as np
from scipy import stats
import pandas_datareader.data as web
from math import log
import pandas as pd
import sys, time, datetime

# Welcome message
print "Thanks for using the Reinforcement Learning Stock Trader by Matija Krolo. If you experience an error, it is most likely because the Equity/Stock you chose to analyize does not have available data before the date you entered. If you encounter an error, please check Yahoo.com/finance to ensure it is not the case."
time.sleep(1)

# Get passed-in arguments
GIVEN_EQUITY, START_DATE = sys.argv[1], sys.argv[2]

# Error check arguments
if len(sys.argv) != 3:
    print "To run: RL-Trader.py [EQUITY] [START DATE - DAY/MONTH/YEAR]\nEx. RL-Trader.py F 1/1/2000"
    exit()

# Get Equity Data
CURRENT_MONTH = datetime.datetime
# Todo: create datetime function for user inputs on end dates
EQUITY = web.get_data_yahoo(GIVEN_EQUITY, end='1/1/2019', start=START_DATE,
                            interval='m')
MKT_VOLATIILTY = web.get_data_yahoo('^VIX', end='1/1/2019',
                                    start=START_DATE, interval='m')
RF_Rate = web.get_data_yahoo('^TNX', end='1/1/2019', start=START_DATE,
                             interval='m')

# Don't edit these
STATES = 3
ACTIONS = ['buy', 'sell']
TOTAL_TRADES = len(EQUITY['Close']) 

# Q-Table generator function
def build_q_table(n_states, actions):
    table = pd.DataFrame(np.zeros((n_states, len(actions))),
                         columns=actions)
    return table

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

# Create dictionary
compile_data = {'EQUITY': EQUITY['Adj Close'], 'RF': RF_Rate['Adj Close'
                ], 'SIGMA': MKT_VOLATIILTY['Adj Close']}

# Compile dataframe from dictionary
data = pd.DataFrame(compile_data)

# Agent brain for RL
def choose_trade(pointer, q_table):
    # Find the trade decision from our trade logic
    analytic_decision = state_logic(pointer)
    # Select state from Q-Table
    state_actions = q_table.iloc[select_state(pointer), :]
    # If the greedy factor is less than a randomly distributed number, or if there are no values
    # on the Q-table, return our analytical trade logic decision
    if np.random.uniform() > EPSILON or state_actions.all() == 0:
        return analytic_decision
    # Otherwise, return what has been working
    else:
        maximum = state_actions.idxmax()
        if str(maximum) == 'buy':
            return 0
        if str(maximum) == 'sell':
            return 1

# Selects the state on the Q-Table
def select_state(pointer):
    # Find the current price of the equity
    current_price = round(data['EQUITY'][pointer], 1)
    # Find the previous price of the equity
    previous_price = round(data['EQUITY'][pointer - 1], 1)
    if current_price > previous_price:
        return 0  # Equity Appreciated
    if current_price == previous_price:
        return 1  # Equity Held Value
    if current_price < previous_price:
        return 2  # Equity Depreciated

# Function that contains our investment logic. Edit this to change how the RL brain acts
def state_logic(pointer):
    # BSM for if the option's exercise price appreciates by 5%
    price_increase = calculate_BSM(data['EQUITY'][pointer],
                                   data['EQUITY'][pointer] * 1.05, # 5% appreciation
                                   data['RF'][pointer] / 100,
                                   data['SIGMA'][pointer] / 100, 31.0 # Roughly one month timeframe
                                   / 365.0)
    # BSM for if the option's exercise price holds its value
    stable_price = calculate_BSM(data['EQUITY'][pointer], data['EQUITY'
                                 ][pointer], data['RF'][pointer] / 100,
                                 data['SIGMA'][pointer] / 100, 31.0
                                 / 365.0)
    # Tinker with this 
    returns = log(stable_price / price_increase)
    # Tinker with the return threshold as well
    if returns <= 2:
        return 0  # Sell
    if returns > 2:
        return 1  # Buy

# Function to find the profit from trades
def determine_payoff(pointer, trade):
    # Check to see if the equity is already in the portfolio
    global inPortfolio
    # Hold the value that the equity was purchased at
    global priceAtPurchase
    if inPortfolio:  # Stock is already owned
        if trade == 0:  # Cannot rebuy the equity; return delta
            print 'Holding Equity at $' + str(round(data['EQUITY'
                    ][pointer], 2))
            print 'Purchase Price: $' + str(round(priceAtPurchase, 2))
            inPortfolio = True
            return 0
        if trade == 1:  # Sell the Equity
            inPortfolio = False  # Remove Equity from portfolio
            print '** Equity sold at $' + str(round(data['EQUITY'
                    ][pointer], 2))
            return data['EQUITY'][pointer] - priceAtPurchase
    if inPortfolio == False:  # Equity is not owned
        if trade == 0:  # Buy the equity
            inPortfolio = True  # Add it to the portfolio
            print '** Equity bought at $' + str(round(data['EQUITY'
                    ][pointer], 2))  # Display Price Equity was purchased at
            priceAtPurchase = data['EQUITY'][pointer]  # Record the price at which the Equity was purchased
            return 0
        if trade == 1:  # Sell
            inPortfolio = False
            print 'Out of the market at $' + str(round(data['EQUITY'
                    ][pointer], 2))
            return 0.0

# Don't edit these
priceAtPurchase = 0
inPortfolio = False

# Runs RL script
def run():
    # Builds the Q-Table
    q_table = build_q_table(STATES, ACTIONS)
    global inPortfolio
    # Assuming 0 profit -- or a portfolio with a reference of $0
    profit = 0
    # Move through all possible trades
    for x in range(TOTAL_TRADES):
        # RL brain chooses the trade
        trade = choose_trade(x - 1, q_table)
        # Find the payoff from the trade
        result = determine_payoff(x, trade)
        # Display to user
        print 'Profit from instance: ' + str(round(result, 2))
        # Slows down script
        time.sleep(.05)
        # Append to profit
        profit += result
        q_predict = q_table.iloc[select_state(x), trade]
        # If statement for last trade, tweak this
        if x == TOTAL_TRADES-1:
            q_target = result + GAMMA * q_table.iloc[select_state(x), :
                    ].max()
        else:
            q_target = result + GAMMA * q_table.iloc[select_state(x), :
                    ].max()
        # Append to located cell in Q-Table || Tweak this
        q_table.iloc[select_state(x), trade] += ALPHA * (q_target
                - q_predict)
        print '\n'
    if inPortfolio:
        print "**** Please note that Equity is still held and may be traded later, this may affect profits ****"
    # Return the Q-Table and profit as a tuple
    return (q_table, profit)

# Ensures everything is loaded
if __name__ == '__main__':
    (q_table, profit) = run()
    print '''\r
Q-table:
'''
    # Add reference column
    q_table["Reference"] = ['When Equity Appreciated', 'When Equity Held Value', 'When Equity Depreciated']
    print q_table
    # Show profits
    print 'Profits from trading ' + GIVEN_EQUITY + ': $' + str(round(profit, 2)) 