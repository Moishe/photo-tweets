from collections import defaultdict
import json
import os
import time
import urllib.parse
import requests

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'

cache = {}

def load_cache():
    global cache
    f = open('cache.json')
    if f:
        cache = json.load(f)
        print(json.dumps(cache))
    else:
        print('cache file not found')

def save_cache():
    global cache
    f = open('cache.json', 'w')
    json.dump(cache, f)

def auth():
    return os.environ.get("BEARER_TOKEN")

def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

def connect_to_endpoint(url, headers):
    if url in cache:
        print("using cached url: %s" % url)
        return cache[url]
    print("url not cached: %s" % url)
    tries = 0
    MAX_TRIES = 8
    backoff = 1
    while tries < MAX_TRIES:
        response = requests.request("GET", url, headers=headers)
        if response.status_code == 200:
            cache[url] = response.json()
            save_cache()
            return response.json()
        elif response.status_code == 429:
            print("Request timed out. Waiting %d second(s) to retry" % backoff)
            tries += 1
            time.sleep(backoff)
            backoff = backoff * 2
        else:
            break
            
    raise Exception(
        "Request returned an error: {} {}".format(
            response.status_code, response.text
        )
    )

def make_authorized_request(path):
    bearer_token = auth()
    url = "https://api.twitter.com/2/{}".format(path)
    print("requesting: %s" % url)
    headers = create_headers(bearer_token)
    json_response = connect_to_endpoint(url, headers)
    return json_response

class PhotoTweet:
    def __init__(self, id):
        # get all the tweet info
        pass

class UserFactory:
    def __init__(self):
        self.all_users = {}

    def get_user(self, id):
        if id in self.all_users:
            return self.all_users[id]
        else:
            u = User(id)
            self.all_users[id] = u
            return u

    def bulk_populate(self, ids=None, users=None):
        if not ids and not users:
            users = self.all_users.values()[:100] # todo: filter this if it ever matters

        if not ids:
            ids = [x.id for x in users]

        params = {
            'ids': ','.join(ids)
        }
        path = 'users?ids={}'.format(','.join(ids))
        user_data = make_authorized_request(path)

        for user in user_data['data']:
            self.all_users[user['id']].set_data(user)

class User:
    def __init__(self, id, data=None):
        self.id = id
        self.data = None

    def set_data(self, data):
        self.data = data

    def get_photos(self):
        params = {
            'max_results': 100,
            'exclude' : 'retweets',
            'expansions': 'attachments.media_keys',
            'media.fields': 'height,media_key,preview_image_url,type,url,width,public_metrics'
        }
        path = 'users/{}/tweets?{}'.format(self.id, urllib.parse.urlencode(params))
        tweets_json = make_authorized_request(path)
        photos = []
        media_map = None
        for tweet in tweets_json['data']:
            if ('attachments' in tweet) and ('media_keys' in tweet['attachments']):
                if not media_map:
                    media_map = {}
                    for media in tweets_json['includes']['media']:
                        if media['type'] == 'photo':
                            media_map[media['media_key']] = media
                
                for media_key in tweet['attachments']['media_keys']:
                    if media_key in media_map:
                        photos.append(media_map[media_key])

        return photos

    def get_friend_ids(self):
        params = {
            'max_results': 10,
            'user.fields': 'id'
        }
        path = 'users/{}/following?{}'.format(self.id, urllib.parse.urlencode(params))
        ids_json = make_authorized_request(path)        
        if 'data' in ids_json:
            return [x['id'] for x in ids_json['data']]
        else:
            return []

class FollowGraph:
    def __init__(self, root_user, user_factory):
        self.root_user = root_user
        self.queue = [root_user.id]
        self.edges = {}
        self.all_ids = set()
        self.user_factory = user_factory

    def populate(self):
        total_processed = 0
        while self.queue and (total_processed < 45):
            total_processed += 1
            print("%d" % total_processed)
            u = self.user_factory.get_user(self.queue.pop())
            friends = u.get_friend_ids()
            self.queue += friends
            self.edges[u.id] = friends

        follower_counts = defaultdict(int)
        for friends in self.edges.values():
            for friend in friends:
                follower_counts[friend] += 1

        self.follower_counts = list(reversed(sorted(follower_counts.items(), key=lambda item: item[1])))

    def top_n(self, n):
        return [self.user_factory.get_user(x[0]) for x in self.follower_counts[:n]]

class RootUser:
    def __init__(self, name):
        self.name = name
        print("created with %s" % self.name)
    
    def populate(self):
        json_response = make_authorized_request('users/by?usernames={}'.format(self.name))
        id = json_response['data'][0]['id']
        u = User(id)
        return u

class UserGraph:
    def __init(self, seed_name):
        # load the user with the name and build the graph of follow/followers out from that user
        self.users_by_id = {}
        self.follows = {}

# basic idea:
#   start at known-good user
#   find everyone they follow
#   for each of these users:
#       add to users_by_id
#       add to follows
#       enqueue at depth for BFS
# once we get to #depth, we can run pagerank to rank users
#
# then, for every user, get _n_ most recent tweets, filtered by

def create_url():
    # Specify the usernames that you want to lookup below
    # You can enter up to 100 comma-separated values.
    usernames = "usernames=moishelettvin"
    user_fields = "user.fields=description,created_at"
    # User fields are adjustable, options include:
    # created_at, description, entities, id, location, name,
    # pinned_tweet_id, profile_image_url, protected,
    # public_metrics, url, username, verified, and withheld
    url = "https://api.twitter.com/2/users/by?{}&{}".format(usernames, user_fields)
    return url

def create_tweet_url():
    url = "https://api.twitter.com/2/tweets?ids=1410202992817496071&expansions=attachments.media_keys&media.fields=duration_ms,height,media_key,preview_image_url,public_metrics,type,url,width"
    return url

def main():
    load_cache()

    ru = RootUser('moishelettvin')
    u = ru.populate()

    uf = UserFactory()

    fg = FollowGraph(u, uf)
    fg.populate()

    users = fg.top_n(10)

    uf.bulk_populate(users=users)

    photo_data = []
    for u in users:
        photos = u.get_photos()
        for photo in photos:
            photo_data.append({
                'photo': photo,
                'user': u.data
            })

    f = open('photos.json', 'w')
    json.dump(photo_data, f, indent=2)

    save_cache()


if __name__ == "__main__":
    main()
