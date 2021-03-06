import requests

from logging import getLogger

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from . import settings
from .models import TwitterAccount, InstagramAccount
from .services.twitter import TwitterAPI

log = getLogger('social.views')


def begin_auth(request):
    twitter = TwitterAPI(
        client_key = settings.SOCIAL_TWITTER_CONSUMER_KEY,
        client_secret = settings.SOCIAL_TWITTER_CONSUMER_SECRET,
        callback_url = request.build_absolute_uri(reverse('social.views.thanks'))
    )

    auth_props = twitter.get_authentication_tokens()
    request.session['auth_props'] = auth_props

    return HttpResponseRedirect(auth_props['auth_url'])

def thanks(request, redirect_url='/admin/social/twitteraccount/'):
    try:
        request.session['auth_props']['resource_owner_key']
    except:
        log.error('wrong domain, your auth_props are not stored in session')
        raise Exception('wrong domain, your auth_props are not stored in session')
    twitter = TwitterAPI(
        client_key = settings.SOCIAL_TWITTER_CONSUMER_KEY,
        client_secret = settings.SOCIAL_TWITTER_CONSUMER_SECRET,
        resource_owner_key = request.session['auth_props']['resource_owner_key'],
        resource_owner_secret = request.session['auth_props']['resource_owner_secret'],
        verifier=request.GET.get('oauth_verifier')
    )
    authorized_tokens = twitter.get_authorized_tokens()
    log.info("authorized_tokens: {}".format(authorized_tokens))


    try:
        account = TwitterAccount.objects.get(screen_name=authorized_tokens['screen_name'])
        account.update_credentials(authorized_tokens)
    except TwitterAccount.DoesNotExist:
        account_info = twitter.show_user(screen_name=authorized_tokens['screen_name'])
        TwitterAccount.create_from_obj(
            account_info,
            oauth_token=authorized_tokens['oauth_token'],
            oauth_token_secret=authorized_tokens['oauth_token_secret'])

    return HttpResponseRedirect(redirect_url)

def instauth(request):
    data = {
        'client_id': settings.SOCIAL_INSTAGRAM_CLIENT_ID,
        'client_secret': settings.SOCIAL_INSTAGRAM_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'redirect_uri': settings.SOCIAL_INSTAGRAM_REDIRECT_URI,
        'code': request.GET.get('code'),
    }

    res = requests.post('https://api.instagram.com/oauth/access_token',
                        data=data)

    if res.ok:
        response = res.json()
        user = response['user']
        print response
        print user
        InstagramAccount.objects.create(
            instagram_id = user['id'],
            username = user['username'],
            name = user['full_name'],
            profile_picture = user['profile_picture'],
            access_token = response['access_token'],
        )

    return HttpResponseRedirect(reverse('admin:social_instagramaccount_changelist'))
