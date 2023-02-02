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
    Main entry point of app.
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
    df = pd.read_excel(f'../data/portfolios.xlsx')
    return df


def load_cashrisks():
    df = pd.read_csv(f'../data/cashrisks.csv')
    return df


def fx_risks() -> Dict[str, Any]:
    portfolios = fx.get_all()
    all_risks = {}
    for portfolio in portfolios.get('Value'):
        all_risks.update({portfolio: fx.get_portfolio(portfolio, dt.date.today()).get('Value')})
    return all_risks


def derivatives_risk():
    portfolios = derivatives.get_all()
    all_risks = {}
    for portfolio in portfolios.get('Value'):
        all_risks.update({portfolio: derivatives.get_portfolio(portfolio, dt.date.today()).get('Value')})
    return all_risks


def hedge(df: pd.DataFrame()):
    df = df
    df1 = df[['client', 'risk_assets', 'risk_liabilities']].copy()
    grouped = df1.groupby("client")
    grouped_sum = grouped.sum()
    grouped_sum['hedge_ratio'] = abs(grouped_sum['risk_assets'] / grouped_sum['risk_liabilities'])
    return grouped_sum


if __name__ == '__main__':
    main()
