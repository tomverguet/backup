import os
import pandas as pd
import quandl
from statics import quandl_api
quandl.ApiConfig.api_key = quandl_api
from statics import sdate_def, now_str, input_dir, cache_dir
output = cache_dir
import pickle
from datetime import timedelta
from argparse import ArgumentParser

def load_cache_quandl(ticker_ls=None, ticker=None, sdate=None, edate=None):
    # input cleaning
    if ticker_ls is None and ticker is None:
        df_index = pd.read_csv(input_dir + 'SP500.txt')
        ticker_ls = df_index['Tickers'].tolist()
    elif ticker_ls is None and ticker is not None:
        ticker_ls = [ticker]
    elif ticker_ls is not None and ticker is None:
        ticker_ls = ticker_ls
        
    if sdate is None:
        sdate = sdate_def
    if edate is None:
        edate = now_str
        
    res_data = pd.DataFrame()
    print "Caching..."
    for ticker in ticker_ls:
        print "..." + ticker
        sdate_req = sdate
        edate_req = edate
        curr_data = pd.DataFrame()
        data = pd.DataFrame()
        quandl_req = False
        if not os.path.exists(output + '/' + ticker):
            quandl_req = True
        else:
            with open(output + '/' + ticker, 'rb') as handle:
                curr_data = pickle.load(handle)
                sdate_curr = min(curr_data['date']).strftime("%Y-%m-%d")
                edate_curr = max(curr_data['date']).strftime("%Y-%m-%d")
            if sdate >= sdate_curr and edate <= edate_curr:
                quandl_req = False
            elif sdate > edate_curr:
                sdate_req = edate_curr
                quandl_req = True
            elif edate < sdate_curr:
                edate_req = sdate_curr
                quandl_req = True               
        if quandl_req:
            data_req = quandl.get_table('WIKI/PRICES', ticker = [ticker],
                                        qopts = { 'columns': ['ticker', 'date', 'close', 'open'] },
                                        date = { 'gte': sdate_req, 'lte': edate_req},
                                        paginate=True)
            if not data_req.empty:
                data_req['close_1'] = data_req['close'].shift(1)
                data_req['daily_return'] = (data_req['close'] - data_req['close_1'])/data_req['close_1']
                if not curr_data.empty:
                    data_req = curr_data.append(data_req)
                    data_req = data_req.sort_values(['date'],ascending=[True])
                    data_req = data_req.reset_index(drop=True)
                with open(output + '/' + ticker, 'wb') as handle:
                    pickle.dump(data_req, handle)
                data = data_req[(data_req['date'] >= sdate) & (data_req['date'] <= edate)]
        else:
            data = curr_data[(curr_data['date'] >= sdate) & (curr_data['date'] <= edate)]
        res_data = res_data.append(data, ignore_index = True)
    print "Done caching"

    return res_data

if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('--ticker_ls', required=False, default=None,
                        help='ticker_ls')
    parser.add_argument('--ticker', required=False, default=None,
                        help='ticker')
    parser.add_argument('--sdate', required=False, default=None,
                        help='start date')
    parser.add_argument('--edate', required=False, default=None,
                        help='end date')

    args = parser.parse_args()

    load_cache_quandl(ticker_ls = args.ticker_ls,
                      ticker=args.ticker,
                      sdate=args.sdate,
                      edate=args.edate)
