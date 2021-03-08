import numpy as np
import pandas as pd
from datetime import datetime
import time


TICKER = 'AAPL'


# Get Income Statement Formatted
def get_stock_income_statement_DataFrame(df_income):  # TICKER

    stock = df_income
    stock.drop('date', axis=1, inplace=True)
    new_index = []
    for date in stock.columns:
        new_index.append(datetime.strptime(date.replace(
            date[len(date)-3:len(date)], ''), '%Y-%m-%d'))
    stock.rename(columns=dict(
        zip(stock.columns[:len(stock.columns)], new_index)), inplace=True)
    stock = stock.T
    stock.dropna(axis=1, inplace=True)
    stock = stock.reindex(index=stock.index[::-1])
    return stock[['revenue', 'netIncome', 'EPS']]


# Get Balance Sheet Formatted
def get_stock_balance_sheet_DataFrame(df_balance):  # TICKER

    stock = df_balance
    new_index = []
    for date in stock.index:
        new_index.append(datetime.strptime(date, '%Y-%m-%d'))
    stock.rename(index=dict(
        zip(stock.index[:len(stock.index)], new_index)), inplace=True)
    stock.dropna(axis=1, inplace=True)
    stock = stock.reindex(index=stock.index[::-1])
    return stock[['totalDebt', 'totalStockholdersEquity', 'retainedEarnings', 'totalAssets', 'totalLiabilities']]


def reindex_stock_df(df):
    new_df = pd.DataFrame()
    new_df = df.copy()
    new_df.index = np.arange(1, len(df.index)+1)
    return new_df


def format_date(date_datetime):
    date_timetuple = date_datetime.timetuple()
    date_mktime = time.mktime(date_timetuple)
    date_int = int(date_mktime)
    date_str = str(date_int)
    return date_str

# Get Closing Price Historical Data From Yahoo Finnace


def get_yahoo_finance_historial_data(TICKER, period1, period2):
    # Import stock historical prices from period 1 and perid 2
    df = pd.read_csv(
        f'https://query1.finance.yahoo.com/v7/finance/download/{TICKER}?period1={period1}&period2={period2}&interval=1mo&events=history&includeAdjustedClose=true', index_col='Date')

    # Reindex the date with datetime
    new_index = []
    for date in df.index:
        new_index.append(datetime.strptime(date, '%Y-%m-%d'))
    df.rename(index=dict(
        zip(df.index[:len(df.index)], new_index)), inplace=True)

    # Relocate the data from 2010, which is 10 years from now - THIS HAS TO BE FIXED TO BE DYNAMIC
    new_df = pd.DataFrame()
    for date in df.loc['20100901':].index:
        if date.month == 10:  # Gets the October of every month - THIS IS GOOD!
            new_df = pd.concat([new_df, df.loc[date]], axis=1)
    new_df = new_df.T
    new_df = new_df['Close']
    new_df = reindex_stock_df(new_df)
    return new_df


def get_final_stock_df(df_income, df_balance):
    # Get Income Statement Dataframe and relocate for the last 10 years
    stock_income_statement = get_stock_income_statement_DataFrame(df_income)
    stock_income_statement = stock_income_statement.loc['20100101':]

    # Get Balance Sheet Datagrame and relocate for the last 10 years
    stock_balance_sheet = get_stock_balance_sheet_DataFrame(df_balance)
    stock_balance_sheet = stock_balance_sheet.loc['20100101':]

    # Get Debt to Equity Ration in Dataframe
    stock_balance_sheet['Debt to Equity'] = stock_balance_sheet['totalDebt'] / \
        stock_balance_sheet['totalStockholdersEquity']

    # Reformat Dataframe
    stock_income_statement = reindex_stock_df(stock_income_statement)
    stock_balance_sheet = reindex_stock_df(stock_balance_sheet)

    # Get Yahoo Historical Price Closing Dataframe
    period1 = format_date(datetime(2011, 9, 1))
    period2 = format_date(datetime(2020, 10, 1))
    yahoo_finance_historial_closing_df = get_yahoo_finance_historial_data(
        TICKER, period1, period2)

    # Get Final Dataframe
    final_stock_df = pd.concat(
        [stock_income_statement, stock_balance_sheet, yahoo_finance_historial_closing_df], axis=1)

    # Get more financial ratios
    final_stock_df['peRatio'] = final_stock_df['Close'] / final_stock_df['EPS']
    final_stock_df['sharesOutstanding'] = final_stock_df['netIncome'] / \
        final_stock_df['EPS']
    final_stock_df['BVPS'] = (final_stock_df['totalAssets'] -
                              final_stock_df['totalLiabilities']) / final_stock_df['sharesOutstanding']
    final_stock_df['BVPS'] = (final_stock_df['totalAssets'] -
                              final_stock_df['totalLiabilities']) / final_stock_df['sharesOutstanding']

    # Return Final Dataframe
    return final_stock_df
