from django.conf import settings


SOCIAL_AUTO_APPROVE = getattr(settings, 'SOCIAL_TWITTER_AUTO_APPROVE', 1)
SOCIAL_FACEBOOK_INTERVAL = getattr(settings, 'SOCIAL_FACEBOOK_INTERVAL', 15)
SOCIAL_TWITTER_INTERVAL = getattr(settings, 'SOCIAL_TWITTER_INTERVAL', 15)

SOCIAL_FACEBOOK_APP_ID = getattr(settings, 'SOCIAL_FACEBOOK_APP_ID', None)
SOCIAL_FACEBOOK_APP_SECRET = getattr(settings, 'SOCIAL_FACEBOOK_APP_SECRET', None)

SOCIAL_TWITTER_CONSUMER_KEY = getattr(settings, 'SOCIAL_TWITTER_CONSUMER_KEY', None)
SOCIAL_TWITTER_CONSUMER_SECRET = getattr(settings, 'SOCIAL_TWITTER_CONSUMER_SECRET', None)

