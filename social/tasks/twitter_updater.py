import json
from datetime import datetime
import time
import Queue
import requests
import logging
from itertools import cycle
from twython import Twython, TwythonError
from urlparse import urlparse, parse_qs
import gevent
from gevent.queue import JoinableQueue

from .. import settings
from ..models import TwitterAccount, TwitterSearch, TwitterMessage, TweetExistsError
from ..settings import SOCIAL_TWITTER_CONSUMER_KEY, SOCIAL_TWITTER_CONSUMER_SECRET


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)




class TwitterUpdater():
    def __init__(self):
        self.accounts = self._accounts_generator()
        self.q = JoinableQueue()
    
    def _accounts_generator(self):
        accounts = cycle(TwitterAccount.objects.all())
        while True:
            a = next(accounts)
            if not a.valid:
                accounts = [x for x in accounts if x.valid]
                if len(accounts) == 0:
                    log.error('!!! ACCOUNTS EXHAUSTED !!!')
                    raise StopIteration

                accounts = cycle(accounts)
                continue
            twitter = Twython(  app_key=SOCIAL_TWITTER_CONSUMER_KEY, 
                                app_secret=SOCIAL_TWITTER_CONSUMER_SECRET, 
                                oauth_token=a.oauth_token, 
                                oauth_token_secret=a.oauth_secret)
            yield twitter

    def update(self):
        #now = int(time.time())
        threads = []
        for term in TwitterSearch.objects.all():
            threads.append(gevent.spawn(self._step, term))
        gevent.joinall(threads)
        log.debug("ALL DONE!")

        # for term in TwitterSearch.objects.all():
        #     self._step(term)
    
    def _step(self, term, max_id=0):
        
        try:
            twitter = self.accounts.next()
        except:
            # no accounts, or they are alld ead
            return

        try:
            log.warning('[twitter] search_term:%s', term.search_term)
            log.warning('[twitter] max_id:%s', max_id)
            gevent.sleep(0)
            response = twitter.search(q=term.search_term, count='100', max_id=max_id)
        except TwythonError:
            log.error('[twython error] hit twitter too much!')
            return
        tweets = response.get('statuses',None)

        if len(tweets) == 0:
            log.warning('[twitter] no tweets for search term %s',term.search_term)
            return
        for tweet in tweets:
            try:
                # create tweet and make sure it's unique based on id_str and search term
                dj_tweet = TwitterMessage.create_from_json(tweet, term)
            except TweetExistsError:
                # item already exists, stop reading
                log.warning('[twitter] kicking out (tweet exists)')
                return
            except Exception as e:
                log(e)
                return
            epoch = int(time.mktime(dj_tweet.date.timetuple()))
            
            if epoch < term.search_until:
                # tweet was created before your limit, stop
                log.warning('[twitter] kicking out (tweet is too old)')
                return
            

        # print(response.get('search_metadata'))
        # sometimes the max_id_str was coming back empty... had to get it here instead
        try:
            max_id = parse_qs(urlparse(response.get('search_metadata').get('next_results')).query).get('max_id')
        except:
            log.warning('issues with twitter: %s', response.get('search_metadata'))
            return
        self._step(term,max_id=max_id)

    # def _step(self, term, max_id=0):
    #     try:
    #         twitter = self._create_twython_object()
    #     except:
    #         return
    #     try:
    #         log.warning('[twitter] search_term:%s', term.search_term)
    #         log.warning('[twitter] max_id:%s', max_id)
    #         response = twitter.search(q=term.search_term, count='100', max_id=max_id)
    #     except TwythonError:
    #         log.error('[twython error] hit twitter too much!')
    #         return
    #     tweets = response.get('statuses',None)
    #     if len(tweets) == 0:
    #         log.warning('[twitter] no tweets for search term %s',term.search_term)
    #         return
    #     for tweet in tweets:
    #         try:
    #             # create tweet and make sure it's unique based on id_str and search term
    #             dj_tweet = TwitterMessage.create_from_json(tweet, term)
    #         except TweetExistsError:
    #             # item already exists, stop reading
    #             log.warning('[twitter] kicking out (tweet exists)')
    #             return
    #         epoch = int(time.mktime(dj_tweet.date.timetuple()))
            
    #         if epoch < term.search_until:
    #             # tweet was created before your limit, stop
    #             log.warning('[twitter] kicking out (tweet is too old)')
    #             return
            

    #     # print(response.get('search_metadata'))
    #     # sometimes the max_id_str was coming back empty... had to get it here instead
    #     try:
    #         max_id = parse_qs(urlparse(response.get('search_metadata').get('next_results')).query).get('max_id')
    #     except:
    #         log.warning('issues with twitter:%s', response.get('search_metadata'))
    #     self._step(term,max_id=max_id)
            
    # def _create_twython_object(self):
    #     account = TwitterAccount.get_next_up()
    #     if not account:
    #         raise Exception("no twitter accounts setup")
    #     twitter = Twython(  app_key=SOCIAL_TWITTER_CONSUMER_KEY, 
    #                         app_secret=SOCIAL_TWITTER_CONSUMER_SECRET, 
    #                         oauth_token=account.oauth_token, 
    #                         oauth_token_secret=account.oauth_secret)
    #     return twitter

