from argparse import ArgumentParser
import matplotlib.pyplot as plt
from pylab import *
from statics import sdate_def, now_str, cache_dir, plot_dir
import os
from cache_quandl import load_cache_quandl
import pickle

def calc_comp_return(ticker_ls=None, ticker=None, sdate=None, edate=None):
    # input cleaning
    if ticker_ls is None and ticker is None:
        ticker_ls = ['AAPL']
    elif ticker_ls is None and ticker is not None:
        ticker_ls = [ticker]
    elif ticker_ls is not None and ticker is None:
        ticker_ls = ticker_ls
        
    if sdate is None:
        sdate = sdate_def
    if edate is None:
        edate = now_str

    output = plot_dir + sdate + '_' + edate + '/'
    if not os.path.exists(output):
        os.mkdir(output)

    # load data
    data = load_cache_quandl(ticker_ls=ticker_ls,
                             ticker=ticker,
                             sdate=sdate,
                             edate=edate)
    
    # data processing:
    slope_dict = {}
    comp_ret_dict = {}
    print "Computing linear regression ..."
    for ticker in ticker_ls:
        print "..." + ticker
        data_tmp = data[data['ticker']==ticker]
        data_tmp = data_tmp.reset_index(drop=True)

        return_ls = []
        if not data_tmp.empty:

            output_plot = output + sdate + '_' + edate + '_' + ticker
            if not os.path.exists(output_plot + '.dict'):        
                for idx, row in data_tmp.iterrows():
                    if idx == 0:
                        curr_return = 1
                    else:
                        curr_return = prev_return * (1 + row['daily_return'])
                    return_ls.append(curr_return)
                    prev_return = curr_return
                data_tmp['comp_return'] = return_ls

                slope, intercept = polyfit(data_tmp.index, data_tmp['comp_return'], 1)

                # data plotting
                title = sdate + '_' + edate + '_' + ticker 
                f, axarr = plt.subplots(3)
                axarr[0].plot(data_tmp['date'],data_tmp['close'],color= 'green')
                axarr[0].set_title(title)
                axarr[1].plot(data_tmp['date'],data_tmp['daily_return'])
                axarr[2].bar(data_tmp.index,data_tmp['comp_return'],0.5)
                axarr[2].plot(data_tmp.index, slope*data_tmp.index+intercept, color = 'red')
                try:
                    plt.tight_layout()
                except:
                    print data_tmp                        
                f.savefig(output + title + '.pdf')
                plt.close()

                comp_ret_ticker = data_tmp['comp_return'].tolist()[len(data_tmp)-1]
                slope_ticker = slope
                
                with open(output_plot + '.dict', 'wb') as handle:
                    lin_reg_dict = {}
                    lin_reg_dict['comp_ret'] = comp_ret_ticker
                    lin_reg_dict['slope'] = slope_ticker
                    pickle.dump(lin_reg_dict, handle)
                # Done with computing linear regression for ticker
                
            with open(output_plot + '.dict', 'rb') as handle:
                lin_reg_dict = pickle.load(handle)
                comp_ret_dict[ticker] = lin_reg_dict['comp_ret']
                slope_dict[ticker] = lin_reg_dict['slope']
            # Done loading limear regressio for ticker
        else:
            print ticker + ' has no value for ' + sdate + '-' +edate
            comp_ret_dict[ticker] = 0
            slope_dict[ticker] = 0

    return comp_ret_dict, slope_dict

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

    calc_comp_return(ticker_ls = args.ticker_ls,
                     ticker=args.ticker,
                     sdate=args.sdate,
                     edate=args.edate)

    
