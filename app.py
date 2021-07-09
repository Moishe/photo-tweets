from flask import Flask
from flask import request
from flask import Response
from flask_cors import CORS

import json
import re
import TwitterPhotos

app = Flask(__name__, static_url_path='')
CORS(app)

def guess_url_stuff(url):
  m = re.search('https://twitter.com/i/lists/([0-9]+)', url)
  if m:
    return {'list_id': m.group(1)}

  m = re.search('https://twitter.com/(\w{1,15})', url)
  if m:
    return {'user_name': m.group(1)}
  
  return {'list_id': '1344411611960901637'}

@app.route("/")
def hello_world():
  return app.send_static_file('index.html')

@app.route("/photos")
def get_photos():
  global app

  url = request.args.get('url')
  params = guess_url_stuff(url)
  app.logger.info(json.dumps(params))

  js = TwitterPhotos.TwitterPhotos(**params).fetch_photo_tweets()
  return Response(js, mimetype='application/json')
