import pandas as pd
from argparse import ArgumentParser
from statics import sdate_def, now_str, input_dir, cache_dir, portfolio_dir
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from classification import load_classification
import pickle
import matplotlib.pyplot as plt

def calc_portfolio(ticker_ls=None, sdate=None, edate=None, backtest= None, invest= None):

    if ticker_ls is None:
        df_index = pd.read_csv(input_dir + 'SP500.txt')
        ticker_ls = df_index['Tickers'].tolist()
    if sdate is None:
        sdate = sdate_def
    if edate is None:
        edate = now_str
    if backtest is None:
        backtest = 3
    if invest is None:
        invest = 1

    portfolio_value = 10000

    back_sdate_dt = datetime.strptime(sdate, '%Y-%m-%d')
    back_sdate = back_sdate_dt.strftime('%Y-%m-%d')

    back_edate_dt = back_sdate_dt + relativedelta(months=+backtest) + timedelta(days=-1)
    back_edate = back_edate_dt.strftime('%Y-%m-%d')

    inv_sdate_dt = back_edate_dt + timedelta(days=1)
    inv_sdate = inv_sdate_dt.strftime('%Y-%m-%d')

    inv_edate_dt = inv_sdate_dt + relativedelta(months=+invest)
    inv_edate = inv_edate_dt.strftime('%Y-%m-%d')

    portfolio_hist = [portfolio_value]
    portfolio_dare = [inv_sdate]

    title = sdate + '_' + edate  + '_' + str(backtest) + 'by' + str(invest)
    while inv_edate < edate:
        top5_ticker = load_classification(sdate=back_sdate_dt.strftime('%Y-%m-%d'),
                                          edate=back_edate_dt.strftime('%Y-%m-%d'))
    
        uninvested = 0
        pnl=0
        for ticker in top5_ticker:
            try:
                with open(cache_dir + ticker) as f:
                    df = pickle.load(f)
                    df_filt = df[(df['date'] >= back_edate) & (df['date'] <= inv_edate)]

                    try:
                        nbr_shares = int(portfolio_value / 5 / float(df_filt.iloc[0]['close']))
                        entry_px = float(df_filt.iloc[1]['open'])
                        uninvested += portfolio_value / 5 - nbr_shares * entry_px
                        exit_px = float(df_filt.iloc[len(df_filt)-1]['close'])
                        ticker_pnl = (exit_px -entry_px) * nbr_shares
                    except:
                        nbr_shares = 0
                        ticker_pnl = 0
                    pnl += ticker_pnl
                    print ticker + ' ' + str(nbr_shares) + ' $' + str(ticker_pnl)
            except:
                print ticker + ' has not data cached'
        portfolio_value += pnl + uninvested
        portfolio_dare.append(inv_edate)
        portfolio_hist.append(portfolio_value)
        print 'total pnl from ' + inv_sdate + ' to ' + inv_edate + ' $'+ str(pnl)
 
        back_sdate_dt = back_sdate_dt + relativedelta(months=+invest)
        back_sdate = back_sdate_dt.strftime('%Y-%m-%d')

        back_edate_dt = back_sdate_dt + relativedelta(months=+backtest) + timedelta(days=-1)
        back_edate = back_edate_dt.strftime('%Y-%m-%d')

        inv_sdate_dt = back_edate_dt + timedelta(days=1)
        inv_sdate = inv_sdate_dt.strftime('%Y-%m-%d')

        inv_edate_dt = inv_sdate_dt + relativedelta(months=+invest)
        inv_edate = inv_edate_dt.strftime('%Y-%m-%d')
    f = plt.figure()
    plt.title(title)
    plt.plot(portfolio_dare, portfolio_hist,color= 'green')
    plt.tight_layout()
    f.savefig(portfolio_dir + title + '.pdf')
    
if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('--ticker_ls', required=False, default=None,
                        help='ticker_ls')
    parser.add_argument('--sdate', required=False, default=None,
                        help='start date')
    parser.add_argument('--edate', required=False, default=None,
                        help='end date')
    parser.add_argument('--backtest', required=False, default=None,
                        help='backtest time horizon')    
    parser.add_argument('--invest', required=False, default=None,
                        help='investment time horizon')
    
    args = parser.parse_args()

    calc_portfolio(ticker_ls = args.ticker_ls,
                   sdate=args.sdate,
                   edate=args.edate,
                   backtest=args.backtest,
                   invest=args.invest)
