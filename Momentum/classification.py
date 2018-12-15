from comp_return import calc_comp_return
from argparse import ArgumentParser
import pandas as pd
import matplotlib.pyplot as plt
from statics import sdate_def, now_str, input_dir, plot_dir

def load_classification(ticker_ls = None, sdate=None, edate=None):
    # load tickers
    if ticker_ls is None:
        df_index = pd.read_csv(input_dir + 'SP500.txt')
        ticker_ls = df_index['Tickers'].tolist()
    if sdate is None:
        sdate = sdate_def
    if edate is None:
        edate = now_str

    # load compounded returns
    comp_ret_dict = {}
    slope_dict = {}
    i = 0
    step = 20
    while i < 500:
        ticker_ls_tmp = ticker_ls[i:i+step]
        comp_ret_dict_tmp, slope_dict_tmp = calc_comp_return(
            ticker_ls = ticker_ls_tmp,
            sdate = sdate,
            edate = edate)
        comp_ret_dict.update(comp_ret_dict_tmp)
        slope_dict.update(slope_dict_tmp)
        i += step

    slope_ls = []
    comp_ret_ls = []
    ticker_ls = []
    for ticker in slope_dict:
        slope_ls.append(slope_dict[ticker])
        comp_ret_ls.append(comp_ret_dict[ticker])       
        ticker_ls.append(ticker)

    # data plotting
    output = plot_dir + '/' + sdate + '_' + edate + '/'
    title = sdate + '_' + edate + '_' + 'SP500'
    f, axarr =  plt.subplots()
    axarr.scatter(slope_ls, comp_ret_ls)
    for i, txt in enumerate(ticker_ls):
        axarr.annotate(txt,(slope_ls[i], comp_ret_ls[i]))
    axarr.set_title(title)
    f.savefig(output + title + '_scatter.pdf')
    f.clf()

    # extract highest momentum tickers
    idx_ls = sorted(range(len(slope_ls)), key=lambda i: slope_ls[i])[-5:]

    top5_ticker = []
    top5_slope = []
    top5_comp_ret = []
    for  idx in idx_ls:
        top5_ticker.append(ticker_ls[idx])
        top5_slope.append(slope_ls[idx])
        top5_comp_ret.append(comp_ret_ls[idx])

    return top5_ticker

if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('--ticker_ls', required=False, default=None,
                        help='ticker_ls')
    parser.add_argument('--sdate', required=False, default=None,
                        help='start date')
    parser.add_argument('--edate', required=False, default=None,
                        help='end date')

    args = parser.parse_args()

    load_classification(ticker_ls = args.ticker_ls,
                        sdate=args.sdate,
                        edate=args.edate)
    
