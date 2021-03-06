'''
Created on Sep 26, 2013
'''

def parse_twitter_picture_embed(msg, width="200px", height="200px"):
    urls = msg.get('entities', {}).get('utls', [])
    
    picture = None
    for url in urls:
        if 'pic.twitter.com':
            picture = url
    
    if not picture:
        return ''

    return '<img src="{}" width="{}" height="{}">'.format(picture, width, height)

def parse_twitter_video_embed(msg, width="200px", height="200px"):
    """ need to put in proper video embed here """
    urls = msg.get('entities', {}).get('urls', [])
    
    video = None
    for url in urls:
        if url.get('expanded_url',None) == None:
            u = url.get('url','')
        else:
            u = url.get('expanded_url','')

        if 'youtu.be' in u or 'youtube.com' in u or 'vine.co' in u:
            video = u

    if video:
        if 'vine.co' in video:
            return '<iframe class="vine-embed" src="{}/embed/simple" frameborder="0" width="{}" height="{}"></iframe><script async src="//platform.vine.co/static/scripts/embed.js" charset="utf-8"></script>'.format(video, width, height)
    
        return '<video src="{}" width="{}" height="{}">'.format(video, width, height)

    return 'no url found'