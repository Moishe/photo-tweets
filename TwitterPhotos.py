import json
import os
import random
import requests
import string
import time
import urllib

def translate_to_simple(photo):
  p = photo['photos'][0]
  return {
      'src': p['url'],
      'width': p['width'],
      'height': p['height'],
      'key': ''.join(random.choice(string.ascii_lowercase) for i in range(10)),
      'title': photo['tweet']['text']
  }
  
class TwitterPhotos:
  def __init__(self, list_id=None, list_name=None, user_name=None):
    self.list_id = list_id
    self.list_name = list_name
    self.user_name = user_name
    self.cache = {}

  def init_cache(self):
    try:
        f = open('cache.json')
        if f:
            self.cache = json.load(f)
        else:
            print('cache file not found')
    except FileNotFoundError:
        self.cache = {}

  def fetch_photo_tweets(self):
    self.init_cache()

    max_id = 0
    photo_data = []
    while len(photo_data) < 80:
        params = {
            'list_id': self.list_id,
            'count': 100,
            'include_entities': False,
            'include_rts': True,
        }
        if max_id > 0:
            params['max_id'] = max_id

        path = "1.1/lists/statuses.json?{}".format(urllib.parse.urlencode(params))
        res = self.make_authorized_request(path, use_cache=False)

        tweet_ids = [x['id'] for x in res]
        photo_data += self.get_photos_from_tweets(tweet_ids)
        max_id = min(tweet_ids)

        photo_data = sorted(photo_data, key=lambda x: time.strptime(x['tweet']['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'))

    simple_photos = []

    for el in photo_data:
      tweet_url = "https://twitter.com/" + el['user']['username'] + "/status/" + el['tweet']['id']

      for photo in el['photos']:
        simple_photos.append({
          'src': photo['url'],
          'width': photo['width'],
          'height': photo['height'],
          'key': ''.join(random.choice(string.ascii_lowercase) for i in range(10)),
          'title': el['tweet']['text'],
          'tweet_url': tweet_url
        })

    return json.dumps(simple_photos)

  def get_photos_from_tweets(self, tweet_ids):
      params = {
          'ids': ','.join([str(x) for x in tweet_ids]),
          'expansions': 'attachments.media_keys,author_id',
          'media.fields': 'height,media_key,preview_image_url,type,url,width,public_metrics',
          'tweet.fields': 'created_at,public_metrics,text',
          'user.fields': 'username'
      }
      path = '2/tweets?{}'.format(urllib.parse.urlencode(params))
      tweets_json = self.make_authorized_request(path)
      photos = []

      media_map = {}
      for media in tweets_json['includes']['media']:
          if media['type'] == 'photo':
              media_map[media['media_key']] = media

      user_id_map = {}
      for user in tweets_json['includes']['users']:
        user_id_map[user['id']] = user

      for tweet in tweets_json['data']:
          if ('attachments' in tweet) and ('media_keys' in tweet['attachments']):
              photo_data = {
                  'photos': [],
                  'tweet': tweet,
                  'user': user_id_map[tweet['author_id']]
              }
              
              for media_key in tweet['attachments']['media_keys']:
                  if media_key in media_map:
                      photo_data['photos'].append(media_map[media_key])

              if len(photo_data['photos']):
                  photos.append(photo_data)
      
      return photos

 
  def auth(self):
      return os.environ.get("BEARER_TOKEN")

  def make_authorized_request(self, path, use_cache=True):
      bearer_token = self.auth()
      url = "https://api.twitter.com/{}".format(path)
      print("requesting: %s" % url)
      headers = self.create_headers(bearer_token)
      json_response = self.connect_to_endpoint(url, headers, use_cache)
      return json_response

  def create_headers(self, bearer_token):
      headers = {"Authorization": "Bearer {}".format(bearer_token)}
      return headers

  def save_cache(self):
      f = open('cache.json', 'w')
      json.dump(self.cache, f)

  def connect_to_endpoint(self, url, headers, use_cache=True):
      if use_cache and url in self.cache:
          print("using cached url: %s" % url)
          return self.cache[url]
      print("url not cached or cache disabled for request: %s" % url)
      tries = 0
      MAX_TRIES = 8
      backoff = 15
      while tries < MAX_TRIES:
          # this is janky, but I want to throttle responses even before we get a 429
          #time.sleep(backoff)
          response = requests.request("GET", url, headers=headers)
          if response.status_code == 200:
              self.cache[url] = response.json()
              self.save_cache()
              return response.json()
          elif response.status_code == 429:
              print("Request timed out. Waiting %d second(s) to retry" % backoff)
              tries += 1
              backoff = backoff * 2
          else:
              break
              
      raise Exception(
          "Request returned an error: {} {}".format(
              response.status_code, response.text
          )
      )

if __name__ == "__main__":
  js = TwitterPhotos('1344411611960901637').fetch_photo_tweets()
  print(json.dumps(js, indent=2))
    
