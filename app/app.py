import sys  # Keep at top to add to add root dir to PYTHONPATH.
from pathlib import Path  # Keep at top to add to add root dir to PYTHONPATH.

root = Path(__file__).parent.parent  # Keep at top to add to add root dir to PYTHONPATH.
sys.path.append(str(root))  # Keep at top to add to add root dir to PYTHONPATH.

import pandas as pd
import datetime as dt
from api import derivatives, fx
from typing import Any, Dict


def main():
    """
    Runs the steps needed to obtain the associated risks per portfolio and the hedge ratio per client.

    :return: Prints the hedge ratio for each client.
    """
    portfolio_data = load_portfolios()
    cashrisks_data = load_cashrisks()
    cashrisks_dict = dict(zip(cashrisks_data['portfolio'], cashrisks_data['risk']))
    fxrisks_data = fx_risks()
    derivative_data = derivatives_risk()
    portfolio_data['risk_assets'] = portfolio_data['portfolio'].map(fxrisks_data)
    portfolio_data.loc[portfolio_data['risk_assets'].isnull(), 'risk_assets'] = portfolio_data['portfolio'].map(
        derivative_data)
    portfolio_data['risk_liabilities'] = portfolio_data['portfolio'].map(cashrisks_dict)
    portfolio_data.to_excel(f'../data/portfolios_inclRisk.xlsx', index=False)
    hedge_result = hedge(portfolio_data)
    print(hedge_result)


def load_portfolios():
    """
    Method to load a dataset containing portfolio data for clients.

    :return: A dataframe containing the portfolio data.
    """
    df = pd.read_excel(f'../data/portfolios.xlsx')
    return df


def load_cashrisks():
    """
    Method to load a dataset containing cash risk data for cash portfolios.

    :return: A dataframe containing the cash risks.
    """
    df = pd.read_csv(f'../data/cashrisks.csv')
    return df


def fx_risks() -> Dict[str, Any]:
    """
    Method to obtain fx risk data for fx portfolios via an API.

    :return: A dictionary containing the fx risk data.
    """
    portfolios = fx.get_all()
    all_risks = {}
    for portfolio in portfolios.get('Value'):
        all_risks.update({portfolio: fx.get_portfolio(portfolio, dt.date.today()).get('Value')})
    return all_risks


def derivatives_risk():
    """
    Method to obtain derivative risk data for derivative portfolios via an API.

    :return: A dictionary containing the derivative risk data.
    """
    portfolios = derivatives.get_all()
    all_risks = {}
    for portfolio in portfolios.get('Value'):
        all_risks.update({portfolio: derivatives.get_portfolio(portfolio, dt.date.today()).get('Value')})
    return all_risks


def hedge(df: pd.DataFrame()):
    """
    Method to sum the asset risks and liability risks per client and calculate the hedge ratio per client

    :param df: A dataframe containing portfolio data for each portfolio.
    :return: A dataframe containing the risk and hedge ratio per client.
    """
    df = df
    df1 = df[['client', 'risk_assets', 'risk_liabilities']].copy()
    grouped = df1.groupby("client")
    grouped_sum = grouped.sum()
    grouped_sum['hedge_ratio'] = abs(grouped_sum['risk_assets'] / grouped_sum['risk_liabilities'])
    return grouped_sum


if __name__ == '__main__':
    main()
