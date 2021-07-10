from flask import Flask
from flask import request
from flask import Response
from flask_cors import CORS

import json
import re
import TwitterPhotos

app = Flask(__name__, static_url_path='')
CORS(app)

@app.route("/")
def hello_world():
  return app.send_static_file('index.html')

@app.route("/photos")
def get_photos():
  global app

  url = request.args.get('url')
  params = TwitterPhotos.guess_url_stuff(url)
  app.logger.info(json.dumps(params))

  js = TwitterPhotos.TwitterPhotos(**params).fetch_photo_tweets()
  return Response(js, mimetype='application/json')
