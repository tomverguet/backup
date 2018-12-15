import os
import csv
import pandas as pd
import tweepy
from argparse import ArgumentParser
from statics import api_key, api_secret, token, token_secret
from statics import output_folder
from datetime import datetime
now = datetime.now()
now_str = now.strftime("%Y-%m-%d")


def get_all_tweets(screen_name):
    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(token, token_secret)
    api = tweepy.API(auth)

    alltweets = []
    new_tweets = api.user_timeline(screen_name = screen_name,count=500)
    alltweets.extend(new_tweets)
    oldest = alltweets[-1].id - 1
    while len(new_tweets) > 0:
        print "... getting tweets before %s" % (oldest)

        new_tweets = api.user_timeline(screen_name = screen_name,
                                       count=500,
                                       max_id=oldest)
        alltweets.extend(new_tweets)
        oldest = alltweets[-1].id - 1
        print "... %s tweets downloaded so far" % (len(alltweets))

    df_tweets = pd.DataFrame([])
    for tweet in alltweets:
        row = pd.Series([tweet.id_str,
                         tweet.created_at.strftime('%Y-%m-%d'),
                         tweet.created_at.strftime('%H:%M:%S'),
                         tweet.text.encode("utf-8")])
        df_tweets = df_tweets.append(row, ignore_index = True)
    df_tweets.columns = ['id', 'date', 'time', 'txt']
    #outtweets = [[tweet.id_str,
    #              tweet.created_at,
    #              tweet.text.encode("utf-8")] for tweet in alltweets]

    output = output_folder + screen_name
    if not os.path.exists(output):
        os.mkdir(output)
    for date in df_tweets['date'].tolist():
        df_tweets_date = df_tweets[df_tweets['date'] == date]
        df_tweets_date.to_csv(output + '/' + str(date) + '_' + screen_name + ',csv',
                              index=False)

        #with open(output + '/' + date + '_' + screen_name + ',csv', 'wb') as f:
        #    writer = csv.writer(f)
        #    writer.writerow(["id","created_at","text"])
        #    writer.writerows(outtweets)
        #pass

def main(accounts_ls = None, sdate=None, edate=None):

    if accounts_ls is None:
        df_accounts = pd.read_csv(output_folder + 'accounts.txt')
    if sdate is None:
        sdate = now_str
    if edate is None:
        edate = now_str

    for acct in df_accounts['screen_name'].tolist():
        print 'Processing ' + acct + ' ...'
        get_all_tweets(acct)

if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('--accounts_ls', required=False, default=None,
                        help='accounts list')
    parser.add_argument('--sdate', required=False, default=None,
                        help='start date')
    parser.add_argument('--edate', required=False, default=None,
                        help='end date')

    args = parser.parse_args()

    main(accounts_ls = args.accounts_ls,
         sdate=args.sdate,
         edate=args.edate)
